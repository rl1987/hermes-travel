# hermes-travel

**Status: experimental.** Actor output shapes are scraped, undocumented, and can change without notice — this plugin was shipped once already with several tools silently returning empty results because of field-name mismatches (see [Known limitations](#known-limitations)). Verify results before relying on them for a real booking decision.

A Hermes trip planner for travelers. Search hotels, homes, and hostels with the same stay dates, compare lodging, and plan a transport leg — then talk about the options as cards (name, price, score, times).

## Tools

Lodging (same args: `destination`, `checkin`, `checkout`, `guests`, `rooms`, `currency`, `max_price`):

- `search_booking` — Find hotels with live rates
- `search_airbnb` — Find short-term homes
- `search_agoda` — Find hotels (Asia-heavy inventory)
- `search_hostelworld` — Find hostels and dorms

Transport:

- `search_flixbus` — Coach buses (Europe-focused)
- `search_rome2rio` — Door-to-door routes
- `search_flights` — Flights, worldwide
- `changi_timetable` — Singapore Changi arrivals/departures

Orchestrators:

- `compare_stays` — Merge lodging sources (`lodging=hotels|homes|hostels|all`)
- `plan_leg` — Merge routes for one origin → destination on a date

Results are stay or transport cards (default cap 8).

## Install

Requires `APIFY_API_TOKEN` ([console.apify.com/account/integrations](https://console.apify.com/account/integrations)) — every search runs an Apify Actor billed to *your* account. All wrapped Actors are on the free tier, but `search_booking` requests per-property detail (`includeDetails`) to get a usable name back, which costs one extra request per property.

**From PyPI:**
```bash
pip install hermes-travel
```

**Directory install** (for a Hermes install that loads plugins from a local dir):
```bash
mkdir -p ~/.hermes/plugins
cp -R /path/to/hermes-travel ~/.hermes/plugins/hermes-travel
hermes plugins enable hermes-travel
```
`hermes plugins install` prompts for the token when missing.

**From a local checkout:**
```bash
pip install /path/to/hermes-travel
```

## Skill

Load `skill_view("hermes-travel:travel-trip")` for trip-planning guidance.

Skills: `travel-trip` (master SOP), `travel-intake`, `itinerary-architecture`, `day-by-day`, `quote-and-docs`. These cover the design phase of a trip (intake → architecture → day-by-day → quote) — not lead qualification/sales, and not post-booking follow-up. No CRM, no payments, no real bookings: this plugin only researches and quotes.

## Known limitations

- Underlying Actors are reverse-engineered from mobile/private APIs, not public documented ones. Field names have shifted before without warning and can shift again — a tool that "returns empty" may mean the shape changed, not that there's no availability.
- `search_flixbus` has no currency field in its output at all; the card's `currency` falls back to whatever was requested, which may not match reality if the Actor silently returns a different one.
- `changi_timetable` reports only one endpoint (the counterpart airport) per row — the other end is inferred from the search direction, not returned by the Actor.
- No worldwide bus/rail coverage outside `search_flixbus` (Europe) and `search_rome2rio` (door-to-door estimates); an earlier India/SE Asia bus tool was dropped for being too region-locked to be worth maintaining.
