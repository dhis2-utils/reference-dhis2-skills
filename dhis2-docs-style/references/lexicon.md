# Lexicon: preferred wording for DHIS2 docs

Format: **avoid** → **use**. Apply in prose only. Never change inside code,
UI labels, API names, quoted release notes or URLs.

## Plain words

- utilize, leverage, employ → use
- facilitate, enable (a person to) → let, help, or "You can…"
- commence, initiate → start
- terminate → end, stop
- ensure → make sure
- in order to → to
- prior to → before
- subsequent to, following → after
- via → through, using, with
- hence, thus, therefore (as filler) → so; or restructure
- whereby, thereby, wherein → where, so, in which
- in the event that → if
- a number of, a variety of, numerous → several, many, or the number
- the majority of → most
- is able to → can
- has the ability to → can
- with respect to, in relation to, with regard to → about, for
- in addition, additionally → also, and
- approximately → about (in prose), "~" is fine in tables
- inform → tell
- obtain → get
- require (noun use "the requirement for") → need, must
- perform (an action) → do, run
- carry out → do, run
- set up (verb) → configure, create
- set-up (noun) → setup, or "configuration"
- reach out → contact
- find out → learn, check
- look at → see, check, open
- make use of → use

## Ambiguous words

- once → after, when
- since (reason) → because
- while (contrast) → but, although
- as (reason) → because
- may → can (ability), might (possibility), "is allowed to" (permission)
- should (requirement) → must
- could, would (system behaviour) → can, does
- it, this, they (unclear) → repeat the noun
- file, record, report, set, run (as verb or noun in one sentence) → rewrite
  so each use is clearly one part of speech

## Filler and softeners

- simply, just, easily, easy, quickly, obviously, of course, basically → delete
- please (in steps) → delete
- note that, please note that, it should be noted that → delete, or use a
  real note block
- it is possible to → You can
- there is/are … that → say the subject: "Three options control…"
- a bit, a little, rather, quite, very → delete or give the value
- robust, seamless, powerful, comprehensive, flexible → say what it does

## Idiom and figurative language

- blank slate → empty
- get to know → learn about / overview of
- up and running → working
- on the fly → while you work / automatically
- out of the box → by default
- under the hood → internally
- deep dive → detailed guide
- bear in mind → remember
- rule of thumb → guideline
- cheat sheet → quick reference
- a handful of → a few, or the number
- ballpark → approximate
- sanity check → check
- dummy data → sample data, test data
- whitelist / blacklist → allowlist / blocklist
- master / slave → primary / replica (and never "master" as a version name)

## Latin abbreviations

- e.g. → for example, such as
- i.e. → that is
- etc. → and so on, or list every item
- vs. → compared with, or "versus" in titles

## UI verbs

- click on → click (buttons, links) / choose (list items, checkboxes, menu items)
- check the box → choose the checkbox
- tick → choose
- select / pick → choose
- hit / press → click (mouse), press (keyboard key)
- hover → move the pointer over
- drag-and-drop → drag (and say where to drop)
- navigate to → go to, open
- left-hand side / right-hand side → "on the left of the screen" or name the panel
- above / below → "the following table", "the previous section", or a link

## Spelling and forms

Rule (DHIS2 design system, confirmed 2026-10-05): **US English, except established DHIS2 terms.**

- organisation unit (and organisation unit group / level) → keep British. This is the established DHIS2 term.
- organisation (other uses), organisations → organization, organizations
- organisational → organizational
- orgunit, org unit → organisation unit (prose; keep in UI or API names)
- meta-data → metadata
- DHIS 2 → DHIS2
- customise, synchronise, summarise, analyse, visualise, authorise → customize, synchronize, summarize, analyze, visualize, authorize
- synchronisation, customisation, visualisation → synchronization, customization, visualization
- colour, behaviour, centre, catalogue, favourite, cancelled → color, behavior, center, catalog, favorite, canceled
- licence → license
- programme → program (keep "Programme" in the proper noun "Health Information Systems Programme")
- email, e-mail → email
- website, web site → website
- log in (verb), login (noun) → log in, login
- set up (verb), setup (noun) → set up, setup
- off-line → offline; nation-wide → nationwide
- & → and; display (verb) → show; access (verb) → open, edit, view (design system)

## Design system glossary (A-Z)

Source: developers.dhis2.org/design-system/patterns/glossary. Avoid → use: display → show; execute → run; launch → start or open; specify → set; dropdown → menu; text box → box; docs → documentation; mandatory, compulsory → required; reload → refresh; config → settings or setup; sign in → log in; drag and drop → drag; impact (verb) → affect; duplicate → copy; e.g., etc. → for example, such as; in order to → to; once (sequence) → after; write, add (input) → enter; complete (a form) → fill out; new/add at the end of a form → create; access (verb) → open, edit, view; this/that with unclear reference → the noun. Data model words with fixed meaning (approve, category, indicator, complete): use only for the DHIS2 object or workflow. "favorite" is replaced by "saved visualization" for new concepts. Use "app", not "application". Conflict to resolve: the glossary prefers "choose" over "select" when instructing a selection.

Measured in dhis2-docs/src on 2026-10-05 : synchronization 103 vs synchronisation 4; color 82 vs colour 4; visualization 78 vs visualisation 2; program 2150 vs programme 31; analyze and analyse tie at 21; behaviour and behavior tie (17 vs 14); organisation 1784 vs organization 50 (almost all "organisation unit").

## Headings

- Title Case → Sentence case ("How to merge indicators"), except app and product names ("Data Entry app")
- A heading or text that names a UI element → the case the app shows, verified in the app's `i18n/en.pot` (for example "Metadata import", not "Metadata Import")
- "How to Merge" and "About merging" → pick one pattern per page; for task
  pages use "Merge indicators" (imperative) or "How to merge indicators"
- A heading with no body text → flag it to the page owner; do not delete it.

## Numbers and dates

- 02/10/26, 10-2-2026 → 2 October 2026, or 2026-10-02
- "Q3" → "July to September" for readers with other fiscal years
- thousands separator → leave as is in examples. In prose, use a space or
  comma consistently on a page.
- Always write the unit: "50 characters", "10 MB".

## Inline formatting

Interface elements (buttons, menu items, tabs, checkboxes, options, job types, panel names): **bold**. New terms at first definition: *italics*. User input and placeholders: `code` or *italics*. Code, commands, file names, properties and API paths: `code`. No quotation marks around interface terms.
