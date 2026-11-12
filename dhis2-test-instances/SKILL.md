---
name: dhis2-test-instances
description: Get a disposable DHIS2 instance to test against and know what is safe to do on it — find one the environment provides, start one locally with Docker (empty or seeded with the Sierra Leone demo database), know when it is ready, or ask the user. Use whenever a task needs a live DHIS2 to verify or try something (an import, an indicator value, an app, an API behaviour, a version difference) and no disposable instance has been given; when the user proposes the public play/demo server for verifying their own changes; when asking where to test; or before running destructive tests against a staging or shared server. Triggers on "spin up a DHIS2", "set up 2.41 and 2.42 in Docker", "test this on a clean 2.42", "just use play for this", "is there a test server I can use", "how do I know it's ready", "reset the test database". Other dhis2-* skills defer to this one for provisioning. Reproducing a suspected DHIS2 bug on play for a ticket is dhis2-bug-report.
---

# DHIS2 test instances

Several dhis2-* skills prove things on a **live, disposable** DHIS2 instance (import
dry-runs, indicator values, app UI tests, integrity fixes, version comparisons). This skill
says how to get one and what you may do with it. It is deliberately tool-agnostic: teams
provision instances in different ways, and an agent should use whichever one its
environment offers.

## What a test instance is

Record these six facts for every instance you use, and put them in reports:

| Fact | Example |
|---|---|
| Base URL reachable **from where the agent runs** | `http://localhost:8080`, `http://dhis2-test:8080` |
| Credentials | `admin` / `district` (demo) or a PAT |
| Exact version | `GET /api/system/info` → `version`, `revision` |
| Seed | empty, Sierra Leone demo 2.42, Laos demo, a user-supplied dump |
| Disposable? | yes only if the user or environment says so, or you created it |
| Optional extras | DB access (`psql` host/port), reset method, host port the user's browser can open |

**Treat an instance as production unless you know it is disposable.** You know an instance
is disposable when you created it, or when the user or the environment's instructions say
so. On any other instance, confirm each write first (method, URL, body).

## Finding or creating one, in this order

1. **The environment already provides one.** Check the agent's instructions (AGENTS.md,
   CLAUDE.md, a system prompt), the environment variables and any MCP servers or CLIs for a
   documented way to create, reset and delete instances. Some teams run an instance broker,
   an Instance Manager or a docker host for agents. If it exists, use it and follow its rules
   on naming, quotas and cleanup. Label what you create so other sessions can recognise it.
2. **The user gave a URL.** Use it. Ask if it is disposable before you write anything.
3. **Docker is available locally** (`docker compose version` works). Start one, as described
   below.
4. **None of the above.** Ask the user for an instance (URL, credentials, version, whether it
   is disposable). Say what you need it for. Don't stall: do the offline part of the task
   first (syntax validation, static review, payload preparation) and mark the live
   verification as pending.

## Local Docker instance

The DHIS2 core image is `dhis2/core:<version>` on Docker Hub, for example `dhis2/core:2.42.3`.
Tags such as `2.42.3` and `2.42` move: they point to the latest build of that
version. The immutable tags carry a timestamp. Pin at least a patch tag (`2.42.3`, not
`2.42`) so reruns and a version matrix test the release you name in the report. Images are multi-arch (amd64/arm64). The
image reads its database settings from `/opt/dhis2/dhis.conf`, and it needs PostgreSQL with
PostGIS. A minimal setup:

```properties
# dhis.conf
connection.dialect = org.hibernate.dialect.PostgreSQLDialect
connection.driver_class = org.postgresql.Driver
connection.url = jdbc:postgresql://db/dhis
connection.username = dhis
connection.password = dhis
```

```yaml
# docker-compose.yml — local and disposable, not for production
services:
  db:
    image: postgis/postgis:16-3.5      # any PostGIS image on a supported Postgres works
    environment: { POSTGRES_USER: dhis, POSTGRES_PASSWORD: dhis, POSTGRES_DB: dhis }
    volumes: [ "./seed:/docker-entrypoint-initdb.d:ro" ]   # optional *.sql.gz seed
    ports: [ "127.0.0.1:5432:5432" ]
  web:
    image: dhis2/core:${DHIS2_VERSION:-2.42.3}
    depends_on: [ db ]
    volumes: [ "./dhis.conf:/opt/dhis2/dhis.conf:ro" ]
    ports: [ "127.0.0.1:8080:8080" ]
```

The `docker-compose.yml` and `docker/DOCKERHUB.md` in the dhis2-core repository are the
reference setup, so check them when something here looks out of date. The official
production deployment lives in `dhis2/docker-deployment`.

**Seeds.**
- *Empty*: start without a seed. DHIS2 creates its schema on first boot (a few minutes) and
  an `admin` / `district` superuser. Use this for import tests where the target must start
  clean.
- *Sierra Leone demo*: put the dump in `./seed/` before the first `up`. Dumps are at
  `https://databases.dhis2.org/sierra-leone/<version>/dhis2-db-sierra-leone.sql.gz`, where
  `<version>` is a release such as `2.42` or `dev`. Use the dump that matches the image's
  minor version. An older dump on a newer image gets migrated by Flyway on first boot,
  which can take tens of minutes. Demo `admin` / `district` logs in, but on some demo
  versions it is not a full superuser (no `ALL`). Check `GET /api/me?fields=authorities`
  before relying on it.
- *A user-supplied dump*: only if the user gives it to you for this purpose.

**Readiness.** A running container is not a ready DHIS2: the container is up minutes
before DHIS2 answers, and the login page can render before the API works. Say this to the
user, and give them a readiness check that polls `GET /api/system/info` with credentials
until it returns 200 with a `version` (an unauthenticated ping or a log line is not
enough). Allow 2–5 minutes for an empty instance, and longer for a seeded one or a
migration. Two instances booting at the same time on one machine slow each other down a
lot. Start them one after another.

**Reset.** Run `docker compose down -v` and then `up`. A new database volume is the only
reliable reset. Deleting metadata through the API leaves audits, sequences and caches
behind.

**Version matrix.** Use one compose project per version (`-p dhis2-241`, `-p dhis2-242`) on
different host ports, with the same seed on each so results are comparable.

## Not the public play servers

`play.im.dhis2.org` is a shared public demo, not a test instance. Don't use it to verify
skill work (imports, indicators, app tests, fixes, version comparisons). Other people
change it constantly, it resets on its own schedule, and anything you write there is
public. That holds even when the user asks for it and even for read-only checks: the
data, the version and the analytics tables on play are not under your control, so a
result there proves nothing about the user's instance. Say why, and decline. The one
exception is reproducing a suspected DHIS2 bug for a ticket (dhis2-bug-report), where a
public, reproducible instance is the point.

Declining play is not the end of the task. Offer a concrete alternative (a local Docker
instance seeded with the Sierra Leone demo of the user's version, or a test instance the
user provides), and do the offline part now: write the exact payload (e.g. the indicator
JSON), the check to run first (`POST /api/indicators/expression/description` with the expression
as a text/plain body validates it and names its operands; verified in dhis2-core 2.42), the analytics run and the `/api/analytics` query that
reads the result, so the verification is one command away once an instance exists. Flag
anything you can already see is wrong, such as a UID that doesn't match the object named.

## Working rules on any test instance

- **Verify credentials first**: `GET /api/me` with Basic auth. DHIS2 locks accounts after
  repeated failed logins, so don't retry a bad password in a loop.
- **Check data recency before relying on relative periods.** Demo snapshots end at
  different dates, and `LAST_12_MONTHS` on a stale seed silently returns nothing.
- **Analytics is not live.** `/api/analytics` reads the analytics tables, so data shows
  there only after an analytics table run on that instance. A freshly restored seed may
  have none yet or stale ones (`lastAnalyticsTableSuccess` in `/api/system/info`). An
  aggregate indicator is evaluated at query time over those tables, so a changed
  expression needs no re-run (dhis2-core 2.42 `DataHandler`), but new data does. After writing data, run analytics
  (`POST /api/resourceTables/analytics`, then poll the task under `/api/system/tasks/ANALYTICS_TABLE/<id>`)
  before you query `/api/analytics`.
- **One heavy job at a time per machine** (boot, seed restore, analytics, large import).
- **A Tomcat restart takes about 1–2 minutes.** If requests suddenly fail with
  connection refused, re-probe `/api/system/info` before you debug your own code.
- **Clean up.** Delete what you created, or list what you left running (URL, version, why) in
  your final message. Never leave an instance running without saying so.
- **Keep instance details out of shared artefacts.** Internal hostnames, ports and
  credentials belong in session notes, not in committed reports or tickets.

## Browser access for the user

If the user needs to look at the instance or a dev server you started, bind it to a port
their browser can reach. Your environment may document forwarded ports for this. Tell
them the exact URL. A dev server on another origin also needs that origin in the
instance's CORS allowlist (recipe and the version-specific endpoint name: `dhis2-docs`
skill; the POST replaces the whole list).
