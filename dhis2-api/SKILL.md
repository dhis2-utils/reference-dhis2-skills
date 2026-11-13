---
name: dhis2-api
description: "Use when working with the DHIS2 Web API: writing curl calls or scripts against the API, ad-hoc calls on a live instance, endpoint behaviour and parameters, filter/fields/paging syntax, partial updates (PATCH) and sharing changes, and API differences between DHIS2 versions ('will this call work on 2.40 and 2.43', an endpoint renamed, a 415 or E1003 after an upgrade). Triggers on requests to connect to a DHIS2 instance, fetch data elements, indicators, organisation units or analytics through the API, find how an endpoint works or what parameters it accepts, check what an API response or error code means, or read the developer docs or dhis2-core source for an API detail. For general DHIS2 how-to and concept questions, use a DHIS2 knowledge search (askdhis2) instead; for bulk metadata export/transform/import, use dhis2-metadata."
---

## Overview

Conventions and verified quirks for calling the DHIS2 Web API, and where to look up what the API does on a given version. The quick reference below answers the common questions without fetching anything; `references/api-quirks.md` holds behaviour the docs don't state.

---

## Looking things up

Use the first source that applies, and check the version of whatever you cite.

**1. DHIS2 knowledge search, if your environment has it.** The DHIS2 knowledge MCP server (public endpoint `https://dhis2docs.mcp.kapa.ai`; tool `search_dhis2_knowledge_sources`) searches the docs, the developer docs, the Community of Practice, Academy material and Jira in one query. Write the query as a full sentence. For an error code or narrow API behaviour the results are often all Jira issues: useful (known bugs, fix versions), but not documentation. Say so when you rely on them, and look for the docs page as well. Results always come back, even when nothing fits; treat weak matches as "not covered".

**2. The docs pages themselves.** docs.dhis2.org publishes machine-readable indexes and serves every page as Markdown. Fetch an index, then the page it links; never guess page URLs.

| Question is about | Index URL |
|---|---|
| Web API, developer guides, Android SDK, app development | `https://docs.dhis2.org/en/llms-develop.txt` (~6 KB) |
| Implementation, system administration, end-user apps | `https://docs.dhis2.org/en/llms-implement.txt`, `llms-manage.txt`, `llms-use.txt` |
| Unsure which section | `https://docs.dhis2.org/llms.txt` (master index, ~94 KB) |

Index links already end in `.md`. For a rendered `.html` URL found elsewhere, replace `.html` with `.md`. Some pages (e.g. `metadata.md`) are very large. If a summarising fetch tool truncates them, save the page with `curl -s <url> -o page.md` and `grep -n` for the section.

**3. dhis2-core source**, when the docs don't settle it (see *Reading DHIS2 core source* below).

**4. A live check** on a disposable instance (`dhis2-test-instances`), when behaviour matters more than what anyone wrote down. Record the version you checked.

## Versions

The indexes link the **latest stable** version (the master `llms.txt` names it; 2.43 as of November 2026). If the user is on a different DHIS2 version, substitute the version segment in the URL: API behaviour changes between releases, and endpoint names do too.

```
dhis-core-version-243      DHIS2 2.43
dhis-core-version-242      DHIS2 2.42
dhis-core-version-241      DHIS2 2.41
dhis-core-version-240      DHIS2 2.40
dhis-core-version-master   development branch
```

Doc examples show API-versioned paths like `/api/33/configuration/corsAllowlist`. The numeric prefix is optional and the unversioned path works; don't copy `/api/NN/` verbatim. Check the endpoint name for the user's version, though: `corsAllowlist` exists from 2.41 (with `corsWhitelist` kept as an alias), while 2.40 only has `/api/configuration/corsWhitelist` (dhis2-core `ConfigurationController`, branches 2.40 and 2.41). The POST replaces the whole list, so GET it first and resend the existing entries.

---

## Reading DHIS2 core source

When the docs don't settle a question (exact authority semantics, what an endpoint really validates), read the implementation. A blobless sparse clone of [dhis2/dhis2-core](https://github.com/dhis2/dhis2-core) is fast (~53 MB, under a minute) and greppable:

```bash
git clone --filter=blob:none --no-checkout --depth 1 --branch 2.42 \
    https://github.com/dhis2/dhis2-core /tmp/dhis2-core
cd /tmp/dhis2-core
git sparse-checkout set dhis-2/dhis-api dhis-2/dhis-services dhis-2/dhis-web-api
git checkout   # REQUIRED: sparse-checkout alone leaves zero files, which looks like a failed clone
```

For a single known file, `raw.githubusercontent.com/dhis2/dhis2-core/<branch>/<path>` also works. GitHub code search requires auth, so grep the sparse clone instead.

---

## Working against an instance

Conventions for ad-hoc API calls (plain `curl` or a few lines of Python — no special tooling needed).

**Credentials.** Look for a `.env` (searching upward from CWD) with:

```
DHIS2_BASE_URL=https://myhost.org/dhis     # no /api suffix
DHIS2_API_TOKEN=d2pat_...                  # personal access token, or
DHIS2_USERNAME=admin                       # Basic auth (typical for sandboxes)
DHIS2_PASSWORD=district
```

If credentials are missing, ask the user, write them to `.env` in CWD (preserving any existing variables), and make sure `.env` is gitignored. Every skill's scripts read these same variables. An older `.env` may have `DHIS2_AUTH=user:password` instead; the `dhis2-metadata` scripts still accept it.

**Auth header for PATs is `Authorization: ApiToken {token}` — NOT `Bearer`.** Basic auth works as usual (`curl -u user:pass`).

**Always `curl -g` against DHIS2 APIs.** Any `fields=` selection with brackets (`fields=categoryCombo[id,name]`) is silently eaten by curl's URL globbing — the failure mode is an empty body, not an error. `-g` disables globbing. `-G --data-urlencode 'fields=…'` also works, because it percent-encodes the brackets; urllib/requests are unaffected.

**Keep responses out of context.** Default to `pageSize=50` and a narrow `fields=` selection (e.g. `fields=id,name`) on collection GETs. When a response may be large (full metadata, analytics, schemas), write it to a file and inspect it selectively (`jq`, Read with offsets) instead of printing it in full.

**Verified quirks live in `references/api-quirks.md`.** Read it before concluding an endpoint is broken, or before writing a script that filters, patches collections or exports metadata for sharing. It covers unsupported filter operators, unsafe index-based JSON Patch paths, unclearable COC codes, SQL-view word bans, and `:owner` exports leaking editors' names.

**Writes.** Before any POST/PUT/PATCH/DELETE, show the request (method, URL, body) and get the user's confirmation, unless the instance is known to be disposable (you created it, or the user said so). A localhost URL alone is not proof: it can be a tunnel to production. To get one, see the `dhis2-test-instances` skill.

---

## Quick reference

Use this to answer the most common API questions without fetching anything.

### Object filters

```
filter=name:like:Malaria
filter=valueType:eq:NUMBER
filter=shortName:ilike:art
```

Operators (2.40–2.43): `eq` `!eq` `gt` `gte` `lt` `lte` `like` `!like` `ilike` `!ilike` `$like`/`$ilike` (starts with) `like$`/`ilike$` (ends with) `token` `!token` `in` `!in` (`in:[a,b]`) `null` `!null` `empty`. `ieq` exists from 2.41 and `!empty` from 2.42; on older versions they fail with 400 E1003 (dhis2-core `DefaultQueryParser`/`DefaultJpaQueryParser`).

Multiple filters default to AND logic. Use `rootJunction=OR` for OR logic:

```
filter=name:like:HIV&filter=name:like:Malaria&rootJunction=OR
```

### Field filters

```
fields=id,name,valueType
fields=:all
fields=:identifiable
fields=id,name,organisationUnits[id,name]   # nested
fields=*,!href,!access                       # exclude fields
```

### Pagination

```
page=1&pageSize=50
```

Response includes a `pager` object: `{ page, pageSize, pageCount, total }`.

### Changing sharing on a single object

Use the dedicated sharing endpoint — not JSON-Patch, not a full-object PUT:

```
PUT /api/sharing?type=dataElement&id=<uid>
Content-Type: application/json

{"object": {
  "publicAccess": "--------",
  "externalAccess": false,
  "userAccesses": [],
  "userGroupAccesses": [{"id": "<groupUid>", "access": "rw------"}]
}}
```

- `type` is the **singular** schema name (`dataElement`, not `dataElements`). `GET /api/schemas?fields=singular,plural,dataShareable` gives the plural→singular map and the `dataShareable` flag (metadata-only vs data sharing) in one call.
- The endpoint changes **only** sharing — it never touches `owner` — and does **not** re-validate the rest of the object, so it works on messy legacy objects that fail import validation.
- It fully replaces `publicAccess`, `externalAccess`, `userAccesses` and `userGroupAccesses` with what you send.
- Access strings are 8-char octets: metadata rw = `rw------`, metadata + read-only data = `rwr-----`, metadata + read/write data = `rwrw----`, none = `--------`.

**Footgun — never JSON-Patch `/sharing`:** `[{"op":"replace","path":"/sharing","value":{"public":"--------",…}}]` returns **200**, applies `userGroups`/`users`, and **silently ignores** `public`/`external` — inside a patch value the fields must be named `publicAccess`/`externalAccess`, not the `public`/`external` aliases a GET shows. The object looks re-shared but stays publicly accessible, and nothing errors.

### Updating single fields (name, code, …)

Partial updates are version-split by content-type:

| DHIS2 version | `PATCH /api/<plural>/<uid>` | Result |
|---|---|---|
| 2.40 | `Content-Type: application/json`, body `{"name":"…"}` | **204** No Content |
| ≥ 2.41 | same request | **415** Unsupported Media Type |
| all (2.40–2.43) | `Content-Type: application/json-patch+json`, body `[{"op":"replace","path":"/name","value":"…"}]` | 200 |

Source: the plain-JSON "old PATCH" handler in `AbstractCrudController` exists on 2.40.12 and is gone from 2.41.0; the JSON Patch handler exists on all four. Live-checked: 204 on 2.40, 415 on 2.43. Portable pattern: send JSON Patch everywhere. Use plain JSON only for 2.40-specific code.

Two general rules for writes:

- **JSON-Patch (and any full-object write) re-validates the whole object**, so it can **409 on pre-existing integrity issues unrelated to your change** (`E6012` "attribute not assigned to type", `E6000`, …) — common on old production metadata. Prefer dedicated endpoints (`/api/sharing`) where they exist; on 2.41+ there is no partial-update escape hatch for other fields.
- **Success isn't always 200.** Partial PATCH returns 204; metadata imports can return 200 with `"status": "ERROR"`/`"WARNING"` in the body. Treat any 2xx as transport success, then check the response body and (for writes that matter) re-GET the object to confirm the change landed.

### Analytics endpoint

```
GET /api/analytics
  ?dimension=dx:UID1;UID2          # data elements / indicators
  &dimension=pe:LAST_12_MONTHS     # period
  &dimension=ou:LEVEL-1            # org unit level
  &displayProperty=NAME
  &skipMeta=false
```

Common period shortcuts: `THIS_YEAR`, `LAST_YEAR`, `LAST_12_MONTHS`, `THIS_QUARTER`, `202301` (specific month).
