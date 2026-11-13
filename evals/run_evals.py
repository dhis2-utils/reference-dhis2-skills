#!/usr/bin/env python3
"""Run skill evals: each case x model x condition (with/without the skill), then grade.

See evals/README.md. Standard library only.
"""
from __future__ import annotations

import argparse
import base64
import urllib.error
import urllib.request
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EVALS_DIR = REPO / "evals"
CONDITIONS = ("with_skill", "without_skill")
HOME = Path.home()
# Agent workspaces live outside the repo under opaque names, so an agent exploring the
# filesystem doesn't stumble on the skills or their evals. Inputs appear as inputs/...
WORK_ROOT = Path(os.environ.get("EVAL_WORK_ROOT", Path(tempfile.gettempdir()) / "skill-evals"))
# A transcript mentioning any of these means the agent saw material it shouldn't have
# (the repo, installed skills, or eval definitions): the run is marked contaminated.
# Only paths that reach skill content count. Bare mentions of ~/.claude (the CLI's own
# harness notes cite ~/.claude/projects/...) or of the repo dir in an env dump do not.
CONTAMINATION_MARKERS = [str(REPO) + "/", str(HOME / ".claude" / "skills"), "~/.claude/skills",
                         str(HOME / ".claude" / "plugins"), "~/.claude/plugins",
                         str(HOME / ".vibe" / "skills"), "~/.vibe/skills",
                         str(HOME / ".agents"), "~/.agents", "evals.json"]
# Extra paths that hold skill content (e.g. other checkouts), separated by os.pathsep.
CONTAMINATION_MARKERS += [m.rstrip("/") + "/" for m in os.environ.get("EVAL_EXTRA_MARKERS", "").split(os.pathsep) if m]

# Environment variables an agent under test must not inherit: instance provisioning hooks and
# credentials (instances reach the agent through the prompt only), device sockets and session
# tokens would make runs non-portable or unfair.
STRIP_ENV_PREFIXES = ("DHIS2_", "ADB_SERVER_SOCKET", "CLAUDE_CODE_", "CLAUDECODE",
                      "SANDBOX_", "PROJECT_")

_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(f"[{dt.datetime.now():%H:%M:%S}] {msg}", flush=True)


_claude_lock = threading.Lock()
PROBE_MODEL = os.environ.get("EVAL_PROBE_MODEL", "claude-haiku-5-5")
PAUSE_SECONDS = int(os.environ.get("EVAL_PAUSE_SECONDS", "600"))
MAX_PAUSE_HOURS = float(os.environ.get("EVAL_MAX_PAUSE_HOURS", "12"))


def claude_available() -> bool:
    """Cheap probe: does the claude CLI answer at all (usage limit, auth, network)?"""
    try:
        p = subprocess.run(["claude", "-p", "--model", PROBE_MODEL, "--setting-sources", "project",
                            "--strict-mcp-config"], input="Reply with OK.", capture_output=True,
                           text=True, timeout=180, cwd=tempfile.gettempdir(), env=agent_env())
        return p.returncode == 0 and "OK" in p.stdout
    except Exception:  # noqa: BLE001
        return False


def wait_for_claude(why: str) -> None:
    """Block (all workers) until the claude CLI answers again, e.g. after a usage-limit window.
    Results are never written for runs that failed because Claude was unavailable."""
    with _claude_lock:  # one waiter probes; the others queue here and re-check quickly
        if claude_available():
            return
        t0 = time.time()
        log(f"PAUSED: claude CLI unavailable ({why}); probing every {PAUSE_SECONDS}s")
        while not claude_available():
            if time.time() - t0 > MAX_PAUSE_HOURS * 3600:
                raise RuntimeError("claude CLI unavailable for too long; giving up")
            time.sleep(PAUSE_SECONDS)
        log(f"RESUMED after {round((time.time() - t0) / 60)} min")


def claude_failed_fast(meta: dict) -> bool:
    """A claude run that exits non-zero within a minute never really started: treat it as
    'Claude unavailable' (usage limit, auth) when the probe agrees, not as a model failure."""
    return str(meta.get("status", "")).startswith("exit") and meta.get("seconds", 999) < 60


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def discover_skills() -> list[str]:
    return sorted(p.parent.parent.name for p in REPO.glob("*/evals/evals.json"))


def load_cases(skill: str) -> list[dict]:
    data = json.loads((REPO / skill / "evals" / "evals.json").read_text())
    return data["evals"]


def is_live(case: dict) -> bool:
    req = case.get("requires", "offline")
    return isinstance(req, dict) and ("instance" in req or "instances" in req)


def mutates(case: dict) -> bool:
    req = case.get("requires")
    if not isinstance(req, dict):
        return False
    insts = req.get("instances") or [req.get("instance")]
    return any(i and i.get("mutates", True) for i in insts)


# ---------------------------------------------------------------- workspace

def rmtree(path: Path) -> None:
    """rm -rf that also removes read-only files (agent tools create some)."""
    for root, dirs, files in os.walk(path):
        for n in dirs + files:
            try:
                os.chmod(os.path.join(root, n), 0o700, follow_symlinks=False)
            except (OSError, NotImplementedError):
                pass
    shutil.rmtree(path, ignore_errors=True)


def install_skill(skill: str, dest: Path) -> None:
    """Copy a skill without its evals (they contain the expected answers)."""
    shutil.copytree(REPO / skill, dest,
                    ignore=shutil.ignore_patterns("evals", ".DS_Store", "__pycache__", "*.pyc"))


def input_path(rel: str) -> str:
    """Where an eval input file appears in the workspace: evals/files/x -> inputs/x."""
    return "inputs/" + rel.split("evals/files/", 1)[-1]


def localise(text: str, skill: str) -> str:
    return text.replace(f"{skill}/evals/files/", "inputs/").replace("evals/files/", "inputs/")


def prepare_workspace(skill: str, case: dict, ws: Path) -> None:
    ws.mkdir(parents=True, exist_ok=True)
    for rel in case.get("files", []):
        src = REPO / skill / rel
        dst = ws / input_path(rel)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.exists():
            shutil.copy2(src, dst)
        else:
            raise FileNotFoundError(f"{skill} case {case['id']}: missing input file {rel}")


SKIP_DIRS = {".claude", "node_modules", ".git", ".venv", "venv", "__pycache__", ".gradle",
             "build", "dist", ".cache", ".yarn", ".pnpm-store", ".d2"}


def snapshot(ws: Path) -> dict[str, float]:
    out = {}
    for root, dirs, files in os.walk(ws):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = Path(root) / f
            try:
                out[str(p.relative_to(ws))] = p.stat().st_mtime
            except OSError:
                pass
    return out


# ---------------------------------------------------------------- instances

_instance_lock = threading.Lock()


def provision(case: dict) -> list[dict] | None:
    """Call DHIS2_EVAL_INSTANCE_CMD once per required instance; None if unavailable."""
    cmd = os.environ.get("DHIS2_EVAL_INSTANCE_CMD")
    if not cmd:
        return None
    req = case["requires"]
    insts = req.get("instances") or [req["instance"]]
    result = []
    for idx, spec in enumerate(insts, 1):
        spec = dict(spec, slot=idx, fresh=bool(spec.get("mutates", True)))
        p = subprocess.run(cmd, shell=True, input=json.dumps(spec), capture_output=True,
                           text=True, timeout=3600)
        if p.returncode != 0:
            raise RuntimeError(f"instance provider failed: {p.stderr[-2000:]}")
        result.append(json.loads(p.stdout.strip().splitlines()[-1]))
    return result


def substitute(prompt: str, instances: list[dict]) -> str:
    keys = {"base_url": "DHIS2_BASE_URL", "username": "DHIS2_USERNAME",
            "password": "DHIS2_PASSWORD", "version": "DHIS2_VERSION"}
    for idx, inst in enumerate(instances, 1):
        for k, ph in keys.items():
            val = str(inst.get(k, ""))
            prompt = prompt.replace("{{%s_%d}}" % (ph, idx), val)
            if idx == 1:
                prompt = prompt.replace("{{%s}}" % ph, val)
    return prompt


def capture_state(case: dict, instances: list[dict], run_dir: Path) -> str:
    """Run the case's state_checks against the instances right after the agent finishes,
    so programmatic assertions are graded on real instance state, not on the agent's claims."""
    out = []
    for chk in case.get("state_checks", []):
        inst = instances[int(chk.get("instance", 1)) - 1]
        url = inst["base_url"].rstrip("/") + chk["path"]
        user = inst.get("username", "")
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        tok = base64.b64encode(f"{user}:{inst.get('password', '')}".encode()).decode()
        req.add_header("Authorization", f"Basic {tok}")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = resp.read().decode(errors="replace")
                status = resp.status
        except urllib.error.HTTPError as e:
            status, body = e.code, e.read().decode(errors="replace")
        except Exception as e:  # noqa: BLE001
            status, body = None, f"{type(e).__name__}: {e}"
        out.append(f"### {chk.get('label', chk['path'])}\nGET {chk['path']} on instance "
                   f"{chk.get('instance', 1)} -> HTTP {status}\n{clip(body, 20_000)}")
    text = "\n\n".join(out)
    if text:
        (run_dir / "state_checks.txt").write_text(text)
    return text


# ---------------------------------------------------------------- runners

def agent_env(extra: dict | None = None) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith(STRIP_ENV_PREFIXES)}
    # Agents that build Android projects would otherwise leave Gradle and Kotlin daemons
    # running after the run (about 1 GB each); several of those exhaust a small host.
    env.setdefault("GRADLE_OPTS", "-Dorg.gradle.daemon=false "
                   "-Dkotlin.compiler.execution.strategy=in-process")
    env.update(extra or {})
    return env


def run_claude(model: dict, prompt: str, ws: Path, run_dir: Path, timeout: int,
               skill: str | None) -> dict:
    if skill:
        install_skill(skill, ws / ".claude" / "skills" / skill)
    cmd = ["claude", "-p", "--model", model["model"], "--setting-sources", "project",
           "--strict-mcp-config", "--dangerously-skip-permissions",
           "--settings", json.dumps({"autoMemoryEnabled": False}),
           "--output-format", "stream-json", "--verbose"]
    t0 = time.time()
    with open(run_dir / "transcript.jsonl", "w") as out, open(run_dir / "stderr.txt", "w") as err:
        try:
            p = subprocess.run(cmd, cwd=ws, input=prompt, stdout=out, stderr=err, text=True,
                               timeout=timeout,
                               env=agent_env({"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}))
            status = "ok" if p.returncode == 0 else f"exit {p.returncode}"
        except subprocess.TimeoutExpired:
            status = "timeout"
    meta = {"status": status, "seconds": round(time.time() - t0, 1)}
    events = read_jsonl(run_dir / "transcript.jsonl")
    for ev in events:
        if ev.get("type") == "result":
            meta.update(cost_usd=ev.get("total_cost_usd"), turns=ev.get("num_turns"),
                        usage=ev.get("usage"), final=ev.get("result"))
    meta["transcript_text"] = render_claude(events)
    meta["skill_used"] = bool(skill) and skill_used_claude(events, skill)
    return meta


def run_vibe(model: dict, prompt: str, ws: Path, run_dir: Path, timeout: int,
             skill: str | None) -> dict:
    home = ws.parent / "home"
    (home / "skills").mkdir(parents=True, exist_ok=True)
    if skill:
        install_skill(skill, home / "skills" / skill)
    prov = model["provider"]
    cfg = [
        'active_model = "eval-model"', "enable_telemetry = false",
        "enable_update_checks = false", "enable_auto_update = false", "",
        "[[providers]]",
        *[f'{k} = "{v}"' for k, v in prov.items()], "",
        "[[models]]", f'name = "{model["model"]}"', f'provider = "{prov["name"]}"',
        'alias = "eval-model"', f'temperature = {model.get("temperature", 0.2)}',
        *([f'thinking = "{model["thinking"]}"'] if model.get("thinking") else []),
        # The levels the model accepts. Vibe retries an over-long compaction at the lowest level
        # ("none" by default), which models without a no-reasoning mode reject, ending the run.
        *([f'thinking_levels = {json.dumps(model["thinking_levels"])}']
          if model.get("thinking_levels") else []),
    ]
    (home / "config.toml").write_text("\n".join(cfg) + "\n")
    (ws.parent / "prompt.txt").write_text(prompt)
    keep = {prov["api_key_env_var"]: os.environ.get(prov["api_key_env_var"], "")}
    cmd = ["vibe", "--prompt-file", str(ws.parent / "prompt.txt"), "--auto-approve", "--trust",
           "--output", "json", "--output-dir", str(ws.parent / "vibe_out"),
           "--time-limit", str(timeout)]
    t0 = time.time()
    nudges = 0
    (run_dir / "stderr.txt").write_text("")
    env = agent_env({"VIBE_HOME": str(home), **keep})
    while True:
        left = int(timeout - (time.time() - t0))
        call = cmd[:-1] + [str(max(left, 60))]
        with open(run_dir / "transcript.json", "w") as out, open(run_dir / "stderr.txt", "a") as err:
            try:
                p = subprocess.run(call, cwd=ws, stdout=out, stderr=err, text=True,
                                   timeout=max(left, 60) + 120, env=env)
                status = {0: "ok", 3: "timeout"}.get(p.returncode, f"exit {p.returncode}")
            except subprocess.TimeoutExpired:
                status = "timeout"
        try:
            entries = json.loads((run_dir / "transcript.json").read_text() or "[]")
        except json.JSONDecodeError:
            entries = []
        exp = ws.parent / "vibe_out" / "export.json"
        # Headless Vibe ends the run whenever the model answers without a tool call. Some
        # models announce a step ("Loading the skill first:") and stop there. Give the
        # same one-word nudge a user would, at most twice, in both conditions.
        stream_err = status == "exit 2" and "without a finish reason" in (run_dir / "stderr.txt").read_text()
        if ((status != "ok" and not stream_err) or nudges >= 2 or time.time() - t0 > timeout - 120
                or not exp.exists() or not (stream_err or stalled(entries))):
            break
        sid = json.loads(exp.read_text()).get("session_id")
        if not sid:
            break
        nudges += 1
        (ws.parent / "prompt.txt").write_text("Continue.")
        cmd = ["vibe", "--resume", sid] + cmd[1:] if cmd[1] != "--resume" else cmd
    meta = {"status": status, "seconds": round(time.time() - t0, 1), "nudges": nudges}
    if exp.exists():
        shutil.copy2(exp, run_dir / "vibe_export.json")
        e = json.loads(exp.read_text())
        meta.update(usage=e.get("usage"), turns=e.get("steps"), vibe_outcome=e.get("outcome"),
                    cost_usd=e.get("cost_usd"))
    meta["transcript_text"] = render_vibe(entries)
    meta["skill_used"] = bool(skill) and skill_used_text(meta["transcript_text"], skill)
    return meta


def stalled(entries: list) -> bool:
    """True when the last assistant message announces work instead of finishing it."""
    texts = []
    for e in entries:
        if isinstance(e, dict) and e.get("role") == "assistant":
            c = e.get("content")
            if isinstance(c, list):
                t = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
            else:
                t = c if isinstance(c, str) else ""
            if t.strip():
                texts.append(t.strip())
    if not texts:
        return True
    last = texts[-1]
    # A false nudge costs one extra turn; a missed stall loses the whole run.
    announces = re.search(r"\b(I'll|I will|Let me(?! know)|Now I|Next,? I|I'm going to)\b", last[-800:])
    return (last.endswith((":", "…", "...")) or (len(texts) == 1 and len(last) < 400)
            or (len(last) < 800 and bool(announces)))


RUNNERS = {"claude": run_claude, "vibe": run_vibe}


# ---------------------------------------------------------------- transcripts

def read_jsonl(path: Path) -> list[dict]:
    out = []
    if path.exists():
        for line in path.read_text(errors="replace").splitlines():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def clip(s: str, n: int) -> str:
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[: n // 2] + f"\n…[{len(s) - n} chars clipped]…\n" + s[-n // 2:]


def render_claude(events: list[dict]) -> str:
    parts = []
    for ev in events:
        t = ev.get("type")
        msg = ev.get("message") or {}
        content = msg.get("content") if isinstance(msg, dict) else None
        if t == "assistant" and isinstance(content, list):
            for c in content:
                if c.get("type") == "text":
                    parts.append(f"ASSISTANT: {c['text']}")
                elif c.get("type") == "tool_use":
                    parts.append(f"TOOL CALL {c.get('name')}: {clip(c.get('input'), 3000)}")
        elif t == "user" and isinstance(content, list):
            for c in content:
                if c.get("type") == "tool_result":
                    body = c.get("content")
                    if isinstance(body, list):
                        body = "\n".join(x.get("text", "") for x in body if isinstance(x, dict))
                    parts.append(f"TOOL RESULT: {clip(body or '', 1500)}")
    return "\n\n".join(parts)


def render_vibe(entries: list[dict]) -> str:
    """Vibe headless JSON: messages, plus 'effect' entries for tool calls."""
    parts = []
    for e in entries:
        t, role = e.get("type"), e.get("role")
        if t == "message" and role == "assistant":
            txt = " ".join(c.get("text", "") for c in e.get("content", []) if isinstance(c, dict))
            if txt.strip():
                parts.append(f"ASSISTANT: {txt}")
        elif t == "effect":
            d = e.get("detail") or {}
            st = e.get("state") or {}
            parts.append(f"TOOL CALL {d.get('toolName') or e.get('title')}: "
                         f"{clip(d.get('input', ''), 3000)}")
            out = st.get("output", st.get("error", ""))
            parts.append(f"TOOL RESULT ({st.get('status')}): {clip(out, 1500)}")
    return "\n\n".join(parts)


def contamination(run_dir: Path) -> list[str]:
    """Markers found in the raw transcript, ignoring the session-init event."""
    hits = set()
    for name in ("transcript.jsonl", "transcript.json"):
        p = run_dir / name
        if not p.exists():
            continue
        for line in p.read_text(errors="replace").splitlines():
            if '"subtype":"init"' in line.replace(" ", ""):
                continue
            hits.update(m for m in CONTAMINATION_MARKERS if m in line)
    return sorted(hits)


def skill_used_claude(events: list[dict], skill: str) -> bool:
    for ev in events:
        content = (ev.get("message") or {}).get("content")
        if ev.get("type") == "assistant" and isinstance(content, list):
            for c in content:
                if c.get("type") == "tool_use":
                    inp = json.dumps(c.get("input", {}))
                    if c.get("name") == "Skill" and skill in inp:
                        return True
                    if f"skills/{skill}/" in inp:
                        return True
    return False


def skill_used_text(text: str, skill: str) -> bool:
    return bool(re.search(rf"(skills/{re.escape(skill)}/|skill[^\n]{{0,40}}{re.escape(skill)})", text))


# ---------------------------------------------------------------- outputs + grading

TEXT_EXT = {".md", ".txt", ".json", ".py", ".sh", ".js", ".ts", ".tsx", ".jsx", ".kt", ".kts",
            ".java", ".sql", ".csv", ".yaml", ".yml", ".toml", ".html", ".xml", ".gradle",
            ".properties", ".env", ".ipynb", ".css", ".webapp", ""}


def collect_outputs(ws: Path, before: dict[str, float], budget: int = 120_000) -> tuple[str, list[str]]:
    after = snapshot(ws)
    changed = sorted(k for k, m in after.items() if before.get(k) != m)
    chunks, used = [], 0
    if len(changed) > 300:
        chunks.append(f"({len(changed)} files changed; showing the first 300 by path)")
        changed = changed[:300]
    for rel in changed:
        p = ws / rel
        if p.suffix.lower() not in TEXT_EXT or p.stat().st_size > 2_000_000:
            chunks.append(f"=== {rel} (binary or large, {p.stat().st_size} bytes)")
            continue
        body = clip(p.read_text(errors="replace"), 20_000)
        if used + len(body) > budget:
            chunks.append(f"=== {rel} (omitted: output budget exhausted)")
            continue
        used += len(body)
        chunks.append(f"=== {rel}\n{body}")
    return "\n\n".join(chunks), changed


GRADER_PROMPT = """You are grading an AI agent's work on a DHIS2 task. Judge each assertion strictly
from the evidence below: the agent's transcript (its messages, tool calls and results) and the
files it wrote. An assertion passes only if the evidence clearly shows it. A claim the agent
made but did not carry out does not count as carrying it out. If the run failed or timed out,
grade what exists.

## Task given to the agent
{prompt}

## What a good answer looks like (reference)
{expected}

## Assertions to grade
{assertions}

## Agent run status: {status}

## Instance state after the run (captured by the harness, not by the agent)
{state}

## Files the agent created or changed
{files}

## Agent transcript
{transcript}

Respond with ONLY a JSON object, no prose before or after:
{{"assertions": [{{"id": 1, "passed": true, "evidence": "short quote or reason"}}, ...],
  "notes": "one or two sentences on the overall quality, including anything wrong that the assertions miss"}}
"""


def grade(grader: dict, case: dict, prompt: str, meta: dict, files_text: str, run_dir: Path,
          timeout: int = 900) -> dict:
    skill_name = run_dir.parts[-4] if len(run_dir.parts) >= 4 else ""
    assertions = "\n".join(f"{i}. {localise(a, skill_name)}"
                           for i, a in enumerate(case["assertions"], 1))
    gp = GRADER_PROMPT.format(prompt=prompt, expected=localise(case.get("expected_output", ""), skill_name),
                              assertions=assertions, status=meta.get("status"),
                              files=files_text or "(none)", state=meta.get("state_text") or "(no state checks for this case)",
                              transcript=clip(meta.get("transcript_text", ""), 150_000))
    (run_dir / "grader_prompt.txt").write_text(gp)
    gdir = run_dir / "grader_ws"
    gdir.mkdir(exist_ok=True)
    cmd = ["claude", "-p", "--model", grader["model"], "--setting-sources", "project",
           "--strict-mcp-config", "--output-format", "json", "--disallowedTools",
           "Bash,Edit,Write,Read,Glob,Grep,WebFetch,WebSearch,Agent,Skill"]
    for attempt in range(3):
        try:
            p = subprocess.run(cmd, cwd=gdir, input=gp, capture_output=True, text=True,
                               timeout=timeout, env=agent_env())
            res = json.loads(p.stdout)
            text = res.get("result", "")
            m = re.search(r"\{.*\}", text, re.S)
            g = json.loads(m.group(0))
            n = len(case["assertions"])
            items = {int(a["id"]): a for a in g.get("assertions", [])}
            g["assertions"] = [dict(id=i, text=case["assertions"][i - 1],
                                    passed=bool(items.get(i, {}).get("passed")),
                                    evidence=items.get(i, {}).get("evidence", "not graded"))
                               for i in range(1, n + 1)]
            g["passed"] = sum(a["passed"] for a in g["assertions"])
            g["total"] = n
            g["grader_cost_usd"] = res.get("total_cost_usd")
            return g
        except Exception as e:  # noqa: BLE001 - retry any grader failure
            err = f"{type(e).__name__}: {e}"
            if not claude_available():
                wait_for_claude(f"grader: {err[:80]}")
            time.sleep(5)
    return {"error": err, "passed": 0, "total": len(case["assertions"]), "assertions": []}


# ---------------------------------------------------------------- orchestration

def run_one(job: dict, args, models: dict) -> dict:
    skill, case, mkey, cond = job["skill"], job["case"], job["model"], job["condition"]
    run_dir = args.out / skill / f"case-{case['id']}" / mkey / cond
    result_path = run_dir / "result.json"
    regrade = args.regrade
    if result_path.exists() and not args.force and not args.regrade:
        prev = json.loads(result_path.read_text())
        if not ((prev.get("grade") or {}).get("error") and "run" in prev):
            return prev
        regrade = True  # the run is fine, only its grading failed (e.g. usage limit)
    if not regrade:
        if run_dir.exists():
            rmtree(run_dir)
        run_dir.mkdir(parents=True, exist_ok=True)
    ws = None  # created per attempt in _execute
    base = {"skill": skill, "case": case["id"], "model": mkey, "condition": cond,
            "live": is_live(case)}

    if regrade:
        if not result_path.exists():
            return dict(base, status="missing")
        r = json.loads(result_path.read_text())
        if "run" not in r:
            return r
        meta = r["run"]
        meta["transcript_text"] = (run_dir / "transcript.txt").read_text()
        if (run_dir / "state_checks.txt").exists():
            meta["state_text"] = (run_dir / "state_checks.txt").read_text()
        files_text = (run_dir / "outputs.txt").read_text() if (run_dir / "outputs.txt").exists() else ""
        r["grade"] = grade(models[args.grader], case, r["prompt"], meta, files_text, run_dir)
        meta.pop("transcript_text", None)
        meta.pop("state_text", None)
        result_path.write_text(json.dumps(r, indent=1))
        return r

    prompt = case["prompt"]
    if is_live(case):
        with _instance_lock:  # live cases share instances: one at a time
            try:
                insts = provision(case)
            except Exception as e:  # noqa: BLE001
                r = dict(base, status="error", error=str(e))
                result_path.write_text(json.dumps(r, indent=1))
                return r
            if insts is None:
                r = dict(base, status="skipped", reason="DHIS2_EVAL_INSTANCE_CMD not set")
                result_path.write_text(json.dumps(r, indent=1))
                return r
            prompt = substitute(prompt, insts)
            return _execute(base, case, prompt, models, mkey, cond, ws, run_dir, args, insts)
    return _execute(base, case, prompt, models, mkey, cond, ws, run_dir, args)


def _execute(base, case, prompt, models, mkey, cond, ws, run_dir, args, insts=None) -> dict:
    skill = base["skill"]
    model = models[mkey]
    prompt = localise(prompt, skill)
    timeout = int(model.get("timeout", args.timeout))
    attempt = 0
    while attempt < 2:
        attempt += 1
        sandbox = WORK_ROOT / uuid.uuid4().hex[:12]
        ws = sandbox / "work"
        prepare_workspace(skill, case, ws)
        before = snapshot(ws)
        log(f"start {skill}#{case['id']} {mkey}/{cond}" + (" (retry)" if attempt > 1 else ""))
        meta = RUNNERS[model["runner"]](model, prompt, ws, run_dir, timeout,
                                        skill if cond == "with_skill" else None)
        if model["runner"] == "claude" and claude_failed_fast(meta) and not claude_available():
            rmtree(sandbox)
            wait_for_claude(f"{skill}#{case['id']} {mkey}/{cond} exited after {meta['seconds']}s")
            attempt -= 1  # not the agent's fault: run it again
            continue
        files_text, changed = collect_outputs(ws, before)
        if insts and case.get("state_checks"):
            meta["state_text"] = capture_state(case, insts, run_dir)
        hits = contamination(run_dir)
        if not args.keep_workspaces:
            rmtree(sandbox)
        # Claude Code keeps a session log per working directory; drop the eval ones.
        slug = re.sub(r"[^A-Za-z0-9]", "-", str(ws))
        if (HOME / ".claude" / "projects" / slug).is_dir():
            rmtree(HOME / ".claude" / "projects" / slug)
        if not hits:
            break
        log(f"contaminated {skill}#{case['id']} {mkey}/{cond}: {hits}")
    (run_dir / "transcript.txt").write_text(meta.get("transcript_text", ""))
    (run_dir / "outputs.txt").write_text(files_text)
    r = dict(base, prompt=prompt, files_written=changed, contaminated=hits, attempts=attempt)
    if not args.no_grade:
        r["grade"] = grade(models[args.grader], case, prompt, meta, files_text, run_dir)
    meta.pop("transcript_text", None)
    meta.pop("state_text", None)
    r["run"] = meta
    (run_dir / "result.json").write_text(json.dumps(r, indent=1, default=str))
    g = r.get("grade", {})
    log(f"done  {skill}#{case['id']} {mkey}/{cond}: {meta['status']} "
        f"{g.get('passed', '?')}/{g.get('total', '?')} in {meta['seconds']}s"
        + (" CONTAMINATED" if hits else ""))
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skills", nargs="*", help="default: every skill with evals/evals.json")
    ap.add_argument("--cases", nargs="*", default=[], help="skill:1,3 filters")
    ap.add_argument("--models", nargs="*", default=["opus", "sonnet", "glm"])
    ap.add_argument("--conditions", nargs="*", default=list(CONDITIONS), choices=CONDITIONS)
    ap.add_argument("--offline-only", action="store_true")
    ap.add_argument("--live-only", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=1200, help="seconds per agent run")
    ap.add_argument("--grader", default="opus", help="model key used for grading (claude runner)")
    ap.add_argument("--no-grade", action="store_true")
    ap.add_argument("--regrade", action="store_true", help="re-grade existing runs only")
    ap.add_argument("--force", action="store_true", help="re-run even if result.json exists")
    ap.add_argument("--run-id", default=None, help="reuse/resume a results directory")
    ap.add_argument("--list", action="store_true", help="print the job list and exit")
    ap.add_argument("--keep-workspaces", action="store_true",
                    help="keep agent workspaces under $EVAL_WORK_ROOT for inspection")
    args = ap.parse_args()

    load_dotenv(REPO / ".env")
    models = json.loads((EVALS_DIR / "models.json").read_text())
    for m in args.models + [args.grader]:
        if m not in models:
            sys.exit(f"unknown model key {m!r}; see evals/models.json")
    if models[args.grader]["runner"] != "claude":
        sys.exit("the grader must use the claude runner")

    case_filter: dict[str, set[int]] = {}
    for c in args.cases:
        s, ids = c.split(":")
        case_filter[s] = {int(i) for i in ids.split(",")}

    jobs = []
    # --cases alone restricts the run to the skills it names
    for skill in args.skills or (sorted(case_filter) if case_filter else discover_skills()):
        for case in load_cases(skill):
            if skill in case_filter and case["id"] not in case_filter[skill]:
                continue
            if args.offline_only and is_live(case):
                continue
            if args.live_only and not is_live(case):
                continue
            for m in args.models:
                for cond in args.conditions:
                    jobs.append({"skill": skill, "case": case, "model": m, "condition": cond})
    if args.list:
        for j in jobs:
            print(j["skill"], j["case"]["id"], j["model"], j["condition"],
                  "live" if is_live(j["case"]) else "offline")
        print(len(jobs), "jobs")
        return

    run_id = args.run_id or dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    args.out = EVALS_DIR / "results" / run_id
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "run.json").write_text(json.dumps(
        {"run_id": run_id, "models": {m: models[m] for m in args.models},
         "grader": models[args.grader]["model"], "argv": sys.argv[1:],
         "started": dt.datetime.now().isoformat()}, indent=1))
    log(f"{len(jobs)} jobs -> {args.out}")

    # Interleave models so one provider's rate limit doesn't serialise the whole run.
    jobs.sort(key=lambda j: (is_live(j["case"]), j["skill"], j["case"]["id"], j["condition"]))
    results = []
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(run_one, j, args, models): j for j in jobs}
        for f in cf.as_completed(futs):
            j = futs[f]
            try:
                results.append(f.result())
            except Exception as e:  # noqa: BLE001
                log(f"FAILED {j['skill']}#{j['case']['id']} {j['model']}/{j['condition']}: {e}")
    log(f"finished {len(results)}/{len(jobs)}; run: python3 evals/report.py {args.out}")


if __name__ == "__main__":
    main()
