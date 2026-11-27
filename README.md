# Reef cue tables

Spawning cue tables for reef aquaria, one per reef, in a fixed format
(`SCHEMA.md`, format version 1). The coral-spawning-controller downloads this
repository on its first start (its default `CUE_TABLES_URL` is https://github.com/realfakedoors-idaho/reef-cue-tables) and plays the table you pick on
its onboarding page.

**Live page: [Spawning Array](https://realfakedoors-idaho.github.io/reef-cue-tables/)**, the spawning records behind these
windows on shared season, lunar and after-sunset axes (served from this
repository's `gh-pages` branch).

* `locales/<locale_id>/cue_table_2027.csv`: 29 reefs, one row per day of 2027:
  sun, moon, full dark, sea temperature and the watch flags from that reef's own
  observed spawning nights. Times in the reference point's zone.
* `locales/locale_profiles.csv`, `locale_genus_windows.csv`,
  `locale_species_windows.csv`: grade, season and moon window per reef, genus and
  species.
* `locales/<locale_id>/light/`, `temp_ladder_2027.csv`: modelled light at depth
  and, where a logger passed the pairing check, in situ temperature.
* `sst/<locale_id>.csv`: the NOAA OISST day-of-year climatology each table uses.
* `reference/okinawa/`: the Okinawa *Stichodactyla gigantea* reference (JAZA tank
  spawns 2020 to 2022): cue parameters, a 792-day calendar from 2026-11-01 and
  its clear-sky light series.
* `arc_catalog.json`: the light and temperature curves a tank can follow, with
  their basis; `data_manifest.json`: the audited files and their fingerprints
  (method in `AUDIT.md`).
* `index.json`: every file, its kind, sha256 and where a controller installs it.

Check a copy (or your own fork after a change):

```
python tools/cue_schema.py index .      # after adding or changing a file
python tools/cue_schema.py validate .
```

Column meanings, grades and gaps: `locales/README.md`. Built from commit `10f8b02`
of the project repository.

## Limits

* Temperature is satellite-only (shape and timing, not reef level) except the
  Great Barrier Reef and French Polynesia.
* Windows come from coral records, not anemones; several reefs are thin, and the
  Caribbean reference point is a placeholder in open Gulf water.
* Nothing here has been validated on an animal.

## Licences

Data produced by this project: CC BY-NC 4.0 (`LICENSE`). `tools/`: MIT
(`LICENSE-CODE`). Third-party data: own terms (`ATTRIBUTION.md`).
