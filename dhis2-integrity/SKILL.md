---
name: dhis2-integrity
description: >-
  DHIS2 metadata REMEDIATION — fixing what is BROKEN in an existing instance or metadata
  dump. Use when the user wants to: make an instance pass DHIS2's data-integrity checks;
  resolve the failures an integrity run reports; de-duplicate near-identical metadata (combos,
  COCs, categories, indicators, data elements); repair broken indicator/program-indicator
  expressions or validation rules; fix structural faults (orphaned stages, wrong category
  combos, invalid org-unit groups/geometry); or trial repairs on a disposable copy and hand back
  a fixed dump or a reviewed change package. Typical phrasings: "make our instance pass the
  integrity checks", "dedupe these combos without losing data", "what's broken in this metadata
  export". Not for authoring new metadata or expressions, exporting, debugging one analytics
  number, provisioning instances or app work (dhis2-metadata, dhis2-indicators, dhis2-docs,
  dhis2-test-instances), or auditing a set of indicators for meaning or values
  (dhis2-indicator-review).
---

# DHIS2 metadata remediation

A method and toolkit for taking a DHIS2 instance, or a metadata `.json` dump, from "many integrity
problems" to "clean, verified, documented". This file is the workflow skeleton; the details are in
`references/`. Applies to DHIS2 2.40–2.43 (the integrity framework exists since 2.38).

## Core principles

1. **Work on a copy.** Restore a dump onto a disposable instance (get one via the
   **dhis2-test-instances** skill) and fix that. It isolates the work and gives you a control baseline.
2. **Snapshot before the first change** (`pg_dump`, or a full metadata export plus `dataValueSets`).
   Without it you cannot prove later that outputs did not change. This is the most common regret.
3. **Integrity-clean is not output-equivalent.** Re-running the checks proves consistency, not that
   indicator values, forms and tracker behaviour are unchanged. Verify outputs separately
   (`references/verification.md`).
4. **Fix what is deterministic; ask about everything else.** A fix is deterministic when exactly one
   outcome is correct and it needs no data or intent you cannot see: whitespace, typos, `(%)` and
   age-range naming, `aggregationType=NONE` on a text DE, quoting a UID in a filter, stripping an
   unsupported `AVG()`, setting a rule priority. Merges, deletions, expression rewrites, group-set,
   period-type, geometry and access changes are judgment calls. Then:
   - **Scope is not autonomy.** "Fix everything" says *which* checks to work through, not that you may
     decide the judgment calls alone. Ask once, up front, whether the user wants to decide each call or
     authorises best-effort decisions. Even with autonomy, document every heuristic choice.
   - **A reviewable deliverable is the decision round.** When the work happens on a sandbox and the
     user asked for output to review before anything is applied (a fixed dump, a change list), don't
     stop to ask: make the best-effort call on each judgment item, apply it in the sandbox, and list
     every call in `decisions.md` and the answer so the review can reverse it.
   - **Broken is not unwanted.** Metadata with clear intent that is merely broken (a rule missing its
     action, a stage that lost its program) is repaired or restored-and-flagged, not deleted. Delete
     only orphan, empty, test or duplicate objects. Exception, **abandonment**: broken *and* untouched
     for years (`lastUpdated`) *and* zero data *and* zero references may be batch-deleted with a
     documented list.
   - **When the answer needs data or intent you lack, revert to original and flag.**
   - **Instance decisions never carry over** between databases (which dataset is canonical, which of
     two classes is true). **Policy decisions may** (merge instead of deleting by `DELETE_` name;
     restore-and-flag broken rules; bucket group-set stragglers into "Other/unknown"), but only as
     pre-selected defaults with provenance, confirmed in the decisions round.
   - Start from each check's own `recommendation` (in `GET /api/dataIntegrity`).
5. **API first; merge endpoints for duplicates; SQL last.** Probe before assuming:
   `POST /api/<type>/merge` with `{}` returns 404/405 when there is no endpoint and 400/409 when there
   is. Availability is version-dependent (verified in dhis2-core):

   | Merge endpoint | 2.40 | 2.41 | 2.42 | 2.43 |
   |---|---|---|---|---|
   | `organisationUnits` | ✔ | ✔ | ✔ | ✔ |
   | `indicators`, `indicatorTypes` | | ✔ | ✔ | ✔ |
   | `dataElements`, `categoryOptions`, `categoryOptionCombos` | | | ✔ | ✔ |
   | `categories`, `categoryCombos` | | | | ✔ |

   On ≤2.42, consolidating duplicate categories or combos that hold data has no endpoint, so
   reference-repointing SQL is legitimate there (or upgrade first). On 2.43 an `E1120`/`E4030` block
   means "use the merge endpoint", not "drop to SQL". `categoryOptionCombos/merge` only merges COCs in
   the same combo with the same options (`E1540`), rewrites indicator/predictor expressions, deletes
   the sources' data-value and approval audits, and never touches custom-form HTML: text-repoint
   the `deUID-cocUID-val` input ids in `dataentryform.htmlcode` yourself after every COC merge.
   Details: `references/playbook.md` §5–6.
6. **Large instances lie.** On instances with 100k+ org units or users, bulk API calls can OOM Tomcat
   (silent disconnects), slow checks time out and return empty, and a low inventory is a partial run.
   Push bulk work to SQL, keep API writes chunked and resumable, run one heavy instance at a time, and
   verify fixed checks with direct SQL (playbook §1, §6).

## Modes

| Situation | Mode |
|---|---|
| Live instance, user comfortable fixing it directly | **Live** (snapshot first) |
| User hands you a metadata dump, or prod is too risky | **Dump → disposable instance**: import, fix there, re-export, apply the reviewed result to prod |
| No instance you may write to (pasted check output, a metadata export, an owner who applies fixes) | **Advisory**: same pipeline, but the deliverable is the fix manifest and its renderings; you never apply |

Advisory is the common real case: agents rarely get write access to a national system. Two limits:

- **Without any runnable instance, do the analysis only.** Ship untested fixes as proposal text marked
  "not exercised against a running DHIS2", every row, deterministic ones included: nothing is "safe",
  "verified" or "ready to apply as written". No import package, playbook or SQL file presented as ready
  to run. Tell the owner to prove the whole set on a disposable copy of their instance (same version)
  before applying it; if you can get such an instance yourself, prove the fixes there first.
- **A question about one or two issues is not an engagement.** Answer it from the playbook and the
  decision model, without inventory, manifest or deliverable set, unless asked for a review.

## Setup

- Connection: `.env` or env vars `DHIS2_BASE_URL` plus `DHIS2_API_TOKEN` or `DHIS2_USERNAME`/`DHIS2_PASSWORD` (older `.env` files with `DHIS2_USER`/`DHIS2_PASS` still work)
  (the dhis2-docs convention). All bundled scripts read them.
- A disposable instance for dump mode or for proving fixes: **dhis2-test-instances** (empty instance,
  same version as the source).
- Direct SQL (optional): `PGHOST`/`PGPORT`/`PGDATABASE`/`PGUSER`/`PGPASSWORD` for the instance's
  PostgreSQL, as reported by whatever provisioned it (playbook §6).
- `pip install -r scripts/requirements.txt`.

## Workflow

Track these as tasks; re-verify after every batch.

### 0. Target and baseline
- **Establish the version first.** Live: `GET /api/system/info`. Dump: top-level `system.version`,
  else property markers (`references/dump-and-sandbox.md`). Version decides check names, merge
  endpoints and SQL table names.
- **Dump mode:** import onto an empty instance of the same version (`scripts/metadata_dump.py import`,
  twice). **Compare default category UIDs** of source and target first; databases created before 2.22
  keep random default UIDs. **Reconcile object counts** after import: the importer silently drops
  corruption a live instance cannot hold, so the rebuild can hide real problems. Record drops as
  findings. Large dumps need a chunked/SQL strategy. All in `references/dump-and-sandbox.md`.
- **Live mode:** snapshot now.
- **Empty instance?** Ask whether to populate synthetic data (`scripts/gen_synthetic_data.py`, after
  import and before the snapshot) or proceed and state "fixes not exercised against data". Without
  data the `E1120`/`E4030` guards never fire and there is nothing to diff
  (`references/synthetic-data.md`).

### 1. Inventory
```bash
python scripts/integrity.py inventory   # summary + slow checks, waits on finishedTime, saves JSON
```
The summary run skips the slow/programmatic checks (21 of 113 on 2.42); results are async and cached.
Re-run until two inventories agree. Treat timeouts, an empty summary or DATA_INTEGRITY jobs stuck in
`SCHEDULED` as "no inventory", never as zero. On large instances `details` can return 0 while
`summary` reports hundreds: derive the list with a direct query. Playbook §1.

### 2. Triage
Bucket every failing check: **deterministic-safe**, **judgment/destructive**, **accepted-unfixable**,
**blocked-by-privilege**. `references/playbook.md` §2–4 gives the fix (and the correct non-fix) per
check family and the API guards. For broken expressions, read the *invalid expressions* list in
playbook §3 (reporting-rate syntax, boolean vs numeric program-indicator expressions, unquoted UIDs,
aggregation functions in validation rules) and state the actual cause, not "invalid syntax". Same
formula is not same meaning: indicators sharing an expression are duplicates only if their names
agree too (§5).

### 3. Decisions: two planned rounds
Ask **all** judgment calls in one batched round before fixing (unless the deliverable is itself the
review, see principle 4): autonomy level, carried policy
defaults, per-type deletion of unused metadata, not-viewed favourites (depends on the age of the
copy), coordinates, manual-review findings, instance-specific ambiguities. Explain each check in plain
words; users don't know the check names. Tell the user to expect **one more batch** for what fixing
uncovers, and collect those discoveries rather than asking one by one. Record everything in
`decisions.md`.

### 4. Fix, highest leverage first
- Write through `scripts/d2_client.py` (every write logged) or an equivalent logged client; SQL through
  `scripts/db_client.py`.
- Duplicates: merge endpoints at the right level (playbook §5). Before deleting any COC or combo, scan
  its references (expressions, form HTML, operands, min-max).
- **Wrong category on a combo that holds data: classify the values first.** Values under COCs built
  from the *intended* categories are only hidden; swapping the category (E1120 blocks the API, so SQL
  on `categorycombos_categories` when there is no duplicate combo to merge into) moves no data. Values
  entered under COCs carrying the *wrong* category's options have no correct home: they need an owner
  decision and an explicit old-COC → new-COC mapping (or keep/archive) before those COCs are removed.
  Playbook §6.
- **After any SQL change to combo/COC structure:** `POST /api/maintenance?cacheClear=true` and
  `categoryOptionComboUpdate`. The update recreates every COC the combo's categories still imply, so
  fix the combo first and delete orphaned COCs after, or they come back.
- Re-run the **broad** summary after each batch: fixes create new violations (playbook §8).
- A connection error mid-run ("Name or service not known") usually means the instance restarted, not
  corruption. Check reachability, restart, and re-run; the scripts write one object at a time and are
  idempotent. Confirm what landed from the operations log.

### 5. Verify outputs, proportional to the fixes
Re-run all checks, then: fixes that touched data or expressions (merges, COC migrations, expression
repairs, category surgery) need the full diff against the control (data values, regenerated analytics,
form COC resolvability, tracker values, dangling references). Purely structural fixes need targeted
spot checks. After any COC/combo change, two checks are mandatory:
- **Per-cell conservation:** for every (data element, period, org unit, attribute option combo), the
  sum of values across COCs is unchanged, except for listed merge collisions and agreed deletions. A
  global row count or per-DE total is not enough.
- **Form resolvability:** every section-form cell and every custom-form `htmlCode` input id resolves
  to a COC of the data element's *current* category combo (existing is not enough). Acceptance: every diff maps to a logged change. `scripts/verify_outputs.py`,
`references/verification.md`.

### 6. Record every kept fix in the fix manifest
`scripts/manifest.py` holds each fix's steps, payloads, preconditions (drift guards: a check guard plus
an identity guard), verify assertions and reversibility, and a `flagged` list for non-fixes. `render`
produces the change proposal (`.md`), import package (`.json`), replay playbook (`.ipynb`) and SQL
export (`.sql`). It must mirror the final decided state: reverted fixes go to `flagged`. Keep integrity
and naming fixes as separate manifests. Rules and gotchas: `references/deliverables.md`.

### 7. Document and hand back
`decisions.md`, operations log, change CSVs, before/after counts, `README.md` (fixed /
accepted-with-reason / blocked-with-remediation), the manifest renderings, and in dump mode the
re-exported `fixed.metadata.json` with a diff against the original. Optional third track: the
manual-review worksheets (`scripts/review_pack.py`, `references/manual-review.md`); their findings go
through the same decisions round. The acronym-prefix/code-standardisation overhaul is out of scope.

## References

- `references/playbook.md` — integrity API mechanics and version differences, triage taxonomy,
  per-check fixes, API guards, merge endpoints, direct SQL (locating the DB, schema notes, version
  landmines, Postgres at scale), naming rules, self-inflicted-wound watch-list.
- `references/dump-and-sandbox.md` — version fingerprinting, restoring onto an empty instance, import
  gotchas, count reconciliation, large-dump strategy, dump diffing.
- `references/synthetic-data.md` — populating a data fixture (E7617 OU scope, 2.43 dataset rules,
  tracker rule engine).
- `references/verification.md` — control baseline, what to diff, acceptance criterion, delta-SQL
  fallback.
- `references/deliverables.md` — fix manifest, drift guards, renderings, SQL for a DBA, tracks.
- `references/manual-review.md` — the assisted manual-review track.

## Scripts

Run any with `-h`. They are small; adapt them per task.

- `d2_client.py` — logged HTTP client (`get/post/put/patch/delete`, `cache_clear`).
- `integrity.py` — `inventory`, `run <checks>`, `details <check>`, `catalog`; fails loudly on
  incomplete runs and unknown check names.
- `db_client.py` — logged psycopg2 wrapper; `fk_refs(table)` lists referencing FKs.
- `metadata_dump.py` — full metadata `export` / `import` / `diff` (small to mid instances). For a gentle,
  anonymised export from a large live instance use dhis2-metadata's `fetch_metadata.py`.
- `gen_synthetic_data.py` — seeded aggregate + tracker data fixture.
- `verify_outputs.py` — control-vs-fixed diffs: `datavalues`, `analytics`, `forms`, `dangling`.
- `review_pack.py` — read-only manual-review worksheets.
- `manifest.py` — fix manifest `validate` / `render` / `demo`.
- `playbook.py` — the notebook renderer used by `manifest.py`; `--demo <path>` writes a sample.

`examples/` holds a complete set rendered for the Sierra Leone demo (manifest, change proposal, import
package, playbook, SQL) and a sample review pack.
