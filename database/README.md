# India bird-migration evidence database

`india_bird_migration.sqlite` is a provenance-first database, not a claim that
every line is a raw GPS path.

## Evidence labels

- `observed_telemetry_published`: a telemetry study exists, but its reusable
  location fixes were not located as an open download.
- `published_pathway`: a route is stated in a publication; it is not an
  individual trajectory.
- `ringing_inventory`: an organisation holds ringing data, but has not
  published a reusable bulk export.
- `seasonal_occurrence_protocol`: an approved recipe for deriving monthly
  occurrence corridors from a GBIF download.

## What is currently included

The database contains explicit published evidence from WII, BNHS and ZSI, and
GBIF query definitions for six India-linked species.  It preserves source
URLs, raw-data availability and reuse status.  Only locality-level route
segments that are directly described by a publication receive geometry.

## What must happen before adding a true track

Insert an `raw_track_imports` row with the public study URL/DOI, licence,
access date and checksum.  Do not infer an individual route from a paper title
or from seasonal occurrence points.

## Rebuild

```sh
python3 database/build_migration_db.py
sqlite3 database/india_bird_migration.sqlite '.tables'
```

## GBIF ingestion rule

Request a GBIF download using each entry in `gbif_query_definitions`. Retain
only CC0/CC BY records, preserve the resulting GBIF download DOI, and label
the outcome as `seasonal occurrence inference`.
