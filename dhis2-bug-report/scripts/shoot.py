#!/usr/bin/env python3
"""Log in to a DHIS2 instance and screenshot an app path.

Examples:
    python shoot.py --base https://play.im.dhis2.org/stable-2-43-2-1 \
        --viz q1CJxWmlbi6 --out pivot.png

    python shoot.py --base https://play.im.dhis2.org/stable-2-43-2-1 \
        --path /dhis-web-maps/index.html --out maps.png --wait 15

    python shoot.py --base ... --viz q1CJxWmlbi6 --out p.png --requests analytics

Notes:
    Find the current play slug with
    curl -s -o /dev/null -w '%{redirect_url}' https://play.dhis2.org/2.43
    Authentication goes through the browser context's request object, which
    shares its cookie jar with the pages, so the app loads already logged in:
    POST /api/auth/login on 2.41+, and on 2.40 (where that endpoint 302s to the
    legacy login page and leaves an anonymous cookie) a Basic-auth GET /api/me,
    which sets a session cookie. The session is verified before the screenshot.
"""
import argparse
import base64
import sys
import time

from playwright.sync_api import sync_playwright


def session_ok(ctx, base):
    """True if the context's cookies alone authenticate (no redirect to login)."""
    r = ctx.request.get(base + "/api/me?fields=id", max_redirects=0)
    return r.status == 200 and "json" in r.headers.get("content-type", "")


def login(ctx, base, user, password):
    # 2.41+: /api/auth/login sets the session cookie.
    r = ctx.request.post(base + "/api/auth/login",
                         data={"username": user, "password": password},
                         headers={"Content-Type": "application/json"},
                         max_redirects=0)
    if r.status < 300 and session_ok(ctx, base):
        return
    # 2.40: no /api/auth/login (302 to the legacy login page). A Basic-auth
    # request to /api/me returns a session cookie into the same jar.
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    r = ctx.request.get(base + "/api/me?fields=id",
                        headers={"Authorization": "Basic " + token}, max_redirects=0)
    if r.status != 200 or not session_ok(ctx, base):
        sys.exit(f"login failed: {r.status} {r.text()[:200]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True, help="instance base URL, no trailing slash")
    p.add_argument("--out", required=True, help="output PNG path")
    p.add_argument("--viz", help="saved visualization uid, opens Data Visualizer at it")
    p.add_argument("--path", help="app path to open instead, e.g. /dhis-web-maps/index.html")
    p.add_argument("--user", default="admin")
    p.add_argument("--password", default="district")
    p.add_argument("--wait", type=int, default=10, help="seconds to settle after load")
    p.add_argument("--selector", default="table",
                   help="wait for this selector (searched inside the app iframe first)")
    p.add_argument("--width", type=int, default=1600)
    p.add_argument("--height", type=int, default=950)
    p.add_argument("--full-page", action="store_true")
    p.add_argument("--ignore-https-errors", action="store_true",
                   help="accept invalid certificates (self-signed test servers, "
                        "TLS-intercepting proxies)")
    p.add_argument("--requests", metavar="SUBSTRING",
                   help="also print request URLs containing this substring")
    a = p.parse_args()

    if not a.viz and not a.path:
        sys.exit("give either --viz or --path")
    target = a.path if a.path else "/dhis-web-data-visualizer/index.html#/" + a.viz

    seen = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--no-sandbox"])
        ctx = browser.new_context(viewport={"width": a.width, "height": a.height},
                                  ignore_https_errors=a.ignore_https_errors)
        login(ctx, a.base, a.user, a.password)

        page = ctx.new_page()
        if a.requests:
            page.on("request", lambda req: seen.append(req.url) if a.requests in req.url else None)
        page.goto(a.base + target, wait_until="load")
        # DHIS2 serves apps inside an iframe from the global shell, so a top-level
        # selector never matches and the wait silently falls through to the sleep.
        # Look inside the frame first, then top level for older shells.
        found = False
        for loc in (page.frame_locator("iframe").locator(a.selector).first,
                    page.locator(a.selector).first):
            try:
                loc.wait_for(timeout=45000)
                found = True
                break
            except Exception:
                continue
        if not found:
            print(f"warning: never saw {a.selector!r}; screenshot may be premature",
                  file=sys.stderr)
        time.sleep(a.wait)
        page.screenshot(path=a.out, full_page=a.full_page)
        browser.close()

    print("saved", a.out)
    for u in dict.fromkeys(seen):
        print("request:", u)


if __name__ == "__main__":
    main()
