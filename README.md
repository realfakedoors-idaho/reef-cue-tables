# Reef cue tables

Spawning cue tables for reef aquaria, one per reef, in a fixed format
(`SCHEMA.md`, format version 1). The coral-spawning-controller downloads this
repository on its first start (its default `CUE_TABLES_URL` is https://github.com/realfakedoors-idaho/reef-cue-tables) and plays the table you pick on
its onboarding page.

**Live page: [Spawning Array](https://realfakedoors-idaho.github.io/reef-cue-tables/)**, the spawning records behind these
windows on shared season, lunar and after-sunset axes (served from this
repository's `gh-pages` branch).

## Quests: help fill the tables

A community effort: every dated spawning night makes a reef's window sharper.
Open an issue to claim one or to ask, then send a pull request. (The full quest
list, including controller work, is at the top of the coral-spawning-controller
README.)

1. **More spawning nights and new reefs.** Add dated spawns (species, date,
   start time after sunset, site, citation, licence) to
   `locales/added_records.csv`; reefs with thin data and reefs not covered yet
   (Seychelles, Lakshadweep, Cook Islands, subtropical eastern Australia) need
   them most. Facts and citations only, never copied text or figures.
2. **Better temperature and light.** Most tables use satellite sea temperature
   (right timing, rough level): in situ reef logger records with an open
   licence, and better light data, improve them.
3. **Aquarium spawns.** Dated spawns from aquaria, starting with the Horniman
   Coral Spawning Project (Jamie Craggs): from the papers by someone with lawful
   access, or from the authors with permission to publish under CC BY-NC 4.0.
   Popular aquarium corals with no record here yet: birdsnest (*Seriatopora*,
   a brooder that releases larvae rather than spawning), the torch coral
   (*Euphyllia glabrescens*) and frogspawn (*Fimbriaphyllia divisa*).
4. **A daily temperature pattern.** An hour-by-hour water temperature pattern
   on spawning reefs, from loggers, to replace the flat daily offsets.
5. **Audit and correct.** Check a table against your own records or the
   sources and report what is off (`AUDIT.md` has the method).
6. **Two-season and split spawning.** Some species spawn in two seasons about
   six months apart (Western Australia, the Maldives, Palau, Singapore); others
   split one season across two full moons in some years. Work out a spawning
   pattern per species and reef from the dated nights (one season, two
   seasons, split, monthly brooder, unknown), give a reef with two seasons two
   windows, and add a moon rule for split years.
7. **A standard pull request format.** One format for changes to the tables
   and to the captive and wild spawning records, in two strengths. **Adding**
   (loose): new nights, reefs or aquarium spawns with the required facts
   (species, date, site, start time if known, captive or wild, citation,
   licence) and the format check passing; reviewers fix small gaps. **Editing**
   (strict): any change to a value already here; one change per pull request,
   old and new value, the reason and source for each, the audit re-run and
   `data_manifest.json` re-pinned. Deliver it as pull request templates and an
   automatic check.

After any change: `python tools/cue_schema.py index .` then
`python tools/cue_schema.py validate .`

## What is in it

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

Column meanings, grades and gaps: `locales/README.md`. Built from commit `59ff0c1`
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
