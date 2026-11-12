---
name: dhis2-indicators
description: "Author, review, and test DHIS2 aggregate indicators and program indicators: numerator/denominator, indicator type or factor, program-indicator expressions and filters, EVENT vs ENROLLMENT analytics type, analytics period boundaries, d2: functions, or why an indicator returns the wrong number. Trigger even without the word 'indicator': 'how do I calculate X in DHIS2', 'this rate looks wrong in analytics', 'count events where…', 'percentage of … by org unit', 'pupil-teacher ratio', 'validate/verify this calculation against the data'. Covers defining the expression, validating its syntax, proving it on a throwaway instance, and documenting it. Owns expression semantics; auditing a whole set of indicators at once (dozens to thousands, with a review meeting and approvals) is dhis2-indicator-review."
---

# DHIS2 indicators and program indicators

This skill covers writing indicators correctly **and** proving they compute what you intend. Treat testing as part of authoring, not an afterthought — an indicator you haven't validated against known data is a guess. The two halves share the same knowledge (expression syntax, factors, COC references, d2 functions), which is why they live in one skill.

Scope is aggregate indicators and program indicators. Predictors and validation rules use the same expression engine and the same testing method, so the approach transfers, but they aren't documented here.

## Workflow

Follow this order. Each step catches a different class of error.

1. **Decide the kind.** Aggregate indicator or program indicator? See the decision below.
2. **Define the expression** from the metadata, not from memory of field names. Resolve real data element / category-option-combo / attribute UIDs from the dataset or program. For aggregate indicators, choose the indicator **type** deliberately — its factor multiplies the result.
   - **Establish the naming convention first.** Before creating anything, confirm how names should be formed: any prefix or grouping tag, casing, how disaggregation is expressed in the name, the `shortName` rule (≤50 chars), and whether a `code` scheme is used. If the user hasn't given one, **ask** — don't invent it. Consistent names are how these objects stay findable in Maintenance and analytics, and renaming a batch afterwards is painful, so it's worth one question up front.
   - **IDs for new objects** must be valid DHIS2 UIDs: exactly 11 characters, `[A-Za-z0-9]`, starting with a letter. Readable hand-made ids (`AncDrop1t3`, 12-character names) fail the import. Generate them (`GET /api/system/id?limit=N`, or `random.choice(ascii_letters) + ''.join(random.choices(ascii_letters + digits, k=10))` offline) or omit `id` and let the server assign one.
3. **Validate the syntax** with the description endpoints (below) before any data exists. This catches bad references and malformed expressions in seconds.
4. **Lint the underlying metadata.** Syntax validity doesn't mean the data elements are configured right. Check that each referenced DE has the expected `aggregationType` (usually SUM), a numeric `valueType`, and that every `#{de.coc}` COC belongs to the DE's current category combo. A DE silently set to `aggregationType: COUNT` breaks the result while the expression looks perfect — neither verification layer catches it. See the pre-flight lint in `references/testing.md`.
5. **Test on a throwaway instance** (get one with `dhis2-test-instances`). Import the metadata, create org units, enter known data, run analytics, and compare analytics output to independently-computed expected values. See `references/testing.md`.
6. **Document** the definition, its meaning, and the test result so the next person can trust and reproduce it.

## Aggregate indicator or program indicator?

Aggregate indicators run over **aggregated data values** (data element × category option combo, already summed into the analytics tables). Use them for dataset/aggregate data: enrolment totals, facility counts, coverage rates.

Program indicators run over the **events or enrollments** of a tracker or event program — one value computed per event or per enrollment, then aggregated. Use them when the unit of analysis is a case, visit, or registration: count of events meeting a condition, time between two stages, a value taken from one enrollment.

A categorical question ("how many schools are public?") is countable in a program indicator (filter on the option) but **not** in an aggregate indicator unless the category is modelled as a category option combo or a boolean data element — an aggregate indicator does arithmetic, never "count where value = X". See `references/aggregate-indicators.md`.

## Anatomy in one screen

**Aggregate indicator** = `factor × numerator / denominator`.

- Numerator/denominator are arithmetic over `#{dataElementUID.categoryOptionComboUID}` (a specific disaggregation) or `#{dataElementUID}` (the sum of all that element's COCs), plus `+ - * /`, parentheses, numbers, `C{constantUID}`, `OUG{orgUnitGroupUID}`, `D{programUID.dataElementUID}`, and `I{programIndicatorUID}`.
- **factor** comes from the indicator **type**: Number ×1, Percentage ×100, "per 1000" ×1000, or custom. A percentage built on a Number type is wrong by 100×. This is the most common authoring error.
- `decimals` controls displayed precision; `annualized: true` scales by period length (use for population-denominator rates, not for school-level counts).

Full patterns, examples, and pitfalls: **`references/aggregate-indicators.md`**.

**Program indicator** has more moving parts, each a place to be wrong:

- **analyticsType**: `EVENT` (each event is a unit) or `ENROLLMENT` (each enrollment is a unit). Determines what gets counted; an enrollment with several events in a repeatable stage is counted once as ENROLLMENT, many times as EVENT.
- **aggregationType**: COUNT, SUM, AVERAGE, COUNT (distinct), etc. — applied across the units.
- **expression**: computed per unit, using `#{programStageUID.dataElementUID}`, `A{attributeUID}`, `V{...}` variables (`event_date`, `enrollment_date`, `value_count`, …), `d2:` functions (`d2:condition`, `d2:hasValue`, `d2:count`, `d2:daysBetween`, …), `C{constantUID}`, and numbers.
- **filter**: a boolean selecting which units count. The expression computes the value; the filter decides membership. Putting selection logic in the expression is a frequent mistake.
- **analyticsPeriodBoundaries**: decide whether an event/enrollment falls in a period by event date or enrollment date. The most common silent error; test it with dates on a period edge. Maintenance adds default boundaries; a PI POSTed through the API without them is **unbounded** (the same all-time value in every period), so always write them out.

Full patterns, d2 reference, boundary recipes, examples, and pitfalls: **`references/program-indicators.md`**.

## Validate syntax before data

The description/validation endpoints confirm references resolve and syntax parses, on any instance, before you set up a test. The methods differ (dhis2-core 2.42 `ProgramIndicatorController`; checked live on 2.43):

- Aggregate numerator/denominator: `GET /api/expressions/description?expression=<url-encoded expr>`
- Program indicator expression / filter: `POST /api/programIndicators/expression/description` / `POST /api/programIndicators/filter/description`. Body: the raw text with `Content-Type: text/plain`, or `{"expression": "<text>"}` with `Content-Type: application/json`. GET returns 405.

```bash
curl -s -u "$AUTH" -H 'Content-Type: text/plain' --data-binary "containsItems(#{<stage>.<de>}, 'X1')" \
  "$BASE/api/programIndicators/filter/description"
```

All of them answer HTTP 200 even for an invalid text, so read the body: `"status": "OK"`, `"message": "Valid"` and a human-readable description mean every UID resolved; `"status": "ERROR"` / "Expression is not valid" names the problem.

**Importing:** `POST /api/indicators` / `POST /api/programIndicators` take **one object** per request. A file wrapped as `{"indicators":[...]}` or `{"programIndicators":[...]}` goes to `POST /api/metadata` (try `importMode=VALIDATE` first).

## Test it (don't skip)

Syntax validity is not correctness. A numerator can be perfectly valid and still reference the wrong COC. Prove the calculation against known data on a fresh, disposable instance. The method, in brief:

- Compute expected values **two independent ways** — once by evaluating the expression over the input (does analytics match the expression?), once from the definition's meaning by classifying data from metadata (does the expression match the intent?). The gap between them is where real bugs hide.
- Feed **distinct, recorded input values** per cell, never constants, so a wrong reference produces a detectably wrong result.
- Cover edge cases: zero/blank denominator, on-threshold values, period-boundary dates, parent aggregation (percentages recombine as Σnum/Σden, never an average of child percentages).

The full procedure — fresh-instance setup, importing metadata (via the `dhis2-metadata` skill), entering data, running analytics, querying, and comparing — is in **`references/testing.md`**.

## When a number looks wrong

A wrong chart usually has several causes; check every object's configuration, not only its expression, and don't stop at the first:

- **Aggregation type vs expression.** A count-style PI (`V{event_count}`, `V{enrollment_count}`, `1`) needs COUNT (or SUM); AVERAGE returns 1 or an SQL error whatever the count. A data element on AVERAGE/COUNT where SUM is meant skews an aggregate indicator just as quietly.
- **Boundaries.** No `analyticsPeriodBoundaries` (API-created) → same value in every period. Fix: `EVENT_DATE` `AFTER_START_OF_REPORTING_PERIOD` + `BEFORE_END_OF_REPORTING_PERIOD`.
- **Cross-stage reads.** An EVENT PI's row holds only its own stage's values: `#{otherStage.de}` is null, so the PI counts 0 although it validates. Anchor on the owning stage, or use ENROLLMENT and prove with a probe PI that the value resolves.
- **ENROLLMENT lookups honour only `EVENT_DATE` boundaries.** `#{stage.de}` and `d2:count*` in an ENROLLMENT PI read events inside the `EVENT_DATE` boundaries (the latest such event); enrollment-date and `PS_EVENTDATE:<stage>` boundaries place the enrollment in a period but don't limit those lookups (dhis2-core 2.42 `DefaultStatementBuilder`, `ProgramCountFunction`; 2.43's new SQL engine handles boundaries differently, so probe there). So "had X at a visit in this quarter" needs `EVENT_DATE` boundaries (or an EVENT PI with `V{tei_count}`), while a value recorded at an *earlier* stage (e.g. at registration, read in the month of a later follow-up visit) disappears under them. Test a record that crosses a period edge.
- **Units.** A percentage's numerator and denominator count the same thing (people/people or visits/visits); say which.
- **Indicator type.** Percent (×100) is right for a percentage; an extra `*100` in the expression is the bug.
- **"I changed it and the chart didn't move" proves nothing.** Analytics responses are cached per URL (`keyCacheStrategy`; up to two weeks on seeded demos). Bypass with `POST /api/maintenance/cacheClear` or a fresh `&_cb=<timestamp>` before judging a change. Definitions apply at query time; changed *data* needs the analytics tables re-run.

**Deliver the fix, not a description of it:** write a corrected metadata file (importable as is: real UIDs, no placeholders, boundaries and aggregation type set, every object you changed or replaced) into the output folder the user or environment uses, plus how to prove it: probe PIs, line-level `/api/analytics/events/query`, test events on both sides of a period edge on a throwaway instance (`references/testing.md`).

## Composition with other skills

- **`dhis2-metadata`** — fetch/split/import the dataset or program dependency export into the test instance, in dependency order. The testing reference assumes you use it.
- **`dhis2-docs`** — look up endpoint behaviour, d2 function signatures, and version-specific details rather than guessing.
- **`dhis2-indicator-review`** — when the job is a whole set of indicators rather than one (a program's PIs, or aggregate indicators): validating hundreds at once, deciding fixes with a programme team, testing them end to end and getting each change approved. It builds on this skill's references; its `references/<type>/behaviours.md` index the same behaviours by ID with the probe evidence behind them.
- **`dhis2-test-instances`** — get, reset and discard the disposable test instance (an environment-provided one, a local Docker instance, or one from the user). Database access helps when root-causing analytics.

## Pitfalls (quick list)

- Wrong indicator type → factor off by 100× (percentage on a Number type).
- Referencing `#{de}` (all COCs) when you meant one disaggregation, or vice versa.
- Text/option-set data elements can't feed an aggregate indicator (no numeric value to sum); model as COCs or booleans.
- Program indicator: EVENT vs ENROLLMENT double-counting (a repeatable stage counts a person once per visit in EVENT); selection logic in the expression instead of the filter; null treated as zero.
- Program indicator, verified on 2.43.2: ENROLLMENT filters compare a blank number as 0 (guard with `d2:hasValue`); ENROLLMENT PIs read events *after* the period unless an `EVENT_DATE` boundary caps them; `offsetPeriods` without `offsetPeriodType` is ignored; the metadata import doesn't validate PI filters at all. With program disaggregation (`categoryMappingIds`), EVENT PIs drop records in band gaps or overlaps from the total too. See `references/program-indicators.md`.
- `d2:daysBetween(a, b)` is `b − a` (dhis2-core 2.43 `D2DaysBetween`): "diagnosed within 1 day of onset" is `d2:daysBetween(onset, diagnosis)`, and reversed arguments make late cases negative, so they pass a `<= 1` test.
- Concluding a function doesn't exist because the `d2:` form failed validation. Multi-select `containsItems()`/`contains()` are **unprefixed** in indicators and PIs (2.41+); `d2:` is the program-rule form. **`contains()` is a substring match**: `contains(x, 'DS1')` also counts `DS10`, `DS11`…, so when one code is a prefix of another use `containsItems()` (whole comma-separated items) and say why. With several codes both require *all* of them; for "any of" write `containsItems(x,'A') || containsItems(x,'B')` (dhis2-core 2.43 `FunctionContains`, `FunctionContainsItems`). See `references/program-indicators.md`.
- Division by zero: two different outcomes. A zero in the indicator's **denominator field** leaves only that cell without a value. A division **inside** the numerator or denominator expression (`(a - b) / a` over denominator 1) with `a = 0` for any requested org unit/period aborts the **whole** analytics request (HTTP 409, E7132) on versions before 2.43, and returns `NaN` for that cell on 2.43.2. Put the divisor in the denominator field; guard unavoidable inner divisions with `if(b != 0, a / b, 0)`.
- Average of facility rates: a normal indicator gives Σnum/Σden at the parent (a weighted rate). An unweighted mean is possible with a guarded `subExpression()` (`references/aggregate-indicators.md`); when you build it, **also ship the pooled indicator in the same file**, labelled, and state the trade-off: every facility weighs the same, so a small clinic counts as much as a hospital and the result is not the population rate.
- DE configured wrong at the source — `aggregationType` not SUM, or a `#{de.coc}` pointing at a COC outside the DE's current combo — breaks results while the expression looks fine. Lint the metadata (step 4).
- Program rule variable names are functional identifiers — program rules reference them by *name* (`#{varName}`, `A{varName}`, `d2:hasValue('varName')`), so renaming or translating a variable while tidying metadata silently breaks every rule using it. The failure shows up as rules that stop firing, not as an error.
- Zeros vanish — a `0` for a DE with `zeroIsSignificant=false` is dropped (by the importer on earlier versions; stored but ignored by analytics on 2.43.2), and analytics omits even significant zeros unless `keyIncludeZeroValuesInAnalytics` is on. Set both when a reported zero must count.
- Testing on a populated instance — always use a fresh, disposable one.
- Reading analytics before the analytics job finished, or after changing data without re-running it.
