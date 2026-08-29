"""Tool handlers — always return a JSON string, never raise."""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

from .apify_client import run_actor_and_collect
from . import shape

# Private internal map — never expose ids to the model.
_ACTORS = {
    "booking": "rl1987~booking-api-scraper",
    "airbnb": "rl1987~airbnb-api-scraper",
    "agoda": "rl1987~agoda-scraper",
    "hostelworld": "rl1987~hostelworld-api-scraper",
    "flixbus": "rl1987~flixbus-api-scraper",
    "rome2rio": "rl1987~rome2rio-api-scraper",
    "flights": "rl1987~hopper-api-scraper",
    "changi": "rl1987~sin-airport-timetable",
}


def _ok_str(args: dict, *keys: str) -> str | None:
    for key in keys:
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _int(args: dict, key: str, default: int) -> int:
    try:
        return int(args.get(key) if args.get(key) is not None else default)
    except (TypeError, ValueError):
        return default


def _price_cap(args: dict, *keys: str) -> float | None:
    for key in keys:
        val = args.get(key)
        if val is None or val == "":
            continue
        try:
            return float(val)
        except (TypeError, ValueError):
            continue
    return None


def _public_error(exc: BaseException | str) -> str:
    msg = str(exc)
    for junk in ("actorId", "Actor ", "apify", "rl1987~"):
        msg = msg.replace(junk, "")
    return json.dumps({"error": msg.strip() or "search failed"})


def _collect(kind: str, payload: dict[str, Any], max_items: int = shape.DEFAULT_CAP) -> dict[str, Any]:
    actor = _ACTORS[kind]
    result = run_actor_and_collect(actor, payload, max_items=max_items)
    return result if isinstance(result, dict) else {"error": "empty"}


def _stay_result(kind: str, payload: dict[str, Any], *, max_price: float | None = None) -> str:
    try:
        raw = _collect(kind, payload)
        if raw.get("error"):
            return json.dumps({"error": str(raw.get("message") or raw["error"])})
        picks = shape.shape_stays(raw.get("items") or [], kind, cap=shape.DEFAULT_CAP, max_price=max_price)
        return json.dumps({"picks": picks})
    except Exception as exc:  # noqa: BLE001
        return _public_error(exc)


def _transport_result(kind: str, payload: dict[str, Any]) -> str:
    try:
        raw = _collect(kind, payload)
        if raw.get("error"):
            return json.dumps({"error": str(raw.get("message") or raw["error"])})
        picks = shape.shape_transport(raw.get("items") or [], kind, cap=shape.DEFAULT_CAP)
        return json.dumps({"picks": picks})
    except Exception as exc:  # noqa: BLE001
        return _public_error(exc)


def _lodging_payload_booking(args: dict) -> tuple[dict[str, Any] | None, str | None, float | None]:
    dest = _ok_str(args, "destination", "search")
    checkin = _ok_str(args, "checkin", "checkIn")
    checkout = _ok_str(args, "checkout", "checkOut")
    if not dest or not checkin or not checkout:
        return None, "Need destination, checkin, and checkout", None
    guests = _int(args, "guests", _int(args, "adults", 2))
    rooms = _int(args, "rooms", 1)
    currency = _ok_str(args, "currency") or "USD"
    max_price = _price_cap(args, "max_price", "budget")
    payload = {
        "search": dest,
        "checkin": checkin,
        "checkout": checkout,
        "rooms": rooms,
        "adults": guests,
        "currency": currency,
        "maxItems": shape.DEFAULT_CAP,
    }
    return payload, None, max_price


def _lodging_payload_airbnb(args: dict) -> tuple[dict[str, Any] | None, str | None, float | None]:
    dest = _ok_str(args, "destination", "search")
    checkin = _ok_str(args, "checkin", "checkIn")
    checkout = _ok_str(args, "checkout", "checkOut")
    if not dest or not checkin or not checkout:
        return None, "Need destination, checkin, and checkout", None
    payload = {
        "searchQueries": [dest],
        "checkIn": checkin,
        "checkOut": checkout,
        "maxListingsPerQuery": shape.DEFAULT_CAP,
        "scrapeListingDetails": False,
        "scrapeReviews": False,
    }
    return payload, None, _price_cap(args, "max_price", "budget")


def _lodging_payload_hostel(args: dict) -> tuple[dict[str, Any] | None, str | None, float | None]:
    dest = _ok_str(args, "destination", "search", "q")
    checkin = _ok_str(args, "checkin", "checkIn", "dateStart")
    checkout = _ok_str(args, "checkout", "checkOut")
    if not dest:
        return None, "Need destination, checkin, and checkout", None
    nights = shape.nights_between(checkin, checkout)
    payload: dict[str, Any] = {
        "q": dest,
        "maxItems": shape.DEFAULT_CAP,
        "numberOfGuests": _int(args, "guests", _int(args, "numberOfGuests", 2)),
        "numNights": nights,
        "currency": _ok_str(args, "currency") or "EUR",
        "includeDetails": False,
    }
    if checkin:
        payload["dateStart"] = checkin
    return payload, None, _price_cap(args, "max_price", "budget")


def search_booking(args: dict, **kwargs) -> str:
    payload, err, max_price = _lodging_payload_booking(args)
    if err:
        return json.dumps({"error": err})
    return _stay_result("booking", payload or {}, max_price=max_price)


def search_airbnb(args: dict, **kwargs) -> str:
    payload, err, max_price = _lodging_payload_airbnb(args)
    if err:
        return json.dumps({"error": err})
    return _stay_result("airbnb", payload or {}, max_price=max_price)


def search_agoda(args: dict, **kwargs) -> str:
    payload, err, max_price = _lodging_payload_booking(args)
    if err:
        return json.dumps({"error": err})
    return _stay_result("agoda", payload or {}, max_price=max_price)


def search_hostelworld(args: dict, **kwargs) -> str:
    payload, err, max_price = _lodging_payload_hostel(args)
    if err:
        return json.dumps({"error": err})
    return _stay_result("hostelworld", payload or {}, max_price=max_price)


def search_flixbus(args: dict, **kwargs) -> str:
    origin = _ok_str(args, "origin", "fromCity")
    dest = _ok_str(args, "destination", "toCity")
    date = _ok_str(args, "date", "departureDate")
    if not origin or not dest or not date:
        return json.dumps({"error": "Need origin, destination, and date"})
    payload = {
        "fromCity": origin,
        "toCity": dest,
        "departureDate": date,
        "adults": _int(args, "guests", _int(args, "adults", 1)),
        "locale": "en",
        "currency": _ok_str(args, "currency") or "EUR",
    }
    return _transport_result("flixbus", payload)


def search_rome2rio(args: dict, **kwargs) -> str:
    origin = _ok_str(args, "origin")
    dest = _ok_str(args, "destination")
    if not origin or not dest:
        return json.dumps({"error": "Need origin and destination"})
    payload: dict[str, Any] = {
        "origin": origin,
        "destination": dest,
        "currency": _ok_str(args, "currency") or "USD",
        "language": "en",
        "includeSchedules": False,
        "includeBookable": False,
        "maxItems": shape.DEFAULT_CAP,
        "includeHotels": False,
    }
    date = _ok_str(args, "date", "departureDate")
    if date:
        payload["departureDate"] = date
    return _transport_result("rome2rio", payload)


def search_flights(args: dict, **kwargs) -> str:
    origin = _ok_str(args, "origin")
    dest = _ok_str(args, "destination")
    date = _ok_str(args, "date", "departureDate")
    if not origin or not dest or not date:
        return json.dumps({"error": "Need origin, destination, and date"})
    payload: dict[str, Any] = {
        "origin": origin,
        "destination": dest,
        "departureDate": date,
        "adults": _int(args, "guests", _int(args, "adults", 1)),
        "includePrediction": False,
        "maxItems": shape.DEFAULT_CAP,
    }
    return_date = _ok_str(args, "return_date", "returnDate")
    if return_date:
        payload["returnDate"] = return_date
    return _transport_result("flights", payload)


def changi_timetable(args: dict, **kwargs) -> str:
    direction = (_ok_str(args, "direction") or "dep").lower()
    if direction not in {"arr", "dep", "both"}:
        direction = "dep"
    payload: dict[str, Any] = {
        "direction": direction,
        "terminal": "all",
        "maxItems": shape.DEFAULT_CAP,
    }
    date = _ok_str(args, "date", "scheduledDate")
    if date:
        payload["scheduledDate"] = date
    return _transport_result("changi", payload)


def _parse_picks(raw: str) -> list[dict[str, Any]]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict) and isinstance(data.get("picks"), list):
        return data["picks"]
    return []


def compare_stays(args: dict, **kwargs) -> str:
    dest = _ok_str(args, "destination")
    checkin = _ok_str(args, "checkin")
    checkout = _ok_str(args, "checkout")
    if not dest or not checkin or not checkout:
        return json.dumps({"error": "Need destination, checkin, and checkout"})
    lodging = (_ok_str(args, "lodging") or "all").lower()
    if lodging not in {"hotels", "homes", "hostels", "all"}:
        lodging = "all"
    fns: list[Callable[[], str]] = []
    if lodging in {"hotels", "all"}:
        fns.append(lambda: search_booking(args))
        fns.append(lambda: search_agoda(args))
    if lodging in {"homes", "all"}:
        fns.append(lambda: search_airbnb(args))
    if lodging in {"hostels", "all"}:
        fns.append(lambda: search_hostelworld(args))

    async def _run_all() -> list[str]:
        return list(await asyncio.gather(*[asyncio.to_thread(fn) for fn in fns]))

    try:
        results = asyncio.run(_run_all())
    except RuntimeError:
        results = [fn() for fn in fns]
    merged: list[dict[str, Any]] = []
    for raw in results:
        merged.extend(_parse_picks(raw))
    budget = _price_cap(args, "budget", "max_price")
    if budget is not None:
        merged = [c for c in merged if c.get("price") is None or c["price"] <= budget]
    picks = shape.merge_cap(shape.sort_stays(merged), shape.DEFAULT_CAP)
    note = f"{len(picks)} stay options for {dest} ({lodging})"
    return json.dumps({"picks": picks, "note": note})


def plan_leg(args: dict, **kwargs) -> str:
    origin = _ok_str(args, "origin")
    dest = _ok_str(args, "destination")
    date = _ok_str(args, "date")
    if not origin or not dest or not date:
        return json.dumps({"error": "Need origin, destination, and date"})
    fns: list[Callable[[], str]] = [lambda: search_rome2rio(args), lambda: search_flights(args)]
    if shape.looks_european(origin, dest):
        fns.append(lambda: search_flixbus(args))
    if shape.looks_changi(origin, dest):
        fns.append(lambda: changi_timetable(args))

    async def _run_all() -> list[str]:
        return list(await asyncio.gather(*[asyncio.to_thread(fn) for fn in fns]))

    try:
        results = asyncio.run(_run_all())
    except RuntimeError:
        results = [fn() for fn in fns]
    merged: list[dict[str, Any]] = []
    for raw in results:
        merged.extend(_parse_picks(raw))
    picks = shape.merge_cap(merged, shape.DEFAULT_CAP)
    return json.dumps({"picks": picks, "note": f"leg {origin} → {dest} on {date}"})


HANDLERS: dict[str, Callable] = {
    "search_booking": search_booking,
    "search_airbnb": search_airbnb,
    "search_agoda": search_agoda,
    "search_hostelworld": search_hostelworld,
    "search_flixbus": search_flixbus,
    "search_rome2rio": search_rome2rio,
    "search_flights": search_flights,
    "changi_timetable": changi_timetable,
    "compare_stays": compare_stays,
    "plan_leg": plan_leg,
}
