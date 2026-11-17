# Research basis for dhis2-docs-style (researched 2026-10-05)

Each rule in SKILL.md traces to one of these sources. Fetches were summarised
by a small model, so wording is close paraphrase, not verbatim. "Unverified"
means no fetched source confirmed it.

## 0. DHIS2's own design system (fetched 2026-10-05; wins where it applies)

Pages: developers.dhis2.org/design-system/patterns/writing/ (Grammar,
punctuation, and style), /principles/content-communication, /patterns/glossary.
These are written for interface text. We treat them as DHIS2's own rules and
apply them to docs where they fit. Quotes are close paraphrase of the fetched pages.

| Rule | Page |
|---|---|
| "Throughout an application, always use sentence case." No title case "unless referring to an application, person, or product." Sentence case for all interface elements. | writing |
| "When referring to elements in an interface, like buttons or sections, use the same capitalization style that the element itself uses." | writing |
| "Use US-EN spelling, as a general rule." Terms like *organisation unit* keep the DHIS2 established spelling. Confirmed on 2026-10-05. | writing |
| Use a serial comma. Do not use please, thank you, sorry. Do not use "will" where the present tense works; use it for the consequences of a user action. Introduce an acronym at first use. | writing |
| Voice: clear, honest, friendly but detached and professional; plain, consistent, not unnecessarily technical words; do not talk down; address the user as "you", sparingly. | content-communication |
| Errors say what went wrong and what can be done. | content-communication |
| "and" not "&"; "show" not "display"; "open/edit/view" not "access" as a verb. Terms such as Approve, Category, Complete, Indicator are used across DHIS2 and need care. | glossary |

Not covered by the design system (so these remain our own decisions): "we",
"click" vs "select", contractions, sentence length, reading grade, Latin
abbreviations. The glossary does not define spellings for "data set" or
"metadata".
**Caveat:** the page is guidance for interface text. It does not say how
documentation headings should be capitalised.

## 1. Software documentation in general

| Rule | Source |
|---|---|
| Second person, active voice, present tense; future only for a truly later event; avoid hypothetical "would" | Google developer documentation style guide: highlights, tense (developers.google.com/style/highlights, /tense) |
| Put the condition before the instruction | Google, highlights |
| Start with verbs, cut "you can", avoid "there is/are"; be brief | Microsoft Writing Style Guide, top 10 tips (learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice) |
| Never "simply", "just", "easy", "quickly"; no "please", exclamation marks, "let's", metaphors, pop culture | Google, tone (developers.google.com/style/tone) |
| Check sentences over 25 words; avoid jargon and abstract verbs (leverage, facilitate, empower) | GOV.UK style guide (guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/) |
| Numbered lists for sequences; imperative verb first; location before action; "Optional:" prefix | Google, procedures |
| Bold UI labels; no directional words (above, below, right-hand) | Google, procedures and ui-elements |
| Replace e.g./i.e./etc. with "for example", "that is"; expand abbreviations at first use; no acronyms as verbs | Google, abbreviations; GOV.UK |
| Inclusive terms (allowlist, person-hours); varied names and non-US examples; alt text; descriptive link text | Google, inclusive-documentation |
| Tutorial: guiding, "we", expected output. How-to: conditional imperatives. Reference: austere, neutral. Explanation: reflective | Diátaxis (diataxis.fr/tutorials, /how-to-guides, /reference, /explanation) |

**Where sources disagree.** Contractions: Microsoft encourages them, GOV.UK
avoids negative contractions. We chose: allowed in tutorials and how-to,
avoided in reference and developer pages. "we": Google and Kubernetes discourage
it, Diátaxis allows it in tutorials. We chose: tutorials only.
**Unverified:** Write the Docs, Red Hat, Apple and IBM guides were not fetched;
no numeric reading-grade target appeared in any fetched Google, Microsoft or
GOV.UK page.

## 2. Open source documentation

| Rule | Source |
|---|---|
| Keep a word list of preferred and avoided terms; defer to a named external guide for everything else | GitLab word list (docs.gitlab.com/development/documentation/styleguide/word_list/) |
| Start the style guide as a short list of decisions and grow it; consistent tone lowers cognitive load | Write the Docs, style guides (writethedocs.org/guide/writing/style-guides/) |
| Frame the guide as guidance with a route to change it ("guidelines, not rules") | Kubernetes style guide (kubernetes.io/docs/contribute/style/style-guide/) |
| Adopt an existing accessibility standard instead of inventing one | The Turing Way style page (summary only) |
| Avoid "we"; name the project. Avoid "there is/are", ambiguous "it", -ing words, Latin abbreviations, idioms (easier to localise) | Kubernetes; GitLab |
| "select" rather than "click" (works across devices) | GitLab word list |
| Replace "currently/new/recently" with version numbers; "X.Y and later", not "and above" | Kubernetes; GitLab word list |
| Remove notes for unsupported versions on a schedule | GitLab availability details |
| Be welcoming: thank newcomers, respond fast, label starter issues | opensource.guide/building-community |

**Unverified:** Django/Python, Fedora/Red Hat, Carpentries guides; the
Kubernetes content guide; the Turing Way's detailed rules.

## 3. Low- and middle-income country (LMIC) and global health context

**This is the thinnest strand. Most of Part 5 in SKILL.md is reasoned from
the survey and from the first and fourth strands, not from LMIC-specific
style guides.** Verified:

- Plain language: active voice, present tense, short words, replace hidden
  verbs (-ment, -tion, -ance), short sentences and sections, tailor to the
  audience, test with real readers (digital.gov plain-language guide).
  ISO 24495-1:2023 sets governing plain-language principles for technical
  writing; the abstract does not list them.
- WHO SMART Guidelines / Digital Adaptation Kits (DAKs) are written around
  named personas and scenarios, then workflows, data elements and indicators.
  They give programme managers, developers and implementers "a common
  language" and are localised by countries (who.int SMART Guidelines page;
  WHO DAK two-pager; PATH article).
- Last-mile digital health design (NextBillion article, not a standard): lean
  text-led interfaces for low-cost handsets; store locally and sync later;
  session-based access on shared devices; localisation is more than
  translation: match terminology to local practice and test with frontline
  workers.
- Principles for Digital Development stress inclusion and local ownership (the
  page says this about software, not about documentation; applying it to docs is
  our inference).

**Unverified (not fetched or failed):** OpenMRS, Bahmni, OpenHIE, CommCare,
KoboToolbox, ODK documentation styles; WHO plain-language guidance; DIAL and
USAID guidance; research on low-bandwidth reading, printing, and
localisation into specific languages. A follow-up pass should fetch these.

## 4. Readers who are not native English speakers

| Rule | Source |
|---|---|
| Shorter sentences are easier to translate; do not chain more than 2 or 3 phrases with and/or/but | Google (developers.google.com/style/translations); Microsoft global writing tips |
| Simple words: utilize→use, commence→start, in order to→to, a number of→some | Google translations; Microsoft use-simple-words |
| Minimise phrasal verbs and gerunds as subjects ("Configuring X is required" → "You must configure X") | Google translations |
| Keep "that", "who" and articles; do not write fragments | Microsoft global writing tips |
| Replace ambiguous pronouns with the noun; use "you", not "the user" | Google translations |
| Avoid dangling -ed/-ing; place "only" correctly | Microsoft; Google |
| Modals: "may" for policy or permission, "might" for possibility, "can" for ability | Google word list |
| "because" not "since"; "after" not "once" | Microsoft; Google |
| Avoid idioms, humour, region-specific references | Google; Microsoft |
| One term per concept, identical capitalisation | Google; Microsoft |
| Dates: "19 January 2017" or ISO 8601; avoid season names | Google, dates-times |
| STE: procedures up to 20 words, descriptions up to 25, paragraphs up to 6 sentences, no more than 3 nouns in a row, about 850 approved words | ClickHelp summary of ASD-STE100 (secondary source; not checked against the spec) |
| Flesch-Kincaid grade 7 to 8 is a common benchmark for technical text, but formulas ignore jargon and content | ClickHelp article on Flesch |

**Where sources disagree.** STE gives hard word counts. Microsoft and Google
give none. We use the STE numbers as flagging thresholds, not pass/fail
limits, because DHIS2 docs are not safety-critical and the STE figures came
from a secondary source.
**Unverified:** CEFR targets for technical writing; machine-translation
research; Red Hat, IBM, Oracle guides; the official ASD-STE100 text.

## 5. What would strengthen this

1. Fetch the ASD-STE100 spec summary and the ISO 24495-1 principles.
2. Fetch OpenMRS, KoboToolbox and CommCare contributor style pages.
3. Test one rewritten page with real readers (district officers) and with
   machine translation into French and Portuguese. Digital.gov calls testing
   the fourth stage of plain language; this project has not done it.
