"""Minimal DHIS2 API client. Every call is appended to <work_dir>/api-log.jsonl (method, path, status, short bodies),
so the evidence write-up can show exactly what was done.

Connection from the environment: DHIS2_BASE_URL, and DHIS2_API_TOKEN (personal access token) or DHIS2_USERNAME +
DHIS2_PASSWORD. The older names DHIS2_URL, DHIS2_TOKEN and DHIS2_USER are still read as fallbacks.
"""
import base64, json, os, random, string, sys, time, urllib.error, urllib.parse, urllib.request

_LOG = None


def _env(*names):
    """First non-empty value among the environment variables (canonical name first, then old aliases)."""
    return next((os.environ[n] for n in names if os.environ.get(n)), None)


def connection():
    """(base_url or None, token or None, username or None, password or None) from the environment."""
    return (_env('DHIS2_BASE_URL', 'DHIS2_URL'), _env('DHIS2_API_TOKEN', 'DHIS2_TOKEN'),
            _env('DHIS2_USERNAME', 'DHIS2_USER'), _env('DHIS2_PASSWORD', 'DHIS2_PASS'))


def _base():
    b = connection()[0]
    if not b:
        sys.exit('set DHIS2_BASE_URL (and DHIS2_API_TOKEN, or DHIS2_USERNAME and DHIS2_PASSWORD)')
    return b.rstrip('/')


def _auth():
    _, tok, u, p = connection()
    if tok:
        return 'ApiToken ' + tok
    if not (u and p):
        sys.exit('set DHIS2_API_TOKEN, or DHIS2_USERNAME and DHIS2_PASSWORD')
    return 'Basic ' + base64.b64encode(f'{u}:{p}'.encode()).decode()


def set_log(path):
    """Log file for this run (normally cfg.out('api-log.jsonl'))."""
    global _LOG
    _LOG = path


def req(method, path, body=None, ctype='application/json', log=True, timeout=900):
    """Returns (status, parsed JSON or {'_raw': text})."""
    data = None
    if body is not None:
        data = body.encode() if isinstance(body, str) else json.dumps(body).encode()
    h = {'Authorization': _auth(), 'Content-Type': ctype, 'Accept': 'application/json'}
    r = urllib.request.Request(_base() + path, data=data, headers=h, method=method)
    try:
        resp = urllib.request.urlopen(r, timeout=timeout)
        status, txt = resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        status, txt = e.code, e.read().decode()
    try:
        j = json.loads(txt) if txt else {}
    except ValueError:
        j = {'_raw': txt[:2000]}
    if log and _LOG:
        with open(_LOG, 'a') as f:
            f.write(json.dumps({'t': time.strftime('%Y-%m-%dT%H:%M:%S'), 'method': method, 'path': path, 'status': status,
                                'request': body if isinstance(body, str) else (json.dumps(body)[:600] if body is not None else None),
                                'response': json.dumps(j)[:800]}) + '\n')
    return status, j


def get(path, **kw):
    s, j = req('GET', path, log=False, **kw)
    if s >= 400:
        raise RuntimeError(f'GET {path}: HTTP {s} {str(j)[:300]}')
    return j


def uid():
    """A valid DHIS2 UID (11 chars, starts with a letter)."""
    return random.choice(string.ascii_letters) + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))


def uids(n):
    return get(f'/api/system/id.json?limit={n}')['codes']


def run_analytics(last_years=3, timeout=3000):
    """Run the analytics tables job and wait. Returns (seconds, final message, level)."""
    s, j = req('POST', f'/api/resourceTables/analytics?lastYears={last_years}&skipResourceTables=false')
    if s >= 400:
        raise RuntimeError(f'analytics trigger failed: HTTP {s} {j}')
    task = j['response']['relativeNotifierEndpoint']
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(10)
        _, n = req('GET', task, log=False)
        if isinstance(n, list) and any(x.get('completed') for x in n):
            done = [x for x in n if x.get('completed')][0]
            req('GET', task)  # log the final state once
            return round(time.time() - t0), done.get('message'), done.get('level')
    return None, 'timeout', None


def analytics(params, log=False):
    """GET /api/analytics with a cache-buster. params: list of (key, value)."""
    q = urllib.parse.urlencode(list(params) + [('_cb', str(random.random()))])
    return req('GET', '/api/analytics.json?' + q, log=log, timeout=300)
