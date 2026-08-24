# hermes-travel-rl1987

Hermes Agent plugin that exposes eight travel tools, each bound to a single **rl1987** Apify Actor. No Bright Data, no universal Apify runner, no third-party Actors.

## Tools

| Tool | Actor |
| --- | --- |
| `search_booking` | `rl1987/booking-api-scraper` |
| `search_airbnb` | `rl1987/airbnb-api-scraper` |
| `search_agoda` | `rl1987/agoda-scraper` |
| `search_hostelworld` | `rl1987/hostelworld-api-scraper` |
| `search_flixbus` | `rl1987/flixbus-api-scraper` |
| `search_rome2rio` | `rl1987/rome2rio-api-scraper` |
| `search_redbus` | `rl1987/redbus-api-scraper` |
| `changi_timetable` | `rl1987/sin-airport-timetable` |

All tools register under toolset `travel`. Each run is started via `POST /v2/acts/{username}~{name}/runs`, polled until `SUCCEEDED` or ~120s, then dataset items are returned (capped at 20).

## Directory install

```bash
mkdir -p ~/.hermes/plugins
cp -R /path/to/hermes-travel-rl1987 ~/.hermes/plugins/hermes-travel-rl1987
hermes plugins enable hermes-travel-rl1987
```

Set `APIFY_API_TOKEN` (https://console.apify.com/account/integrations). `hermes plugins install` prompts for it when missing.

## Pip install

```bash
pip install /path/to/hermes-travel-rl1987
# entry point: hermes_agent.plugins → hermes-travel-rl1987 = hermes_travel_rl1987
```

## Skill

Load `skill_view("hermes-travel-rl1987:travel-trip")` for trip-planning guidance that uses only these eight tools.
