# Evidence ladder

For each claim type: the **primary** evidence that can settle it, what can
**corroborate** it, and what **never settles it alone**. When primary evidence
is not available in the time you have, the verdict is Unverified. It is not
Confirmed on corroboration alone.

## By claim type

| Claim type | Primary | Corroborates | Never settles alone |
|---|---|---|---|
| Expression functions and operators, per expression type | Registration maps in `dhis2-core`: `DefaultExpressionService.java` (indicator, predictor, validation rule), `ExpressionMapBuilder.java` (program indicator), `ParserUtils.java` (common set), at the release branch | Developer manual at the same branch; a test expression on a pinned instance | ANTLR grammar (`dhis2/dhis2-antlr-expression-parser`); Jira design tickets such as DHIS2-4469 |
| Screens and actions an app offers | App repo at the shipped tag: `src/pages/*/` (one directory per screen), routes, sidebar config | Live pinned instance; app FE tests | Sidebar as described in docs; changelog lines |
| Backend capability (endpoint exists, accepts X) | Controller mapping in `dhis2-core` per release branch (for example `@PostMapping("/merge")` via `git show <branch>:<path>`) | OpenAPI spec of a pinned instance; developer docs at that branch | Frontend having a screen for it |
| Frontend gating by core version | Version checks in app source: `useConfig().serverVersion`, `d2.system.version.minor`, feature maps such as MMA `src/lib/featuresApiSupport/support.ts` | Live check on two pinned versions | Changelog wording ("gated to v43+") |
| App availability on a core version | `minDHIS2Version` / `maxDHIS2Version` in `d2.config.js` at the tag; App Hub compatibility | Bundled-version survey; pinned instance | Docs version branch the page sits on |
| UI string (label, button, title, option) | `i18n/en.pot` msgids plus the page component, at the tag | Pinned instance screenshot, read directly | Any docs diff; old screenshots |
| Nav path | App sidebar/route config at the tag; live sidebar | Screenshot in the PR, read directly | Overview-page card titles (singular vs plural trap) |
| Default value, constraint, validation | Form helper or schema in app source (for example `form-helper.js`); backend `*Params`/`ImportOptions` classes and schema | Pinned instance; regression case with a recent confirmation date | Docs prose on any branch |
| Behaviour (what happens, ordering, aggregation) | Backend service code (for example `DefaultResourceTableService` ordering); analytics SQL | Regression suite case; BE tests; live test on a pinned instance | CoP answers; Kapa |
| Version boundary | Code history: `git log -S` plus first containing tag, per section | Jira Fix Version and Resolution (and QA comments naming builds); release and upgrade notes; deprecated-features table in `dhis2-releases` | Diff between two docs branches; the oldest branch you compared |
| Released vs merged | `git tag --contains <commit>` in the app repo; App Hub release list | Package version at the tag | Commit on the default branch |
| Shipped vs proposed | Code in the registration map, controller or screen | Jira Resolution (not Status) | Design ticket, however detailed |
| Product bug vs doc error | Jira bug with tested builds; regression suite bug log | Live repro on a pinned instance | Docs silence |
| Link or anchor exists | Request to the published URL | Heading search across all federated repos, with auto-slug rules | Grep of one dhis2-docs checkout |
| Screenshot content | The pixels, opened directly | String inventory at the tag | Filename, caption, alt text |
| Commit authors, dates, owners | `git log` in a real clone; GitHub API | | A spreadsheet Owner field; graph edges derived from it |

## Source catalogue

**Code**
- `dhis2/dhis2-core`, release branches `2.40`, `2.41`, `2.42`, `2.43`, `master`.
- App repos (`dhis2/<app>`), each with its own release tags. Most apps are
  continuously released, so their UI changes follow the app version, not the
  core version.

**Tests**
- `dhis2-regression-tests` (clone it into a scratch directory): the test
  cases, and the README "Bugs and behaviour discrepancies" log with
  confirmation dates. Note which suites are not wired into CI.
- App FE tests (Cucumber, Jest, Cypress). Jest tests can sit next to the
  component, under `__tests__` or under `__test__`. Any index built on one
  glob misses the others.
- `dhis2-core` back-end tests.

**Release records**
- Supported versions: `downloads/v1/versions/stable.json` in the `dhis2/dhis2-releases` repo (same data as `releases.dhis2.org/v1/versions/stable.json`, which is often blocked). Large: check that the whole file came back.
- `dhis2/dhis2-releases`: release notes, upgrade notes, deprecated features.
- App CHANGELOGs and App Hub release lists (leads only).

**Tickets and community**
- Jira: Fix Version, Resolution, comments. REST at `https://dhis2.atlassian.net/rest/api/2/issue/<KEY>` (jira.dhis2.org is often blocked).
- CoP and Kapa: orientation and reader-impact signals. They are never evidence.

**Live**
- `play.im.dhis2.org` version-pinned instances, named by patch release
  (`stable-2-43-1` form) plus `dev`. Patch instances are replaced as new
  patches ship, so read the current names from the play index instead of
  reusing a name from an earlier audit. The API takes the public
  demo login (`-u admin:district`). A browser redirect to the login page does
  not mean the check is blocked. The rendered UI needs a browser session.
- OpenAPI spec of a pinned instance.

**Docs corpus (for existence and coverage claims)**
docs.dhis2.org builds from about 20 repos through `@github(<repo>, <path>, <branch>)`
refs in `dhis2-docs-builder`, and per version. As of 2026-08-18:
`academy-dhis2-fundamentals`, `aggregate-data-entry-app`, `app-management-app`,
`approval-app`, `cache-cleaner-app`, `capture-app`, `dashboard-app`,
`data-visualizer-app`, `dhis2-android-docs`, `dhis2-android-sdk`, `dhis2-docs`,
`dhis2-docs-implementation`, `dhis2-releases`, `line-listing-app`, `maps-app`,
`metadata-package-development`, `route-manager-app`, `training-docs`,
`usage-analytics-app`, `user-profile-app`. Recheck the builder config, because
the list grows (import-export-app and scheduler-app docs moves were in
progress on 2026-09-29).
