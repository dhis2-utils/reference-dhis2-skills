# Corpus survey: tone and level in the current docs (2026-10-05)

Method: shallow clones of dhis2/dhis2-docs, import-export-app, scheduler-app,
data-visualizer-app, metadata-management-app. Measured 20 pages with
`scripts/measure.py` (code, tables, headings and links excluded) and read the
opening passages of 9. Pass counts are signals, not scores. Note that
import-export-app and scheduler-app have no docs folder on the default branch
yet; the user docs for those apps still live in dhis2-docs.

## Whole-tree counts (dhis2-docs/src, matched case-insensitively)

| Pattern | user (47 files) | developer (33) | sysadmin (49) |
|---|---|---|---|
| "organisation unit" / "organization unit" (the established term is British) | 1149 / 11 | 487 / 22 | 1 / 1 |
| "orgunit" / "org unit" | 158 / 35 | 269 / 133 | 0 / 0 |
| "meta-data" / "metadata" | 15 / 751 | 4 / 482 | 0 / 31 |
| "DHIS 2" / "DHIS2" | 15 / 1085 | 31 / 386 | 32 / 645 |
| "master" | 62 | 11 | 12 |
| em dash | 109 | 3 | 17 |
| "e.g." / "i.e." / "etc" | 101 / 18 / 33 | 52 / 22 / 12 | 40 / 6 / 9 |
| "click on" | 68 | 1 | 1 |
| "in order to" | 52 | 44 | 13 |
| "above" / "below" | 122 / 151 | 72 / 147 | 22 / 52 |
| " we " | 155 | 171 | 40 |
| " please " | 23 | 34 | 5 |

## Per-page measures

| Page | Words | Avg sentence | % >25 words | Grade | Em dash | e.g./i.e./etc | simply/just | we | will | passive | click | above/below |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| user/importexport-app.md | 2969 | 22.3 | 29 | 13.0 | 2 | 5 | 1 | 2 | 22 | 57 | 32 | 9 |
| user/scheduling.md | 4241 | 17.5 | 15 | 10.1 | 0 | 1 | 6 | 0 | 61 | 96 | 16 | 2 |
| user/using-the-aggregate-data-entry-app.md | 1580 | 14.2 | 9 | 7.9 | 0 | 0 | 1 | 1 | 9 | 30 | 17 | 2 |
| user/configure-metadata.md | 23181 | 14.7 | 10 | 9.6 | 1 | 4 | 8 | 2 | 138 | 304 | 341 | 22 |
| user/configure-metadata-management.md | 15250 | 15.3 | 13 | 10.3 | 71 | 1 | 5 | 0 | 71 | 219 | 194 | 33 |
| user/manage-users-user-roles-and-user-groups.md | 3709 | 15.3 | 12 | 9.5 | 0 | 3 | 2 | 2 | 22 | 43 | 67 | 7 |
| user/data-approval.md | 2582 | 19.4 | 28 | 12.3 | 0 | 0 | 2 | 1 | 11 | 87 | 2 | 16 |
| user/analyze-data-in-pivot-tables.md | 2323 | 15.4 | 15 | 9.3 | 0 | 0 | 2 | 2 | 15 | 21 | 48 | 1 |
| user/what-is-dhis2.md | 2634 | 20.6 | 27 | 13.3 | 0 | 8 | 5 | 4 | 4 | 52 | 2 | 2 |
| user/control-data-quality.md | 2080 | 14.1 | 8 | 11.3 | 0 | 2 | 0 | 0 | 12 | 33 | 25 | 2 |
| developer/web-api/tracker.md | 10975 | 15.2 | 8 | 10.5 | 3 | 10 | 9 | 25 | 81 | 230 | 0 | 17 |
| developer/web-api/metadata.md | 12224 | 14.7 | 8 | 10.3 | 0 | 13 | 8 | 22 | 101 | 262 | 0 | 38 |
| developer/web-api/analytics.md | 10774 | 19.1 | 14 | 12.7 | 3 | 6 | 5 | 0 | 61 | 211 | 1 | 30 |
| data-visualizer-app: docs/data-visualizer.md | 2449 | 17.0 | 19 | 10.4 | 4 | 3 | 3 | 0 | 15 | 58 | 35 | 4 |
| metadata-management-app: docs/user/merging-metadata.md | 549 | 15.2 | 0 | 10.4 | 0 | 0 | 0 | 0 | 6 | 0 | 12 | 0 |
| sysadmin/index.md | 788 | 14.9 | 8 | 15.3 | 0 | 1 | 0 | 3 | 1 | 8 | 0 | 2 |
| android/android-aggregate-data-capture-app.md | 257 | 18.4 | 7 | 9.0 | 0 | 0 | 2 | 0 | 4 | 5 | 1 | 0 |
| tutorials/add-a-custom-db-language.md | 295 | 14.8 | 5 | 6.6 | 0 | 0 | 1 | 2 | 4 | 4 | 0 | 1 |

## Similarities

1. **Spelling is mostly US already, with one British term.** Exact-word counts in
   dhis2-docs/src: synchronization 103 vs synchronisation 4, color 82 vs
   colour 4, visualization 78 vs visualisation 2, favorite 151 vs favourite 2,
   program 2150 vs programme 31. Analyze/analyse tie at 21 and
   behavior/behaviour are 14 vs 17. "Organisation" (1784 vs 50) is almost all
   "organisation unit", the established term the design system keeps British.
   *An earlier version of this survey called the docs "British English"; that
   was wrong. It came from counting the one established term.*
2. **"DHIS2" is already the dominant form** (1085 vs 15 in user pages).
3. **Most pages sit around grade 9 to 11** with an average sentence of 14 to 17
   words. That is better than most documentation sets. The problem is not the
   average; it is the long tail.
4. **Procedures are generally written as imperatives** in newer pages.

## Differences

1. **Three eras of voice.**
   - *Training-manual era* (what-is-dhis2, importexport-app intro, data-approval):
     long, noun-heavy sentences, 27 to 29% over 25 words, grade 12 to 13,
     passive and abstract subjects ("It allows data to be reviewed and approved
     at selected levels"), formal connectors (hence, thus, fulfil, details for
     which can be found below), "we show".
   - *Application-guide era* (scheduling, pivot tables, configure-metadata):
     imperative, second person, 14 to 17 words per sentence.
   - *Product-writing era* (Data Entry app, newer app-repo pages): friendly,
     contractions, short, "Looking to enter individual-level data? Check out…",
     bolded lead-in labels.
2. **Developer pages talk differently.** "We" appears 20+ times in tracker.md
   and metadata.md ("we will show"), "should help you", "reach out". The user
   guide almost never says "we".
3. **Em dashes.** The house rule says none, but configure-metadata-management
   (the Metadata Management app chapter) has 71, and the user tree has 109 in
   total. Almost all are in this one chapter.
4. **Title Case vs sentence case headings.** The MMA repo uses "How to Merge
   Indicators"; dhis2-docs uses sentence case.
5. **Different words for the same action.** The Data Entry app says "Choose",
   scheduling says "Select"/"Click", MMA repo says "Click on" and "Check the
   boxes", the older chapters say "click on" (68 times).
6. **Orientation words.** "Above/below" appears 122 and 151 times in the user
   tree. These fail on small screens, screen readers, and after machine
   translation.
7. **Acronyms and local shorthand.** "PHCs, CHCs", "HIS", "COC", "PI" appear
   without expansion in several intros.
8. **Old facts in new prose.** what-is-dhis2 still names "JRE 7 or higher" and
   a list of countries "currently" using DHIS2. These are audit issues, not
   style issues, and the skill only flags them.
9. **Hard-wrapped vs long-line files.** dhis2-docs mostly hard-wraps at 70 to
   80 characters; the app repos use one line per paragraph. A style edit must
   preserve whichever the file uses or the diff turns to noise.
10. **Empty or placeholder headings.** merging-metadata.md has an empty
    "About merging metadata" section.

## What this implies for the skill

- Do not try to flatten everything to one voice. Move the three eras toward
  the application-guide voice and keep the product-writing friendliness in
  tutorials and how-to pages.
- Most of the gain is in the long tail: sentences over 25 words, passive
  openings, "above/below", Latin abbreviations and the em-dash chapter.
- The biggest consistency risk is *between repos*: app-repo docs are written
  by different people with a different default. A shared skill and style guide is the cheapest way to align them.
