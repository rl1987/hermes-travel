---
name: travel-trip
description: Plan trips using only the eight rl1987 travel tools (Booking, Airbnb, Agoda, Hostelworld, FlixBus, Rome2Rio, redBus, Changi timetable).
---

# Plan a trip with rl1987 travel tools

Use **only** these tools. Do not call Bright Data, generic web scrape, or any Apify Actor that is not owned by `rl1987`.

## When to use which tool

1. **Door-to-door options** — `search_rome2rio` with `origin` + `destination`. Add `departureDate` if the user has a day. Keep `includeHotels` off; use lodging tools instead.
2. **Europe coaches** — `search_flixbus` (`fromCity`, `toCity`, `departureDate`).
3. **India / redBus markets** — `search_redbus` (`source`, `destination`, `dateOfJourney`, optional `country`).
4. **Singapore Changi flights** — `changi_timetable` (`direction` arr/dep/both, `scheduledDate`, optional `terminal`). Not a worldwide flight search.
5. **Hotels (global, live rates)** — `search_booking` (`search`, `checkin`, `checkout`, `rooms`, `adults`, `currency`, `maxItems` default 20). Set `includeDetails` only if you need facilities/address.
6. **Hotels (Asia-heavy inventory)** — `search_agoda` with the same stay fields.
7. **Homes / rooms** — `search_airbnb` (`search`, `checkIn`, `checkOut`). Leave `scrapeListingDetails` false unless the user asks for amenities.
8. **Hostels / dorms** — `search_hostelworld` (`q` city, `dateStart`, `numNights`, `numberOfGuests`). Prefer `includeDetails` false for a first pass.

## Workflow

1. Confirm cities, dates, party size, budget, and lodging style.
2. Pull transport first (`search_rome2rio`, then FlixBus/redBus/Changi as relevant).
3. Search lodging on the nights implied by transport. Cap results at 20.
4. Compare 3–5 options: price, location, duration, cancellation if present.
5. Ask before spending extra Actor credits on `includeDetails` / listing details.

## Dates

Pass ISO dates `YYYY-MM-DD`. Do not invent sold-out inventory. If a tool returns `error`, explain it and try a sibling lodging/transport tool rather than a non-rl1987 Actor.
