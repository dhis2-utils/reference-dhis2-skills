"""Shared HTTP helpers for the prototyping scripts.

Connection comes from the environment, never from defaults in code:

    export DHIS2_BASE_URL=http://localhost:8080  # no trailing slash needed
    export DHIS2_API_TOKEN=d2pat_...             # personal access token, or
    export DHIS2_USERNAME=<user> DHIS2_PASSWORD=<password>

The older D2_URL, D2_TOKEN and D2_AUTH=<user>:<password> are still read as
fallbacks. Every script also takes --url to override DHIS2_BASE_URL.
"""
import json
import os
import sys


def _env(*names):
    """First non-empty value among the variables (canonical name first)."""
    return next((os.environ[n] for n in names if os.environ.get(n)), None)


def auth_from_env():
    """('token', pat) or ('basic', (user, password)) or None, canonical names first."""
    tok = _env("DHIS2_API_TOKEN", "D2_TOKEN")
    if tok:
        return "token", tok
    user = os.environ.get("DHIS2_USERNAME")
    if user:
        return "basic", (user, os.environ.get("DHIS2_PASSWORD", ""))
    if os.environ.get("D2_AUTH"):
        return "basic", tuple(os.environ["D2_AUTH"].split(":", 1))
    return None


def session(url=None):
    """Return (requests.Session, base_url). Exits with a clear message when
    requests is missing or the connection is not configured."""
    try:
        import requests
    except ImportError:
        sys.exit("needs requests: python3 -m venv .venv && .venv/bin/pip install requests")
    base = (url or _env("DHIS2_BASE_URL", "D2_URL") or "").rstrip("/")
    if not base:
        sys.exit("set DHIS2_BASE_URL (or pass --url)")
    s = requests.Session()
    auth = auth_from_env()
    if not auth:
        sys.exit("set DHIS2_API_TOKEN, or DHIS2_USERNAME and DHIS2_PASSWORD")
    if auth[0] == "token":
        s.headers["Authorization"] = "ApiToken " + auth[1]
    else:
        s.auth = auth[1]
    return s, base


def as_json(r):
    """r.json(), or exit with the status and the start of the body (an HTML login
    page, a proxy error) when the server did not answer with JSON."""
    try:
        return r.json()
    except ValueError:
        sys.exit(f"{r.request.method} {r.url} -> HTTP {r.status_code}, not JSON: {r.text[:200]!r}")


def metadata_errors(report):
    """Yield (type, uid, errorCode, message) from a /api/metadata import report."""
    body = report.get("response", report)
    for tr in body.get("typeReports", []):
        for orr in tr.get("objectReports", []):
            for er in orr.get("errorReports", []):
                yield (tr.get("klass", "").rsplit(".", 1)[-1], orr.get("uid"),
                       er.get("errorCode"), er.get("message", ""))


def tracker_errors(report):
    """Yield (trackerType, uid, errorCode, message) from a /api/tracker import report."""
    for e in report.get("validationReport", {}).get("errorReports", []):
        yield e.get("trackerType"), e.get("uid"), e.get("errorCode"), e.get("message", "")


def load_json(path):
    with open(path) as f:
        return json.load(f)
