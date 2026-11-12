---
name: dhis2-metadata
description: "Use whenever the user works with DHIS2 metadata in bulk, on disk or from a live instance — exporting or downloading configuration (especially from a production server), anonymizing, redacting or minimizing metadata for sharing or for AI/LLM context, splitting or transforming metadata.json, comparing or validating configuration, importing or copying metadata between instances, or analysing import/export errors. Triggers on metadata.json, schemas.json, dataElements/indicators/programs/orgUnits/categoryCombos, PII in metadata, sharing/translations stripping, import reports (E5002, E4000, E1127), dummy-data generation for a program or dataset (a full comparative PoC is dhis2-prototyping), and program documentation. Use it even without the word 'metadata': 'what does this program look like', 'why did the import fail', 'get me the config from prod', 'make this safe to share'. Authoring indicator expressions themselves is dhis2-indicators."
---

## Overview

Two modes, same three scripts:

1. **Prepare metadata for analysis** — export (or start from a file), strip what is noise or sensitive, split per type so the model can `Read` one type at a time. For investigating configuration, program-indicator work, dummy data, documentation, feeding AI.
2. **Transfer metadata between instances** — fetch a slice, transform, import per type in dependency order.

Read this file fully before running anything; the safety notes matter.

## Scripts

`scripts/` next to this file; plain `python`, only dependency `requests` (`pip install requests`). Network scripts take `--url`/`--auth` or fall back to `$DHIS2_BASE_URL` plus `$DHIS2_API_TOKEN` (a personal access token) or `$DHIS2_USERNAME`/`$DHIS2_PASSWORD`; an older `$DHIS2_AUTH` (`user:pass` or `token:<PAT>`) is still read. `--help` has the full CLI.

| Script | Purpose |
|---|---|
| `fetch_metadata.py` | Export `metadata.json`/`schemas.json` from a live instance: one bulk request, or per type with `--types`/`--all-types`, filters, pagination and throttling for production. Accepts the transform flags below and applies them server-side first (`fields=:owner,!sharing,...`), then locally; `--split` writes per-type files too. |
| `transform_metadata.py` | Same transforms on a metadata file already on disk (`--split-dir` per type, or `--out` single file). Importable module shared with fetch. |
| `import_metadata.py` | POST a directory of per-type files to `/api/metadata` in dependency order; `--schemas` derives order and circular groups (preferred); chunking, async polling, `--resume` for huge loads. |

## Before exporting: decide with the user

Nothing sensitive is removed silently, so ask which of these apply — most users have not thought about it and will want some of them:

| Decision | Flag | Why it matters |
|---|---|---|
| Real names, emails, phones, credentials | `--anonymize` | Users, org unit contacts, and every `createdBy`/`lastUpdatedBy` carry them |
| Sharing settings | `--unshare` | Sharing IDs rarely align across instances; noise for analysis |
| Translations | `--delocalize` | Bulk of the bytes on multilingual instances; needed only for locale work |
| Org unit names | `--redact-ou-names` | Facility/school names can identify people or places |
| Org unit coordinates | `--drop-coordinates` | GPS points are location data |
| Include `users` at all? | `--exclude users` | Default to excluding for anything cross-instance (see safety) |

`createdBy`/`lastUpdatedBy` are excluded by default in fetch: they are re-stamped on import and are the main PII leak (creator's name and username on every object). Pass explicit `--fields` to keep them.

## Transform flags

All flags compose. In `fetch_metadata.py` each also becomes server-side `!field` exclusions, so removed data never leaves the server; the local pass still runs because field filtering does not reach embedded objects (legends inside legendSets, members inside userGroups).

- **`--anonymize`** — strips PII/credential fields everywhere, reduces user references to `{id}`, gives top-level users placeholder `firstName`/`surname`/`username` so they stay importable, removes `href` (the server URL) and cuts the export's `system` block to its `version`. Cannot see PII in custom `attributeValues` or free text (descriptions, comments): see *Sharing a file* below.
- **`--unshare`**, **`--delocalize`** — remove sharing/access fields, remove `translations`.
- **`--minimize`** — keep only schema `owner && persisted` properties minus bookkeeping, reduce references to `{id}`. Needs the version-matching `schemas.json`: the instance's own, or the bundled `schemas-vNN.json` for the file's `system.version` minor (2.41.3 → `schemas-v41.json`; a different patch is fine for analysis). Analysis only: on a `:owner` export it saves ~10–15% (embedded objects carry the noise), and it can strip a rarely-used owned property that a round-trip needs.
- **`--redact-ou-names`**, **`--drop-coordinates`** — org unit placeholders / geometry removal.

Defaults: AI consumption `--anonymize --minimize --unshare --delocalize`; instance transfer `--unshare --delocalize` (never `--minimize`).

## Sharing a file (AI chat, consultant, partner)

The transforms are a first pass, not the whole job. Before handing the file over:

- **Drop `users` and `userGroups` entirely** (`--exclude users,userGroups` on fetch; on a file, delete the keys with `jq`/Python) rather than shipping placeholder users, and tell the user why: they are not needed to analyse configuration, and if anyone imports the file, each user object overwrites the target user with the same UID or username. Remove `createdBy`/`lastUpdatedBy` references to the dropped users as well.
- **Read the free text and custom attribute values yourself.** Descriptions, comments, `attributeValues` (contact person, owner, phone attributes) and names embedded in any of them escape `--anonymize`. Remove the names (do not invent replacement text), and **tell the user this is a manual step on every future export**, listing what you found and how you handled it.
- **Verify**: grep the output for every real name, username, email, phone and the server hostname you saw in the input; check that the formulas the user cares about are byte-identical to the input.

## Workflow snapshots

```bash
# Prep for AI, from a live instance (bulk request: fine on small/throwaway instances)
python scripts/fetch_metadata.py --metadata --schemas --split --out ./export \
    --anonymize --minimize --unshare --delocalize
# → Read ./export/split/programs.json etc., never the whole metadata.json

# Same from production: per type, paginated, throttled, no users
python scripts/fetch_metadata.py --all-types --page-size 200 --delay 0.3 --schemas \
    --exclude users --anonymize --unshare --delocalize --split --out ./export

# Metadata already on disk
python scripts/transform_metadata.py ./metadata.json --schemas references/schemas-v42.json \
    --anonymize --minimize --unshare --delocalize --split-dir ./split

# Copy a slice between instances
python scripts/fetch_metadata.py --types dataElements,indicators --filter "name:like:Malaria" \
    --unshare --delocalize --split --out ./slice
python scripts/import_metadata.py --src ./slice/split --schemas ./slice/schemas.json \
    --url $TARGET --auth $TARGET_AUTH --exclude users,userGroups
```

Without `--schemas` on import, add `--passes 2` for forward references; judge by the final pass's errors. Import does not strip sharing unless `--skip-sharing` is passed — decide at export time with `--unshare`.

**Reading an import result:**
- **Absence from the error list is not success.** A type missing from the non-OK responses may have been skipped, never sent, or lost in a whole-batch crash (`409`, `status=ERROR`, empty `typeReports`: nothing of that type was imported, workflows §7). After every import, compare the target with the source split files **per type: object count and UID set**, and report that table, not "no errors".
- **Fixing an `E5002` by adding the missing object to the slice**: bring that object's own required references too (an indicator needs its `indicatorType`; a data element its category combo chain), or the next run fails one level down. Scan the slice for dangling references before re-running (workflows §5).
- **Server-side dry run before a real import into a system that matters**: metadata `POST /api/metadata?importMode=VALIDATE` (validates without committing; send one combined payload, since a single type validated alone fails on references to types not yet on the target); data values `POST /api/dataValueSets?dryRun=true`. `import_metadata.py --dry-run` only prints the order.

## Writing data values (dummy data, generators)

Any script that POSTs `/api/dataValueSets` should: send one payload per data set with top-level `"dataSet"` (on 2.43+ the server otherwise detects one per data element and rejects the whole payload when they map to none or to several, E8003/E8002), only for org units that data set is assigned to and periods of its `periodType` (complete past periods); send an explicit `categoryOptionCombo` from each data element's own category combo (an omitted one lands on the default COC); offer `dryRun=true` (e.g. a `--dry-run` flag) and tell the user to run it first on a new version; and parse the import summary (`status`, `importCount` imported/updated/ignored, `conflicts`) instead of printing raw response text. 2.43 traps and error codes: workflows §4.

Recipes and verified traps in `references/workflows.md`: import-error traps (§2), dummy data (§4), pre-import validation (§5), huge imports (§7), program documentation (§8), translating metadata (§9), troubleshooting (§10).

## Bundled schemas

`references/schemas-v40..v43.json` are `/api/schemas` exports (~2 MB each, `href`/`namespace`/`apiEndpoint`/`gistPreferences` stripped) from 2.40.11, 2.41.11, 2.42.7.1 and 2.43.2.1. Never `Read` them; pass them via `--schemas`, or query them with `jq`/Python (e.g. `required` properties per type, §5). They are for offline work on a file of known version: match the minor version (any 2.41.x file → `schemas-v41.json`). With a live instance prefer its own schemas (`fetch_metadata.py --schemas`): owned/persisted flags can change between patch releases (validation rule `shortName` became owned in a 2.41/2.42 patch), and a schema from a different minor version silently keeps or strips the wrong properties. That patch drift matters for transfer, which never uses `--minimize` anyway. If the version of a `metadata.json` is unknown (check its `system.version`), ask. When a new DHIS2 version ships, add `schemas-vNN.json` from its latest patch, stripped the same way.

## Critical safety notes

1. **Never import users without explicit thought.** A user object in the payload overwrites any target user with the same UID (or username) — renaming, re-roling or disabling it — and the target's accounts are not yours to change. Make no assumptions about admin accounts or their UIDs: on production systems the built-in admin is usually disabled, and UIDs differ per system. Default to `--exclude users` on cross-instance imports and confirm before importing `users.json`. Excluding `userGroups` cascades into notification templates and dashboards; importing userGroups with membership stripped is safe.
2. **Imports modify shared systems.** Confirm target URL and auth first, unless you know the target is disposable. Offer a server-side dry run (above), and when it matters, rehearse on a disposable instance first (see the `dhis2-test-instances` skill).
3. **`--minimize` requires a matching schema**, or the server rejects the payload with E4000.
4. **Anonymize is "safe to share", not deniability.** User objects stay (with placeholders) unless excluded, UIDs stay, custom attribute values and free text are untouched.
