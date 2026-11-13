# What analytics can reach

Use this to check, per candidate model, that every required indicator and breakdown is computable. Behaviour marked (2.42.6) was verified on that version in a household-enumeration PoC, and re-checked with a minimal reproduction on 2.42.7.1 where noted; verify anything else on the target version (a disposable instance and a `filter/description` validation call are cheap). Expression syntax itself belongs to `dhis2-indicators`.

## The reach rules

| A program indicator in program P can use | Yes / no |
|---|---|
| Data elements of P's stages | Yes. EVENT indicators: the event's own stage. ENROLLMENT indicators: values from P's events, by default the latest event of each stage in the boundaries |
| Tracked entity attributes | Yes, if the attribute is assigned to P (a program attribute). An attribute set in another program becomes readable in P only when it is also a program attribute of P (it can be hidden in P's form) (2.42.6, 2.42.7.1). The expression validator does not check this: it accepts any attribute or other program's stage, and the PI fails only when queried (E7145) |
| Data of another program Q, including Q's enrollments or events | No. Not even "is enrolled in Q". Workaround: Q sets an attribute (rule ASSIGN) that P also carries |
| The parent's attributes across a relationship | No. Copy what is needed onto the member at creation |
| The number of relationships of a type | Yes: `d2:relationshipCount('<relationshipTypeUid>')` (the count only, no values from the other end), e.g. contacts per index case. Without an argument it counts all relationships |
| Another enrollment of the same tracked entity (an earlier episode in the same program) | No. An ENROLLMENT indicator sees one enrollment; facts that must survive re-enrollment go in attributes |
| Enrollment and event dates, org units, status | Yes (`V{enrollment_date}`, `V{event_date}`, `V{program_stage_id}`, `V{current_date}` evaluated at query time) |

Consequences to state in a design comparison:
- A **member as an event** in the parent's enrollment can be broken down by parent attributes (pattern 2 and the roster half of pattern 4).
- A **member as its own tracked entity** cannot, unless those attributes are copied onto it (pattern 3, 5, 6 and the follow-up half of 4).
- **Line lists reach further than indicators, but only as lists.** Since 2.41, tracked entity line lists (`/api/analytics/trackedEntities/query/<trackedEntityType>`, the Line Listing app's tracked entity input) show one row per tracked entity with attributes and data from several programs of that type. Event and enrollment queries accept a dimension `<relationshipTypeUid>.<programIndicatorUid>`, which evaluates the program indicator over the records linked by that relationship type (source: `QueryItemLocator`/`RelationshipTypeJoinGenerator`, 2.40–2.43; not exercised live). Use them for case lists and data checks. Neither gives an aggregate indicator that dashboards can break down by the other program's or the parent's values.
- **Totals spread over two programs** (in-school children in one, out-of-school in another) are possible as an aggregate indicator adding two program indicators, but lose a single disaggregated total (2.42.6).

## Org unit of an indicator

`orgUnitField` decides which org unit a value is counted at: the enrollment org unit (default for ENROLLMENT), the event org unit (default for EVENT), the registration org unit (REGISTRATION), the owner at the start or end of the period (OWNER_AT_START / OWNER_AT_END), or a data element / attribute of value type ORG_UNIT.

- "By school where the child enrolled" needs an ORG_UNIT data element in the follow-up stage, used as `orgUnitField`.
- **OWNER_AT_END works as a PI `orgUnitField` on 2.42.7.1** (4 and 2 transferred enrollments counted at their new schools for the year, all at the district for the quarter before the transfers). It falls back to the enrollment org unit **without warning** when the ownership analytics table is empty, which is what a 2.42.6 PoC saw after 510 transfers. The `orgUnitField=OWNER_AT_END` query parameter on `/api/analytics/enrollments/*` had no effect on 2.42.7.1. Use ownership for "counted where the person is now", and check on the target version that it reaches analytics: transfer a few test enrollments, run analytics, and compare an OWNER_AT_END PI with an ENROLLMENT one. A data element that copies the current service point duplicates ownership and must be updated at every transfer; keep it as a last resort for a version where ownership analytics is shown not to work, not as a default.

## Breakdowns

- **Sex and age bands**: on 2.42+, one program indicator with a disaggregation category combo and `categoryMappings` on the program replaces one indicator per cell (`ProgramCategoryMapping` exists from 2.42; verified on 2.42.6 and 2.43; saved ~60 indicators per design). Before 2.42, plan one program indicator per cell. A PI queried with a category it does not have returns E7145 ("Query failed because of a syntax error") instead of a clear message; requested together with a PI that has the category, it is silently dropped from the response (2.42.7.1).
- **Multi-select fields** (MULTI_TEXT, e.g. "reasons, up to three"): countable per item with `containsItems(#{stage.de}, 'CODE')` (or `contains(...)`) in PIs since 2.41 (no `d2:` prefix; the functions are not in 2.40's expression parser; program rules use `d2:contains`). Keep one multi-select for entry; no per-option yes/no fields are needed.
- **"Latest state" measures** (current outcome of a follow-up): ENROLLMENT indicator reading the latest event value. **History measures** ("retained a term later", "visited at least once") need repeatable events, not edits of one event: edits overwrite.
- **Completion and outcome rates are cohort measures.** "TPT completion" or "enrolled a term later" needs a denominator fixed by an entry period (started TPT in Q1) and a numerator read after the follow-up time has passed (6 months later), as ENROLLMENT indicators with the enrollment date (or the start event's date) as the period boundary. "Completed / all enrollments" mixes people still on treatment with those who finished. State the reporting lag.
- **Overdue work**: `V{current_date}` against due dates works in a PI, but working lists are usually the better tool for action (see `access-and-workflow.md`).

## Checklist per indicator

For each indicator in the brief, write down for each model: the program, EVENT or ENROLLMENT, the filter, the org unit field, the disaggregation, and "not reachable: <reason>" where it fails. Generate that "not supported" list in the metadata generator rather than by hand if you prototype: it becomes the comparison table's column and cannot drift.
