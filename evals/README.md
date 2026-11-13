# Skill evals

Every skill has `evals/evals.json`: realistic tasks with checkable assertions. The harness
in this directory runs each task with and without the skill, on several models, and has a
grader model check the assertions. The result answers two questions: **does the skill help**,
and **for which models**?

## Running

```bash
# Prerequisites: Python 3.10+; the `claude` CLI (logged in) for Claude models;
# `vibe` (pip install mistral-vibe) + MISTRAL_API_KEY for Mistral-hosted models.
python3 evals/run_evals.py --skills dhis2-docs dhis2-indicators \
    --models opus sonnet glm --conditions with_skill without_skill
python3 evals/report.py evals/results/<run-id>     # writes REPORT.md + summary.json
```

Useful flags: `--cases dhis2-docs:1,3` (pick cases), `--offline-only`, `--jobs 4`
(parallel runs), `--timeout 1200` (seconds per run), `--grader opus`.

Models are defined in `evals/models.json`. To add a model, add an entry with a runner
(`claude` or `vibe`) and the model id. Vibe models also take a `provider` block, `thinking` (the
reasoning level) and `thinking_levels` (the levels the model accepts). Set `thinking_levels` for a
model that cannot turn reasoning off: Vibe retries an over-long context compaction at the lowest
level, `none` by default, and such a model rejects it and ends the run.

## Live-instance cases

Some cases need a running DHIS2. They declare it in `requires`:

```json
"requires": {"instance": {"seed": "sierra-leone", "version": "2.42"}}
```

`seed` is `sierra-leone` or `empty`. Add `"mutates": false` when the case only reads; the
provider can then reuse an instance instead of resetting it. A case that needs two instances
(e.g. copy from a source to a target) uses `"instances": [{...}, {...}]` and the numbered
placeholders `{{DHIS2_BASE_URL_1}}`, `{{DHIS2_BASE_URL_2}}` and so on. Before each such run, the harness calls the command
in `DHIS2_EVAL_INSTANCE_CMD` once per instance, with the requirement on stdin, plus `slot` (1, 2, …) and `fresh`
(true unless `mutates` is false). The command prints
`{"base_url": ..., "username": ..., "password": ..., "version": ...}`, and the harness
substitutes `{{DHIS2_BASE_URL}}`, `{{DHIS2_USERNAME}}`, `{{DHIS2_PASSWORD}}` and
`{{DHIS2_VERSION}}` in the prompt. Point this at whatever provisions instances in your
setup: a docker compose wrapper, an instance broker, or a script that echoes a fixed test
server. Without it, live cases are skipped and reported as `skipped`. Live cases must
never point at a production or public play server.

A live case can also list `state_checks`: GET requests the harness runs against the
instances right after the agent finishes, with the credentials the agent was given. The
responses go to the grader as "instance state after the run", so assertions about the end
state (UIDs copied, login still works) are graded on the instance, not on what the agent
says it did:

```json
"state_checks": [
  {"label": "Target ANC data elements", "instance": 2,
   "path": "/api/dataElements?filter=name:$like:ANC&fields=id&paging=false"}
]
```

## evals.json format

```json
{
  "skill_name": "dhis2-docs",
  "evals": [
    {
      "id": 1,
      "prompt": "What the user types. Realistic, specific, with the context a user would give.",
      "expected_output": "One paragraph: what a good answer does and contains.",
      "files": ["evals/files/input.json"],
      "requires": "offline",
      "assertions": [
        "One objectively checkable statement per line about the transcript or output files"
      ],
      "notes": "Why this case exists / what trap it probes (not shown to the agent)."
    }
  ]
}
```

- `files` are paths relative to the skill directory, under `evals/files/`. The harness
  copies them into the agent's empty working directory as `inputs/...` and rewrites
  `evals/files/` to `inputs/` in the prompt, expected output and assertions, so the agent
  never sees where the evals live.
- `requires` is `"offline"` (no DHIS2 needed; network for docs/GitHub may be used) or an
  object as above.
- **Assertions must be checkable by a grader that sees only the final transcript, the
  files written and any `state_checks` output**. Name the file, the field and the value. Prefer assertions a capable
  model *without* the skill would plausibly fail: the trap the skill exists to prevent.
  Avoid style or length assertions.
- Keep 3–4 cases per skill, with at least 2 offline. Cases should take an agent under
  ~15 minutes.

## Trigger tests

`evals/trigger-evals.json` (optional, per skill) lists `{"query", "should_trigger"}` pairs
for checking that a skill's description makes it load when it should and stay quiet when it
shouldn't. These are not run by `run_evals.py`. Use a description-optimisation tool such as
the skill-creator skill's loop.

## Reading results

`report.py` gives, per model: the score with and without the skill, the delta, and how often
the agent actually loaded the skill. A skill **helps** a model when the delta is clearly
positive. A small delta with a high baseline means the model already knows the material,
and the skill mainly costs context for that model. A low score *with* the skill points to
skill content the model cannot use, or to an assertion that needs revisiting. The "failed
with the skill" list at the end is the place to start. Results go to `evals/results/`
(gitignored). Summaries worth keeping are copied to `evals/RESULTS.md`.
