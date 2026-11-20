#!/usr/bin/env python3
"""Check a dhis2-core PR title and description against the backend team's PR guide.

Usage:
  python3 scripts/check_pr_description.py pr_description.md --title "fix: Reject week 53 [DHIS2-12345]"
  python3 scripts/check_pr_description.py pr_description.md --type perf --no-ai
  gh pr view 123 --json title,body -q .body | python3 scripts/check_pr_description.py - --type fix

Checks the mechanical rules (sections, headings, word count, Jira line, hint text,
title format, AI Assisted line). It also warns on long sentences and filler words,
but a passing run does not prove the text is good STE: still read it.
Exit code: 1 if any ERROR, else 0. Standard library only.
"""
import argparse
import re
import sys

SECTIONS = {  # required sections in order; Caveats is optional where listed
    "fix": (["Problem", "Solution", "Proof"], True),
    "feat": (["What", "Why", "How"], True),
    "perf": (["Problem", "Solution", "Results"], False),
    "refactor": (["Problem", "Solution"], False),
    "chore": (["What"], False),
    "ci": (["What", "Solution"], False),
    "test": (["Problem", "Solution"], False),
    "docs": (["What"], False),
}
HINTS = ["1-3 sentences", "(optional", "full link to the Jira", "max 1 paragraph",
         "linking it to key place", "use bullets for several", "[full link"]
FILLER = ["basically", "simply", "in order to", "actually", "just ", "really",
          "very ", "obviously", "brand new", "note that", "it should be noted"]
JIRA_LINE = re.compile(r"^\*\*Jira\*\*: https://dhis2\.atlassian\.net/browse/[A-Z][A-Z0-9]+-\d+\s*$")
TITLE = re.compile(r"^(?P<type>[a-z]+): (?P<subject>.+)$")

out = {"ERROR": [], "WARN": []}


def err(msg): out["ERROR"].append(msg)
def warn(msg): out["WARN"].append(msg)


def check_title(title):
    m = TITLE.match(title.strip())
    if not m:
        err(f"title must be '<type>: <Subject>' with a lower-case prefix: {title!r}")
        return None
    t, subject = m["type"], m["subject"]
    if t not in SECTIONS:
        err(f"title prefix '{t}:' is not one of {', '.join(SECTIONS)} (build/dependency changes use chore:)")
    if not subject[:1].isupper():
        err(f"title subject must start with a capital letter: {subject!r}")
    if subject.rstrip().endswith("."):
        err("title must not end with a period")
    if not re.search(r"\[[A-Z][A-Z0-9]+-\d+\]", subject):
        warn("title has no Jira key in brackets, e.g. [DHIS2-12345] (most PRs have one)")
    bare = re.sub(r"\s*\[[A-Z][A-Z0-9]+-\d+\]", "", title).strip()
    if len(bare) > 50:
        warn(f"title is {len(bare)} characters without the Jira key; the guide asks for at most 50")
    return t


def strip_code(lines):
    fenced, res = False, []
    for ln in lines:
        if ln.strip().startswith("```"):
            fenced = not fenced
            continue
        res.append("" if fenced else ln)
    return res


def check_body(body, typ, ai):
    lines = body.splitlines()
    words = len(body.split())
    if words > 250:
        err(f"{words} words; maximum is 250 (headings included). Cut, or move detail to a PR doc in wow-backend pr/")
    elif words > 150:
        warn(f"{words} words; aim for 150 or fewer")

    text = strip_code(lines)
    heads = []
    for i, ln in enumerate(text, 1):
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", ln)
        if m:
            level, name = len(m[1]), m[2]
            if level != 3:
                err(f"line {i}: heading '{ln.strip()}' must be h3 (### {name})")
            heads.append(name)
        elif re.match(r"^\*\*[^*]+\*\*:?\s*$", ln.strip()):
            err(f"line {i}: bold line used as a heading ({ln.strip()}); use the template's ### sections")
        for h in HINTS:
            if h.lower() in ln.lower():
                err(f"line {i}: template hint text left in: {h!r}")
    for h in heads:
        if re.fullmatch(r"(?i)tests?|testing", h.strip()):
            err(f"section '{h}' is not allowed; in a fix, name the test in Proof (one sentence)")

    if typ:
        required, caveats = SECTIONS[typ]
        allowed = required + (["Caveats"] if caveats else [])
        names = [h.replace("(optional)", "").strip() for h in heads]
        extra = [h for h in names if h not in allowed]
        if extra:
            err(f"{typ} sections are {' / '.join(required)}{' (+ optional Caveats)' if caveats else ''}; remove: {', '.join(extra)}")
        core = [h for h in names if h in required]
        if core != required:
            err(f"{typ} needs sections {required} in that order; found {names}")
        if "Caveats" in names and names[-1] != "Caveats":
            err("Caveats must be the last section")

    jira = [ln for ln in lines if re.search(r"(?i)\bjira\b", ln) and not ln.startswith("#")]
    keys = re.findall(r"\b(?:DHIS2|TECH|DEVOPS)-\d+\b", body)
    if jira:
        for ln in jira:
            if "atlassian.net" in ln or ln.lower().startswith(("jira", "**jira")):
                if not JIRA_LINE.match(ln.strip()):
                    err(f"Jira line must be '**Jira**: https://dhis2.atlassian.net/browse/KEY-123' (full URL, no markdown link): {ln.strip()!r}")
    elif keys:
        warn(f"mentions {keys[0]} but has no '**Jira**: <full URL>' line")
    else:
        warn("no Jira line; most PRs have one")

    nonempty = [ln.strip() for ln in lines if ln.strip()]
    last = nonempty[-1] if nonempty else ""
    has_ai = "AI Assisted" in nonempty
    if has_ai and last != "AI Assisted":
        err("'AI Assisted' must be the last line")
    if ai is True and not has_ai:
        err("AI wrote a large part of the PR: put 'AI Assisted' on the last line")
    if ai is False and has_ai:
        err("remove 'AI Assisted': the author says AI did not write a large part")

    prose_lines = [re.sub(r"`[^`]*`", "X", re.sub(r"^\s*(?:[-*]|\d+\.)\s+(?:\[.\]\s+)?", "", ln))
                   for ln in text if ln.strip() and not ln.lstrip().startswith(("|", "#", "**Jira**"))]
    prose = "\n".join(prose_lines)
    for ln in prose_lines:
        for s in re.split(r"(?<=[.!?])\s+", ln):
            n = len(s.split())
            if n > 20:
                warn(f"sentence has {n} words (STE max 20): {s.strip()[:90]}...")
    low = " " + prose.lower() + " "
    for f in FILLER:
        if f" {f}" in low:
            warn(f"filler word: {f.strip()!r}")
    if re.search(r"\b(is|are|was|were|be|been|being)\s+\w+ed\b", prose):
        warn("possible passive voice (STE prefers active); check sentences with 'is/was ...ed'")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", help="description file, or - for stdin")
    p.add_argument("--title", help="PR title; also selects the template type")
    p.add_argument("--type", choices=SECTIONS, help="template type if no --title")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--ai", dest="ai", action="store_true", default=None, help="AI wrote a large part")
    g.add_argument("--no-ai", dest="ai", action="store_false", help="AI did not")
    a = p.parse_args()
    body = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    typ = check_title(a.title) if a.title else None
    typ = typ if typ in SECTIONS else a.type
    if not typ:
        warn("no --title or --type: section checks skipped")
    check_body(body, typ, a.ai)
    for level in ("ERROR", "WARN"):
        for m in out[level]:
            print(f"{level}: {m}")
    print(f"{len(body.split())} words, {len(out['ERROR'])} errors, {len(out['WARN'])} warnings")
    sys.exit(1 if out["ERROR"] else 0)


if __name__ == "__main__":
    main()
