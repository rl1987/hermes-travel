"""hermes-travel-rl1987 directory plugin — registration."""

from pathlib import Path

try:
    from . import schemas, tools
except ImportError:
    schemas = tools = None  # type: ignore

_TOOL_NAMES = [
    "search_booking",
    "search_airbnb",
    "search_agoda",
    "search_hostelworld",
    "search_flixbus",
    "search_rome2rio",
    "search_redbus",
    "changi_timetable",
    "compare_stays",
    "plan_leg",
]


def register(ctx):
    if schemas is None or tools is None:
        raise ImportError("plugin must be imported as a package")
    mapping = [
        (schemas.SEARCH_BOOKING, tools.search_booking),
        (schemas.SEARCH_AIRBNB, tools.search_airbnb),
        (schemas.SEARCH_AGODA, tools.search_agoda),
        (schemas.SEARCH_HOSTELWORLD, tools.search_hostelworld),
        (schemas.SEARCH_FLIXBUS, tools.search_flixbus),
        (schemas.SEARCH_ROME2RIO, tools.search_rome2rio),
        (schemas.SEARCH_REDBUS, tools.search_redbus),
        (schemas.CHANGI_TIMETABLE, tools.changi_timetable),
        (schemas.COMPARE_STAYS, tools.compare_stays),
        (schemas.PLAN_LEG, tools.plan_leg),
    ]
    for schema, handler in mapping:
        ctx.register_tool(name=schema["name"], toolset="travel", schema=schema, handler=handler)

    here = Path(__file__).resolve().parent
    skills_dir = here / "skills"
    if skills_dir.is_dir():
        for child in sorted(skills_dir.iterdir()):
            skill_md = child / "SKILL.md"
            if child.is_dir() and skill_md.exists():
                ctx.register_skill(child.name, skill_md)
