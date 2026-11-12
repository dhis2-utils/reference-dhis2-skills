# Aggregate indicators — authoring reference

## Contents

- Anatomy and fields
- Expression syntax
- Indicator types and the factor
- Common patterns (totals, disaggregation, ratios, percentages, annualized)
- Categorical data: why option sets don't work and what to do
- How the engine evaluates an indicator (verified behaviours)
- Pitfalls

## Anatomy and fields

An aggregate indicator computes `factor × (numerator / denominator)`, where the factor comes from the indicator type. Key fields on the object:

- `name`, `shortName` (≤50 chars), `code` (optional), `description`. Follow the agreed naming convention (see the workflow in SKILL.md — if none was given, ask before creating, don't invent one).
- `numerator`, `numeratorDescription`, `denominator`, `denominatorDescription` — the descriptions are shown to users and should state plainly what each side counts.
- `indicatorType` — reference to an IndicatorType, which carries the `factor`.
- `decimals` — displayed precision (null = default).
- `annualized` — scales the value by the number of periods in a year (see below).

The numerator and denominator operate on **aggregated data values**: data already summed into the analytics tables by data element and category option combo. The analytics engine evaluates the arithmetic per org unit and period, aggregating numerator and denominator separately before dividing.

## Expression syntax

Operands inside numerator/denominator:

- `#{dataElementUID.categoryOptionComboUID}` — one specific disaggregation (e.g. a single class × sex cell).
- `#{dataElementUID}` — the sum of **all** that data element's category option combos.
- `#{dataElementUID.categoryOptionComboUID.attributeOptionComboUID}` — pin the attribute combo too (rare).
- `C{constantUID}` — a constant.
- `OUG{orgUnitGroupUID}` — count of org units in a group (useful for "number of facilities" style denominators).
- `D{programUID.dataElementUID}`, `A{programUID.attributeUID}`, `I{programIndicatorUID}` — pull program data or a program indicator into an aggregate indicator.
- Operators: `+ - * /`, parentheses, numeric literals.
- Functions for null/zero safety: `if(condition, x, y)`, `isNull(...)`, `isNotNull(...)`, `firstNonNull(...)`, `greatest(...)`, `least(...)`.
- `subExpression(...)` (2.40+) may reference **several** data elements or operands (dhis2-core 2.41 builds one SQL column per item). It is not limited to one data element. It is evaluated per org unit per *requested* period (the inner query groups by `ou` and the query's period-type column, e.g. `quarterly`, in 2.40–2.43), so a quarterly query evaluates the subexpression once per facility-quarter (data summed within the quarter), not once per facility-month.
- **Average of facility rates is possible** (don't tell users it isn't): the default indicator gives Σnum/Σden at the parent (a weighted rate); for an unweighted mean of facility rates use a guarded subexpression, e.g. numerator `subExpression(if(#{A} > 0, (#{A} - #{B}) / #{A}, 0))`, denominator `subExpression(if(#{A} > 0, 1, 0))` → Σ(facility rates) / number of facilities with A > 0. Outer aggregation of a subexpression defaults to SUM (`.aggregationType(AVERAGE)` overrides it); missing values inside it read as 0 (2.41.10 source). Deliver it **together with** the pooled indicator (same file, both labelled), and flag the weighting trade-off: each facility weighs the same, so a clinic with 3 visits moves the mean as much as a hospital with 3,000, and the result is not the population rate. Prove it on a throwaway instance.

Example null-safe denominator so a missing value yields no result rather than an error:

```
if(isNotNull(#{qoiU4awdpxQ}), #{qoiU4awdpxQ}, 1)
```

Prefer leaving a zero/blank denominator to return no value (DHIS2 omits the row) over forcing a 1 — forcing a 1 silently produces a meaningless number. Use the `if` form only when you specifically want a fallback.

## Indicator types and the factor

The indicator **type** sets the factor that multiplies `numerator/denominator`:

- **Number** — factor 1. Counts and ratios. A pupil-teacher ratio (learners ÷ teachers) is a Number-type indicator with the teacher count as denominator; it is *not* a percentage even if a spec labels it "%".
- **Percentage** — factor 100. Anything that should read 0–100.
- **Per mille / per 10,000 / per 100,000** — factors 1000 / 10,000 / 100,000, for population-rate style measures.
- **Custom** — any factor.

Getting this wrong is the single most common aggregate-indicator error: a percentage built on a Number type is off by 100×, a ratio built on a Percentage type by the same. On a fresh instance, indicator types must exist *before* importing indicators that reference them, and you must confirm the factor — importers move objects but don't check that "Percentage" really has factor 100.

## Common patterns

**Total (sum of a disaggregated element).** Use `#{de}` to sum every COC:

```
numerator:   #{eBTbIITRm3H} + #{tno1y7kW71Z} + …      (sum of the relevant elements)
denominator: 1
type: Number
```

**Sex (or any single category) disaggregation.** There is no "filter by category option" in an aggregate expression. Enumerate the category option combos that carry that option. To get "girls", sum every COC whose category option is Female across the relevant elements:

```
numerator: #{DE1.femaleCOC1} + #{DE1.femaleCOC2} + … + #{DE2.femaleCOC1} + …
```

Build these lists from metadata (group the dataset's category option combos by their category combo, then pick the COCs whose category option set includes the one you want) rather than by hand — it is easy to miss or duplicate a COC, and a wrong COC is invisible unless your test data uses distinct values per cell.

**Ratio (per one).** Learners per teacher, learners per classroom, learners per stream:

```
numerator:   <enrolment total expression>
denominator: #{ERcw4yZuSSd}      (teachers)
type: Number      ← factor 1, NOT Percentage
decimals: 1
```

**Percentage.** Share of a total:

```
numerator:   <girls expression>
denominator: <total expression>
type: Percentage   ← factor 100
decimals: 1
```

**Annualized rates.** `annualized: true` divides by the fraction of the year the period covers, so a quarterly value is scaled to an annual figure. Use it for population-denominator coverage/incidence rates where the denominator is an annual population. Do **not** use it for simple counts or for school-census style indicators where the period already represents the reporting cycle — it will distort the number.

## Categorical data: why option sets don't work

An aggregate indicator does arithmetic on numeric aggregated values. A data element backed by an **option set with valueType TEXT** stores an option code (text) and has aggregationType NONE — it never enters the numeric analytics path, so it cannot appear in a numerator. Even if the option codes are numeric, the data element's valueType decides whether analytics treats them as numbers; and even then, summing or averaging nominal codes is meaningless.

To count by category in aggregate analytics you must move the categorisation into something numeric:

- Model the characteristic as a **category** so each option becomes a category option combo; then `#{de.cocForOptionX}` counts the units in that option.
- Or create one **boolean / TRUE_ONLY** data element per option; each aggregates as a count and drops into an indicator.

Numeric-looking option codes do **not** rescue this, and they still can't give a "count where value = X". For per-record display of a categorical value, show the data element directly (custom report, line listing, data value API) — no indicator. Counting by option *is* native to program indicators (filter on the option), which is one reason to choose that path.

## How the engine evaluates an indicator (verified behaviours)

Confirmed on 2.43.2 with probe indicators over hand-made data; re-check on other versions before relying on an edge case. The IDs match `dhis2-indicator-review/references/indicators/behaviours.md`, which has the probe evidence and the recipe.

- **A1 Missing operands.** An operand with no data reads 0 if at least one other operand on the same side (numerator or denominator) has data. If every operand on a side is missing, that side is null and the indicator has no value. A constant doesn't rescue a side (`#{a} + 0` is null where `a` has no data). Only operands actually visited count: `if()` evaluates its condition and the branch taken; operands inside `isNull`, `isNotNull` and `firstNonNull` don't count. `OUG{}`, `C{}` and `[days]` are not operands for this rule; `R{}` is. An unknown data element UID is just a missing operand, and `/api/expressions/description` still says "Valid".
- **A2 Denominator 0 or null** → no value (the row is omitted).
- **A5 Aggregate first, then evaluate.** Each operand is aggregated over org units and periods by its aggregation type, then the expression is evaluated once on those totals. So a parent value is Σnum ÷ Σden, and a ratio written inside the numerator is the ratio of the totals.
- **A6 Aggregation types over time and org units.** SUM adds. COUNT counts stored values (three reports of 7, 9 and 11 give 3). AVERAGE is the plain mean of every value in the period and org units (no weighting by days). AVERAGE_SUM_ORG_UNIT averages over time per org unit (weighted by days), then sums over org units; data in a **longer** period than the query (a yearly population for a month) is used as it is.
- **A7 SUM data in a longer period is not used.** A yearly SUM data element has no value for any month or quarter.
- **A8 `annualized`** multiplies by 365 ÷ days in the query period (January 365/31, Q1 365/90, a year 1).
- **A9 Rounding** to `decimals`; unset means 2 decimals.
- **A14/A15** `OUG{group}` counts the group's org units at or below the queried org unit, whatever the data; `C{constant}` is its value; `[days]` is the number of days in the query period.
- **A17 Functions:** `if`, `isNull`, `isNotNull`, `firstNonNull` (0 when every argument is null), `greatest`, `least`, `log`, `log10`, `^`, `%`. A bare boolean as a whole side (numerator `isNotNull(#{b})`) reads 0; use it inside `if()`.
- **A20 A side the server can't parse reads 0, silently.** The old reporting-rate form `#{dataSet.REPORTING_RATE}` imports fine, is "not well-formed" for `/api/expressions/description`, and makes a numerator 0 everywhere (a denominator gives no value). Use `R{dataSet.REPORTING_RATE}`.
- **A21 `R{ds.REPORTING_RATE}`** is 100 × complete registrations ÷ expected reports at or below the org unit; it is rounded to 2 decimals before entering the expression unless the query has `skipRounding=true`. An assigned parent org unit counts as an expected report. With no complete registrations at all on the instance, analytics fails with E7144.

## Pitfalls

- **Factor / indicator type** wrong → off by 100× (or 1000×). Confirm every percentage uses a factor-100 type and every ratio a factor-1 type.
- **`#{de}` vs `#{de.coc}`** — `#{de}` is the sum of all COCs; if you meant one disaggregation, name the COC, and vice versa.
- **Missing COC in a disaggregated sum** — undetectable unless test data uses distinct per-cell values. Generate the COC list from metadata.
- **Forcing a denominator to 1** to dodge divide-by-zero — produces a meaningless number; prefer letting it return no value.
- **Division by zero inside the expression is not null-safe.** A zero *denominator field* gives no value, but `a / b` with `b = 0` *within* the numerator or denominator aborts the whole analytics request with `409 E7132 "Expression violation. Maybe an indicator caused division by zero?"`, taking every other indicator in the request down with it (seen on earlier versions). **On 2.43.2 the behaviour differs** (verified with probe indicators): the request succeeds and the affected cell comes back as `"NaN"`, with or without rounding; `log(0)` gives `-Infinity`. Either way the number is wrong, and which one you get depends on the version, so probe it. Guard inner divisions with `if(b != 0, a / b, 0)` or restructure.
- **A guarded 0/1 denominator turns into an average at higher levels.** To make per-facility cells blank on purpose (denominator 1 where reporting, 0 elsewhere), remember the denominator sums as it aggregates up, so the parent value becomes Σnum/Σ(flags) — an average. If the indicator should sum, wrap the flag in a subexpression with `.aggregationType(MAX)` so it stays 1 at every level.
- **Parent aggregation of percentages** — analytics recomputes Σnum/Σden×factor at the parent, which is correct; do not expect the average of child percentages. The same holds inside an expression: every operand is aggregated first (over org units and periods, by its aggregation type) and the expression is evaluated once on the totals, so a ratio written inside the numerator (`(a - b) / a` over denominator 1) gives the ratio of the totals at the parent, not a sum of facility ratios (verified on 2.43.2). Missing operands read as 0 unless every operand on that side of the indicator is missing, in which case the indicator has no value.
- **Time aggregation** — numerator/denominator aggregate across periods by each element's `aggregationType` (SUM, AVERAGE, LAST). An AVERAGE or LAST element behaves differently from SUM when a year is built from months.
- **Data element `aggregationType` set wrong at the source** — an element that should sum but ships with `COUNT`, `AVERAGE`, or `LAST` produces wrong indicator values, and the expression looks fine. This is invisible to expression review; check the DE config directly (see the pre-flight lint in `testing.md`).
- **`zeroIsSignificant` and stored zeros** — a `0` for a DE with `zeroIsSignificant=false` is lost: dropped by the importer on earlier versions, stored but ignored by analytics on 2.43.2. Analytics also omits stored zeros unless `keyIncludeZeroValuesInAnalytics` is on. If a real reported zero must count (e.g. in a denominator or a count), set both. A dropped zero is a missing value (see A1 below), so a facility reporting 0 shows no value instead of 0 %.
- **Legacy / wrong COCs** — a `#{de.coc}` whose COC isn't in the DE's current category combo imports and validates cleanly but never carries data, so the term silently contributes nothing. Derive COCs from current metadata.
- **Text/option-set elements** can't be summed — see above.
