"""Tool handlers — always return a JSON string, never raise."""

from __future__ import annotations

import json
from typing import Any, Callable

from .apify_client import MAX_ITEMS, run_actor_and_collect

ACTORS = {
    "search_booking": "rl1987~booking-api-scraper",
    "search_airbnb": "rl1987~airbnb-api-scraper",
    "search_agoda": "rl1987~agoda-scraper",
    "search_hostelworld": "rl1987~hostelworld-api-scraper",
    "search_flixbus": "rl1987~flixbus-api-scraper",
    "search_rome2rio": "rl1987~rome2rio-api-scraper",
    "search_redbus": "rl1987~redbus-api-scraper",
    "changi_timetable": "rl1987~sin-airport-timetable",
}


def _cap(value: Any, default: int = MAX_ITEMS) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return default
    if n <= 0:
        return default
    return min(n, MAX_ITEMS)


def _ok_str(args: dict, *keys: str) -> str | None:
    for key in keys:
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _run(actor: str, payload: dict[str, Any], max_items: int = MAX_ITEMS) -> str:
    try:
        result = run_actor_and_collect(actor, payload, max_items=max_items)
        return json.dumps(result, default=str)
    except Exception as exc:  # noqa: BLE001 — handlers must never raise
        return json.dumps({"error": str(exc), "actorId": actor})


def search_booking(args: dict, **kwargs) -> str:
    search = _ok_str(args, "search")
    checkin = _ok_str(args, "checkin")
    checkout = _ok_str(args, "checkout")
    if not search or not checkin or not checkout:
        return json.dumps({"error": "Need search, checkin, and checkout"})
    max_items = _cap(args.get("maxItems"))
    payload: dict[str, Any] = {
        "search": search,
        "checkin": checkin,
        "checkout": checkout,
        "rooms": int(args.get("rooms") or 1),
        "adults": int(args.get("adults") or 2),
        "currency": _ok_str(args, "currency") or "USD",
        "maxItems": max_items,
    }
    if args.get("includeDetails") is not None:
        payload["includeDetails"] = bool(args.get("includeDetails"))
    return _run(ACTORS["search_booking"], payload, max_items)


def search_airbnb(args: dict, **kwargs) -> str:
    search = _ok_str(args, "search", "query")
    check_in = _ok_str(args, "checkIn", "checkin")
    check_out = _ok_str(args, "checkOut", "checkout")
    if not search or not check_in or not check_out:
        return json.dumps({"error": "Need search, checkIn, and checkOut"})
    max_items = _cap(args.get("maxListingsPerQuery") or args.get("maxItems"))
    payload: dict[str, Any] = {
        "searchQueries": [search],
        "checkIn": check_in,
        "checkOut": check_out,
        "maxListingsPerQuery": max_items,
        "scrapeListingDetails": bool(args.get("scrapeListingDetails", False)),
        "scrapeReviews": False,
    }
    return _run(ACTORS["search_airbnb"], payload, max_items)


def search_agoda(args: dict, **kwargs) -> str:
    search = _ok_str(args, "search")
    checkin = _ok_str(args, "checkin")
    checkout = _ok_str(args, "checkout")
    if not search or not checkin or not checkout:
        return json.dumps({"error": "Need search, checkin, and checkout"})
    max_items = _cap(args.get("maxItems"))
    payload: dict[str, Any] = {
        "search": search,
        "checkin": checkin,
        "checkout": checkout,
        "rooms": int(args.get("rooms") or 1),
        "adults": int(args.get("adults") or 2),
        "currency": _ok_str(args, "currency") or "USD",
        "maxItems": max_items,
        "includeDetails": bool(args.get("includeDetails", False)),
    }
    return _run(ACTORS["search_agoda"], payload, max_items)


def search_hostelworld(args: dict, **kwargs) -> str:
    q = _ok_str(args, "q", "search")
    if not q:
        return json.dumps({"error": "Need q (location)"})
    max_items = _cap(args.get("maxItems"))
    payload: dict[str, Any] = {
        "q": q,
        "maxItems": max_items,
        "numberOfGuests": int(args.get("numberOfGuests") or 2),
        "numNights": int(args.get("numNights") or 2),
        "currency": _ok_str(args, "currency") or "EUR",
        "includeDetails": bool(args.get("includeDetails", False)),
    }
    date_start = _ok_str(args, "dateStart", "checkin")
    if date_start:
        payload["dateStart"] = date_start
    return _run(ACTORS["search_hostelworld"], payload, max_items)


def search_flixbus(args: dict, **kwargs) -> str:
    from_city = _ok_str(args, "fromCity")
    to_city = _ok_str(args, "toCity")
    departure = _ok_str(args, "departureDate")
    if not from_city or not to_city or not departure:
        return json.dumps({"error": "Need fromCity, toCity, and departureDate"})
    payload: dict[str, Any] = {
        "fromCity": from_city,
        "toCity": to_city,
        "departureDate": departure,
        "adults": int(args.get("adults") or 1),
        "locale": _ok_str(args, "locale") or "en",
        "currency": _ok_str(args, "currency") or "EUR",
    }
    return _run(ACTORS["search_flixbus"], payload)


def search_rome2rio(args: dict, **kwargs) -> str:
    origin = _ok_str(args, "origin")
    destination = _ok_str(args, "destination")
    if not origin or not destination:
        return json.dumps({"error": "Need origin and destination"})
    max_items = _cap(args.get("maxItems"))
    payload: dict[str, Any] = {
        "origin": origin,
        "destination": destination,
        "currency": _ok_str(args, "currency") or "USD",
        "language": _ok_str(args, "language") or "en",
        "includeSchedules": bool(args.get("includeSchedules", False)),
        "includeBookable": bool(args.get("includeBookable", False)),
        "maxItems": max_items,
        "includeHotels": False,
    }
    departure = _ok_str(args, "departureDate")
    if departure:
        payload["departureDate"] = departure
    return _run(ACTORS["search_rome2rio"], payload, max_items)


def search_redbus(args: dict, **kwargs) -> str:
    source = _ok_str(args, "source")
    destination = _ok_str(args, "destination")
    date_of = _ok_str(args, "dateOfJourney")
    if not source or not destination or not date_of:
        return json.dumps({"error": "Need source, destination, and dateOfJourney"})
    max_items = _cap(args.get("maxItems"))
    payload: dict[str, Any] = {
        "source": source,
        "destination": destination,
        "dateOfJourney": date_of,
        "country": _ok_str(args, "country") or "india",
        "maxItems": max_items,
        "pageSize": min(max_items, 20),
    }
    return _run(ACTORS["search_redbus"], payload, max_items)


def changi_timetable(args: dict, **kwargs) -> str:
    max_items = _cap(args.get("maxItems"))
    direction = (_ok_str(args, "direction") or "dep").lower()
    if direction not in {"arr", "dep", "both"}:
        direction = "dep"
    terminal = (_ok_str(args, "terminal") or "all").lower()
    payload: dict[str, Any] = {
        "direction": direction,
        "terminal": terminal,
        "maxItems": max_items,
    }
    scheduled = _ok_str(args, "scheduledDate")
    if scheduled:
        payload["scheduledDate"] = scheduled
    return _run(ACTORS["changi_timetable"], payload, max_items)


HANDLERS: dict[str, Callable] = {
    "search_booking": search_booking,
    "search_airbnb": search_airbnb,
    "search_agoda": search_agoda,
    "search_hostelworld": search_hostelworld,
    "search_flixbus": search_flixbus,
    "search_rome2rio": search_rome2rio,
    "search_redbus": search_redbus,
    "changi_timetable": changi_timetable,
}
