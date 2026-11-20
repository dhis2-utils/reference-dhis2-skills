Branch: perf/DHIS2-34567-orgunit-path-cache
PR title I plan to use: "perf: cache org unit paths in user org unit checks [DHIS2-34567]"

What I changed:
- DefaultOrganisationUnitService.isInUserHierarchy(uid, user) called
  organisationUnitStore.getByUid(uid).getPath() for every call. During a
  tracker import of 50,000 events this runs once per event -> 50k SELECTs.
- Now a request-scoped Caffeine cache (OrgUnitPathCache, max 10k entries)
  holds uid -> path. Same results, same access rules.

Numbers (my laptop, Sierra Leone demo DB 2.42, import of 50,000 synthetic events
via POST /api/tracker?async=false, 3 runs each, median):
- before: 212 s total, 50,113 org unit SELECTs (pg_stat_statements)
- after:   61 s total,    312 org unit SELECTs
- heap peak unchanged (~1.9 GB, JFR)
New JMH-free perf test: TrackerImportOrgUnitPerfTest#import50kEvents in dhis-test-performance.
Unit test OrgUnitPathCacheTest checks eviction and that a moved org unit is not served stale within a new request.
