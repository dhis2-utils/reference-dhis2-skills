---
name: dhis2-docs-style
description: >
  Edit or review DHIS2 documentation prose for tone, plain language and
  technical level, for readers who often use English as a second language and
  work in low- and middle-income health systems. Covers house rules (no em
  dashes, no verification narration, "DHIS2", no "master"), Simplified
  Technical English, voice by page type (tutorial, how-to, reference,
  explanation), terminology and spelling consistency, and wording for
  translation. Use when asked to check or standardize tone, wording,
  readability or reading level of docs; before publishing a flattened or new
  page; and when writing prose for dhis2-docs or an app-repo docs folder.
  Not for facts (dhis2-docs-audit), page placement
  or markdown structure, screenshots and PRs (dhis2-docs-contribution).
---

# DHIS2 Docs Style (v2.9)

This skill applies the DHIS2 documentation style rules written down in the parts below. The research behind them is in `references/research-basis.md`.

This skill changes how a page says things. It never changes what the page
claims. The accuracy and version work is done by `dhis2-docs-audit`. This pass
makes the result easy to read for the people who use it.

## Who we write for

Write for a reader who is **competent in their job and reads English as a
second or third language**. Typical readers: a district HMIS officer, a data
clerk, a national system administrator, an implementing partner, a developer
who builds on the API. Assume these conditions:

- Many readers use browser machine translation (French, Portuguese, Spanish,
  Arabic and others). Text that is clear and literal translates well.
- Some read on slow or metered connections, on shared computers, or on phones.
- Readers know their health program. They may not know DHIS2 words,
  Java, or Western office idiom.
- Developers are expert in code but are still often non-native readers.

The goal is not "simple for beginners". The goal is **easy to parse in one
pass, by an expert who is reading in a second language**.

## Two kinds of rule

**House rules** (Part 1) and the **team decisions**
(see "Confirmed decisions" at the end) are applied without asking.
**Researched defaults** come from published guides
(`references/research-basis.md`) and a survey of the current docs
(`references/corpus-survey-2026-10-05.md`). The **DHIS2 design system writing
guidelines** (https://developers.dhis2.org/design-system/patterns/writing/ and
.../principles/content-communication) are DHIS2's own rules for interface
text. Where they cover a point, they win over general guides. Apply all of
these, but when one conflicts with a page's established, deliberate choice,
flag it rather than overwrite it.

## Part 1. House rules (always apply)

1. **No em dashes.** Replace each (—, or " -- ") with a comma, colon,
   parentheses or two sentences. Do not touch dashes inside code or URLs.
2. **No verification narration.** Never write "confirmed live on 2.43.1",
   "as observed on …", "verified against the app" in rendered prose. If a
   future check is needed, use an HTML comment: `<!-- VERIFY IN APP: … -->`.
3. **"DHIS2", not "DHIS 2".** Keep "DHIS 2" only inside established proper
   nouns, URLs, paths and quoted release text.
4. **Never write "master" in reader-facing text.** Say "current version".
   Leave DHIS2-authored URLs that contain `dhis-core-version-master`.
5. **Simplified Technical English** in procedures and reference (Part 3).

## Part 2. Voice

| Do | Not |
|---|---|
| Address the reader as "you" | "the user", "users", "one" |
| Use the imperative in steps: "Choose **Save**." | "Save should be selected", "You will need to click" |
| Use present tense for what the system does: "DHIS2 creates a UID." | "will create", "would create", "will have been created" |
| Name the subject: "DHIS2 stores…", "The app shows…" | "we", "our" (ambiguous about who "we" is) |
| Put the condition before the action: "If you use X, choose Y." | "Choose Y if you use X" in steps where the condition decides if the step applies |
| State a fact once, plainly | "Please note that", "It should be noted that", "Note that" as a throat-clearer |
| Be neutral about difficulty | simply, just, easy, easily, quickly, obviously, of course, straightforward |

Other voice points:

- Do not use "please", "thank you" or "sorry" in instructions (design system: they
  add noise without adding value).
- **No contractions** anywhere: write "does not", "cannot", "it is", "you are".
  Possessives ("the system's setting") are fine.
- Use "will" only for the consequence of a user action ("If you delete the
  group, DHIS2 will remove its members"). Otherwise use the present tense
  (design system).
- Use a serial comma: "data elements, indicators, and programs" (design system).
- Do not use exclamation marks, humor, rhetorical questions, or slang. Tone
  is clear, honest, and friendly but detached and professional (design system).
- Do not call a step "easy". A step is short or it is not.
- Use "should" only for a real recommendation. Use "must" for a requirement
  and "can" for an ability or option. Use "might" for possibility. Avoid
  "may" (it can mean permission or possibility). Avoid "could" and "would" for
  system behaviour.
- **Grammar and punctuation** (design system): end every sentence with a
  period. List items under three words, headings, titles and interface labels
  take none. Use sentence case everywhere except app, person and product
  names. Never use all caps for sentences or paragraphs. Start statements with
  verbs where possible. Avoid the DHIS2 data model in interface-facing text
  ("event" for "tracked entity instance" in user messages). Introduce an
  acronym at first use. Prefer short, clear words and use one keyword for one
  concept.
- **Refer to interface elements** with the same capitalization the element
  uses, in bold and never in quotation marks (design system: "Press Update",
  not "Press "Update""). See the inline formatting table in Part 4.
- Avoid "we". Tutorial pages may use it ("we will create…") because the learner
  and the author do the task together.
- **Exception for developer pages:** "the user" is allowed when it means the
  end user of an app that the developer builds ("Timestamp when the user
  created the object on the client"). Address the reader of the page as "you".
- **Page openings and objectives** depend on the page type (Part 6):
  - **Explanation pages** open with a **scope statement**: one or two
    sentences that say what the page explains, or the questions it answers.
    Match the lead-in to the form: "This chapter explains:" before statements,
    "This chapter answers:" before questions. Questions are fine here. They
    match the "why" question that bounds an explanation (Diátaxis). Do not
    write "After reading this chapter you will be able to understand". Do not
    list objectives on an explanation page.
  - **Tutorials and training-style chapters** use objectives with observable
    verbs that the page content actually teaches: "Compare patient-based and
    aggregate data", "Configure a data set for monthly reporting". Avoid
    understand, know, learn and be aware of, which nobody can observe. Do not
    promise a verb the chapter does not teach (do not write "Configure" for a
    purely conceptual chapter). Keep one grammar form across the list, and
    make each item complete the lead-in sentence.
  - **How-to and reference pages** have no objectives. The title and the first
    sentence say what the page is for.
  - Rewriting an objective or a scope statement can change what the page
    claims. Propose the change and ask, do not apply it silently.

## Part 3. Sentences (Simplified Technical English, adapted)

- **One idea per sentence. One action per step.** Split "configure X and then
  check Y" into two steps.
- **Length.** Aim for 20 words or fewer in a step, 25 or fewer in
  explanation. Look hard at any sentence over 25 words. Split any sentence
  over 35 words unless it is a list.
- **Active voice.** Passive is acceptable only when the actor is unknown or
  unimportant ("the job is stored"). Never use it to hide who clicks.
- **Keep small words.** Keep "that", "the", "a", "who". Do not drop them to
  save space. "Choose the checkbox of each folder that you want to sync."
- **Verbs, not noun forms.** "when you merge two categories", not "during the
  merging of two categories". "To delete", not "for the deletion of".
- **No stacks of more than three nouns.** "organisation unit group set
  membership list" becomes "the list of members in an organisation unit
  group set".
- **Clear pronouns.** If "it", "this" or "they" could point to two things,
  repeat the noun.
- **Avoid "there is/are" openings and sentences that start with "It is
  possible to".** Say what happens: "You can…".
- **Avoid -ing and -ed phrases that dangle.** "Configure limits based on the
  storage space available" becomes "Configure limits. Base them on the storage
  space available."
- **Place "only" next to the word it limits.**
- **Lists:** a parenthetical (a), (b), (c) list inside one sentence becomes a
  real list.
- Remove an inline "Note:" prefix when the sentence works without it. Keep
  real `> **Note**` blocks.
- **Say what the reader should see.** After an important step, add the
  result: "The import summary opens."

### Procedures

Use numbered steps for sequences and bullets otherwise.

- **Procedure heading.** Use one heading pattern for all procedures on a page,
  for example "Add a data element". Do not mix "Creating a queue", "Manage a
  queue" and "How to delete a queue". If the page already has a dominant
  pattern, follow it. If it is mixed, flag the choice for the page owner and do not
  pick one silently.
- **Prerequisites before step 1.** When they matter, state what the reader
  needs before the first step: the user role or authority, the DHIS2 version,
  and the starting screen. Take authority and version facts from the source or
  flag them for audit. Never invent an authority name.
- **Seven steps or fewer.** If a procedure has more than seven steps, suggest
  splitting it into smaller procedures, each with its own heading. This is a
  **structural change**: suggest it, do not make it.
- **Same shape for every step.** Start each step with a verb. Put where before
  what: "In the **Scheduler** app, choose **New job**." Use the same sentence
  structure in every step. Write each step as a complete sentence with a
  capital letter and a period.
- **End with the finishing action.** The last step names the action that
  completes the task, for example "Click **Save**.", and does not leave it
  implied.
- **No lead-in.** Remove lead-ins such as "Follow these steps" and "Do the
  following". The heading and the first step are enough. Links and downloads
  can go inside steps.
- Bold only the UI element, never a whole phrase around it.
- When a step starts with a bold title that repeats the step ("**Go to the
  list:** Click…"), merge the title into the step. It is still a **structural
  change**, so list it as one in the report. Merging two lines into one is
  allowed here even though you otherwise keep line structure.
- **Menu paths.** A short path (up to three items) can use a right angle
  bracket with a space before and after, with each label in bold: **Menu** >
  **Submenu** > **Command**. Screen readers may skip the `>` sign and read the
  labels as one run, which can confuse a listener. Write a long path (more than
  three items) or an important path out as steps. Keep each label exactly as
  the app shows it.

## Part 4. Words

Prefer the short, literal word. Full list: `references/lexicon.md`. Key swaps:

| Avoid | Use |
|---|---|
| utilize, leverage, facilitate | use, help |
| in order to | to |
| prior to, subsequent to | before, after |
| via | through, using, with |
| hence, thus, whereby, thereby | so, because, where |
| once (for "after") | after, when |
| since (for "because") | because |
| e.g., i.e., etc. | for example, that is, and so on (or list all) |
| click on | click (buttons, links) or choose (list items, checkboxes, menu items) |
| above, below, right-hand side, the green button | the following table, the previous section, a link, or the control's label |
| a number of, a variety of | some, several (or the number) |
| ensure | make sure (when a person acts), or restructure |
| allows you to, enables you to | lets you, or "You can…" |
| leverage, robust, seamless, powerful, flexible, comprehensive | say what it does, with numbers if possible |
| phrasal verbs: set up (verb), carry out, find out, reach out | configure, do, learn, contact |
| idiom: blank slate, get to know, up and running, on the fly | plain statement |

Spelling and terms:

- **US English spelling** (customize, synchronize, color, behavior, analyze,
  canceled), as the DHIS2 design system says ("Use US-EN spelling, as a general
  rule") and as confirmed on 2026-10-05. **Established DHIS2 terms keep
  their spelling**: "organisation unit" (and group, level) stays British.
  "program" and "enrollment" are already US. Convert stray British forms in the
  prose you edit. Do not convert quoted text, proper nouns ("Health
  Information Systems Programme"), API names or UI labels. Other uses of
  "organisation" (partner organizations) become "organization".
- **"organisation unit"** in prose. Use "org unit" only where the UI or API
  does. Never "orgunit" in prose. The JSON field `orgUnit` stays in code.
- **"metadata"**, one word. Not "meta-data".
- **One name per thing, per page.** Match the app's own UI label exactly,
  including capital letters. Do not change a UI label to fix style.
- **Check the label, do not trust the page.** The design system says UI text
  is sentence case, and refers to an element "using the same capitalization
  style that the element itself uses". Docs often keep old Title Case labels
  that the app no longer shows. Before you keep or change the case of a label,
  look it up as an `msgid` in the app repo's `i18n/en.pot` (use the file at the
  tag of the version the page covers; the default branch is only the newest
  version) or on a live instance. If the app shows sentence case ("Metadata
  import") and the page shows Title Case ("Metadata Import"), change the page
  and list it under "Applied: UI label case". If you cannot find the label,
  leave it and flag it.
- **Find a control by its label.** Never rely on position, shape or color
  alone: write "Choose **Save**", not "Choose the green button on the right".
  You can add where the control is as well as its label ("the **Save** button
  at the bottom of the form"), but the label must always be there.
- **Icons.** Always give the icon's name, and add a short description if it
  helps: "Choose **Edit** (pencil icon)". Never refer to an icon by its picture
  alone, because the same symbol can mean different things to different
  readers. If an icon has no visible label, take its name from the app's
  `i18n/en.pot` or its tooltip, or flag it.
- **Inline formatting** (industry standard, and the design system rule not to
  use quotation marks for interface terms). One style per kind of text, on
  every page:

  | Kind of text | Style | Example |
  |---|---|---|
  | Interface elements the reader clicks or chooses: buttons, menu items, tabs, checkboxes, options, sidebar items, job types | **Bold** | Click **Save**. In the sidebar, click **Metadata import**. |
  | Interface text the reader only reads: panel and section names, labels, messages | **Bold** | The **Job summary** shows the progress. |
  | New terms at their first definition | *Italics* | A *job queue* runs jobs one after another. |
  | Text the reader types, and placeholders | `Code` or *italics*; code font if it must be exact | Enter `admin` in the **Username** field. |
  | Code, commands, file names, properties, API paths, parameters, values in JSON | `Code` | Edit `dhis.conf`. Set `encryption.password`. |
  | Emphasis of an ordinary word | *Italics*, sparingly | The result is available for *one hour*. |

  Do not put interface terms in quotation marks and do not use italics for
  them. Use quotation marks only for quoted text and for an example value
  that is not a label. Keep the label's exact words and capitals (verify in
  `i18n/en.pot`). A label that wraps across lines stays in one bold span.
  Old names of renamed items are bold, without quotation marks.
- **App and product names** are capitalised, and "app" stays lowercase:
  "the Data Entry app", "the Capture app", "Import/Export app" (design system).
- **Acronyms:** write them out at first use on each page, then use the short
  form: "health management information system (HMIS)". For local acronyms
  (PHC, CHC) **do not guess** the expansion: leave them and flag them.
- **Other forms:** "data set" (two words, as in the UI), "license" (noun and
  verb), "offline" (not "off-line"), "nationwide" (not "nation-wide"),
  "program" (the DHIS2 object and the general word; keep "Programme" only in
  a proper noun such as "Health Information Systems Programme").
- **Marketing adjectives** (comprehensive, flexible, powerful, robust): delete
  them when the sentence still works. If the adjective carries the claim,
  keep it and flag it for the page owner. Never add facts to replace it.
- **Headings in sentence case**: "How to merge indicators", not "How to Merge
  Indicators". A heading that names a UI element follows the verified label
  (previous rule). A heading that names an app keeps the app name's capitals:
  "Using the Data Entry app".
- **Interface verbs** (design system): "and", not "&"; "show", not
  "display"; "open", "edit" or "view", not "access" as a verb.
- **Glossary** (design system A-Z glossary,
  https://developers.dhis2.org/design-system/patterns/glossary). Prefer these
  words. Avoid the words in the second column:

  | Use | Avoid |
  |---|---|
  | show | display |
  | run | execute |
  | start, open | launch |
  | set | specify |
  | menu (or drop the word) | dropdown, drop-down |
  | box (with its label name) | text box |
  | documentation | docs |
  | required | mandatory, compulsory |
  | refresh | reload |
  | settings, setup | config (use "configuration" only in technical settings) |
  | log in, log out | sign in, sign out |
  | drag | drag and drop |
  | affect, or state the consequence | impact (verb) |
  | copy | duplicate (an item) |
  | for example, such as | e.g., etc. |
  | to | in order to |
  | after (for sequence) | once (use "once" only for counting) |
  | enter (text in a field) | write, add |
  | fill in (one field), fill out (a form) | complete (a form) |
  | upload (a file), import (data) | |
  | create (finishes an add or new action) | new, add at the end of a form |
  | remove (item stays elsewhere), delete (item is destroyed) | |
  | search (free text), filter (by attributes) | |
  | open, edit, view | access (verb) |
  | the noun, not "this" or "that" when the reference is unclear | |

  Terms with a fixed meaning in the data model: use "approve" only for data
  approval, "category" only for the data model object (otherwise "group"),
  "indicator" only for the data model object, "complete" only for data
  completion status, "saved visualization" not "favorite" for a new concept.
  Use "app", not "application", unless technical.
- **Numbers and dates:** write dates as "2 October 2026" or ISO 2026-10-02.
  Never 02/10/26. Do not name seasons. Spell out units the first time.

## Part 5. Context for global health readers

- **Examples** use recognizable health-system settings: a clinic, a district,
  a stock-out, a monthly report. Do not use US-specific examples (state
  names, "Acme", dollar prices) unless they are API test data.
- **Do not hide information in images.** A screenshot must be described by the
  sentence before it. The step must still work if the image does not load.
- **Connection and device.** If a task is slow, large or needs a good
  connection, say so before the step. If a step is risky on a shared computer
  (saving a password, staying signed in), say so.
- **Offline.** Where the feature works offline or can sync later, say that
  plainly.
- **Local differences.** Do not assume one national structure. Say "your
  national or district level" rather than "your state".
- **Translation safety.** Avoid humor, metaphor, sports and food idioms,
  puns, and cultural references. Keep the same word for the same concept.
  Avoid sentences that depend on a pun between two meanings (file, record,
  report, set, run).
- **Do not talk down.** Plain language is not simplistic language. Keep the
  technical word the reader needs and define it once.

## Part 6. Tone by page type

Match the page's Diátaxis type. Do not mix registers in one section.

| Type | Tone | Typical wording | Opening |
|---|---|---|---|
| **Tutorial** (learning) | Warm, guiding, concrete; "we" allowed | "Now create a data set." "You should see…" | Objectives with observable verbs |
| **How-to** (a task) | Direct, conditional imperatives, no theory | "To merge two indicators, …" | Title and first sentence; prerequisites before step 1 |
| **Reference** (facts to look up) | Neutral, austere, complete, no opinion, no marketing | "Type: Integer. Default: 10." | Title and first sentence |
| **Explanation** (why) | Reflective, calm; may weigh options | "DHIS2 stores…. This means…" | Scope statement: what the page explains or the questions it answers |

Developer pages: keep the technical level, but still apply Parts 1 to 4.
Never remove technical precision to gain readability. Add a one-sentence
definition instead.

## Part 7. Version and time wording

- Replace "currently", "recently", "new", "now" and "latest" with a version
  number or "in this version", unless the sentence is truly timeless.
  If you do not know the right version, **keep the word and flag the claim for
  audit**. Never invent a version. You may delete "currently" when the verb
  is already present tense and no time contrast is meant.
- **Write DHIS2 core versions as v42, not 2.42.** Drop the "2." and put a "v"
  in front. "2.42" and "v42" are the same version in two notations, and the
  docs use "v42". Examples: "DHIS2 v42", "v41 and later", "from v39 to v41",
  "Upgrade to v42". Do not write "version v42" (the "v" already says
  version).
- Write "v41 and later", not "v41 and above" and not "v41+".
- Write version headings as "v40 and earlier" (no "Version" prefix). Keep the
  existing `{ #anchor }` on the heading, because other pages link to it.
- **Patch versions stay in full** ("2.41.3", "2.42.2") until the patch
  notation is decided. Do not mix notations in one sentence: if a sentence
  holds a patch version, leave the whole sentence as written and flag it.
- Convert prose only. Never convert URLs, code, anchors, quoted text, Jira
  text, git tags or app version numbers (the Data Entry app's 101.1.0 is an
  app version, not a core version). Image alt text is prose, so convert it,
  and flag the image if its own labels still show the old notation.
- Do not write the version story in prose beyond a short note. Version
  differences belong in the heading-scoped pattern used by the flattened pages.

### Version-difference sections (targeted, machine-readable)

A version-difference section is written for a chunker as well as for a
person. A chunker splits a page on headings and reads the version from the
heading text. A retrieved chunk arrives alone, so it must make sense without
the page around it. These sections are the one place where the preference for
short prose and no repetition does not apply.

1. **Heading, never a bold label.** Start each block with a real heading in
   one of two fixed forms, with one version expression per heading:
   "v42 and earlier" for something that applies only up to that version, and
   "v43 and later" for something that starts at that version. Add an anchor
   id that repeats the section and the expression, for example
   `{ #analytics_v43_and_later }`. Do not write a heading that describes a
   difference in free words ("What changed in v43"), because a chunker cannot
   read the version from it.
2. **Placement.** Put the block immediately after the table or the paragraph
   it describes. For a table, use these headings after the table, one heading
   per version expression. Keep the version note in the table row as well.
   Stating a difference in both places is intended, so crawlers find it. Do
   not remove either copy as a duplicate.
3. **One statement per line.** Write each statement as one complete sentence
   on its own line. A bullet is allowed here even for a short item.
4. **Each statement stands alone.** Name the app, the full setting or control
   name in bold, and the version. Do not use "it", "this setting", "these
   settings", "the five ... settings", "above", "below", "the same" or "all
   other settings". If a line would need the previous line to make sense,
   repeat the names.
5. **Direction in the sentence.** Start with "In v42 and earlier," or "From
   v43," so the sentence keeps its version if it is retrieved without its
   heading.
6. **Only verified differences.** Write a statement only for a difference the
   audit has verified. A statement that something is available in all
   versions does not get its own heading. Keep that fact in the table.
7. **Retire with the version.** When a version leaves the support window,
   delete its heading and statements in the same change.

## What this skill must never change

These are protected. If a style rule seems to require changing one, **leave it
and flag it**:

- UI labels, menu paths, button names, authority names, setting names
- Code, inline code, JSON, API paths, parameter names, `{ #anchors }`
- Version numbers, numbers, units, defaults, limits, dates of releases
  (the one allowed change is the notation 2.42 to v42, see Part 7; the number
  itself never changes)
- Link targets, image paths, table structure and column meaning
- Quoted text, release notes, error messages as they appear
- The **strength** of an obligation: keep "recommended" as a recommendation
  ("strongly recommends that you…"), "important" as important, "must" as
  must. Do not upgrade "it is important to" to "you must", and do not
  downgrade "highly recommended" to "should".
- The meaning. If a rewrite could change a claim, ask.

If while editing you notice something that looks factually wrong or out of
date, do **not** fix it silently. List it under "Flagged for audit" and hand
it to `dhis2-docs-audit`.

## Procedure

1. **Classify the page.** Type (tutorial / how-to / reference / explanation),
   reader (user / admin / developer), and whether it is app-repo or
   dhis2-docs. State this at the top of your report. If the page mixes types
   (an explanation intro followed by steps), classify each section and apply
   the tone of that section's type. Suggest, but do not make, a split.
2. **Measure.** Run `python scripts/measure.py <file>`. Note average sentence
   length, % of sentences over 25 words, grade (target 11 or lower), and counts
   of the flagged words. These are signals, not scores. Never optimize a number at the cost
   of meaning.
3. **Mechanical pass (apply).** Em dashes, "DHIS 2", "master", "e.g./i.e./etc.",
   "click on", "in order to", "utilize", "please", spelling, "meta-data",
   Title Case headings, "above/below" where a link or noun can replace it,
   "Follow these steps" lead-ins.
4. **Sentence pass (apply, list the notable ones).** Split long sentences,
   convert passive to active where the actor is clear, remove "simply/just",
   reduce noun stacks, restore dropped articles and "that".
5. **Consistency pass.** One term per concept on the page. Acronyms expanded
   once. Terms match the UI labels. Consistent verbs in steps (do not mix
   click/choose/press for the same control). One heading pattern for the
   procedures. Icons named. No control found by position or color alone.
   Version-difference sections follow Part 7 (heading pattern, standalone
   statements). Do not merge or shorten them as repetition.
6. **Protect check.** Run `python scripts/verify.py <before> <after>`. It
   must show no change in code spans, links, anchors, images or numbers.
   The only expected number differences are version notation changes
   (2.42 to v42).
   Bold-label changes are listed for review: each removed label must be a
   step title or a phrase you un-bolded on purpose, never a UI label.
7. **Re-measure** and report.

Edit in place and keep the file's existing line wrapping. Do not re-wrap
paragraphs. Re-wrapping makes the diff unreadable and hides the real change.
When a sentence is split, keep the new lines in the same place if possible.

## Report format

```
Page: <path>   Type: <…>   Reader: <…>
Before → After: avg sentence <x → y>, >25 words <a% → b%>, grade <g → h>
Applied (counts, use these types): em dashes · DHIS 2 → DHIS2 · Latin
abbreviations · filler removed · plain-word swaps · passive → active ·
long sentences split · noun forms → verbs · "we"/"the user" removed ·
click/choose · spelling and typos · UI label case · headings ·
acronyms expanded · icons named · position or color references replaced ·
lead-ins removed · structural.
Notable rewrites: 3–8 before/after pairs, chosen for teaching value.
Left alone on purpose: …
Flagged for the page owner: style choices that need a decision (mixed procedure
heading patterns, procedures over seven steps, objective or scope statement
rewrites).
Flagged for audit: possible factual issues (do not fix).
```

Ask about, rather than apply: changing a page's established voice wholesale,
removing a sentence, merging or reordering sections, splitting a procedure that
has more than seven steps, rewriting objectives or adding a scope statement,
and any rewrite where the reader might lose a technical qualification.

## Confirmed decisions (2026-10-05, 2026-10-06, 2026-10-14, 2026-10-20)

1. **"we"**: avoid. Tutorial pages may still use it when the learner and author
   do the task together.
2. **Bold step titles** ("**Go to the list:** Click…"): merge the title into the
   step. Still list it as a structural change in the report.
3. **"click" and "choose"**: click for buttons and links, choose for list items,
   checkboxes and menu items. Do not use "select" as a verb (decision 11).
4. **Contractions**: avoid everywhere.
5. **Reading grade**: aim for US grade 11 or lower, for user and developer
   pages. This is a signal only, because formulas ignore jargon.
6. **UI label case**: keep the case the app shows, and verify it (see Part 4).
7. **No automated linter** (2026-10-09): the rules stay as written rules that
   this skill applies. The team will not add an automated
   check to the docs submission process, because it adds steps for authors.
8. **Spelling** (2026-10-05, final): US-EN, as the design system says, except
   "organisation unit" (and group, level), which keeps its established British
   spelling. A short-lived British-English decision the same day was withdrawn.
9. **Glossary and grammar** (2026-10-05): the design system A-Z glossary and
   grammar rules are part of the skill (Part 2 and Part 4).
10. **Interface terms** (2026-10-06): write them in bold, never in quotation
    marks. Use the inline formatting table in Part 4. Italics are for new
    terms and emphasis, code font is for code, commands, files and API names.
11. **choose, not select** (2026-10-06): the design system glossary wins. Use "choose"
    for list items, checkboxes and menu items, and "click" for buttons and links.
    Labels keep their exact words, and
    "selected" as an adjective is fine.
12. **Procedure, menu path, icon, position and color rules** (2026-10-14,
    adopted after comparing the Online Academy content guidelines): the
    procedure rules in Part 3, the menu path rule (short paths can use `>`,
    long or important paths are written as steps), icons named, and controls
    found by label and never by position or color alone.
13. **Explanation pages open with a scope statement** (2026-10-14): one or two
    sentences saying what the page explains or the questions it answers, with a
    matching lead-in. No objectives and no "understand" on explanation pages.
    Tutorials and training-style chapters use verb objectives that the content
    teaches. How-to and reference pages have no objectives.
14. **Version notation** (2026-10-14): DHIS2 core versions are written v42,
    not 2.42. This is the current way the team talks about versions, and it
    applies to existing pages too (retroactively). Patch versions are not
    decided yet and stay in full.
15. **Version-difference sections are machine-readable** (2026-10-20): they use
    the headings "v42 and earlier" and "v43 and later", one version expression
    per heading, placed right after the table or paragraph they describe.
    Each statement is one standalone line that names the app, the full setting
    names and the version. Restating the table notes is intended and is not
    removed as duplication. These sections are exempt from the short-prose and
    no-repetition preferences. First applied on the System Settings app page.

## Handoff

- Facts, versions, "does the UI say this": **dhis2-docs-audit**
- Which site or space the content belongs in: the docs team's placement guidance
- Anchors, tables, image paths, branch, commit, PR: **dhis2-docs-contribution**
- Reference: `references/research-basis.md`, `references/lexicon.md`
  and `references/corpus-survey-2026-10-05.md`