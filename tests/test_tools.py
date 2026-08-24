import json
import os
from io import BytesIO
from unittest.mock import patch

import pytest

os.environ.setdefault("APIFY_API_TOKEN", "test-token")

from hermes_travel_rl1987 import apify_client, tools
from hermes_travel_rl1987.apify_client import ApifyError


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


def test_missing_token(monkeypatch):
    monkeypatch.delenv("APIFY_API_TOKEN", raising=False)
    with pytest.raises(ApifyError, match="APIFY_API_TOKEN"):
        apify_client._token()


def test_search_booking_validation():
    out = json.loads(tools.search_booking({"search": "Amsterdam"}))
    assert "error" in out


def test_search_booking_mocked_http(monkeypatch):
    monkeypatch.setenv("APIFY_API_TOKEN", "test-token")
    calls = []

    def fake_urlopen(req, timeout=30):
        url = req.full_url
        method = req.get_method()
        calls.append((method, url))
        if method == "POST" and "/acts/" in url and url.endswith("/runs"):
            assert "rl1987~booking-api-scraper" in url
            body = json.loads(req.data.decode())
            assert body["search"] == "Amsterdam"
            assert body["maxItems"] == 20
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
            return _FakeResp([{"name": "Hotel A", "price": 120}])
        raise AssertionError(f"unexpected {method} {url}")

    monkeypatch.setattr(apify_client.time, "sleep", lambda *_: None)
    monkeypatch.setattr(apify_client.urllib.request, "urlopen", fake_urlopen)
    raw = tools.search_booking(
        {
            "search": "Amsterdam",
            "checkin": "2026-09-01",
            "checkout": "2026-09-03",
        }
    )
    data = json.loads(raw)
    assert data["status"] == "SUCCEEDED"
    assert data["count"] == 1
    assert data["items"][0]["name"] == "Hotel A"
    assert data["actorId"] == "rl1987~booking-api-scraper"


def test_search_airbnb_maps_queries(monkeypatch):
    monkeypatch.setenv("APIFY_API_TOKEN", "test-token")
    captured = {}

    def fake_run(actor, payload, max_items=20):
        captured["actor"] = actor
        captured["payload"] = payload
        return {"status": "SUCCEEDED", "items": [], "count": 0, "actorId": actor}

    monkeypatch.setattr(tools, "run_actor_and_collect", fake_run)
    raw = tools.search_airbnb(
        {"search": "Lisbon", "checkIn": "2026-09-01", "checkOut": "2026-09-04"}
    )
    data = json.loads(raw)
    assert captured["actor"] == "rl1987~airbnb-api-scraper"
    assert captured["payload"]["searchQueries"] == ["Lisbon"]
    assert captured["payload"]["scrapeReviews"] is False
    assert data["status"] == "SUCCEEDED"


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
        {"fromCity": "Berlin", "toCity": "Munich", "departureDate": "2026-12-20"}
    )
    data = json.loads(raw)
    assert "error" in data
    assert "network down" in data["error"]


def test_register_tools():
    registered = []

    class Ctx:
        def register_tool(self, **kwargs):
            registered.append(kwargs)

        def register_skill(self, name, path):
            registered.append(("skill", name, str(path)))

    from hermes_travel_rl1987 import register

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
    ]
    assert all(r["toolset"] == "travel" for r in registered if isinstance(r, dict))
