"""hermes-travel — trip planner tools for stays and transport."""

from pathlib import Path

from . import schemas, tools

__all__ = ["register"]

_TOOLS = [
    ("search_booking", schemas.SEARCH_BOOKING, tools.search_booking),
    ("search_airbnb", schemas.SEARCH_AIRBNB, tools.search_airbnb),
    ("search_agoda", schemas.SEARCH_AGODA, tools.search_agoda),
    ("search_hostelworld", schemas.SEARCH_HOSTELWORLD, tools.search_hostelworld),
    ("search_flixbus", schemas.SEARCH_FLIXBUS, tools.search_flixbus),
    ("search_rome2rio", schemas.SEARCH_ROME2RIO, tools.search_rome2rio),
    ("search_redbus", schemas.SEARCH_REDBUS, tools.search_redbus),
    ("changi_timetable", schemas.CHANGI_TIMETABLE, tools.changi_timetable),
    ("compare_stays", schemas.COMPARE_STAYS, tools.compare_stays),
    ("plan_leg", schemas.PLAN_LEG, tools.plan_leg),
]


def register(ctx):
    for name, schema, handler in _TOOLS:
        ctx.register_tool(name=name, toolset="travel", schema=schema, handler=handler)

    here = Path(__file__).resolve().parent
    skills_dir = None
    for candidate in (here / "skills", here.parent.parent / "skills"):
        if candidate.is_dir():
            skills_dir = candidate
            break
    if skills_dir is not None:
        for child in sorted(skills_dir.iterdir()):
            skill_md = child / "SKILL.md"
            if child.is_dir() and skill_md.exists():
                ctx.register_skill(child.name, skill_md)
