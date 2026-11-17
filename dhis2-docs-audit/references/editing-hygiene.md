# Editing hygiene, when you apply findings

- Before you edit a list, run `grep -n '^#'` and confirm the heading above
  it. Look-alike sections (Metadata Import and Tracked Entities Import) can
  have different options.
- After you write, grep for the change. Edits can fail without an error.
- Do not drop stale text without a record. Log each deliberate removal, with
  its evidence, in the report.
- If the file changed since you last read it, say what you changed and how
  to revert it.
- Keep unreleased or unverified material out of the page. List it as pending.
  Proposed doc text may contain only behaviour you verified in this run. A
  ticket or a forum post that says something happens is not verification.
- Before you propose adding something, check that the published page does
  not already document it in another table or section.
- Keep verification notes out of rendered prose (no "confirmed live on
  stable-X" in the page). They belong in the report and the registers.
