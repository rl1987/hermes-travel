import json
import os

os.environ.setdefault("APIFY_API_TOKEN", "test-token")

from hermes_travel import apify_client, schemas, tools
from hermes_travel.apify_client import ApifyError


class _FakeResp:
    def __init__(self, payload, status=200):
        self._raw = json.dumps(payload).encode("utf-8") if not isinstance(payload, bytes) else payload
        self.status = status

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


import pytest


def test_missing_token(monkeypatch):
    monkeypatch.delenv("APIFY_API_TOKEN", raising=False)
    with pytest.raises(ApifyError, match="APIFY_API_TOKEN"):
        apify_client._token()


def test_search_booking_validation():
    out = json.loads(tools.search_booking({"search": "Amsterdam"}))
    assert "error" in out


def test_search_booking_mocked_http(monkeypatch):
    monkeypatch.setenv("APIFY_API_TOKEN", "test-token")

    def fake_urlopen(req, timeout=30):
        url = req.full_url
        method = req.get_method()
        if method == "POST" and "/acts/" in url and url.endswith("/runs"):
            assert "rl1987~booking-api-scraper" in url
            body = json.loads(req.data.decode())
            assert body["search"] == "Amsterdam"
            return _FakeResp(
                {
                    "data": {
                        "id": "run1",
                        "status": "RUNNING",
                        "defaultDatasetId": "ds1",
                    }
                }
            )
        if method == "GET" and "/actor-runs/run1" in url:
            return _FakeResp(
                {
                    "data": {
                        "id": "run1",
                        "status": "SUCCEEDED",
                        "defaultDatasetId": "ds1",
                    }
                }
            )
        if method == "GET" and "/datasets/ds1/items" in url:
            return _FakeResp([{"name": "Hotel A", "price": 120, "url": "https://example.com/a"}])
        raise AssertionError(f"unexpected {method} {url}")

    monkeypatch.setattr(apify_client.time, "sleep", lambda *_: None)
    monkeypatch.setattr(apify_client.urllib.request, "urlopen", fake_urlopen)
    raw = tools.search_booking(
        {
            "destination": "Amsterdam",
            "checkin": "2026-09-01",
            "checkout": "2026-09-03",
        }
    )
    data = json.loads(raw)
    assert "actorId" not in data
    assert "actorId" not in raw
    assert data["picks"][0]["name"] == "Hotel A"
    assert data["picks"][0]["source"] == "booking"
    assert data["picks"][0]["price"] == 120


def test_search_airbnb_maps_queries(monkeypatch):
    monkeypatch.setenv("APIFY_API_TOKEN", "test-token")
    captured = {}

    def fake_run(actor, payload, max_items=8):
        captured["actor"] = actor
        captured["payload"] = payload
        return {"status": "SUCCEEDED", "items": [{"title": "Loft", "price": 90}], "count": 1}

    monkeypatch.setattr(tools, "run_actor_and_collect", fake_run)
    raw = tools.search_airbnb(
        {"destination": "Lisbon", "checkin": "2026-09-01", "checkout": "2026-09-04"}
    )
    data = json.loads(raw)
    assert captured["actor"] == "rl1987~airbnb-api-scraper"
    assert captured["payload"]["searchQueries"] == ["Lisbon"]
    assert captured["payload"]["scrapeReviews"] is False
    assert "actorId" not in data
    assert data["picks"][0]["name"] == "Loft"
    assert data["picks"][0]["source"] == "airbnb"


def test_hostel_nights_from_dates(monkeypatch):
    captured = {}

    def fake_run(actor, payload, max_items=8):
        captured["payload"] = payload
        return {"status": "SUCCEEDED", "items": [{"name": "Dorm", "price": 20}]}

    monkeypatch.setattr(tools, "run_actor_and_collect", fake_run)
    tools.search_hostelworld(
        {"destination": "Berlin", "checkin": "2026-09-01", "checkout": "2026-09-04", "guests": 1}
    )
    assert captured["payload"]["numNights"] == 3
    assert captured["payload"]["dateStart"] == "2026-09-01"


def test_timeout_returns_json(monkeypatch):
    monkeypatch.setenv("APIFY_API_TOKEN", "test-token")

    def fake_urlopen(req, timeout=30):
        if req.get_method() == "POST":
            return _FakeResp({"data": {"id": "runx", "status": "RUNNING", "defaultDatasetId": "ds"}})
        return _FakeResp({"data": {"id": "runx", "status": "RUNNING", "defaultDatasetId": "ds"}})

    monkeypatch.setattr(apify_client.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(apify_client.time, "sleep", lambda *_: None)
    ticks = {"n": 0}

    def mono():
        ticks["n"] += 1
        return 0.0 if ticks["n"] == 1 else 999.0

    monkeypatch.setattr(apify_client.time, "monotonic", mono)
    result = apify_client.run_actor_and_collect("rl1987~flixbus-api-scraper", {}, timeout_s=1)
    assert result["error"] == "timeout"


def test_handler_never_raises(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("network down")

    monkeypatch.setattr(tools, "run_actor_and_collect", boom)
    raw = tools.search_flixbus(
        {"origin": "Berlin", "destination": "Munich", "date": "2026-12-20"}
    )
    data = json.loads(raw)
    assert "error" in data
    assert "network down" in data["error"]
    assert "actorId" not in data


def test_register_tools():
    registered = []

    class Ctx:
        def register_tool(self, **kwargs):
            registered.append(kwargs)

        def register_skill(self, name, path):
            registered.append(("skill", name, str(path)))

    from hermes_travel import register

    register(Ctx())
    names = [r["name"] for r in registered if isinstance(r, dict)]
    assert names == [
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
    assert all(r["toolset"] == "travel" for r in registered if isinstance(r, dict))
    blob = json.dumps([r["schema"]["description"] for r in registered if isinstance(r, dict)]).lower()
    assert "apify" not in blob
    assert "rl1987/" not in blob


def test_descriptions_have_no_vendor_leak():
    for schema in schemas.ALL:
        d = schema["description"].lower()
        assert "apify" not in d
        assert "rl1987/" not in d


def test_compare_stays_parallel(monkeypatch):
    def fake_run(actor, payload, max_items=8):
        if "booking" in actor:
            return {"items": [{"name": "B Hotel", "price": 80, "reviewScore": 8}]}
        if "agoda" in actor:
            return {"items": [{"name": "A Hotel", "price": 70, "score": 9}]}
        if "airbnb" in actor:
            return {"items": [{"name": "Home", "price": 90}]}
        if "hostel" in actor:
            return {"items": [{"name": "Hostel", "price": 25}]}
        return {"items": []}

    monkeypatch.setattr(tools, "run_actor_and_collect", fake_run)
    data = json.loads(
        tools.compare_stays(
            {
                "destination": "Lisbon",
                "checkin": "2026-09-01",
                "checkout": "2026-09-03",
                "guests": 2,
                "lodging": "hotels",
            }
        )
    )
    assert "note" in data
    assert "actorId" not in data
    names = [p["name"] for p in data["picks"]]
    assert names[0] == "A Hotel"
    assert "Home" not in names


def test_skip_junk_rows(monkeypatch):
    def fake_run(actor, payload, max_items=8):
        return {"items": [{"price": 1}, {"name": "Good Place", "price": 40}]}

    monkeypatch.setattr(tools, "run_actor_and_collect", fake_run)
    data = json.loads(
        tools.search_booking(
            {"destination": "Rome", "checkin": "2026-09-01", "checkout": "2026-09-02"}
        )
    )
    assert len(data["picks"]) == 1
    assert data["picks"][0]["name"] == "Good Place"


def test_plan_leg_europe(monkeypatch):
    seen = []

    def fake_run(actor, payload, max_items=8):
        seen.append(actor)
        return {"items": [{"name": "Trip", "from": "Berlin", "to": "Munich", "price": 19}]}

    monkeypatch.setattr(tools, "run_actor_and_collect", fake_run)
    data = json.loads(
        tools.plan_leg(
            {"origin": "Berlin", "destination": "Munich", "date": "2026-12-20", "guests": 1}
        )
    )
    assert any("rome2rio" in a for a in seen)
    assert any("flixbus" in a for a in seen)
    assert "picks" in data
    assert "actorId" not in data
