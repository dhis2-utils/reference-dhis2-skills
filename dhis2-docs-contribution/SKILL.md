---
name: dhis2-docs-contribution
description: >
  Prepare and submit a documentation change to the dhis2/dhis2-docs GitHub
  repo, or to an app repo's docs/user folder — placing screenshots in the correct resources/images folder with the
  right capture settings and markdown syntax, running the formatting check
  for app-repo docs, then branching, committing, and
  opening a PR per DHIS2's git conventions. Use whenever the user wants to
  submit a docs fix, add or update a screenshot in the DHIS2 docs, commit
  changes to dhis2-docs, or open a pull request against it — even if they just
  say "commit this doc change" or "add this screenshot to the docs".
---

# DHIS2 Docs Contribution

You are taking a documentation change from "edited locally" to "PR open
against `dhis2/dhis2-docs`" (or an app repo's `docs/user` folder). This
normally goes wrong in five places, and this skill exists to prevent all of
them:

1. Screenshots land in the wrong folder or in the wrong format.
2. Commits and PRs do not follow DHIS2's conventions.
3. The change reaches the wrong branches: it lands on `master` only when it
   also needed a backport, or it is pushed to the upstream repo when the user
   must go through a personal fork.
4. The file path is guessed from the published URL
   (`docs.dhis2.org/.../use/...`), which does not match the repo layout.
5. An app-repo PR fails the repo's formatting check.

Everything here is grounded in the repo's own README
(https://github.com/dhis2/dhis2-docs), the DHIS2 developer portal's git
workflow page (https://developers.dhis2.org/docs/conceptual/git-workflow),
and hands-on verification against the live repo — if any of those have
changed since, trust the live source over this skill.

## Step 1: Locate the target file and confirm push access

**The file layout is flat, not nested by section.** User documentation lives
directly under `src/user/<page>.md`; developer documentation lives under
`src/developer/<page>.md`. There is no `content/<section>/` folder — that
shape belongs to the *published* URL structure (built by the separate
`dhis2-docs-builder` repo), not the source layout. Don't infer a nested path
from a URL; find the real one.

The reliable way to find a page's source is the repo's own recommended
route: open the page on docs.dhis2.org and click the **Edit (pencil) icon**
at the top — it links straight to the file in the repo, so you can read off
the exact `src/user/...` or `src/developer/...` path (and which branch it
lives on) rather than guessing.

**Confirm push access before doing anything else** — don't assume either
way:
```sh
git remote -v
```
- If `origin` already points at `dhis2/dhis2-docs` and pushes succeed, the
  user has direct push access — branch straight off `origin/master` (or the
  relevant version branch) and skip the fork steps below.
- Otherwise, this needs to go through a personal fork. Confirm the fork
  exists and both remotes are wired up:
  ```sh
  git remote -v
  # expect: origin   -> git@github.com:<your-account>/dhis2-docs.git
  #         upstream -> git@github.com:dhis2/dhis2-docs.git
  ```
  If `upstream` is missing: `git remote add upstream https://github.com/dhis2/dhis2-docs.git`.
  If there's no local clone at all, ask the user for the clone path (or fork
  + clone first) rather than running git commands against the wrong
  directory.

For **very small fixes** (typo, one-line wording change) with no local clone
at hand, the low-friction path is the browser-based edit: on docs.dhis2.org
click the same Edit (pencil) icon, edit in GitHub — this auto-forks for you
if needed — preview, and click "Propose file change" → "Create pull
request". Mention this option when the change is trivial; use the full
fork/git flow below for anything involving new images or multi-file changes.

## Step 2: Place and format screenshots correctly

**Folder:** images live in a shared `resources/images/` directory under each
section — `src/user/resources/images/<topic>/` or
`src/developer/resources/images/<topic>/` — organized by topic/chapter
subfolder (e.g. `resources/images/metadata-management/`,
`resources/images/android/`), **not** mirrored per-page, since the doc pages
themselves are flat files with no nesting. Check for an existing topic
subfolder before inventing a new one — reuse it if the page you're editing
already has one.

**Capture settings** (for screenshots of the DHIS2 web interface):
- Browser window set to **1440×900** (the repo recommends the Chrome "Window
  Resizer" extension for this).
- Capture with a tool like Chrome's "Fireshot" extension — visible-area
  capture is the default; full-page/scrolled capture is fine too, but keep
  the *width* at 1440px even then.
- Android app screenshots: **360×640**.

If a supplied screenshot doesn't match these dimensions, say so — don't
silently resize a distorted capture. A crop can fix an oversized capture; it
can't fix a wrong browser width, which needs a retake.

**Markdown reference syntax:**
- Plain image: `![](resources/images/<topic>/<file>.png)`
- Captioned figure (renders centered, italic caption below):
  `![Approving and accepting](resources/images/data_approval/approval_level_steps.png)`
- Sizing/alignment via trailing curly-brace attributes:
  `![](resources/images/<topic>/foo.png){ width=50% }` or, centered,
  `![](resources/images/<topic>/foo.png){ .center width=50% }`. Prefer
  percentages over fixed pixels so the image scales across output formats.

**Localization:** a translated image is saved *alongside* the original with
the language code appended before the extension — e.g. the French version of
`resources/images/<topic>/my_screenshot.png` is
`resources/images/<topic>/my_screenshot_fr.png`. The markdown link keeps
pointing at the English original; the build swaps in the localized file
automatically for that language edition. Only do this if the user is
actually supplying a localized image — don't invent placeholder translations.

## Step 2b: Content conventions (edits beyond screenshots)

When the change touches prose, headings, links, or tables rather than just
images, follow the repo's markdown conventions (CommonMark + a few
extensions):

- **Section anchors:** give referenced headings a stable id with a trailing
  hash in curly braces — `## Validation { #webapi_validation }` — and link to
  it from anywhere as `[link](#webapi_validation)`. Keep ids unique
  (lowercase + underscores) **across the whole doc set, not just the page you're
  editing** — the site compiles pages into a full-document form and resolves
  duplicate ids to the "closest" one, which silently cross-wires two
  sections that happen to share an id. A topic-specific prefix on new
  anchors (e.g. `mm_` for a Metadata Management page) is a cheap way to
  guarantee uniqueness without having to check every existing id. Prefer
  anchor links over file-path links in inter-document references — paths
  break because docs are compiled into both per-page and full-document
  forms.
- **Tables:** prefer GFM pipe tables over HTML — they translate far better.
  Reserve HTML tables for genuinely complex layouts. Add a caption with a
  preceding `Table: <caption>` block.
- **Includes:** `!INCLUDE "../other_dir/other_file.md"` pulls in another file;
  always use a relative path.
- **Naming:** the docs are moving to the compact form **"DHIS2"** consistently
  in prose (historically "DHIS 2"). Respect the compact form in variables and
  paths as they already appear.

## Step 3: Run the formatting check before you commit and push

App repos (`dhis2/<app>-app`) run `yarn d2-style check` in CI. For a docs
folder that means Prettier on every `.md` and `.yml` file, and the PR fails if
any file is not formatted. Run it after the last edit and before the commit
and push in Step 4, every time: a PR that was pushed without it has failed CI
before. Say in the handover that it passed.

- Run it on the files that will be committed, not on scratch copies: in the
  app repo, `yarn d2-style check`. Where the docs folder has no
  `package.json`, run `npx @dhis2/cli-style check text <docs-folder>`. Fix with
  `apply` instead of `check`, then run `check` again until it is clean. Both
  commands use the Prettier config that the repos use.
- Prettier will turn `*emphasis*` into `_emphasis_`, pad table columns, and
  re-indent nested lists. Check the words are unchanged afterwards.
- Also before handover: strip VERIFY and DECISION comments from the committed
  copy, and drop `index.md` if it is unused. Follow your team's convention for
  crediting AI assistance in commit messages and PR bodies.
- If the shell cannot run Node or reach the npm registry, say the check was
  not run and give the contributor the commands (`yarn install`, `yarn
  d2-style check`, `yarn d2-style apply`) instead of implying it passed.
- The `dhis2/dhis2-docs` repo itself does not run this check; this step is
  for app-repo docs.

## Step 4: Decide the target version(s)

DHIS2 docs are versioned — the repo keeps one long-lived branch per
supported DHIS2 release (named `2.<minor>`, e.g. `2.43`, `2.42`, `2.41` — not
`v43`) alongside `master`. **Before branching, ask which versions the change
needs to reach.** Two cases:

- **Master only** (new content, or a fix only relevant to the current line):
  use the *Standard workflow* below.
- **Needs backporting** to one or more older supported versions (most fixes
  to existing, still-shipped content): use the *Backport workflow*. The JIRA
  ticket, if any, should state the target versions.

Don't silently land a change on `master` alone when it also applies to
supported version branches — that's the most common way a doc fix fails to
reach the readers who hit the problem.

### Standard workflow (master only)

**Branch naming:** prefix with the JIRA ticket key if one exists, then a
short descriptive slug: `dhis2-1337/fix-typo-capture-app` (case of the
ticket-key prefix doesn't matter, dash or underscore separator both seen in
the wild — pick one and stay consistent within the branch). If there's no
ticket (a small doc fix usually won't have one), a plain descriptive branch
name is fine.

**Commit message — Conventional Commits format:**
```
<type>: <description>

[optional body]
[optional footer]
```
For docs content changes, `docs:` is the natural type (use `fix:` if you're
specifically correcting an error rather than adding/expanding content).
Don't pre-squash commits before pushing — DHIS2 squash-merges at merge time
and wants the compliant Conventional Commits message written *then*; granular
commits on the branch are fine and even useful for review.

**Commands** (branch off up-to-date upstream; push to `origin`, which is
`dhis2/dhis2-docs` directly if the user has push access, or their fork
otherwise):
```sh
git fetch upstream   # or 'origin' if there's no separate fork remote
git checkout -b dhis2-1337/fix-typo-capture-app upstream/master   # or a plain descriptive name
git add src/user/<file>.md src/user/resources/images/<topic>/<new-image>.png
git commit -m "docs: fix typo in capture app chapter"
git push -u origin dhis2-1337/fix-typo-capture-app
```
Double-check the image file itself is staged alongside the `.md` change —
a PR that references an image not in the diff will build broken.

### Backport workflow (multiple version branches)

When the change targets several versions (say `2.42`, `2.41`, `2.40`), base
it on the **latest common ancestor** of those branches so it merges cleanly
into each, then produce one feature branch per target:

```sh
git fetch upstream
git merge-base --octopus upstream/2.42 upstream/2.41 upstream/2.40   # -> <ancestor-hash>
git checkout -b dhis2-1337/fix-capture-app-patch <ancestor-hash>
# make + commit the change once on the patch branch
```
Then, for each target version, branch off that version and merge the patch
branch in (resolving conflicts per version if they arise):
```sh
git checkout -b dhis2-1337/fix-capture-app-2.42 upstream/2.42
git merge dhis2-1337/fix-capture-app-patch
git push -u origin dhis2-1337/fix-capture-app-2.42
# repeat for 2.41, 2.40 ...
```
This opens one PR per version branch (Step 5). Only reach for this flow when
backporting is actually required; master-only changes should stay on the
Standard workflow. Avoid `cherry-pick` for backporting unless you're certain
the branches will never be combined.

## Step 5: Open the PR

If pushing from a personal fork, tell `gh` the head is
`<your-github-username>:<branch>` and the base is the upstream branch:
```sh
gh pr create --repo dhis2/dhis2-docs --base master \
  --head <your-github-username>:dhis2-1337/fix-typo-capture-app \
  --title "docs: fix typo in capture app chapter" \
  --body "<what changed and why; link the JIRA ticket if any>"
```
If pushing with direct access (no fork), drop `--head` and let `gh` infer
the branch from the current checkout.

**If `gh` isn't installed or available**, open the compare URL directly in a
browser instead — this works from a fork just as well:
```
https://github.com/dhis2/dhis2-docs/compare/master...<your-github-username>:dhis2-docs:<branch>?expand=1
```
(swap `master` for the target version branch on a backport PR). Fill in the
title and body on the resulting "Open a pull request" page.

Write the PR title as a valid Conventional Commits message too — reviewers
may use it as-is for the squash-merge commit. For a **backport**, open one
PR per version, each with `--base <version-branch>` (e.g. `--base 2.42`) and
its matching head branch; note the version in each body.

## Step 6: Report back

Tell the user: the target version(s) and which workflow was used, branch
name(s), files changed (including new images and their final path), and the
PR URL(s). There's no local preview server for this repo, but CI builds one
automatically — DHIS2's `dhis2-docs-builder` CI posts a comment on the PR
with a live preview link in the shape
`https://docs.dhis2.org/temp/PR/<pr-number>/en/home.html` once the build
finishes; point the user at that comment rather than describing the change
in the abstract. Say whether the formatting check passed (app-repo docs). Flag anything uncertain (wrong screenshot resolution,
missing fork/clone, no JIRA ticket, unclear version targets). Don't merge —
DHIS2's own review process decides that.

## Out of scope

This skill covers *contribution mechanics* — getting a change correctly
formatted, branched, and opened as a PR. It does not cover verifying that
the content itself is factually correct (checking a claimed function list,
API behavior, or UI flow against the live app or source code) — treat that
as a separate step before you get here, not something this skill's process
guarantees.

Also, `dhis2-docs` is only one of roughly twenty repos that
`dhis2-docs-builder` federates content from (per-app repos, training-docs,
academy repos, and others). If the page in question isn't actually part of
`dhis2-docs`, this skill's git/PR mechanics may still apply loosely but the
specific paths and conventions above won't — confirm which repo actually
owns the page first.

## Gotchas this skill exists to prevent

- Handing over an app-repo push without running the Prettier check first —
  CI step `yarn d2-style check` then fails the PR (Step 3).
- Assuming the file lives under a `content/<section>/` path inferred from
  the published URL — it doesn't; the real layout is flat, under
  `src/user/` or `src/developer/`.
- Images dropped in a repo-root or doc-root `images/` folder, or nested to
  mirror a page path, instead of the shared topic-based
  `resources/images/<topic>/` folder.
- Screenshots at the wrong browser width (not 1440px) — inconsistent look
  across the doc set, and not fixable by cropping alone.
- Commit/PR titles that aren't valid Conventional Commits — causes manual
  cleanup at squash-merge time.
- Forgetting to `git add` the new image file itself, not just the `.md`
  referencing it.
- Localized image saved under a new/different link path instead of the
  `_<langcode>` suffix convention — the build's localization swap won't find
  it.
- Landing a fix on `master` only when it also applies to supported version
  branches — readers on those versions never get it. Ask about version
  targets up front.
- Assuming a fork is (or isn't) required instead of checking — pushing to
  `upstream` without push rights fails; assuming a fork is needed when the
  user actually has direct access adds unnecessary steps.
- File-path links between documents instead of unique section-id anchors —
  break when docs are compiled into full-document form. Also watch for
  anchor id collisions with *other* pages, not just within the page being
  edited.
