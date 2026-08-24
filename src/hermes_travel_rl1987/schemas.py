"""Tool schemas for the eight rl1987 travel Actors."""

SEARCH_BOOKING = {
    "name": "search_booking",
    "description": (
        "Search Booking.com accommodations via rl1987/booking-api-scraper. "
        "Use for hotels, apartments and live room prices by destination and stay dates. "
        "Do not use for Airbnb, Agoda, hostels, buses, or airport flights."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "search": {
                "type": "string",
                "description": "Destination (city, region, landmark), e.g. Amsterdam",
            },
            "checkin": {"type": "string", "description": "Check-in date YYYY-MM-DD"},
            "checkout": {"type": "string", "description": "Check-out date YYYY-MM-DD"},
            "rooms": {"type": "integer", "description": "Number of rooms", "default": 1},
            "adults": {"type": "integer", "description": "Number of adult guests", "default": 2},
            "currency": {
                "type": "string",
                "description": "ISO currency code for prices",
                "default": "USD",
            },
            "maxItems": {
                "type": "integer",
                "description": "Max properties to return (capped at 20)",
                "default": 20,
            },
            "includeDetails": {
                "type": "boolean",
                "description": "Include static property details (slower)",
                "default": False,
            },
        },
        "required": ["search", "checkin", "checkout"],
    },
}

SEARCH_AIRBNB = {
    "name": "search_airbnb",
    "description": (
        "Search Airbnb listings via rl1987/airbnb-api-scraper. "
        "Use for short-term homes/rooms by destination and stay dates. "
        "Pass one destination string; the plugin maps it to searchQueries."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "search": {
                "type": "string",
                "description": "Destination as typed into Airbnb search, e.g. Chiang Mai, Thailand",
            },
            "checkIn": {"type": "string", "description": "Check-in YYYY-MM-DD"},
            "checkOut": {"type": "string", "description": "Check-out YYYY-MM-DD"},
            "maxListingsPerQuery": {
                "type": "integer",
                "description": "Max listings (capped at 20)",
                "default": 20,
            },
            "scrapeListingDetails": {
                "type": "boolean",
                "description": "Fetch full listing details (slower)",
                "default": False,
            },
        },
        "required": ["search", "checkIn", "checkOut"],
    },
}

SEARCH_AGODA = {
    "name": "search_agoda",
    "description": (
        "Search Agoda accommodations via rl1987/agoda-scraper. "
        "Use for Asia-heavy hotel inventory, live prices and review scores."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "search": {"type": "string", "description": "Destination, e.g. Bangkok"},
            "checkin": {"type": "string", "description": "Check-in YYYY-MM-DD"},
            "checkout": {"type": "string", "description": "Check-out YYYY-MM-DD"},
            "rooms": {"type": "integer", "default": 1},
            "adults": {"type": "integer", "default": 2},
            "currency": {"type": "string", "default": "USD"},
            "maxItems": {"type": "integer", "default": 20},
            "includeDetails": {"type": "boolean", "default": False},
        },
        "required": ["search", "checkin", "checkout"],
    },
}

SEARCH_HOSTELWORLD = {
    "name": "search_hostelworld",
    "description": (
        "Search Hostelworld hostels via rl1987/hostelworld-api-scraper. "
        "Use for budget dorms and hostel private rooms."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "q": {"type": "string", "description": "City, neighbourhood, or property name"},
            "dateStart": {"type": "string", "description": "Check-in YYYY-MM-DD (enables live prices)"},
            "numNights": {"type": "integer", "description": "Nights (1-31)", "default": 2},
            "numberOfGuests": {"type": "integer", "default": 2},
            "currency": {"type": "string", "default": "EUR"},
            "maxItems": {"type": "integer", "default": 20},
            "includeDetails": {"type": "boolean", "default": False},
        },
        "required": ["q"],
    },
}

SEARCH_FLIXBUS = {
    "name": "search_flixbus",
    "description": (
        "Search FlixBus trips via rl1987/flixbus-api-scraper. "
        "Use for coach buses in Europe (and other FlixBus markets) between two cities on a date."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "fromCity": {"type": "string", "description": "Origin city, e.g. Berlin"},
            "toCity": {"type": "string", "description": "Destination city, e.g. Munich"},
            "departureDate": {"type": "string", "description": "Departure YYYY-MM-DD"},
            "adults": {"type": "integer", "default": 1},
            "currency": {"type": "string", "default": "EUR"},
            "locale": {"type": "string", "default": "en"},
        },
        "required": ["fromCity", "toCity", "departureDate"],
    },
}

SEARCH_ROME2RIO = {
    "name": "search_rome2rio",
    "description": (
        "Search Rome2Rio multi-modal routes via rl1987/rome2rio-api-scraper. "
        "Use to compare train, bus, flight, ferry and driving options between two places."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Origin place, address, airport, or lat,lng"},
            "destination": {"type": "string", "description": "Destination place"},
            "departureDate": {"type": "string", "description": "YYYY-MM-DD when requesting schedules/fares"},
            "currency": {"type": "string", "default": "USD"},
            "language": {"type": "string", "default": "en"},
            "includeSchedules": {"type": "boolean", "default": False},
            "includeBookable": {"type": "boolean", "default": False},
            "maxItems": {"type": "integer", "default": 20},
        },
        "required": ["origin", "destination"],
    },
}

SEARCH_REDBUS = {
    "name": "search_redbus",
    "description": (
        "Search redBus coach services via rl1987/redbus-api-scraper. "
        "Use for intercity buses in India and other redBus markets."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "source": {"type": "string", "description": "Origin city, e.g. Bengaluru"},
            "destination": {"type": "string", "description": "Destination city, e.g. Chennai"},
            "dateOfJourney": {"type": "string", "description": "Travel date YYYY-MM-DD"},
            "country": {
                "type": "string",
                "description": "redBus market, e.g. india, singapore",
                "default": "india",
            },
            "maxItems": {"type": "integer", "default": 20},
        },
        "required": ["source", "destination", "dateOfJourney"],
    },
}

CHANGI_TIMETABLE = {
    "name": "changi_timetable",
    "description": (
        "Fetch Singapore Changi (SIN) arrival/departure timetable via "
        "rl1987/sin-airport-timetable. Use only for SIN airport flights."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "direction": {
                "type": "string",
                "description": "arr, dep, or both",
                "default": "dep",
            },
            "scheduledDate": {"type": "string", "description": "YYYY-MM-DD (Asia/Singapore)"},
            "terminal": {
                "type": "string",
                "description": "all, 1, 2, 3, or 4",
                "default": "all",
            },
            "maxItems": {"type": "integer", "default": 20},
        },
        "required": [],
    },
}

ALL = [
    SEARCH_BOOKING,
    SEARCH_AIRBNB,
    SEARCH_AGODA,
    SEARCH_HOSTELWORLD,
    SEARCH_FLIXBUS,
    SEARCH_ROME2RIO,
    SEARCH_REDBUS,
    CHANGI_TIMETABLE,
]
