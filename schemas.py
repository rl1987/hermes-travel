"""Tool schemas — traveler-facing, no vendor internals."""

_LODGING_PROPS = {
    "destination": {"type": "string", "description": "City or area to stay in"},
    "checkin": {"type": "string", "description": "Check-in date YYYY-MM-DD"},
    "checkout": {"type": "string", "description": "Check-out date YYYY-MM-DD"},
    "guests": {"type": "integer", "description": "Number of guests", "default": 2},
    "rooms": {"type": "integer", "description": "Number of rooms", "default": 1},
    "currency": {"type": "string", "description": "ISO currency for prices", "default": "USD"},
    "max_price": {"type": "number", "description": "Skip stays above this price"},
}

_LODGING_REQ = ["destination", "checkin", "checkout"]

SEARCH_BOOKING = {
    "name": "search_booking",
    "description": (
        "Find hotels with live rates for a destination and stay dates. "
        "Best for hotels and apartments worldwide. Not for homes, hostels, buses, or flights."
    ),
    "parameters": {
        "type": "object",
        "properties": dict(_LODGING_PROPS),
        "required": list(_LODGING_REQ),
    },
}

SEARCH_AIRBNB = {
    "name": "search_airbnb",
    "description": (
        "Find short-term homes and rooms for a destination and stay dates. "
        "Not for hotels, hostels, buses, or flights."
    ),
    "parameters": {
        "type": "object",
        "properties": dict(_LODGING_PROPS),
        "required": list(_LODGING_REQ),
    },
}

SEARCH_AGODA = {
    "name": "search_agoda",
    "description": (
        "Find hotels with live rates, especially Asia-heavy inventory. "
        "Use with destination and stay dates. Not for homes, hostels, or transport."
    ),
    "parameters": {
        "type": "object",
        "properties": dict(_LODGING_PROPS),
        "required": list(_LODGING_REQ),
    },
}

SEARCH_HOSTELWORLD = {
    "name": "search_hostelworld",
    "description": (
        "Find hostels and dorms with live prices for a destination and stay dates. "
        "Not for hotels, homes, or transport."
    ),
    "parameters": {
        "type": "object",
        "properties": dict(_LODGING_PROPS),
        "required": list(_LODGING_REQ),
    },
}

SEARCH_FLIXBUS = {
    "name": "search_flixbus",
    "description": (
        "Find coach buses between two cities on a date, mainly Europe. "
        "Use origin, destination, and travel date."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Origin city"},
            "destination": {"type": "string", "description": "Destination city"},
            "date": {"type": "string", "description": "Travel date YYYY-MM-DD"},
            "guests": {"type": "integer", "description": "Adult passengers", "default": 1},
            "currency": {"type": "string", "default": "EUR"},
        },
        "required": ["origin", "destination", "date"],
    },
}

SEARCH_ROME2RIO = {
    "name": "search_rome2rio",
    "description": (
        "Find door-to-door routes (train, bus, flight, ferry, drive) between two places. "
        "Use this first when comparing how to get there."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Origin place"},
            "destination": {"type": "string", "description": "Destination place"},
            "date": {"type": "string", "description": "Travel date YYYY-MM-DD"},
            "currency": {"type": "string", "default": "USD"},
        },
        "required": ["origin", "destination"],
    },
}

SEARCH_FLIGHTS = {
    "name": "search_flights",
    "description": (
        "Find flights between two airports or cities on a date, worldwide. "
        "One-way by default; pass return_date for a round trip."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Origin airport or city"},
            "destination": {"type": "string", "description": "Destination airport or city"},
            "date": {"type": "string", "description": "Departure date YYYY-MM-DD"},
            "return_date": {"type": "string", "description": "Return date YYYY-MM-DD for a round trip"},
            "guests": {"type": "integer", "description": "Adult passengers", "default": 1},
        },
        "required": ["origin", "destination", "date"],
    },
}

CHANGI_TIMETABLE = {
    "name": "changi_timetable",
    "description": (
        "Find Singapore Changi (SIN) airport arrivals and departures for a date. "
        "Not a worldwide flight search."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Origin hint (city or SIN)"},
            "destination": {"type": "string", "description": "Destination hint (city or SIN)"},
            "date": {"type": "string", "description": "Scheduled date YYYY-MM-DD"},
            "direction": {"type": "string", "description": "arr, dep, or both", "default": "dep"},
        },
        "required": [],
    },
}

COMPARE_STAYS = {
    "name": "compare_stays",
    "description": (
        "Compare lodging options for a trip. lodging=hotels uses hotels from multiple "
        "sources, homes uses short-term homes, hostels uses hostels, all uses those that apply. "
        "Returns ranked stay cards."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "destination": {"type": "string", "description": "City or area"},
            "checkin": {"type": "string", "description": "Check-in YYYY-MM-DD"},
            "checkout": {"type": "string", "description": "Check-out YYYY-MM-DD"},
            "guests": {"type": "integer", "default": 2},
            "budget": {"type": "number", "description": "Optional max price filter"},
            "lodging": {
                "type": "string",
                "description": "hotels, homes, hostels, or all",
                "default": "all",
            },
        },
        "required": ["destination", "checkin", "checkout"],
    },
}

PLAN_LEG = {
    "name": "plan_leg",
    "description": (
        "Plan one travel leg: always compare door-to-door routes and flights, plus coaches "
        "or airport timetable when origin/destination suggest Europe or Singapore."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "origin": {"type": "string"},
            "destination": {"type": "string"},
            "date": {"type": "string", "description": "Travel date YYYY-MM-DD"},
            "guests": {"type": "integer", "default": 1},
        },
        "required": ["origin", "destination", "date"],
    },
}

ALL = [
    SEARCH_BOOKING,
    SEARCH_AIRBNB,
    SEARCH_AGODA,
    SEARCH_HOSTELWORLD,
    SEARCH_FLIXBUS,
    SEARCH_ROME2RIO,
    SEARCH_FLIGHTS,
    CHANGI_TIMETABLE,
    COMPARE_STAYS,
    PLAN_LEG,
]
