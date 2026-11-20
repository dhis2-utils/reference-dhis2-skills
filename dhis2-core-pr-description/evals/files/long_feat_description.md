## Summary

This pull request introduces a brand new capability to the analytics export functionality that has been requested by a number of users over a long period of time. Basically, in order to make it possible for users to export analytics data in Parquet format, we have added a new renderer and wired it into the existing analytics controller infrastructure. This is a significant improvement for data scientists and analysts who simply want to load DHIS2 data into tools like pandas, DuckDB or Spark without having to convert from CSV first, which was previously very slow and error-prone.

## Changes

- Added `ParquetGridRenderer` in `dhis-service-analytics` that takes a `Grid` and writes it as Apache Parquet using the parquet-avro library
- Added new endpoint `GET /api/analytics.parquet` in `AnalyticsController`
- Added new endpoint `GET /api/analytics/events/query/{program}.parquet` in `EventQueryController`
- Added `parquet-avro` 1.14.1 and `hadoop-common` (with most transitive deps excluded) to `dhis-service-analytics/pom.xml`
- Column types are mapped from `ValueType`: numbers become DOUBLE, dates become TIMESTAMP_MILLIS, everything else is STRING
- Metadata (the `metaData` section of the JSON response) is not included in the Parquet file because Parquet has no natural place for it
- Updated the OpenAPI annotations so the new media type `application/vnd.apache.parquet` appears in the docs
- Refactored `GridUtils.toCsv` slightly so that both renderers share the header logic

## Testing

- Added `ParquetGridRendererTest` with 14 unit tests covering all value types
- Added `AnalyticsControllerParquetTest` that calls the endpoint and reads the file back with parquet-avro
- Manually tested with DuckDB on the Sierra Leone demo database: `SELECT * FROM 'analytics.parquet'` works and returns 1,240 rows for the ANC dashboard query
- Ran the full analytics test suite locally, all green

## Notes

The war file grows by about 9 MB because of hadoop-common. We tried to exclude more, but parquet-avro needs `org.apache.hadoop.conf.Configuration` at runtime. In the future we could look at parquet-java's new hadoop-free API once it is released. Also note that very large grids are written fully in memory before streaming, so this is not suitable for exports above a few million rows.

Jira: DHIS2-23456
