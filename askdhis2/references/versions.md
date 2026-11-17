# Version handling

Read this when the answer depends on the DHIS2 release, or the user named one.

## What is versioned

| Section | Versioned? | Path shape |
|---|---|---|
| `use/user-guides/` | Yes | `.../dhis-core-version-2NN/...` |
| `develop/using-the-api/` | Yes | `.../dhis-core-version-2NN/...` |
| `implement/` | Mostly no | A small legacy release-information tail is versioned |
| `manage/` | No | No version segment exists |
| `topics/` | No | No version segment exists |

About 60% of pages carry no version at all. Do not construct a version path for
`manage/` or `topics/`; it does not exist. Version-pinning a hosting or
server-administration URL is wrong even when the user named a version.

The token uses the 2.x form: v43 → `dhis-core-version-243`, plus `-master` for
unreleased content. Tokens seen in testing: 240 to 243 and master. New releases
add tokens, so read the URLs you get back.

**Do not rely on a remembered "current stable".** Read it from the first lines
of `llms.txt` ("Latest stable release: vNN") or from the release notes you
retrieve.

## The retrieval tool has no version filter

It takes one `query` argument. Three levers, most reliable last:

1. **Name the version in the query.** It lifts that version's share of chunks
   (about 1 in 10 to 3 in 10 in testing) but `master` and neighbouring versions
   keep appearing. Never assume the results are only that version.
2. **Query across a boundary.** For a version-sensitive answer, ask for the
   user's version and the adjacent one, then compare. If they disagree, you have
   found a real boundary. Report it.
3. **Read the version from the returned URLs.** This is the real check. For every
   chunk you rely on, look at its `dhis-core-version-2NN` segment.

## Failure modes

**Silent substitution.** A query about 2.40 returned no 2.40 chunks and quietly
supplied 2.41, although 2.40 docs exist. If you asked about one version and every
chunk came from another, say so.

**Versioned pages can be stale.** A page can lag the
product (the 2.42 Users page still showed the removed nested `userCredentials`
object). Check release notes and Jira before you trust it.

**Chunks with no URL** cannot carry a version claim. Do not list them as sources.

## Ask, or answer and flag?

Default to answering and naming the boundary.

- **Infer first.** A version mentioned in passing, a pasted URL with a version
  segment, or an endpoint that exists only in some releases all tell you.
- **Version-sensitive, none given** → answer for the current stable release, say
  which, and name the boundary you know.
- **Unversioned topic** (hosting, `manage/`, training) → answer. Version is not a
  variable.

Ask first only when all three hold: the right answer reverses across releases,
you cannot infer the version, and a wrong guess is costly or hard to undo
(upgrade and migration steps, bulk or destructive operations, security).
