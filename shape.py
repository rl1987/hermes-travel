"""Normalize actor dataset rows into stay/transport cards. Internal only."""

from __future__ import annotations

from datetime import datetime
from typing import Any

DEFAULT_CAP = 8
STAY_SOURCES = frozenset({"booking", "airbnb", "agoda", "hostelworld"})
TRANSPORT_SOURCES = frozenset({"flixbus", "rome2rio", "flights", "changi"})

EUROPE_HINTS = (
    "europe", "eu ", " uk", "united kingdom", "england", "scotland", "wales",
    "ireland", "france", "paris", "lyon", "marseille", "germany", "berlin",
    "munich", "hamburg", "cologne", "frankfurt", "spain", "madrid", "barcelona",
    "italy", "rome", "milan", "florence", "venice", "naples", "portugal",
    "lisbon", "porto", "netherlands", "amsterdam", "rotterdam", "belgium",
    "brussels", "bruges", "austria", "vienna", "switzerland", "zurich", "geneva",
    "prague", "czech", "budapest", "hungary", "poland", "warsaw", "krakow",
    "sweden", "stockholm", "norway", "oslo", "denmark", "copenhagen",
    "finland", "helsinki", "greece", "athens", "croatia", "zagreb", "split",
    "romania", "bucharest", "bulgaria", "sofia", "slovakia", "slovenia",
    "estonia", "latvia", "lithuania", "vilnius", "riga", "tallinn",
)

CHANGI_HINTS = ("singapore", "changi", "sin airport", "airport sin", "sin,", "sin ")


def _s(row: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        val = row.get(key)
        if val is None:
            continue
        if isinstance(val, str) and val.strip():
            return val.strip()
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return str(val)
        if isinstance(val, list) and val and all(isinstance(x, str) for x in val):
            joined = ", ".join(x.strip() for x in val if x and x.strip())
            if joined:
                return joined
    nested = row.get("location") or row.get("address") or row.get("geo")
    if isinstance(nested, dict):
        found = _s(nested, *keys)
        if found:
            return found
    return None


def _n(row: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        val = row.get(key)
        if isinstance(val, bool) or val is None:
            continue
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            cleaned = val.replace(",", "").replace("$", "").strip()
            try:
                return float(cleaned)
            except ValueError:
                continue
        if isinstance(val, dict):
            nested = _n(val, "amount", "value", "price", "min", "from", "total", "perStay", "perNight", "book")
            if nested is not None:
                return nested
    return None


def _id_from(row: dict[str, Any], source: str, idx: int) -> str:
    raw = _s(row, "id", "propertyId", "hotelId", "listingId", "tripId", "uid", "url", "tripUid", "slice_id", "fare_id")
    if raw:
        return f"{source}:{raw}"[:120]
    return f"{source}:{idx}"


def nights_between(checkin: str | None, checkout: str | None) -> int:
    if not checkin or not checkout:
        return 2
    try:
        a = datetime.strptime(checkin[:10], "%Y-%m-%d")
        b = datetime.strptime(checkout[:10], "%Y-%m-%d")
        delta = (b - a).days
        return max(1, min(delta, 31))
    except ValueError:
        return 2


def looks_european(*places: str) -> bool:
    blob = " ".join(p.lower() for p in places if p)
    return any(h in blob for h in EUROPE_HINTS)


def looks_changi(*places: str) -> bool:
    blob = " ".join((" " + p.lower() + " ") for p in places if p)
    return any(h in blob or "chang" in blob and "sing" in blob for h in CHANGI_HINTS) or " sin" in blob or blob.strip().endswith("sin") or "changi" in blob or "singapore" in blob


def extract_stay(row: Any, source: str, idx: int = 0) -> dict[str, Any] | None:
    if not isinstance(row, dict):
        return None
    # Some actors (e.g. booking, in search mode) only surface name/city/score
    # under a nested container and need includeDetails-style opt-in fields.
    lookup: dict[str, Any] = dict(row)
    for container_key in ("details", "address", "location", "price"):
        nested = row.get(container_key)
        if isinstance(nested, dict):
            for k, v in nested.items():
                lookup.setdefault(k, v)
    name = _s(lookup, "name", "title", "propertyName", "hotelName", "listingName", "displayName")
    if not name:
        return None
    price = _n(row, "price", "displayPrice", "priceFrom", "minPrice", "totalPrice", "fromPrice", "pricePerNight")
    currency = _s(lookup, "currency", "currencyCode", "priceCurrency") or "USD"
    score = _n(lookup, "score", "reviewScore", "rating", "guestRating", "stars", "overallRating")
    area = _s(lookup, "area", "neighbourhood", "neighborhood", "district", "city", "address", "subtitle")
    url = _s(lookup, "url", "link", "deeplink", "bookingUrl", "deep_link_url")
    kind = _s(lookup, "kind", "type", "propertyType", "accommodationType") or (
        "hostel" if source == "hostelworld" else "home" if source == "airbnb" else "hotel"
    )
    src = source if source in STAY_SOURCES else "booking"
    card: dict[str, Any] = {
        "id": _id_from(row, src, idx),
        "name": name,
        "kind": kind,
        "area": area,
        "price": price,
        "currency": currency,
        "score": score,
        "url": url,
        "source": src,
    }
    return card


def extract_transport(
    row: Any, source: str, idx: int = 0, *, default_currency: str | None = None
) -> dict[str, Any] | None:
    if not isinstance(row, dict):
        return None
    name = _s(
        row,
        "name", "title", "operator", "companyName", "airline", "flightNumber",
        "routeName", "mode", "operators", "provider", "primary_carrier", "carrier",
    )
    if not name:
        return None
    mode = (_s(row, "mode", "vehicle", "transportType", "kind") or (
        "flight" if source in {"changi", "flights"} else "bus" if source == "flixbus" else "route"
    )).lower()
    src = source if source in TRANSPORT_SOURCES else "rome2rio"
    if source == "changi":
        direction = _s(row, "direction")
        other = _s(row, "airport")
        frm, to = (other, "SIN") if direction == "arr" else ("SIN", other)
    else:
        frm = _s(row, "from", "origin", "fromCity", "departureCity", "fromName", "source", "departureCityName", "fromCityInput")
        to = _s(row, "to", "destination", "toCity", "arrivalCity", "toName", "arrivalCityName", "toCityInput")
    card: dict[str, Any] = {
        "id": _id_from(row, src, idx),
        "mode": mode,
        "from": frm,
        "to": to,
        "depart": _s(
            row, "depart", "departure", "departureTime", "scheduledDeparture", "std", "dateOfJourney",
            "departureDate", "departureDateInput", "departure_time", "departure_date",
            "scheduled_time", "scheduled_date", "display_timestamp",
        ),
        "arrive": _s(
            row, "arrive", "arrival", "arrivalTime", "scheduledArrival", "sta",
            "arrivalDate", "arrival_time",
        ),
        "durationMin": _n(row, "durationMin", "durationMinutes", "duration", "travelTime", "duration_minutes"),
        "price": _n(
            row, "price", "displayPrice", "fare", "minPrice", "fromPrice",
            "priceTotalWithFee", "priceTotal", "priceOriginal", "price_total", "priceLow", "priceHigh",
        ),
        "currency": _s(row, "currency", "currencyCode", "priceCurrency") or default_currency or "USD",
        "operator": _s(row, "operator", "companyName", "airline", "carrier", "operators", "provider", "primary_carrier") or name,
        "url": _s(row, "url", "link", "deeplink"),
        "source": src,
    }
    return card


def shape_stays(items: Any, source: str, *, cap: int = DEFAULT_CAP, max_price: float | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(items, list):
        return out
    for i, row in enumerate(items):
        card = extract_stay(row, source, i)
        if not card:
            continue
        if max_price is not None and card.get("price") is not None and card["price"] > max_price:
            continue
        out.append(card)
        if len(out) >= cap:
            break
    return out


def shape_transport(
    items: Any, source: str, *, cap: int = DEFAULT_CAP, default_currency: str | None = None
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(items, list):
        return out
    for i, row in enumerate(items):
        card = extract_transport(row, source, i, default_currency=default_currency)
        if not card:
            continue
        out.append(card)
        if len(out) >= cap:
            break
    return out


def sort_stays(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(c: dict[str, Any]) -> tuple:
        price = c.get("price")
        score = c.get("score") or 0
        return (price if isinstance(price, (int, float)) else 1e18, -float(score))

    return sorted(cards, key=key)


def merge_cap(cards: list[dict[str, Any]], cap: int = DEFAULT_CAP) -> list[dict[str, Any]]:
    return cards[:cap]
