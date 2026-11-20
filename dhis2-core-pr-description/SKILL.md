---
name: dhis2-core-pr-description
description: >
  Write, rewrite or review the title and description of a pull request to
  dhis2/dhis2-core (the DHIS2 Java backend) so it follows the backend team's
  PR description guide in dhis2/wow-backend: one template per title prefix
  (fix, feat, perf, refactor, chore, ci, test, docs), h3 sections, at most 250
  words, Simplified Technical English, a full-URL Jira line, and an "AI Assisted"
  last line. Use whenever the user opens, drafts or edits a dhis2-core PR, runs
  `gh pr create` in a dhis2-core checkout, asks "write the PR description",
  "what prefix should this PR have", or says a PR description is too long,
  even if they do not mention templates. Also use when reviewing whether an
  existing dhis2-core PR description is acceptable.
---

# dhis2-core PR descriptions

Two humans must approve each dhis2-core PR. They must understand it from less than one
page. The backend team's guide (`dhis2/wow-backend`, `pr-templates/`) fixes the shape of
every description. This skill gives that shape and a checker for it. The full guide and all
templates with real examples are in `references/` (see `references/upstream.txt` for the
synced version).

Generic PR habits fail this guide. Do not use `## Summary`, `## Changes` or `## Testing`
sections, test checklists, bare Jira keys, or lower-case title subjects.

## 1. Title

`<type>: <Imperative subject with a capital letter> [DHIS2-12345]`

- `type` is one of `fix`, `feat`, `perf`, `refactor`, `chore`, `ci`, `test`, `docs`.
  It selects the description template. Build changes (Maven, dependencies, packaging,
  CVE bumps) use `chore`. Do not use `build:`, `deps:` or a scope such as `fix(deps):`.
- Capital letter after the prefix ("Cache", not "cache"). No period at the end.
- Put the Jira key in brackets. Aim for 50 characters or fewer for the subject.

| Prefix | Use for |
|---|---|
| `fix` | Bug fix |
| `feat` | New feature or new behaviour |
| `perf` | Faster or less memory, same behaviour |
| `refactor` | New code structure, same behaviour |
| `chore` | Clean-up, maintenance, build and dependency changes |
| `ci` | CI workflows and pipelines |
| `test` | Test code only |
| `docs` | Documentation only |

## 2. Description: fill the skeleton for the type

Every description is exactly this, top to bottom:

```
(optional link line, e.g. "Follow-up to #26010." or a link to the PR doc)

**Jira**: https://dhis2.atlassian.net/browse/DHIS2-12345

### <section 1>
...
### <section n>
...

AI Assisted        <- only if AI wrote a large part of the PR
```

The sections, in this order. No other sections. Caveats only where listed:

| Type | Sections |
|---|---|
| `fix` | Problem, Solution, Proof, (optional) Caveats |
| `feat` | What, Why, How, (optional) Caveats |
| `perf` | Problem, Solution, Results |
| `refactor` | Problem, Solution |
| `chore` | What |
| `ci` | What, Solution |
| `test` | Problem, Solution |
| `docs` | What |

What goes in each section:

- **Problem / What**: 1-3 sentences. The bug, gap or slowness, with the user-visible effect
  (for example "gives HTTP 500"). Name the entry point in the code: a class, method or
  endpoint (`DataValueSetImportValidator.validateDataValuePeriodExists`).
- **Why** (feat): what users cannot do today and why they need it.
- **Solution / How**: 1-3 sentences, or bullets for several separate parts. For refactor,
  say that the behaviour stays the same. For feat, say how to use it (endpoint,
  parameter, setting).
- **Proof** (fix): one short paragraph. Name the test that fails without the fix and passes
  with it.
- **Results** (perf): the key numbers, before and after, as sentences or a small table.
  **Always state the method**: dataset, load, number of runs, tool. Name the performance
  test class or method if there is one.
- **Caveats** (fix, feat only): behaviour changes, risks or limits that a reviewer must
  know. Most PRs do not need it. If the input has such facts (a bigger war file, a memory
  limit, a new error code), put them here. Do not drop them.

Hard rules:

- **The Jira line is `**Jira**: <full URL>`**. Do not write a bare key or a markdown link.
  Leave it out only if there is no Jira issue.
- **There is no Test, Tests or Testing section, and no test checklist.** Do not write "all
  tests pass". Tests go into Proof (fix) or Results (perf) only.
- **All headings are h3 (`###`)**. Bold lines are not headings.
- **Maximum 250 words** including headings (`wc -w`). Aim for 150. Do not list every
  changed file or every test.
- Remove all template hint text and unused optional parts.
- **"AI Assisted" is the last line if AI wrote a large part of the PR.** This is true when
  you, the agent, wrote the code or most of the description. Leave it out if the user says
  they wrote it without AI.
- For a very large PR you can add an optional PR doc in `dhis2/wow-backend` `pr/`. See
  `references/guide.md`, "Large PRs". The description still keeps the template and the
  limit.

## 3. Language: ASD-STE100 Simplified Technical English

- One statement per sentence, maximum 20 words.
- Active voice: "The import rejects the row", not "The row is rejected".
- One term for one meaning, the same term everywhere.
- No filler: "basically", "simply", "in order to", "very", "actually".
- Subject, verb and object near each other. No clause inside a clause: write two
  sentences. Start with the main statement.
- Bullets only for several separate points. Do not make a list from one or two sentences.

## 4. Check, then read

```bash
python3 scripts/check_pr_description.py pr_description.md --title "fix: Reject week 53 [DHIS2-12345]" --ai
# --no-ai if the user wrote it without AI; --type <t> instead of --title if there is no title yet
gh pr view <n> -R dhis2/dhis2-core --json body -q .body | python3 scripts/check_pr_description.py - --type fix
```

Fix every ERROR. Read each WARN: long sentences, filler and passive voice are hints, not
proofs. The checker does not judge content. Read the text again as the reviewer: can they
find the entry point, and see what changes and why?

## Example (fix)

Title: `fix: Give conflict for invalid week 53 [DHIS2-12345]`

```
**Jira**: https://dhis2.atlassian.net/browse/DHIS2-12345

### Problem
A data value import with period `2023W53` gives HTTP 500.
ISO year 2023 has only 52 weeks, so `PeriodType.getPeriodFromIsoString` returns null.
`DataValueSetImportValidator.validateDataValuePeriodExists` then throws a NullPointerException.

### Solution
The validator adds the new conflict `E7648` (period not valid) for such a row.
The import continues with the other rows.

### Proof
`DataValueSetImportValidatorTest` imports `2023W53` and expects `E7648`.
A second test checks that `2020W53` is still valid.

AI Assisted
```

More examples, one set for each type, are in `references/templates/<type>.md`.

## Keeping the references current

`references/` is a copy of `dhis2/wow-backend` `pr-templates/` (plus the title rules
in `references/title-rules.md`). To refresh it, run `bash scripts/sync_upstream.sh` (it uses
`master`, or pass a ref) and review the diff. If the upstream sections change, update the
`SECTIONS` table in `scripts/check_pr_description.py` and the table above.
