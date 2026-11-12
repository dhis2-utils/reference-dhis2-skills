# Deliverables — the fix manifest and its renderings

Everything an engagement hands over is **rendered from one fix manifest** (`scripts/manifest.py`), so
the formats cannot drift apart. Record each fix in the manifest while you work it out, not afterwards.
`examples/manifest-sl-demo.json` (with its rendered proposal, import package, playbook and SQL file
alongside) is a full exemplar on the Sierra Leone demo database.

## What the manifest holds

One JSON file. Per fix: its check, decision ref, rationale, exact steps with payloads,
**preconditions**, verify assertions, reversibility and importability. Plus a **`flagged`** list of
non-fixes (judgment calls left to the owner, reverted fixes).

`manifest.py render` emits:

| Rendering | Purpose |
|---|---|
| **Change proposal** (`.md`) | The human-readable review document. Always delivered. |
| **Import package** (`.json`) | The importable subset, for teams that only trust the Import/Export app. |
| **Replay playbook** (`.ipynb`, via `scripts/playbook.py`) | Operator console for what imports can't express (merges, guarded SQL, data migrations). Runs `DRY_RUN` first, cell by cell, with verify gates: dedicated → staging → production. |
| **SQL export** (`sql-fixes-*.sql`) | Every `sql` step as a standalone psql-ready block: BEGIN/COMMIT per fix, ordering warnings, cache-clear reminders. |

`manifest.py validate` checks the schema and warns about the unsafe shapes listed below. `demo` writes
a minimal example.

## The manifest must mirror the FINAL decided state

A manifest built from first-pass auto-fixes will, on replay, re-apply decisions that were later
**reverted** (delete the program rules the owner chose to keep, force a reverted Unknown-group fix).
Only fixes that were **applied and kept** become entries. Everything reverted or left as a judgment
call goes in `flagged`, rendered as "Flagged for owner — do NOT auto-fix" in every format. Re-render
after every decision review. Order entries that cascade (categories → category combos → COCs) by
dependency.

## Preconditions are the drift guards

Tested: a playbook rendered for one instance and run against a different one **skipped every fix**
(missing UIDs, checks already 0, identity probes failing) and its verify cells failed loudly.

- Every fix carries `check_nonzero` (skip when already applied or never present) **plus at least one
  identity guard**: an `object_exists`/name probe of something the fix targets. A check-level guard
  alone can pass on the wrong instance (both fail the same check for different reasons). Match on
  markers that survive the clone chain (UIDs and names of targeted objects), so a legitimate copy of
  the right database passes and another organisation's database fails.
- The playbook **also requires an operator acknowledgment**: the setup cell prints the target's
  `systemName`, URL and key counts, and the operator copies the printed name into `CONFIRM_TARGET`
  before any fix cell runs. Fingerprints catch the wrong database; the ack catches the right database
  at the wrong time (prod when staging was meant).
- Derive-at-runtime steps also guard inside their loop (act only on objects matching the recorded
  names/UIDs and expected state), so a precondition slip degrades to a no-op.
- **Use the target version's check names.** Names differ across versions (see playbook §1). `check()`
  raises on an unknown name and a rendered precondition raises on a timeout, so neither can skip a fix
  as "already 0". (Before this, an unknown name timed out, read as 0, and the fix was skipped as if
  applied.)

## Step guarantees (manifest and every rendering)

- **UID-based, never numeric ids.** SQL cells call `resolve_id(table, uid)` at runtime; numeric ids
  differ per instance. For derived sets (orphans, not-viewed favourites, scarce groups, duplicates)
  write logic that re-derives the targets at runtime instead of hard-coding thousands of UIDs.
- **New objects get a pre-generated, fixed UID.** Generate it once while authoring (`new_uids()` →
  `/api/system/id`, or reuse the UID from the dedicated instance) and create via `ensure(path, uid,
  body)` (create-by-UID, skip if present). A bare `POST` gets a fresh UID per run: re-runs duplicate
  the object, references don't line up across dedicated → staging → prod, and there is nothing stable to
  reverse. Only the identity is fixed; compute derived fields such as membership at runtime.
- **Idempotent** cells and a top-of-notebook `DRY_RUN` switch.
- **Verify cells** that re-run the integrity check and assert the expected count (0 or a documented
  residual).
- **Visible pending state.** Writes, merges and check recomputes can take 30–120 s. The helpers print a
  flushed "waiting on API/DB" line before each call and replace it with status + elapsed; `check()`
  shows a live elapsed counter.
- **SQL cells gated** (DB route + `ALL`), in order, each followed by `cache_clear()`.

## SQL steps: written for a DBA, not for you

Direct DB access from the playbook environment is the exception. Usually only a DBA on the server can
run SQL. The playbook detects this (`SQL_MODE`): with `PG*` env vars its SQL cells execute directly;
without them each SQL cell prints the statement and its block reference in the `.sql` export and pauses
for the DBA, so the notebook still drives the order and the verify cells prove each fix landed.

- Author SQL as dedicated `sql` steps, UID-based (subqueries or `resolve_id`). `sql()` buried inside a
  `code` step cannot be exported; `validate()` warns.
- **Self-guarding (idempotent).** The `.sql` file runs without the playbook's preconditions, so each
  statement is a state transition whose WHERE matches the pre-fix state (`SET new WHERE old`; a re-run
  reports 0 rows), INSERTs use `ON CONFLICT DO NOTHING`, and accumulating updates consume their source
  rows in the same transaction. `validate()` flags common re-run-unsafe shapes.
- **Tiered guards.** Destructive steps (DELETE, `INSERT … SELECT` data migration) also carry a `guard`:
  a boolean SQL predicate asserting the expected pre-fix state, e.g.
  `EXISTS (SELECT 1 FROM categorycombo WHERE uid='…' AND name='…')`. Renderers emit it as a
  `DO $$ … RAISE EXCEPTION … $$` block inside the same transaction, so on drift the whole fix rolls back.
  "GUARD FAILED" is the guard working: verify the target before retrying. `validate()` warns when a
  destructive step has no guard.

## API-only targets

Hosted instances with no PostgreSQL route are common. The manifest has no API-only variant, so give
each DB-dependent fix an API re-expression (in its rationale or as a second fix) and flag the ones that
cannot be re-expressed. Re-expressions used on one hosted 2.38 engagement:

- PostGIS validity → a list of known-bad geometries.
- Audit-based "viewed in 12 months" → view counts.
- SQL data removal → `POST /api/maintenance/dataPruning/organisationUnits/{uid}` (playbook §3).

## Authoring gotchas

- `code` steps are assembled as Python f-strings. Double every literal `{}` in generated code; a segment
  left as a plain string ships literal `{o['id']}` into URLs (400 at replay).
- A non-interactive runner (`nbconvert --execute`) cannot set gate variables such as `CONFIRM_TARGET`
  or a per-fix confirmation flag; the operator edits the cell first.
- No bilingual output. If the national team needs another language, add a post-processor for the
  markdown cells.
- Rendered file names are slugified from the engagement name.

## Launch instructions ship with the playbook

The admin who replays the notebook needs the concrete how-to. `scripts/playbook.py` writes it into the
intro cell; also drop a short `RUN-playbook.md` next to the deliverables:

```bash
pip install jupyterlab httpx python-dotenv psycopg2-binary
export DHIS2_BASE_URL=https://your-instance.org DHIS2_USERNAME=admin DHIS2_PASSWORD=...   # or DHIS2_API_TOKEN
jupyter lab playbook.ipynb
# headless machine: add --no-browser --ip 0.0.0.0 --port <a port the user's browser can reach>
# no UI at all: jupyter nbconvert --execute playbook.ipynb  (honours DRY_RUN)
```

## Tracks — one manifest per track

- **(a) Integrity remediation**: high-confidence structural fixes. Invisible to end users.
- **(b) Deterministic naming fixes**: whitespace, obvious typos, ` (%)` on percentage indicators,
  age-range notation (playbook §7). Auto-applicable but changes user-visible labels, so admins may
  review or apply it on a different cadence.
- **(c) Assisted manual review** (optional): evidence worksheets, never fixes
  (`references/manual-review.md`). Only decisions confirmed in the decisions round enter (a) or (b).

**Out of scope:** the acronym-prefix (`TB_`/`MAL_`…) and code-standardisation overhaul. It is a
governance exercise needing stakeholder alignment: no renames and no rename-proposal table. A
descriptive inventory (current prefix patterns, code coverage, inconsistency counts) is allowed as an
appendix.

## The rest of the hand-over

`decisions.md`, the operations log (from `d2_client.py`), per-category change CSVs, a before/after
counts table, and a `README.md` summary (fixed / accepted-with-reason / blocked-with-remediation). In
dump mode also the re-exported `fixed.metadata.json` and its diff against the original
(`references/dump-and-sandbox.md`).
