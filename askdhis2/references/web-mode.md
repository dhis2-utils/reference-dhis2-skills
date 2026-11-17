# Web mode (no DHIS2 knowledge MCP)

Last verified 2026-10-26. Site policies change, so use the probe, not memory.

## Probe once, remember the answer

Fetch `https://docs.dhis2.org/en/llms.txt`.

- **Content comes back** → **direct mode** (the expected case today). Use the
  index and the `.md` pages it links.
- **A robots or permission refusal comes back** → **mirror mode**. Skip the docs
  domain and use the GitHub sources below. Until October 2026 `robots.txt` blocked
  all agents except three search crawlers; that block has since been lifted. It
  could return.

A refusal is a publisher rule. Do not report it to the user as a network,
allowlist or rendering problem. The pages are fully server-rendered.

## Direct mode

- `llms.txt` lists about 700 pages under **Use, Implement, Manage, Develop,
  Topics**. Narrower indexes are cheaper when you know the area: `llms-use.txt`,
  `llms-implement.txt`, `llms-manage.txt`, `llms-develop.txt`, `llms-topics.txt`;
  `llms-master.txt` for unreleased content; `llms-v{N}.txt` for older releases.
- Any docs page URL becomes its Markdown source by swapping `.html` for `.md`.
- `robots.txt` sets `Crawl-delay: 5`. Fetch pages one after another. Do not fire
  parallel fetches at the domain.
- `robots.txt` disallows `/archive/`, `/javadoc/` and `/*/search/`. Do not use
  the site's own search page. Use the index, or a web search with `site:`.
- The version label on an index heading is a hint, not proof. One heading
  ("Software Release Information") carried a v41 label while the top of the
  file said v43 was stable. Confirm the version from the page URL or text.
- If a `.md` fetch returns an opaque blob instead of text, it is still
  Markdown. (This was the case until October 2026.)

## Mirror mode: sources you can read

| Source | Use for |
|---|---|
| `dhis2/dhis2-docs` on GitHub (raw) | The docs content itself: same Markdown, same text |
| `dhis2/dhis2-releases` on GitHub (raw) | Release notes, upgrade and migration notes, breaking changes |
| developers.dhis2.org | Web API, app platform, developer guides |
| community.dhis2.org | Real-world problems and workarounds |
| dhis2.org | Product overview, release landing pages |

In mirror mode the GitHub source is the docs, not a last resort. The section
layout (Use / Implement / Manage / Develop / Topics) maps to the repo layout.

## Either mode

- Docs for "how does it work". CoP for "why does it not work". Release notes for
  "what changed".
- Never drop a claim silently because a fetch came back empty. Find it in a
  reachable source, or say plainly that you could not confirm it.
- Web mode cannot see Jira issues or Academy transcripts well. For a narrow bug
  or error-code question, say that coverage is thinner than with the MCP.
