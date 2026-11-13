# Out-of-school children (OOSC) follow-up — design v0.3

Target: DHIS2 2.42, web Capture for school staff, Capture Android for enumerators. Go-live in five weeks.

## What exists

- **Household listing** program (tracked entity type *Household*), live for six months. Household
  attributes: head of household name, *Female-headed household* (YES_ONLY), *Distance to nearest
  school (km)* (NUMBER), village. Children are found during the listing.
- **Learner registry** program (tracked entity type *Learner*) run by the education department.
  Schools register their learners there. Same instance.

## New: OOSC follow-up program

- Tracked entity type *Learner* (shared with the registry). Each out-of-school child found in the
  listing is registered in **OOSC follow-up** at the district org unit and linked to the household
  with a relationship *Household → Child*. Ownership is then transferred to the school that takes the
  child on.
- Attributes: first name, last name, date of birth, sex, **Learner ID**, **Age group**.
  - *Learner ID* is generated with the text pattern `ORG_UNIT_CODE(...) + "-" + SEQUENTIAL(#####)`,
    so the ID shows which school registered the child. School org unit codes look like
    `SCH_00412`, `SCH_00977`.
  - *Age group* (option set 6-11 / 12-14 / 15-17) is assigned by a program rule from the date of
    birth. A second rule hides it on the registration form, to keep the form short.
- Stage **Follow-up visit** (repeatable): visit date, outcome, *Reason out of school*.
  - *Reason out of school* is a free TEXT data element in the pilot (two districts, ~900 children
    entered so far). After the pilot we will turn it into an option set with the codes the pilot
    produced.

## Dashboards and lists

1. OOSC by sex and age group: one program indicator per sex × age-group cell (6 per measure,
   4 measures = 24 PIs).
2. OOSC by female-headed household and by distance band, from program indicators in OOSC follow-up.
3. % of OOSC already registered in the learner registry: program indicator in OOSC follow-up that
   counts children with an enrollment in the Learner registry program.
4. Children currently followed, per school: program indicator with `orgUnitField: OWNER_AT_END`,
   so a transferred child counts at the new school.
5. Schools' to-do list: a tracked entity working list in web Capture, "Follow-up overdue", filtered
   on event status OVERDUE.

## Questions for review

Anything here that will not work as intended on 2.42, or that we will regret after go-live?
