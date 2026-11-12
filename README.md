# ai-skills-dhis2

[Agent Skills](https://agentskills.io) for working with [DHIS2](https://dhis2.org): building and
reviewing apps, authoring and auditing indicators, handling metadata, remediating integrity
problems, designing tracker programs, reporting bugs and running proofs of concept. Each skill
is a folder with a `SKILL.md`, plus references, scripts and evals.

| Skill | Purpose |
|---|---|
| `create-dhis2-app` | Scaffold a lightweight vanilla-JS DHIS2 tool from the tool-template (no React/App Platform). |
| `dhis2-android-sdk-app` | Build a native Android app on the DHIS2 Android SDK: tracker writes, rule engine, sync, tests. |
| `dhis2-app-review` | Review and test DHIS2 web apps: static review, Playwright UI testing, multi-version checks. |
| `dhis2-bug-report` | Reproduce a suspected DHIS2 bug, check Jira for duplicates, isolate it, and write the ticket. |
| `dhis2-docs` | Work with the DHIS2 Web API and look up official DHIS2 documentation. |
| `dhis2-indicators` | Author, validate and test aggregate indicators and program indicators. |
| `dhis2-indicator-review` | Validate, review with the programme team, fix, test end to end and approve indicators at scale. |
| `dhis2-integrity` | Remediate broken or duplicate metadata so an instance passes DHIS2 data-integrity checks. |
| `dhis2-metadata` | Export, split, transform, compare, validate and import DHIS2 metadata in bulk. |
| `dhis2-prototyping` | Run a comparative DHIS2 proof of concept: generated metadata, synthetic data, verified indicators, scripted entry flows, report. |
| `dhis2-test-instances` | Get a disposable DHIS2 to test against (from your environment, local Docker, or the user) and use it safely. |
| `dhis2-tracker-design` | Design and review tracker data models: entity types, programs vs stages vs relationships, access, analytics reach. |

**Not covered (yet):** App Platform app development (React, `@dhis2/app-runtime`, `@dhis2/ui`);
use the official developer documentation at [developers.dhis2.org](https://developers.dhis2.org).
Program-rule authoring is not covered either.

Supported DHIS2 versions: 2.40–2.43. Version-specific behaviour is marked in the skills.

## Install

Copy or symlink the skill folders into your agent's skills directory:

- **Claude Code**: `~/.claude/skills/` (all projects) or `<project>/.claude/skills/`
- **Mistral Vibe**: `~/.vibe/skills/`, or a directory listed in `skill_paths`
- **Other agents** that support Agent Skills: see their documentation
- **claude.ai**: `scripts/build-skill-bundles.sh` builds one uploadable zip per skill into
  `dist/`

```bash
git clone https://github.com/dhis2-util/ai-skills-dhis2
ln -s "$PWD"/ai-skills-dhis2/dhis2-* "$PWD"/ai-skills-dhis2/create-dhis2-app ~/.claude/skills/
```

Install them all. The skills refer to each other by name (e.g. `dhis2-indicators` sends
provisioning to `dhis2-test-instances`).

## Live instances

Several skills prove their work on a **disposable** DHIS2 instance instead of trusting their
own reasoning. `dhis2-test-instances` describes how an agent gets one. It uses whatever your
environment provides first: an instance broker, an Instance Manager, a docker host, or a
URL you give it. Then it falls back to a local Docker instance (empty, or seeded with the
Sierra Leone demo database), and finally to asking you. If your team has its own
provisioning tool, document it in your agent's instructions (AGENTS.md, CLAUDE.md) and the
skills will use it. The skills never use the public play servers for testing. The one
exception is reproducing a bug for a ticket.

## Evals

Every skill has `evals/evals.json`: realistic tasks with checkable assertions. `evals/`
holds a harness that runs each task with and without the skill across models (Claude via
the `claude` CLI, Mistral-hosted models via the Vibe CLI), and has a grader model score the
assertions. See [evals/README.md](evals/README.md) for how to run it, and
[evals/RESULTS.md](evals/RESULTS.md) for the latest results.

## Contributing

Read [AGENTS.md](AGENTS.md) first. This is a public repository: examples use only the
public DHIS2 demo databases (Sierra Leone, Laos), and lessons from real deployments must be
anonymised. When you change a skill, run its evals before and after.

## License

BSD 3-Clause; see [LICENSE](LICENSE).
