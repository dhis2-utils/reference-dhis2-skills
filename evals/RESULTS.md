# Eval results

Latest full run: **2026-11-12**, all skills, harness in this directory; the 9 skills now in the repo
have 34 cases (28 offline, 6 live). dhis2-api was re-run on 2026-11-13 after its rename. Each case ran once per model and condition (with the skill installed, and without any
skill), and Claude Opus 5.5 graded the assertions. Score = mean fraction of assertions passed per
case. These are single runs, so a few points' difference on one skill is noise; treat the per-skill
numbers as a map of weak spots, not as a ranking.

Models:

| Key | Model | Runner |
|---|---|---|
| opus | Claude Opus 5.5 | `claude` CLI |
| sonnet | Claude Sonnet 5.5 | `claude` CLI |
| glm | GLM 5.3 Flash, reasoning "high" | Vibe CLI headless, Mistral API |

## Offline cases (28 cases × 3 models × 2 conditions = 168 runs)

| Model | With skill | Without | Δ |
|---|---|---|---|
| Claude Opus 5.5 | 97% | 55% | +42 |
| Claude Sonnet 5.5 | 95% | 46% | +50 |
| GLM 5.3 Flash | 91% | 39% | +53 |

Every model loaded the skill in 100% of with-skill runs.

| Skill | Opus with / without | Sonnet with / without | GLM with / without |
|---|---|---|---|
| dhis2-app-review | 91 / 44 | 82 / 26 | 83 / 35 |
| dhis2-api (was dhis2-docs) | 100 / 56 | 94 / 61 | 94 / 49 |
| dhis2-indicator-review | 98 / 37 | 100 / 42 | 95 / 27 |
| dhis2-indicators | 100 / 68 | 97 / 47 | 86 / 58 |
| dhis2-integrity | 100 / 43 | 100 / 29 | 91 / 24 |
| dhis2-metadata | 100 / 53 | 100 / 39 | 89 / 46 |
| dhis2-prototyping | 89 / 49 | 89 / 35 | 100 / 27 |
| dhis2-test-instances | 100 / 72 | 100 / 61 | 96 / 44 |
| dhis2-tracker-design | 100 / 69 | 97 / 62 | 89 / 36 |

dhis2-api was renamed from dhis2-docs on 2026-11-13 and refocused on the Web API (documentation
lookups now go to a DHIS2 knowledge search first); its row and the totals use a re-run of its three
offline cases after the change.

On 2026-11-13 the facts behind dhis2-indicators #1, dhis2-prototyping #1 and dhis2-tracker-design #2
were re-verified on live instances (see *Changes* below), two of those cases' assertions corrected, and
all three cases re-run; their rows and the totals include those re-runs. The prototyping drop for Opus
and Sonnet (8→6, 7→6 of 9) is on age-band category mappings and `containsItems()`, which the re-check
did not touch: single-run variance on a long task.

## Live cases

Live cases need a disposable DHIS2 instance (`DHIS2_EVAL_INSTANCE_CMD`, see README.md) and take
10–40 minutes each. The live round covers indicators #4, integrity #2 and metadata #3; metadata #3
grades the instances' state after the run (`state_checks`), not the agent's claims. 3 cases × 3
models × 2 conditions = 18 runs, on DHIS2 2.42 instances (empty, or seeded from the Sierra Leone
demo for the metadata source).

| Case | Opus with / without | Sonnet with / without | GLM with / without |
|---|---|---|---|
| dhis2-indicators #4 | 9/9 / 8/9 | 7/9 / 6/9 | 8/9 / 6/9 |
| dhis2-integrity #2 | 7/8 / 6/8 | 8/8 / 4/8 | 6/8 / 2/8 |
| dhis2-metadata #3 | 7/8 / 6/8 | 7/8 / 6/8 | 8/8 / 6/8 |
| **Mean** | **92% / 80%** | **88% / 64%** | **88% / 56%** |

The gain is smaller on live tasks than offline: with a real instance to probe, models find part of
what the skill would tell them. The largest live gap is integrity remediation: without the skill,
Sonnet (4/8) and GLM (2/8) deduplicated by editing the JSON instead of merging on the sandbox, which
on a real instance would orphan the data behind the removed objects.

Skipped from the live round:
- **dhis2-api #2**: low value for the cost (a single API lookup on a live instance).
- **dhis2-app-review #3** and **dhis2-integrity #1**: left out to keep the round short; integrity #1
  also overlaps the skill's worked example (see Suitability).

## Findings

**The skills help every model, the most on the weakest.** Without a skill, Sonnet and GLM miss most
DHIS2-specific traps (version-dependent endpoints, silent 200 responses, merge-endpoint limits,
analytics boundaries). With the skill, Sonnet is on par with Opus, and GLM 5.3 Flash closes most of
the gap.

**GLM headless runs stall.** In the Vibe CLI's programmatic mode GLM sometimes announces the next step
("I'll download Gradle in the background while writing the module.") and ends its turn without
doing it. The harness detects this (a short last message that announces work, or ends with a
colon) and resumes the session with "Continue." up to twice, in both conditions. Before the nudge,
the stalls cost GLM about 13 points with the skill. The detector was widened twice during this
review after missing stalls; affected runs were re-run.

**Long GLM sessions hit a Vibe compaction fallback.** When a compaction request reasons too long,
Vibe retries it with reasoning off; GLM 5.3 accepts only low/high/max and rejects the retry, which
ends the run (one 41-minute live run). Listing the model's `thinking_levels` in `models.json` makes
the retry use `low`.

**GLM is weakest on long remediation answers.** On dhis2-integrity it sometimes skips
merge-endpoint limits (E1540, 2.43-only combo/category merges) or validates only some of its
expression repairs. The skill states all of these; the model does not always carry them through a
long answer.

**Unattended runs expose "ask first" rules.** dhis2-integrity told the agent to batch all judgment
calls into one question round before fixing. Run unattended, Sonnet asked and stopped, delivering
nothing (4/8 on live #2). The skill now treats a requested reviewable deliverable on a sandbox as
the decision round: make best-effort calls, apply them in the sandbox, list each one for review.
Sonnet then scored 8/8.

**Two assertions most models miss.** dhis2-app-review #2 asks to fix a flaky Playwright test's
timeouts; the row-count bug (client-side pagination) is a hidden extra that the skill covers but no
model spots unprompted. dhis2-app-review #4 expects the migration advice to name the review's UI
suite as acceptance tests; models paraphrase it ("same flows before and after").

**Contamination.** Without the skill, agents sometimes go looking for skills or the eval definitions
on the machine. The harness flags any transcript that touches the repository, an installed skills
directory or `evals.json`, retries once, and excludes the run if it happens again (1 of 168 runs:
Opus without the skill reading `~/.claude/skills`). Run the harness on a machine without these
skills installed globally for cleaner baselines.

## Changes made because of the evals

Fixes made in this review, each prompted by with-skill failures:

- **dhis2-indicator-review**: eval extracts rebuilt so they no longer match `examples/` (the first
  version let agents copy the answers from the examples).
- **dhis2-integrity**: COC merge does not repoint custom-form HTML; `categoryOptionComboUpdate`
  recreates COCs the combo still implies; advisory fixes must be labelled untested; a reviewable
  deliverable replaces the up-front question round; export the fixed dump whole and check that no
  removed UID remains.
- **dhis2-indicators**: exact program-indicator validation call; "when a number looks wrong" section.
- **Re-verified facts (2026-11-13, live probes on 2.40.12, 2.41.11, 2.42.7.1 and 2.43.2.1)**: an inner
  division by zero in an aggregate indicator gives `NaN` on all four versions (the skills had said E7132
  before 2.43); E7132 comes from divisions computed in SQL (program indicators, `subExpression()`), and
  an `if()` guard avoids it. ENROLLMENT program-indicator lookups ignore `PS_EVENTDATE` boundaries on
  2.43 as on 2.42. Tracker-design claims re-checked on 2.42.7.1: `OWNER_AT_END` works as a PI org-unit
  field (it falls back silently when the ownership table is empty), so ownership is the default way
  to count people where they are now and a copied org-unit data element only a last resort; the
  rest held.
- **dhis2-api (then dhis2-docs), dhis2-test-instances**: wider descriptions (Sonnet did not load them in the first round).

## Suitability

Every skill has evals that discriminate (with-skill well above without). No skill is unsuitable for
evals. Limits worth knowing:

- **dhis2-integrity, live #1**: the skill's `examples/` folder contains a worked remediation of the
  same Sierra Leone demo, so a with-skill score would partly measure copying; it was not run. The
  other integrity cases use synthetic dumps that differ from the examples.
