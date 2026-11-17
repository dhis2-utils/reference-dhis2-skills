# Recipes

Run all git work in a **scratch directory**. Never run git against a repo
that someone else has checked out and is working in (for example a shared or
mounted folder), not even in a scratch worktree.

Keep one clone cache per session and reuse it:

```sh
C=${AUDIT_CACHE:-$HOME/.cache/dhis2-audit}; mkdir -p "$C"
get() { [ -d "$C/$1" ] || { git init -q "$C/$1" && git -C "$C/$1" remote add origin https://github.com/dhis2/$1.git; }; }
# fetch only the refs you need, shallow and blob-less; blobs arrive on `git show`
ref() { git -C "$C/$1" fetch -q --filter=blob:none --depth 1 origin "$2"; }
get dhis2-core; ref dhis2-core '+refs/heads/2.43:refs/remotes/origin/2.43'; cd "$C/dhis2-core"
```

Every command below prints only the lines that decide the claim. Add
`| head -50` when you are not sure how much will come back.

## Access routes (try all before recording "blocked")

| Need | First route | If that fails |
|---|---|---|
| Supported versions | `git clone --depth 1 https://github.com/dhis2/dhis2-releases` then `downloads/v1/versions/stable.json` | `releases.dhis2.org/v1/versions/stable.json` |
| Release and upgrade notes, deprecated features | same `dhis2-releases` clone: `releases/<version>/`, `deprecated-features.md` | GitHub web |
| Jira ticket | `curl https://dhis2.atlassian.net/rest/api/2/issue/<KEY>?fields=fixVersions,resolution,status,comment` | `jira.dhis2.org` |
| Live API on a pinned version | `curl -u admin:district https://play.im.dhis2.org/<instance>/api/system/info` (and `/api/apps`, `/api/schemas/<type>`, expression `/description` endpoints) | other instance names from the play index |
| Live UI | browser tools, if connected; say that a person must look if they are not | never replace with an API result |
| Published docs page | `curl -sI https://docs.dhis2.org/en/...` then fetch; check the page ends with `</html>` | builder nav in `dhis2-docs-builder` to find the real path |
| App bundled with a core release | `git show <core-tag>:dhis-2/dhis-web-server/apps-to-bundle.json` (for example 2.43.0 pins `import-export-app#v101.3.1`). Use the tag: a release branch head may point at `#master` | `/api/apps` on the pinned play instance |

Agent environments with restricted network access often block some of these
hosts, typically `play.dhis2.org`, `jira.dhis2.org`, `releases.dhis2.org` and
the GitHub REST API, while still allowing `git clone` from github.com. The
same data is reachable through the other routes above, so a refusal from one
host is not a blocked check. Record which route you used.

## Fetch one file from a large repo

```sh
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/<org>/<repo>.git
cd <repo> && git fetch --filter=blob:none --depth 1 origin <branch>:refs/remotes/origin/<branch>
git ls-tree -r --name-only origin/<branch> | grep -i <name>   # find the path
git show origin/<branch>:<path>                              # read it
```

Guessed raw.githubusercontent URLs mostly return 404, and the code-search API
is often blocked. `git ls-tree` is the reliable way to find a path. Big clones
run background gc: keep greps short.

## Compare one file across core release branches

```sh
for b in 2.40 2.41 2.42 2.43 master; do
  git fetch --filter=blob:none --depth 1 origin $b:refs/remotes/origin/$b
  echo "== $b"; git show origin/$b:<path> | grep -n '<mapping or field>'
done
```

Check the actual mapping or field (for example `@PostMapping("/merge")`),
not only that the file exists.

## Date a change (version boundary)

**Tags first.** Check the string at each release and patch tag in scope. This
needs only the tags, not the history, and is the cheapest way to find the
boundary (it also catches backports to patch releases):

```sh
git fetch -q --filter=blob:none --depth 1 origin '+refs/tags/2.4*:refs/tags/2.4*'
for t in $(git tag -l '2.4[0-3]*' | sort -V); do
  printf '%-10s %s\n' "$t" "$(git show $t:<path> 2>/dev/null | grep -c '<string>')"
done
```

The first tag with a non-zero count is the boundary. For app repos, use the
app's own tags (`v101.*`) and map them to core later.

**Then the commit,** only when the report needs it. A depth-1 clone has no
history. Use the blob-less clone, restricted to the path:

```sh
git clone --filter=blob:none https://github.com/<org>/<repo>.git && cd <repo> && git fetch --tags
git log -S'<string>' --format='%h %ad %s' --date=short -- <path>
git tag --contains <sha> | sort -V | head -3        # first release carrying it
git show <last-tag-before>:<path> | grep -n '<string>'
git show <first-tag-after>:<path> | grep -n '<string>'
```

Then map the app tag to a core version (`minDHIS2Version` at that tag, the
bundled-version survey). Do not assume that the commit date matches a core
release.

## Validate worked examples (pass G)

```sh
I=https://play.im.dhis2.org/stable-2-43-1
while IFS= read -r e; do
  printf '%s => ' "$e"
  curl -s -u admin:district -H 'Content-Type: text/plain' --data "$e" \
    $I/api/programIndicators/expression/description | jq -c '{status,message}'
done < examples.txt
```

Use `/filter/description` for boolean filters and
`/api/indicators/expression/description` for indicators. A parse error on a
doc example is a finding.

## Corroborate a UI string on a pinned instance

The served app bundle shows which strings a pinned instance ships:

```sh
curl -s -u admin:district $I/api/apps | jq -r '.[] | select(.key=="import-export") | .version, .baseUrl'
# then fetch the app's JS from that baseUrl and grep for the string
```

This shows that the string ships. It does not show that it renders. Only the UI does that.

## Who changed a doc line, and when

`git log -L <start>,<end>:<file>` or `git log -S'<text>' -- <file>` in
dhis2-docs. The person who asked may have written the line themselves, and
the history often explains why it says what it says.

## Merged or released?

```sh
git tag --contains <sha>          # empty = unreleased
git describe --tags --abbrev=0    # latest tag on the branch
```

## UI string inventory and diff (pass D)

```sh
git show <tagA>:i18n/en.pot | grep '^msgid' | sed 's/^msgid "//;s/"$//' | sort -u > a.txt
git show <tagB>:i18n/en.pot | grep '^msgid' | sed 's/^msgid "//;s/"$//' | sort -u > b.txt
comm -23 a.txt b.txt   # removed (or old name of a rename)
comm -13 a.txt b.txt   # added (or new name of a rename)
```

Compare the page labels with the inventory without reading either in full:

```sh
grep -o -E '\*\*[^*]+\*\*' <section.md> | sed 's/\*\*//g' | sort -u > labels.txt
grep -v -x -F -f b.txt labels.txt   # labels in the page that the app does not ship
```

A label in that output is a candidate finding (check case, ellipses and
interpolated strings such as `{{count}}` before you report it). For
direction B, list the in-scope screen's msgids that the page never uses.

Then read `src/pages/<Page>/*.jsx` to see which inputs each screen renders,
in which order, under which conditions (for example
`show={values.format == 'csv'}`), and which values are hardcoded constants
rather than form fields (`const isAsync = true`).

## Frontend version gates

```sh
git grep -n -E 'serverVersion|system\.version|minorVersion|VERSION_SUPPORT' -- src
```

Apps can use two gate mechanisms at once. Check each gated component
separately. Do not read one gate as covering a whole feature.

## Large published pages

Tool fetches can truncate without an error (seen at about 75,000 and about
119,000 characters). Fetch with `curl -s -o page.html` and assert the end
(`tail -c 200 page.html` shows `</html>`) and the size (`wc -c`), then grep
the file for what you need. Use a browser only when the content is rendered
by JavaScript. Check that JSON closes and Markdown ends at a real ending.

## Screenshot triage (pass E)

```sh
for img in $(grep -o -E '\(([^)]*\.(png|jpg|gif))' <page.md> | tr -d '('); do
  echo "$(git log -1 --format=%ad --date=short -- "$img") $img"
done | sort
```

Compare each date with the latest string change for the screen it shows
(pass D). Open the images that SKILL.md pass E selects. List the others under
"Not checked" with the reason.

## Anchor or page existence

1. Fetch the published page that **holds the link** and read the link's
   rendered `href` (`grep -o 'href="[^"]*<anchor>[^"]*"' page.html`). The
   docs builder rewrites links, including same-page anchors that point at
   another repo's page, so the source Markdown is not what readers get.
   Then request that `href`. If it loads with the `id`, the link works.
2. Otherwise, search the heading text across all federated repos (list in
   `evidence-ladder.md`). Remember auto-slugs: `toc` `permalink: true`
   gives every heading a lowercase, hyphenated id in addition to any
   explicit `{ #id }`.

## Regression suite as ground truth

Clone `dhis2-regression-tests` into a scratch directory and read the cases
that touch the page. Read every candidate case yourself: matches scored on
generic vocabulary are a known false-positive pattern. Check each bug note's
confirmation date against the app's latest commit: a later fix can make the
note stale.
