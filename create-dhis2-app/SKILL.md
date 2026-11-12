---
name: create-dhis2-app
description: "Scaffold a new, simple vanilla-JavaScript DHIS2 tool from the dhis2/tool-template: no React, no TypeScript, no App Platform. Use when the user wants a lightweight admin tool, system utility, cleanup tool or quick DHIS2 helper in plain JS with direct DOM manipulation. Triggers on 'simple DHIS2 app', 'vanilla DHIS2 tool', 'lightweight admin tool', 'tool-template', 'no React', 'quick DHIS2 utility', or when the user says they don't need the full App Platform. Also the reference for tool-template conventions (d2api.js helpers, .env proxy, d2-manifest). Not for React/@dhis2/ui/App Platform apps (use d2-app-scripts and the App Platform docs), reviewing an existing app (dhis2-app-review), or general DHIS2 API questions (dhis2-docs)."
---

# Create a DHIS2 tool from the tool-template

Scaffold a new DHIS2 web app from [dhis2/tool-template](https://github.com/dhis2/tool-template):
plain JavaScript with ES modules, Webpack 5 and direct DOM manipulation. No React, TypeScript,
App Platform or `@dhis2/ui`. It is meant for system-administration tools, not end-user apps.
The template's README states it is verified against DHIS2 2.40–2.43: on 2.41 and older the
bundled legacy header bar is shown, and on 2.42+ the app renders inside the global shell.

The recommended route for most DHIS2 apps is the
[App Platform](https://developers.dhis2.org/docs/app-platform/getting-started)
(`npx @dhis2/cli-app-scripts init <name>`), which brings React, `@dhis2/ui`, translations
(`d2-app-scripts i18n`), offline/PWA support (`pwa.enabled` in `d2.config.js`) and the app
runtime. The tool-template has none of these: it is an online admin tool with English-only
markup. **If the requirements need offline use, translations, or non-technical end users entering
data, this is the wrong template even when the user asks for it by name.** Say so, be honest that
the App Platform means React, and ask before scaffolding anything.

## Workflow

### 0. Check the directory

| Finding | Means |
|---|---|
| `d2.config.js` exists, or `package.json` depends on `@dhis2/app-runtime` | App Platform project. Wrong template; stop. |
| `package.json` has a `"manifest.webapp"` block, or `src/js/d2api.js` exists | Existing tool-template project. Don't scaffold; help with the actual request using the conventions below. |
| `src/js/d2api.js` where `d2PostThenGet` takes only an endpoint, or `webpack.config.js` passes the whole `dhisConfig` to `DefinePlugin` | A copy of an **older template** (v0.3.x or earlier); see "Older copies" below. |
| Empty or near-empty | Scaffold into the **current directory** (don't create a subdirectory). |

### 1. Confirm the template and gather details

If the user asked for a simple/vanilla tool, go ahead. If they mention React, TypeScript,
`@dhis2/ui` or the App Platform, confirm before scaffolding.

Ask only for what the user hasn't given:

- **Package name**, kebab-case (`data-integrity-checker`). Becomes `package.json` `name` and
  the zip filename `compiled/<name>.zip`.
- **Display name**, human-readable (`Data Integrity Checker`). Becomes `manifest.webapp.name`,
  which DHIS2 uses for the app key and menu entry (see step 3).
- **One-line description.**
- **Developer / organisation** for `manifest.webapp.developer`. If not given, keep the
  template's values and tell the user to change them.

Default version: `0.1.0`.

### 2. Clone and reinitialise

```bash
git clone --depth 1 https://github.com/dhis2/tool-template .
rm -rf .git CHANGELOG.md
git init
```

If the directory isn't empty, clone into `tmp=$(mktemp -d)`, copy `"$tmp"/.` over (skipping
`.git`), then `git init`.

Keep `.github/workflows/`: `ci.yml` lints and builds the zip on every PR and push to `main`;
`release.yml` builds and attaches the zip to a GitHub release when a `v*.*.*` tag is pushed,
and only warns if the tag and `package.json` version differ.

### 3. Customise

**`package.json`**
- `name`, `description`, `version` (top level).
- **`"manifest.webapp".name` → the display name.** `d2-manifest` builds `manifest.webapp`
  from the top-level `name`/`version`/`description` and then overlays the `"manifest.webapp"`
  block, so the template's `"name": "Tool Template"` there wins over the top-level `name`.
  DHIS2 derives the app key from the manifest name (non-alphanumerics stripped, spaces → `-`,
  so `Tool-Template`) and the menu authority from it (`M_Tool_Template`). Leave it unchanged
  and every tool built from the template installs under the same key and replaces the
  previous one on the instance.
- `"manifest.webapp".developer` if the user gave developer details.
- Leave `appType`, `icons` and the build scripts alone. To change the icon, replace
  `src/img/icons/app_logo_48x48.png` and `app_logo_96x96.png` at the same paths.

**`src/index.html`**: set `<title>` to the display name. Keep `<div id="dhis-header-bar">`.
Replace the `#mainView` content (including the Hello button) with a heading and a one-line
"edit `src/app.js` to get started" placeholder.

**`src/app.js`**: keep the imports (`d2Get` from `./js/d2api.js`, `loadLegacyHeaderBarIfNeeded`
and its call, `./css/style.css`). Remove the `testApi`/`window.helloWorld` demo code, since
the button that called it is gone, and leave the file as a clean entry point. ESLint flags an
unused `d2Get` import, so either use it (e.g. log `/api/system/info` version) or remove it.

**`README.md`**: replace with the app name, description, requirements (Node >= 20.19, yarn,
`zip`), getting started (`cp .env.template .env`, `yarn install`, `yarn start`,
`yarn run zip`), and a note on configuring `.env`.

**`AGENTS.md`**: update the Context section to name the new app and its purpose. Keep the
rules and architecture sections; they still apply.

### 4. Set up

```bash
node --version      # must satisfy package.json engines: >= 20.19.0 (CI uses 22)
cp .env.template .env
yarn install
```

If Node is too old, say so and stop; the later failure is cryptic. Use **yarn, not npm**: the
repo tracks only `yarn.lock` (`package-lock.json` is gitignored) and CI installs with
`--frozen-lockfile`.

`.env` holds `DHIS2_BASE_URL` and either `DHIS2_API_TOKEN` (a personal access token, sent as
`Authorization: ApiToken …`) or `DHIS2_USERNAME`/`DHIS2_PASSWORD`, plus optional
`DHIS2_DEV_PORT`. Tell the user to fill it in before `yarn start`. If there is no instance to
develop against, see `dhis2-test-instances`.

### 5. Verify the scaffold

```bash
yarn run zip
```

This runs lint → webpack build → `d2-manifest` → zip, the same chain CI and releases use, and
fails early if the `zip` binary is missing. Then check `build/manifest.webapp`: `name` must be
the display name, not `Tool Template`. Fix any failure before continuing.

### 6. Initial commit

```bash
git add -A
git commit -m "Initial scaffold from dhis2/tool-template"
```

### 7. Orient the user

- **App logic**: `src/app.js` is the entry point; add modules in `src/js/`.
- **UI**: `src/index.html`, styles in `src/css/style.css`.
- **DHIS2 API**: always use the helpers in `src/js/d2api.js`, never raw `fetch`:
  `d2Get(endpoint)`, `d2PostJson(endpoint, body)`, `d2PutJson(endpoint, body)`,
  `d2Delete(endpoint)`, and `d2PostThenGet(endpoint, body?, getEndpoint?, maxTries=10, intervalMs=1000)`,
  which POSTs, then polls `getEndpoint` (default: the POST endpoint) until the response is
  non-empty and **rejects on timeout**. The helpers handle the base URL (`../../..` when
  installed, same-origin in dev) and error parsing.
- **Dev server**: `yarn start` on port 8081, or `DHIS2_DEV_PORT`. If the user's browser can
  only reach certain forwarded ports, set `DHIS2_DEV_PORT` to one of them. Every request goes
  same-origin through the webpack-dev-server proxy, which adds the credentials from `.env`.
  The instance needs no CORS allowlist entry, and credentials never reach the browser bundle.
- **Deploy**: `yarn run zip` → `compiled/<name>.zip`; upload it in App Management or
  `POST /api/apps`. Users without `ALL` need the app's `M_…` authority to open it.
- **Lint**: `yarn run lint` (4-space indent, double quotes, semicolons).

## Older copies of the template

Tools copied before v0.4.0 (July 2026; tags in `dhis2/tool-template`) differ in ways that cause
real problems. Compare with the current template (`git clone --depth 1` it to a temp dir) and
bring over:

- **Dev credentials in the bundle and CORS.** v0.3.x `webpack.config.js` passes `dhisConfig`
  (instance URL + `Authorization` header from `.env`) to `DefinePlugin` for dev builds, so the
  browser calls the instance cross-origin with the credentials in the served JS; that is why such
  projects needed a CORS allowlist entry. Current: `DHIS_CONFIG` is `{ baseUrl: "" }` in dev,
  every call goes same-origin through the dev-server proxy, which adds the header. Tell the user
  to rotate credentials that were exposed. (v0.2.x used `d2auth.json` instead of `.env`.)
- **`d2PostThenGet` timeouts.** v0.3.x resolves with the last, empty poll result after 10 tries,
  so callers report "nothing found" on a slow server. Current: it rejects on timeout and takes
  `(endpoint, body?, getEndpoint?, maxTries, intervalMs)`; callers must catch the rejection and
  can raise the polling budget for slow checks (data integrity on large instances).
- **Smaller items:** an explicit `"manifest.webapp".name` (v0.3.x has none, so the menu name and
  app key follow the npm package name), `engines.node >=20.19.0`, yarn only (`package-lock.json`
  gitignored, CI uses `--frozen-lockfile`), `.github/workflows/ci.yml` and `release.yml`,
  `DHIS2_DEV_PORT`.

## Rules

These keep the app consistent with the template; preserve them:

- **Vanilla JS only**: no React, Vue or other frameworks.
- **Keep Webpack**: don't swap in Vite or another bundler; the dev proxy and packaging depend on it.
- **No hard-coded URLs or credentials**: they belong in `.env`, which is gitignored.
- **Use the `d2api.js` helpers** for every DHIS2 call, and surface API errors to the user.
- **Keep the `d2-manifest` step** that generates `manifest.webapp` on build.
- **Verify after changes**: `yarn run lint` after JS edits, `yarn run zip` after significant ones.
