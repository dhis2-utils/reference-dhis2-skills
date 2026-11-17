# Docs audit: <page or PR> (<YYYY-MM-DD>)

## Scope and coverage

- Mode: <claim / section or PR / page>. Page(s) and sections: <paths, headings>. Base: <branch, SHA or mtime>.
- Versions: <range>. Corpus searched: <repos and branches>.
- Coverage: <n> claims, <n> checked. Directions: <A, B>. Passes: <run / required but not run>. Images: <n opened of n in scope>.
- Registers read (if kept): <false-positive log, debt rows AD-###>, or "none kept".

## Findings

One block per finding, most severe first.

### F-1 <short title> (<Sev>, <finding type>)

- **Doc says:** <quote, with section heading>
- **Evidence shows:** <one or two lines> (register rows <#n>)
- **Verdict:** <Refuted / Conflicting / …>. **Found by:** <pass and direction>
- **Suggested action:** <fix text, caveat, Jira ticket, or no action>

## Confirmed without change

<Count, and "see claims register". Do not list them one by one.>

## Open items

Every Unverified, Inferred and Conflicting row, and every pass not run, with
what would close it. These go into the debt register.

| AD ID | Claim | Why open | What would close it |
|---|---|---|---|

## Register updates

- Debt register: added <AD-###>, closed <AD-###>.
- False-positive log: added <FP-###>.
- Audit log: row added.
- Register updates pending (registers not available): <none, or the text to add>

## Handoff

<What the contributor needs to do (target repo, branches, screenshots), or "none">
