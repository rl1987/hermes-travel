"""Start an rl1987 Apify Actor run and poll its dataset.

Uses the public HTTP API so tests can mock urllib. Actor ids use the
``username~name`` form in ``/v2/acts/{username}~{name}/runs``.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

API_BASE = "https://api.apify.com/v2"
DEFAULT_TIMEOUT_S = 120
POLL_INTERVAL_S = 2.0
MAX_ITEMS = 20
TERMINAL = frozenset({"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT", "TIMED_OUT"})


class ApifyError(Exception):
    """Non-raising callers convert this to error JSON."""


def _token() -> str:
    token = (os.environ.get("APIFY_API_TOKEN") or "").strip()
    if not token:
        raise ApifyError(
            "Missing APIFY_API_TOKEN. Get one at "
            "https://console.apify.com/account/integrations"
        )
    return token


def _request(
    method: str,
    url: str,
    *,
    token: str,
    body: dict[str, Any] | None = None,
    timeout: float = 30,
) -> Any:
    data = None
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ApifyError(f"Apify HTTP {exc.code}: {detail[:500]}") from exc
    except urllib.error.URLError as exc:
        raise ApifyError(f"Apify request failed: {exc.reason}") from exc


def start_actor_run(actor_tilde: str, run_input: dict[str, Any], *, token: str) -> dict[str, Any]:
    """POST /v2/acts/{username}~{name}/runs and return the run object."""
    encoded = urllib.parse.quote(actor_tilde, safe="~")
    url = f"{API_BASE}/acts/{encoded}/runs"
    payload = _request("POST", url, token=token, body=run_input)
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict) or not data.get("id"):
        raise ApifyError(f"Unexpected start response: {payload!r}"[:500])
    return data


def get_run(run_id: str, *, token: str) -> dict[str, Any]:
    url = f"{API_BASE}/actor-runs/{urllib.parse.quote(run_id)}"
    payload = _request("GET", url, token=token)
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict):
        raise ApifyError(f"Unexpected run response: {payload!r}"[:500])
    return data


def list_dataset_items(dataset_id: str, *, token: str, limit: int = MAX_ITEMS) -> list[Any]:
    qs = urllib.parse.urlencode({"limit": limit, "clean": 1})
    url = f"{API_BASE}/datasets/{urllib.parse.quote(dataset_id)}/items?{qs}"
    payload = _request("GET", url, token=token)
    if isinstance(payload, list):
        return payload[:limit]
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"][:limit]
    raise ApifyError(f"Unexpected dataset response: {payload!r}"[:500])


def run_actor_and_collect(
    actor_tilde: str,
    run_input: dict[str, Any],
    *,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    max_items: int = MAX_ITEMS,
) -> dict[str, Any]:
    """Start, poll until SUCCEEDED (or timeout), return dataset items.

    Never used uncaught by tool handlers — they wrap this.
    """
    token = _token()
    run = start_actor_run(actor_tilde, run_input, token=token)
    run_id = run["id"]
    deadline = time.monotonic() + timeout_s
    status = run.get("status") or "READY"
    dataset_id = run.get("defaultDatasetId")

    while status not in TERMINAL:
        if time.monotonic() >= deadline:
            return {
                "error": "timeout",
                "message": f"Actor {actor_tilde} run {run_id} did not finish within {timeout_s}s",
                "status": status,
                "runId": run_id,
                "actorId": actor_tilde,
            }
        time.sleep(POLL_INTERVAL_S)
        run = get_run(run_id, token=token)
        status = run.get("status") or status
        dataset_id = run.get("defaultDatasetId") or dataset_id

    if status != "SUCCEEDED":
        return {
            "error": "run_failed",
            "message": f"Actor {actor_tilde} ended with status {status}",
            "status": status,
            "runId": run_id,
            "actorId": actor_tilde,
        }

    if not dataset_id:
        return {
            "error": "no_dataset",
            "message": "Run succeeded but no defaultDatasetId was returned",
            "runId": run_id,
            "actorId": actor_tilde,
        }

    items = list_dataset_items(dataset_id, token=token, limit=max_items)
    return {
        "actorId": actor_tilde,
        "runId": run_id,
        "datasetId": dataset_id,
        "status": "SUCCEEDED",
        "count": len(items),
        "items": items,
    }
