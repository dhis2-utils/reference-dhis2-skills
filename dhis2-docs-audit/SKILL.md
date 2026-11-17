---
name: "dhis2-docs-audit"
description: "Fact-check DHIS2 documentation (a chapter, table, PR, single claim, or a claimed difference between versions) against the evidence that decides behaviour: dhis2-core and app source, release tags, tests, Jira, the live API and version-pinned instances. Never against other docs. Use when asked to check, verify, audit or review doc accuracy; when someone shares a dhis2-docs PR and asks if it is right; before any fix that touches a reference table, capability list, nav path, UI label or \"supports X\" claim; and before a docs diff becomes a version note. Also triggers on \"does this look right\", \"where did this come from\", \"did we miss anything\", \"check this against the source\". Run it whenever a page is audited, migrated or revised. Hands off to dhis2-docs-contribution for the edit and PR."
---

# DHIS2 Docs Audit

The goal is documentation that is accurate, not documentation that looks
checked. Every rule here comes from a real miss, and the misses compound: an
audit can follow every rule but one and still ship a wrong page. Run the whole
procedure for the scope you were given. The scope can be small, but nothing
inside it is skipped without being listed under "Not checked".

Three ideas carry the skill:

1. **Two directions.** "Is everything in the page real?" and "Is everything
   real in the page?" are different checks. Running one tells you nothing
   about the other.
2. **Evidence, not echoes.** Other docs, forum posts, a changelog, a design
   ticket or a test suite can all repeat the same error. Go to what decides
   behaviour, for the version the claim is about.
3. **Say exactly what you checked.** Each finding carries a verdict, the
   evidence, and the scope of the search. A reader six weeks later must be
   able to tell what was and was not run.

## Working economically

Effort goes into the checks, not into reading or writing. These rules cut
cost without cutting a check:

- **Read the answer, not the file.** Never print a whole source file, `.pot`
  file, JSON file or page to find one fact. Use `git show <ref>:<path> | grep -n`,
  `comm`, `jq` or `diff` and print only the lines that decide the claim
  (`| head -50` as a guard). Read a whole file only when the claim is about
  the file's whole structure, for example the inputs a screen renders.
- **One clone per repo per session.** Keep clones in one scratch cache
  directory and reuse them for every claim. Clone blob-less, and fetch only
  the branches and tags you need. Never clone the same repo twice.
- **Date with tags before history.** For a version boundary, first check the
  string at each release and patch tag in scope (`git show <tag>:<path> | grep`).
  This needs no history fetch. Use `git log -S` only to find the exact commit
  after the tags have shown where the change is. Recipes: `references/recipes.md`.
- **Ask one question per command.** Batch lookups in one shell call (a loop
  over tags or object types) instead of one tool call each.
- **Write each fact once.** The register holds the evidence. The report and
  the reply cite register rows (`#12`) instead of repeating the evidence.
  Confirmed rows get a citation and nothing else.
- **Delegate only with a narrow brief.** If you hand a check to another
  agent, give it the claim, the evidence route to use or avoid, and the
  expected output. Do not ask it to re-audit the page.

## Step 0: Set up before you read the page

1. **Size the run.** Decide the mode from the request and say it in the reply:
   - **Claim mode:** one claim or one table. Register rows and findings go
     in one combined file, and the reply is the main output.
   - **Section or PR mode:** the sections, or the diff hunks, named in the
     request, plus every other place in the corpus that carries the same
     claims (Step 0.4).
   - **Page mode:** a whole page audit, migration or revision. Every
     section is in scope.
   Passes and exit criteria apply to the scope you chose. Everything outside
   it goes on the "Not checked" list as a single line (for example "Sections
   other than Metadata Import: not audited").
2. **Read your team's registers, if you keep them.** Registers are optional
   plain files that persist between audits (for example a folder in a docs
   repo or a wiki page):
   - A **false-positive log**: patterns that looked like faults and were not.
     Check every candidate finding against it before you report it.
   - A **debt register**: open verification debts. Pull the rows for the
     scope you are auditing.
   - An **audit log**: earlier audits, with the passes they ran. Do not repeat
     a pass that was already done on the same base, but do rerun any pass it
     lists as not run.
   If you have no registers, or cannot reach them, carry on and put the
   register updates in the report under "Register updates pending".
3. **Confirm the base.** The page owner can edit between sessions. Audit the
   current copy (read it in place or fetch it again, then diff it against what
   you last saw), and record the branch and commit or mtime you audited.
4. **Fix the versions and the corpus.**
   - **Supported versions:** read `downloads/v1/versions/stable.json` in the
     `dhis2/dhis2-releases` repo (releases.dhis2.org is often blocked; the
     repo copy is the same data). Do not assume. Extract only the version
     list with `jq`.
   - **Every page that carries the claim:** search the corpus for the topic,
     not only the page you were given. The same fact often lives on a how-to
     page, a reference page and an app-repo page. Use one `git grep -l` per
     repo (file names only), then read only the matching sections. Name the
     page each finding applies to.
   - **Corpus:** docs.dhis2.org is federated from about 20 repos (list in
     `references/evidence-ladder.md`), so dhis2-docs alone is never "the docs".

## Step 1: Build the claims register

Copy `templates/claims-register.md` and list every checkable claim in scope:
one row per claim, with its type. Start with a mechanical sweep of the
in-scope text (one `grep -n` each for bold and quoted labels, `>` nav paths,
version strings, links and anchors, images, code blocks and app names), then
read the prose for capability, behaviour and negative claims, which no grep
finds.

| Type | Examples |
|---|---|
| Enumeration | function tables, object-type lists, format lists, option lists |
| Capability | "supports X", "you can merge Y" |
| Negative or universal | "only three", "not supported", "always blocks", "no way to" |
| UI string | sidebar item, page title, field label, button, option label |
| Nav path | "Go to Categories > Category options" |
| Default or constraint | default values, limits, required fields, validation |
| Behaviour | what happens when, ordering, aggregation rules |
| Version boundary | "2.41 and earlier", "since 2.42", version-difference headings |
| Screenshot | image content, caption, alt text |
| Link or anchor | cross-references, external URLs |
| App reference | the name of any app that a step, note, table cell, link or screenshot sends the reader to, especially an app that has been replaced or renamed |
| Worked example | an expression, request, payload or value the reader is told to use |

For every enumeration, add rows from the **source side** too: list what the
source contains, not only what the page mentions. That is the direction-B
half of the register, and it is the step most often skipped.

Mark risk. Negative or universal claims, enumerations, version boundaries and
UI strings are high risk: they are the claim types behind most past misses.
If the register is too large to check in full, check all high-risk rows first,
then prioritise the rest by reader impact. Record what you leave unchecked. Do
not leave it out.

## Step 2: Choose the evidence for each claim

Use `references/evidence-ladder.md`. For each claim type it gives the primary
evidence, what can corroborate it, and what can never settle it alone. Traps
to keep in mind:

- The ANTLR grammar parses every function for every expression type. Only
  the registration maps decide what a type allows.
- A Jira ticket marked "Done" with "Resolution: Duplicate" is usually a
  superseded design, not a shipped feature.
- Merged is not released. Use `git tag --contains <commit>`.
- A frontend screen is not a backend capability, and the reverse is also true.
  Check both.
- Code at HEAD is not "version X". Pin the source to the tag that version
  shipped with. For continuously released apps, map app version to core
  version through `minDHIS2Version` and the bundled-version data.
- A changelog line or a test assertion is a lead, not proof. A frontend
  app's CHANGELOG is still the cheapest lead for "is this screen new": read
  it (grep it) before you diff source.
- A version-pinned play instance shows the app bundled with that patch. It
  says nothing about current source, and current source says nothing about it.

**Before you record a check as blocked, try the other routes** in
`references/recipes.md` ("Access routes"). Past runs gave up on checks that
were reachable: the play API accepts the public demo login, Jira has a REST
host that is not blocked, and the supported-versions file is in a GitHub
repo. "Blocked" is a finding only after every listed route failed.

Date the thing the claim is about. For "screen X shipped in version Y",
date the screen's own file (for example `src/pages/<type>/Merge.tsx`), not a
related string such as an authority constant, which can land earlier.
Look for reverts as well: `git log --diff-filter=AD -- <file>` shows each
time the file was added or deleted, so a screen that shipped, was reverted
and came back is not dated from its first add.

Clone and read repos into a **scratch directory**, never inside a checkout
that someone else is working in. Git run against another person's working
checkout can leave lock files that break their next command.

## Step 3: Run the passes

Pick the passes from the claim types in your register. A pass is required
when the scope holds a claim of its type, and not otherwise. Record in the
register which pass each row got.

| Claim types in scope | Required passes |
|---|---|
| Any claim | A |
| Enumeration, capability, option list, or a screen described in full | A, B |
| Version boundary, version note, "new" or "removed" | C |
| UI string, nav path, app page steps | D |
| Screenshot | E (tiered, see below) |
| UI or behaviour claim that source cannot settle at its own level, or a source-versus-doc conflict | F |
| Worked example | G |
| Every section in scope | H |

- **A. Page → source.** Each claim exists and is correct in the evidence.
  This finds wrong entries, overclaims and fabrications.
- **B. Source → page.** Each item the source contains is in the page or has
  been left out deliberately. This finds omissions.
- **C. Version boundaries.** For each version claim, find the change at the
  tags (release and patch tags, not only `.0`: changes are often backported,
  for example present at 2.42.1 but not at 2.42.0), then get the exact
  commit, and look for an external record (Jira fix version, release or
  upgrade notes, deprecated-features table). Boundaries apply per section,
  not per page: the same option can go from two sections in two different
  releases. The oldest branch you compared is the edge of your comparison
  set, not the product's history. "Version 2.40 and earlier" often means
  "earlier than we looked". Only add a version note for a change a reader on
  a supported version could still meet.
- **D. UI text.** Build each in-scope screen's string inventory from source
  (`i18n/en.pot` msgids plus the page component's rendered inputs), diff it
  between the tags in scope, and compare it with every bold or quoted label
  in the in-scope sections, in both directions. Docs do not record UI changes
  reliably, so no docs diff can find them. Include defaults and conditional
  fields. Compare with `comm` or `grep -F -f` and read only the mismatches
  (recipe in `references/recipes.md`).
- **E. Screenshots (tiered).** Open an image when any of these is true:
  1. Its section has a changed UI string (pass D), a refuted or conflicting
     claim, a version boundary, or an app reference (pass H).
  2. The request is about the images, or the section's steps depend on the
     image to be followed.
  3. The image file was last changed before the latest change to the
     strings of the screen it shows (`git log -1 --format=%ad -- <image>`
     against the pass D change date). It is probably stale.
  Do not trust filenames or alt text for an image you open. Every image in
  scope that you do not open goes on the "Not checked" list with the reason
  (for example "12 images not opened: sections had no string change, images
  newer than last string change"). Never write that an unopened image is
  correct.
- **F. Live confirmation (tiered).** Use the API on a version-pinned
  `play.im.dhis2.org` instance (`-u admin:district`) for every claim about
  what is installed or what the server accepts. It is cheap. Use the
  rendered UI (browser) only where it is the only evidence at the claim's
  level: a claim about what a user sees that source and the served bundle
  leave open, a conflict between signals, or a claimed absence. A negative
  from one entry point is provisional. Try the object's options menu as well
  as the row click, and get a second independent look before you call
  something absent. If no browser is available, say that a person must look.
- **G. Worked examples.** Run every example expression, request or value in
  the scope through a validator if one exists (for example
  `/api/programIndicators/expression/description`,
  `/api/indicators/expression/description`). Batch them in one shell loop.
  Broken examples sit next to the claims you were asked about and are cheap
  to catch.
- **H. Replaced and renamed apps.** Grep the in-scope text (prose, steps,
  notes, nav paths, table cells, link text, alt text and "Related
  information") for every app that has been replaced, renamed or split. Run
  it as its own pass, because the claim around the name is usually still
  true and nothing else flags it. The app list and the five questions to
  settle for each hit are in `references/replaced-apps.md`. Read it when the
  grep has a hit. A new app name beside an old screenshot, an old name left
  in a note or a "Related information" list, and a link only to the old app
  are all doc errors (S3, or S2 if the reader cannot complete the task
  without the old app).

## Step 4: Triangulate and resolve conflicts

- **Independence.** The confirming evidence must be independent of the
  claim. A field copied from a spreadsheet into a knowledge graph and then cited
  back is circular. A verification must use a different method from the
  measurement it checks. When you delegate verification, tell the checker
  which tool produced each number and require a different route. Assign the
  known-bad items to a named checker, and reconcile the assignments against
  the findings list afterwards.
- **Conflict is a finding.** When two signals disagree (for example, the
  regression suite says a control is missing and current source renders it),
  record the verdict as **Conflicting**, cite both with dates, and name the
  check that would settle it. Never settle a conflict by picking the newer
  or the more authoritative-sounding source.
- **Match evidence to the claim's level.** Code shows that a component is
  there. It does not show that the component renders for this user, format
  or state. Only another observation at the same level can refute a live
  observation. Code plus the served bundle can make a live claim doubtful,
  but it cannot make it false.
- **Check the observer.** Before you treat a missing UI element as absent,
  confirm that the test user can see it: authority-gated controls are hidden
  from the play `admin` if that user lacks the authority (`/api/me?fields=authorities`).
- **A challenge is a new signal, not a verdict.** When a requester or a colleague
  says something is wrong, check each part against the evidence and report
  which parts held and which did not. Do not flip the whole finding.

## Step 5: Treat absence claims with extra care

"X is not documented", "X does not exist" and "this anchor is dead" are
negative claims, and they fail silently when the corpus is incomplete.

- Check that the corpus is complete before you reason about it. A fetched
  file must end the way a file ends. A character count in a tool result
  describes what came back, not what exists. For large pages, assert the
  length (`wc -c`, `tail -c 200`) rather than reading the whole page.
- Name the corpus in the finding. "Not in dhis2-docs `src/user` on branch
  2.43" is defensible. "Not in the docs" needs all the federated repos and
  all the branches.
- Prefer the published artifact for existence questions. One request to the
  live URL settles whether a page or anchor exists. For a link, read the
  rendered link on the published page that holds it: the builder rewrites
  links, so a link that looks dead in Markdown can work for readers.
- **Test your own instruments.** Before you trust a negative from a command
  you wrote, a glob, an indexer or a grep, run it against a known positive,
  and ask where the answer could be that the tool does not look.
- Never write specific details (names, dates, commit authors, URLs) that you
  did not verify. Vague uncertainty is acceptable. False precision is not.

## Step 6: Give each finding a verdict, a type and a severity

**Verdict** (one per claims-register row):

| Verdict | Meaning |
|---|---|
| Confirmed (source) | Matches source at the pinned version. Cite file:line and tag or SHA. |
| Confirmed (live) | Seen on a named, version-pinned instance, with date. |
| Refuted | Evidence contradicts the claim. Cite it. |
| Conflicting | Independent signals disagree. Cite both and name the tie-breaker. |
| Inferred | Follows from a pattern, not observed (for example, labels inferred from sibling sections). |
| Unverified | Not checked. Say why and what would check it. |
| Accepted exception | Matches an entry in the false-positive log, if your team keeps one. Cite the entry. |

**Finding type:** doc error (wrong), doc gap (missing), product bug (the doc
may be right and the product wrong: route it to Jira, and consider a caveat),
real version difference, app-version difference (continuously released app,
not tied to a core version), or not a finding.

**Severity:** S1: leads a reader to lose data, break config or build a wrong
calculation. S2: a task fails or a reader is misled about capability. S3: a
wrong detail such as a label, count or path that a reader can work around.
S4: cosmetic.

## Step 7: Exit criteria

Do not call the scope audited until each of these is true for the claims in
scope, or is listed in the reply as not done:

- [ ] Every high-risk register row has a verdict other than Unverified.
- [ ] Pass B ran for every enumeration.
- [ ] Every version boundary is dated from code and has at least one external record.
- [ ] Every version note was checked against the supported-versions list. A
      change older than the oldest supported version needs no note: say so.
- [ ] Each pass that the Step 3 table requires ran. Each image in scope was
      opened or is listed as not opened, with the reason.
- [ ] Pass H ran on every section in scope: each mention of a replaced or renamed app has a verdict, and each page has one fallback note where instances may lack the new app.
- [ ] Every negative claim names its corpus.
- [ ] Every Conflicting and Inferred row is in the report's open items, and in the debt register if you keep one.
- [ ] Candidate findings were checked against the false-positive log, if you keep one.

## Step 8: Report, and update the registers if you keep them

**The reply to the requester is the deliverable. Side files are only records.**
The reply must stand alone:

1. The answer in the first two sentences.
2. The findings, each with its verdict label (from the Step 6 set) and
   one-line evidence (file and tag, or instance and date), in the reply
   itself.
3. The page each change goes on, and the proposed text if a change is needed.
   Proposed text may contain only behaviour you verified in this run (a
   ticket or forum post is not verification), and must not add what the
   published page already documents in another table or section.
4. A **"Not checked"** list naming the mode and scope, the directions run
   (A, B or both), every pass not run,
   every route that failed, every image not opened, and every limit on the
   search (for example "master only", "button label only"). Nothing may
   appear only in a side file.
5. Register changes stated as done only if the file was written. Otherwise
   say "pending".

Keep the reply tight: the answer, a short findings list or table, the page
changes, and "Not checked". Do not list confirmed claims one by one in the
reply: give the count and point to the register.

In section, PR and page mode, also save the claims register and the report
(`templates/audit-report.md`). The report holds the findings, the coverage
line ("52 claims; 41 checked; directions A+B; passes C, D, E run; F not
run") and the open items. It cites register rows for the evidence and does
not copy it. "Verified against X" without the direction and the scope is
not an acceptable sentence.

Then update the registers, if your team keeps them. If it does not, the
report's "Open items" and "Register updates" sections carry the same
information, and you do not claim that any register was written.

- Add every Unverified, Inferred and Conflicting row, and every deliberate
  omission, to the debt register with an ID (`AD-###`). Close the debts you
  resolved and cite the evidence.
- Add each correction ("this looked like a fault but was not") to the
  false-positive log as an `FP-###` entry: pattern, why it was not a fault,
  what to check next time.
- Add one row to the audit log: date, base, scope and mode, passes run,
  counts by verdict, and a link to the report.

## Applying findings, and handoff

If you edit the page yourself, read `references/editing-hygiene.md` first.

Making the edit and opening the PR is a different job (branching, screenshot
placement, fork or upstream, backports). Hand off to
**dhis2-docs-contribution**, with the report and the claims register as
inputs. Run **dhis2-docs-style** on the page before it is published, so that
the wording is consistent. This skill checks the correctness and
completeness of content that already exists.
