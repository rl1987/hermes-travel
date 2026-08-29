# hermes-travel

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

## Directory install

```bash
mkdir -p ~/.hermes/plugins
cp -R /path/to/hermes-travel ~/.hermes/plugins/hermes-travel
hermes plugins enable hermes-travel
```

Set `APIFY_API_TOKEN`. `hermes plugins install` prompts for it when missing.

## Pip install

```bash
pip install /path/to/hermes-travel
```

## Skill

Load `skill_view("hermes-travel:travel-trip")` for trip-planning guidance.

Skills: `travel-trip` (master SOP), `travel-intake`, `itinerary-architecture`, `day-by-day`, `quote-and-docs`.
