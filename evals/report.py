#!/usr/bin/env python3
"""Summarise an eval run: python3 evals/report.py evals/results/<run-id> [more run dirs...]

Writes REPORT.md and summary.json into the first run directory. Several run directories
are merged; a later directory's result for the same (skill, case, model, condition) wins.
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def load(dirs: list[Path]) -> dict:
    res, models = {}, {}
    mj = Path(__file__).with_name("models.json")
    if mj.exists():  # default labels and order; run.json may hold only the models of a partial re-run
        models.update({k: v.get("label", k) for k, v in json.loads(mj.read_text()).items()})
    for d in dirs:
        run = json.loads((d / "run.json").read_text()) if (d / "run.json").exists() else {}
        models.update({k: v.get("label", k) for k, v in run.get("models", {}).items()})
        for p in d.rglob("result.json"):
            r = json.loads(p.read_text())
            res[(r["skill"], r["case"], r["model"], r["condition"])] = r
    return {"results": res, "models": models}


def rate(rs: list[dict]) -> tuple[float | None, int]:
    graded = [r for r in rs if r.get("grade", {}).get("total") and not r.get("contaminated")]
    if not graded:
        return None, 0
    # Mean of per-case pass fractions, so long assertion lists don't dominate.
    return statistics.mean(r["grade"]["passed"] / r["grade"]["total"] for r in graded), len(graded)


def pct(x: float | None) -> str:
    return "–" if x is None else f"{100 * x:.0f}%"


def main() -> None:
    dirs = [Path(a) for a in sys.argv[1:]]
    if not dirs:
        sys.exit(__doc__)
    data = load(dirs)
    res, labels = data["results"], data["models"]
    skills = sorted({k[0] for k in res})
    models = sorted({k[2] for k in res}, key=lambda m: list(labels).index(m) if m in labels else 99)

    by = defaultdict(list)
    for (s, c, m, cond), r in res.items():
        by[(s, m, cond)].append(r)
        by[("*", m, cond)].append(r)

    summary = {"skills": {}, "overall": {}}
    lines = ["# Skill eval report", "",
             "Score = mean fraction of assertions passed per case (graded by "
             f"{json.loads((dirs[0] / 'run.json').read_text()).get('grader', '?') if (dirs[0] / 'run.json').exists() else '?'}). "
             "Δ = with skill − without skill. *Used* = share of with-skill runs where the agent "
             "actually loaded the skill.", ""]

    lines += ["## Overall", "", "| Model | With skill | Without | Δ | Used | Runs |", "|---|---|---|---|---|---|"]
    for m in models:
        w, nw = rate(by[("*", m, "with_skill")])
        wo, nwo = rate(by[("*", m, "without_skill")])
        used = [r for r in by[("*", m, "with_skill")] if "run" in r]
        u = sum(bool(r["run"].get("skill_used")) for r in used) / len(used) if used else None
        d = None if w is None or wo is None else w - wo
        summary["overall"][m] = {"with": w, "without": wo, "delta": d, "used": u}
        lines.append(f"| {labels.get(m, m)} | {pct(w)} | {pct(wo)} | "
                     f"{'–' if d is None else f'{100 * d:+.0f}'} | {pct(u)} | {nw}+{nwo} |")

    lines += ["", "## Per skill", ""]
    head = "| Skill | " + " | ".join(f"{labels.get(m, m)} with / without (Δ)" for m in models) + " |"
    lines += [head, "|---|" + "---|" * len(models)]
    for s in skills:
        row, summary["skills"][s] = [s], {}
        for m in models:
            w, _ = rate(by[(s, m, "with_skill")])
            wo, _ = rate(by[(s, m, "without_skill")])
            d = None if w is None or wo is None else w - wo
            summary["skills"][s][m] = {"with": w, "without": wo, "delta": d}
            row.append(f"{pct(w)} / {pct(wo)} ({'–' if d is None else f'{100 * d:+.0f}'})")
        lines.append("| " + " | ".join(row) + " |")

    lines += ["", "## Per case", ""]
    for s in skills:
        cases = sorted({k[1] for k in res if k[0] == s})
        lines += [f"### {s}", "", "| Case | Model | With | Without | Used | Time with (s) | Notes |",
                  "|---|---|---|---|---|---|---|"]
        for c in cases:
            for m in models:
                w = res.get((s, c, m, "with_skill"), {})
                wo = res.get((s, c, m, "without_skill"), {})

                def cell(r):
                    if r.get("status") in ("skipped", "error"):
                        return r["status"]
                    g = r.get("grade") or {}
                    st = (r.get("run") or {}).get("status")
                    base = f"{g.get('passed', '?')}/{g.get('total', '?')}" if g else "–"
                    return base + ("" if st in (None, "ok") else f" ({st})")
                note = (w.get("grade") or {}).get("notes", "").replace("|", "/").replace("\n", " ")
                lines.append(f"| {c} | {labels.get(m, m)} | {cell(w)} | {cell(wo)} | "
                             f"{'yes' if (w.get('run') or {}).get('skill_used') else 'no'} | "
                             f"{(w.get('run') or {}).get('seconds', '–')} | {note[:300]} |")
        lines.append("")

    bad = [k for k, r in sorted(res.items()) if r.get("contaminated")]
    if bad:
        lines += ["## Excluded: contaminated runs", "",
                  "These agents read the repo, installed skills or eval definitions; their scores are excluded.", ""]
        lines += [f"- {s}#{c} {labels.get(m, m)} {cond}: {', '.join(res[(s, c, m, cond)]['contaminated'])}"
                  for (s, c, m, cond) in bad] + [""]

    lines += ["## Assertions failed with the skill", "",
              "Candidates for skill fixes (or for loosening an over-strict assertion).", ""]
    for (s, c, m, cond), r in sorted(res.items()):
        if cond != "with_skill":
            continue
        for a in (r.get("grade") or {}).get("assertions", []):
            if not a["passed"]:
                lines.append(f"- **{s}#{c} {labels.get(m, m)}**: {a['text']} — _{a.get('evidence', '')[:240]}_")

    out = dirs[0]
    (out / "REPORT.md").write_text("\n".join(lines) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(f"wrote {out / 'REPORT.md'}")


if __name__ == "__main__":
    main()
