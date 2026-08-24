"""hermes-travel-rl1987 — travel tools wrapping only rl1987 Apify Actors."""

from pathlib import Path

from . import schemas, tools

__all__ = ["register"]


def register(ctx):
    ctx.register_tool(
        name="search_booking",
        toolset="travel",
        schema=schemas.SEARCH_BOOKING,
        handler=tools.search_booking,
    )
    ctx.register_tool(
        name="search_airbnb",
        toolset="travel",
        schema=schemas.SEARCH_AIRBNB,
        handler=tools.search_airbnb,
    )
    ctx.register_tool(
        name="search_agoda",
        toolset="travel",
        schema=schemas.SEARCH_AGODA,
        handler=tools.search_agoda,
    )
    ctx.register_tool(
        name="search_hostelworld",
        toolset="travel",
        schema=schemas.SEARCH_HOSTELWORLD,
        handler=tools.search_hostelworld,
    )
    ctx.register_tool(
        name="search_flixbus",
        toolset="travel",
        schema=schemas.SEARCH_FLIXBUS,
        handler=tools.search_flixbus,
    )
    ctx.register_tool(
        name="search_rome2rio",
        toolset="travel",
        schema=schemas.SEARCH_ROME2RIO,
        handler=tools.search_rome2rio,
    )
    ctx.register_tool(
        name="search_redbus",
        toolset="travel",
        schema=schemas.SEARCH_REDBUS,
        handler=tools.search_redbus,
    )
    ctx.register_tool(
        name="changi_timetable",
        toolset="travel",
        schema=schemas.CHANGI_TIMETABLE,
        handler=tools.changi_timetable,
    )

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
