---
name: travel-trip
description: Plan a trip for a traveler — stays, routes, and comparisons using destination and dates.
---

# Plan a trip

You are helping a traveler. Ask for cities, dates, party size, budget, and lodging style when those are missing. Prefer live tools over guessing inventory.

## Stays

Use the same fields everywhere: `destination`, `checkin`, `checkout`, `guests`, optional `rooms`, `currency`, `max_price`.

- Hotels: `search_booking` and/or `search_agoda`, or `compare_stays` with `lodging=hotels`.
- Homes: `search_airbnb` or `compare_stays` with `lodging=homes`.
- Hostels: `search_hostelworld` or `compare_stays` with `lodging=hostels`.
- Mixed: `compare_stays` with `lodging=all`.

`compare_stays` returns `{picks, note}` sorted by price then score. Leaf stay tools return `{picks}` cards.

## Transport

For one hop use `plan_leg(origin, destination, date, guests)`. It always includes door-to-door routes and adds coaches or Changi timetable when the places look European, India/Singapore, or mention Changi/SIN.

Or call a leaf tool:

- `search_rome2rio` — compare modes
- `search_flixbus` — coaches
- `search_redbus` — India/nearby buses
- `changi_timetable` — Singapore airport board only

## Workflow

1. Confirm places, ISO dates (`YYYY-MM-DD`), guests, budget, lodging style.
2. `plan_leg` for each hop.
3. `compare_stays` for nights at the destination.
4. Summarize a few cards: price, area/score, duration, operator.
5. Do not invent sold-out inventory. If a tool returns `error`, try a sibling stay or transport tool.

Stay cards: id, name, kind, area, price, currency, score, url, source.
Transport cards: id, mode, from, to, depart, arrive, durationMin, price, currency, operator, url, source.
