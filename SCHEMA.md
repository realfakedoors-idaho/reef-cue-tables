# Cue-table format, version 1

Schema name `reef-cue-tables`, `schema_version` `1.0`. A reader accepts any 1.x
and refuses another major version. The reference reader and validator is
`tools/cue_schema.py` (the same file as the controller's `scripts/cue_schema.py`).

## index.json

```json
{"schema": "reef-cue-tables", "schema_version": "1.0",
 "generated_utc": "2026-11-25T00:00:00Z", "source_commit": "abc1234",
 "locales": [{"id": "gbr", "name": "Great Barrier Reef", "grade": "rich",
              "table": "locales/gbr/cue_table_2027.csv"}],
 "files": [{"path": "locales/gbr/cue_table_2027.csv", "kind": "cue_table",
            "install": "data/locales/gbr/cue_table_2027.csv",
            "sha256": "...", "bytes": 12345}]}
```

* Every file in the repository is listed, except the front matter (`README.md`,
  `SCHEMA.md`, `AUDIT.md`, the licence files, `ATTRIBUTION.md`, `tools/`).
* `sha256` is over the bytes with CRLF folded to LF.
* `install` is where a controller copies the file, always under `data/`, never
  with `..`; `null` for documents that are not installed.
* `kind` decides the path pattern, the install path and the required columns
  (a file may have more columns, never fewer).

## Kinds

| Kind | Path | Required columns or keys |
|---|---|---|
| `cue_table` | `locales/<id>/cue_table_<year>.csv` | date, doy, month_day, sunrise, sunset, astro_dusk, astro_dawn, moonrise, moonset, moon_illum_pct, moon_age_d, days_after_full, photoperiod_min, full_dark_min, temp_clim_c, sst_clim_c, watch_season, watch_moon, watch, watch_start_after_sunset_min, watch_end_after_sunset_min. One row per day of one whole year, no gaps; temperatures in C between -2 and 40 |
| `temp_ladder` | `locales/<id>/temp_ladder_<year>.csv` | date, doy, month_day, sst_clim_c, temp_l1_c |
| `light_ladder` | `locales/<id>/light/<id>_light_ladder_daily.csv` | date, par_clear_surface, kd_par, par_depth_l1 |
| `light_model` | `locales/<id>/light/*.json` or `*.csv` | (model parameters, free form) |
| `profiles` | `locales/locale_profiles.csv` | locale_id, name, grade, focus, ref_lat, ref_lon, ref_tz_h, season_start, season_end, daf_lo, daf_hi, table |
| `genus_windows` | `locales/locale_genus_windows.csv` | locale_id, genus, grade, n_nights, season_start, season_end, daf_lo, daf_hi |
| `species_windows` | `locales/locale_species_windows.csv` | locale_id, species, genus, grade, n_nights, season_start, season_end, daf_lo, daf_hi |
| `locale_defs` | `locales/locales.csv` | locale_id, name |
| `records` | `locales/added_records.csv` | locale_id, date_local, species, source_citation |
| `sst` | `sst/<id>.csv` | date, sst_c |
| `sst_meta` | `sst/<id>.json` | locale_id, dataset, period |
| `reference_params` | `reference/<id>/cue_params.json` | reference_site, sst_fit, safety_band_c, max_step_c_per_day, watch, offset_schedule |
| `calendar` | `reference/<id>/spawn_calendar_<start>.csv` | date, cue_date, offset_days, target_c, photoperiod_min, moon_illum_pct, days_after_full |
| `calendar_meta` | `reference/<id>/spawn_calendar_<start>.meta.json` | columns |
| `arc_selection` | `reference/<id>/arc_selection.json` | |
| `light_series` | `reference/<id>/*_10min.csv` | sun_alt_deg, moon_alt_deg, moon_illum_pct, full_dark, total_lux_clear |
| `arc_catalog` | `arc_catalog.json` | |
| `manifest` | `data_manifest.json` | files |
| `doc` | `locales/README.md` | (not installed) |

Column meanings: `locales/README.md`. Watch flags: `watch_season` (the night is
in the reef's season arc), `watch_moon` (in its moon arc), `watch` (both; blank
for a thin reef).

## Adding a reef

1. Add the files under `locales/<id>/` (and `sst/<id>.*`), with the columns above.
2. Add its row to `locales/locale_profiles.csv` and `locales/locales.csv`.
3. `python tools/cue_schema.py index .`, then `python tools/cue_schema.py validate .`
4. Audited tables are also pinned in `data_manifest.json` (method in `AUDIT.md`);
   a controller warns at start when a pinned file does not match.
