# Locale cue tables

Built by `python scripts/locale_cues.py` (generated 2026-11-06) from `data/pseudosync/locales.csv`. Okinawa's own cue table stays `data/meta_table.csv` and `data/spawn_calendar_*.csv`; the generator reproduces its sun and moon columns for 2027 exactly (3,285 cells compared, no mismatch), so the other tables are the same method at a different point.

Nothing here is moved onto the Okinawa calendar. Each table is the locale's own sky and the locale's own observed window, on the locale's own dates (year 2027, one row per day, times in the reference point's zone, the longitude rounded to a whole hour).

## Files

* `locale_profiles.csv`: one row per locale, ranked by records.
* `locale_genus_windows.csv`: one row per locale and genus with at least 8 spawning nights. Use this, not the pooled window, once a target genus is chosen: species key on their own nights.
* `<locale_id>/cue_table_2027.csv`: the sky table with watch flags, for every locale except Okinawa.

## What a window means

The unit is the spawning **night** (one site on one date). Records are the Coral Spawning Database in situ rows, the Atlantic and other-region rows, and wild anemone events from the hub (captive tank events are left out). The moon age is days after the last true full moon at the site's sunset.

| Column | Meaning |
|---|---|
| `grade` | `rich` 40 or more nights, `usable` 10 to 39, `thin` under 10 (an outline only) |
| `season_start` to `season_end` | shortest arc of the year holding 80 percent of the nights (can cross New Year) |
| `daf_lo` to `daf_hi` | the same for the moon's cycle, days after full moon |
| `R_season`, `R_lunar` | 0 means spread evenly, 1 means every night on one day |
| `focus` | `focused` when both R are at least 0.6; `broad` means the locale mixes species that spawn in different seasons or moon phases, so use its genus rows |
| `min_p10`, `min_p50`, `min_p90` | minutes after sunset when spawning began (rows with a start time; blank under 5 rows) |
| `dark_h_median` | hours of full dark (sun below 18 degrees and moon down) in the 18 h after sunset on the spawning nights |
| `watch` (table) | the night is in the season arc and the moon arc; blank for a `thin` locale |

## Gaps

* **Temperature, two columns that are never mixed.** `temp_clim_c` is the reef's own water temperature (level 0): held only for the Great Barrier Reef (Davies Reef AIMS daily climatology, 1998 to 2015) and empty elsewhere. A third, `temp_l1_c` (level 1, in situ logger), sits in `<locale_id>/temp_ladder_2027.csv` for the locales whose logger passed the pairing check (`scripts/temp_logger_pair.py`): the Great Barrier Reef (Havannah Island) and French Polynesia (Moorea LTER2). The setup page offers it as "reef logger". `sst_clim_c` is satellite sea-surface temperature (level 4): the day-of-year mean of NOAA OISST v2.1 at the nearest 25 km sea cell to the reference point, 2011 to 2020, smoothed with a 15-day running mean (`scripts/fetch_locale_sst.py`, raw files in `data/external/oisst_locales/`, cell and fetch date in each `.json`). It gives shape and timing; the level can differ from the reef by a few tenths of a degree, so do not set a tank to it as if it were a reef reading. Profile columns `sst_*` give the annual mean and range, and the value and weekly rise at the spawning peak. Cross-check at the Great Barrier Reef: OISST minus the Davies in situ climatology has mean 0.00 C and spread 0.6 C (range -1.1 to +0.9), from different cells and years. Okinawa's `sst_*` columns come from the NOAA CRW 5 km file already held (2020 to 2022, three years only).
* **Light**: sun and moon are computed. Daylight brightness and cloud are held for Okinawa only (`data/okinawa_light/`).
* **Reference point**: the median position of the locale's spawning nights. For wide locales (see the lat and lon spread columns: Red Sea, Indian Ocean, Melanesia, Polynesia) one point stands for all of it.
* **Caribbean reference point** is the median of Belize, the Florida Keys and the Flower Garden Banks, which falls in the open Gulf of Mexico: its sky is a fair stand-in for the Florida Keys and the Gulf banks, but its SST is open-water, not reef. Treat it as a placeholder until a single Caribbean site is chosen.
* **Subtropical eastern Australia** has no table: its one record has no year.
