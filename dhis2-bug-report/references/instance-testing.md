# Instance testing

## Play instances

Public Sierra Leone demos, login `admin` / `district`. This skill is the one place where using them is appropriate: a bug report needs a recipe anyone can follow on a public instance. Never use them for anything but reproduction, and keep writes to small, named test objects.

Find the current URL by following the redirect rather than guessing a slug:

```bash
curl -s -o /dev/null -w '%{redirect_url}\n' https://play.dhis2.org/2.42
# -> https://play.im.dhis2.org/stable-2-42-7-1
```

Slugs are `stable-<major>-<minor>-<patch>[-<hotfix>]` (in November 2026: `stable-2-43-2-1`, `stable-2-42-7-1`, `stable-2-41-11`) and change with every patch release; an old slug returns 404. `https://play.im.dhis2.org/dev` runs the next version (`2.44-SNAPSHOT`). Releases that have left play (2.40 by late 2026) redirect to the instance list at `https://im.dhis2.org/public/instances`. To test such a version, or anything that needs more than small test objects, use a disposable instance (see `dhis2-test-instances`) and say in the ticket that it is not a public demo.

`curl -g` for anything with brackets in `fields=`, otherwise curl's globbing silently eats the query and returns an empty body.

Analytics tables on play are rebuilt nightly. `lastAnalyticsTableSuccess` in `/api/system/info` tells you how stale the figures are, which matters if you are reporting exact numbers.

Use fixed periods (`202601`) rather than relative ones (`LAST_3_MONTHS`) in test objects and in the ticket. Relative periods make the numbers unreproducible next month.

## Versions

Three separate facts, all worth recording.

Core version:

```
GET /api/system/info      -> version, revision, buildTime
```

Installed app version — the manifest is behind authentication, so use a session cookie or basic auth:

```
GET /<app-path>/manifest.webapp     e.g. /dhis-web-data-visualizer/manifest.webapp
                                    -> name, version, core_app
```

If the manifest 302s to the login page, the request is unauthenticated. Log in first and reuse the cookie jar: `POST /api/auth/login` with `{"username":..,"password":..}` on 2.41+; on 2.40 that endpoint doesn't exist (302 to the legacy login page, anonymous cookie), so use Basic auth on each request, or a Basic-auth `GET /api/me` to get a session cookie.

To confirm the manifest is not stale, grep the compiled bundle for its version string. Read `index.html`, take the asset filenames from the `src`/`href` attributes, fetch the main bundle and look for `appVersion`.

Latest published version, through the instance's App Hub proxy:

```
GET /api/appHub/v2/apps?query=<App%20Name>
```

The result carries a `versions` array, each entry with `version`, `channel`, `minDhisVersion`, `maxDhisVersion` and a `created` epoch in milliseconds. Sort by version to find the newest, and note the channel — a newer version on a non-stable channel is a different claim from a newer stable release. `GET /api/appHub/v2/apps/<id>` does not return the same structure, so use the query form.

Cross-check against the repo when it matters:

```
https://raw.githubusercontent.com/dhis2/<app-repo>/master/package.json
```

Core apps often declare a wide compatibility range (`minDhisVersion` 2.40, no maximum), so one app build can serve several core versions. When it does, say so in the ticket: a fix lands once rather than needing backports.

## Analytics calls worth making

Values, with the metadata that explains how the app will aggregate them:

```
GET /api/analytics.json
  ?dimension=dx:<items>&dimension=pe:<periods>&dimension=ou:<orgunits>
```

Aggregation types per item — this is where `totalAggregationType` lives, and it is often the explanation for a totals bug:

```
GET /api/analytics?dimension=dx:<items>,pe:<period>&filter=ou:<ou>
    &skipData=true&includeMetadataDetails=true
```

Without `includeMetadataDetails=true` the metadata items carry only a name, which tells you nothing.

Numerator, denominator, factor, multiplier and divisor per row:

```
GET /api/analytics?dimension=dx:<items>,pe:<period>&filter=ou:<ou>&includeNumDen=true
```

Compare these columns across item types. Empty `multiplier`/`divisor` on one item type and populated on another is a strong lead when a computed cell comes out as `NaN`.

To see what an app actually asks for, capture its network requests in the headless browser rather than guessing. See `screenshots.md`.

## Creating a temporary visualization

The single-object POST accepts the layout through `columns` / `rows` / `filters`, and derives `dataDimensionItems`, `organisationUnits` and `periods` from the items you put there.

```json
{
  "name": "ZZTEST short description",
  "type": "PIVOT_TABLE",
  "colTotals": true, "rowTotals": true, "colSubTotals": true, "rowSubTotals": true,
  "digitGroupSeparator": "SPACE", "aggregationType": "DEFAULT",
  "columns": [{"dimension": "dx", "items": [
    {"id": "fbfJHSPpUQD"},
    {"id": "BfMAe6Itzgt.ACTUAL_REPORTS"}
  ]}],
  "rows": [
    {"dimension": "ou", "items": [{"id": "ImspTQPwCqd"}, {"id": "O6uvpzGd5pu"}]},
    {"dimension": "pe", "items": [{"id": "202601"}, {"id": "202602"}]}
  ],
  "filters": [],
  "sharing": {"public": "rw------"}
}
```

Data items go in `columns[].items` (or `rows[].items`) as plain ids. Completeness items use the composite form `<dataSetUid>.ACTUAL_REPORTS`, `.EXPECTED_REPORTS`, `.REPORTING_RATE`, `.ACTUAL_REPORTS_ON_TIME`, `.REPORTING_RATE_ON_TIME`.

Then open it in the app at `/<app-path>/index.html#/<uid>`.

### Traps

On the single-object `POST`/`PUT /api/visualizations`, sending the export-shape fields (`dataDimensionItems`, `periods`, `organisationUnits`, a `relativePeriods` object, `columnDimensions`/`rowDimensions`/`filterDimensions`) returns 201 and silently drops them; the object comes back with `dataDimensionItems: []`. Relative periods would go in as `pe` items (`{"id":"LAST_12_MONTHS"}`), but use fixed ones in test objects (see above). `POST /api/metadata` is the reverse: it keeps the export shape (a `relativePeriods` object becomes `rawPeriods`) and ignores `columns`/`rows`/`filters` (verified 2.42.6 and 2.43.1). Always read the object back before trusting it — request `:owner` fields, not the default field set, because the default view hides the difference.

`"sharing": {"public": "rwrw----"}` fails with E3011, since visualizations are not data-shareable. Use `rw------`.

Subtotal cells only render when an axis carries two or more dimensions. If subtotals are the thing under test and no subtotal row appears, check the layout before concluding the option is broken.

Verification pattern after any create:

```
GET /api/visualizations/<uid>?fields=:owner
```

Confirm the item list, the dimensions, the periods and the org units all survived.

### Cleanup

```
GET    /api/visualizations?fields=id,name&filter=name:like:ZZTEST&paging=false
DELETE /api/visualizations/<uid>
```

Re-run the GET afterwards and confirm it returns nothing.
