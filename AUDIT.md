# Cue table audit: method

Script: `scripts/audit_cue_tables.py`. Scope: the 29 locale cue tables `data/locales/<id>/cue_table_2027.csv`, which have 365 rows and 21 columns each (10,585 rows in all), checked against `data/locales/locale_profiles.csv` and the raw OISST files.

## Why this design

The tables are generated, not typed. A generator's faults come in clusters, not scattered:
- a wrong time zone or reference point spoils one whole locale;
- a wrong column formula spoils one whole column;
- a wrong edge case spoils one regime, such as events near midnight, the year wrap or the arc edges.

Random row-level errors come in only through input data, such as a gap in the raw SST.

An efficient audit therefore has three parts:

1. **Exhaustive automated checks.** Use them wherever a check is cheap. Recomputing 10,585 rows takes about 30 s, so there is no reason to sample, and no sampling error.
2. **Residuals kept as numbers, not only pass or fail.** A binary check sees only errors larger than its tolerance. The mean residual sees much smaller ones. With n rows and spread sd, it detects a bias of about 4·sd/√n.
   - Example: moon times, sd 0.5 min, 365 rows per locale. A per-locale bias of about 0.1 min is visible, far inside the 6-minute tolerance.
   - The report gives a z score for each family and locale against the pooled mean, and flags |z| > 4.
3. **Sampling only for the costly oracle**, the external USNO API, and stratifying the sample to match how faults cluster:
   - **One random date for every locale first.** A fault that spoils a whole locale is then found with certainty, whatever the overall sample size.
   - **Then the edge regimes:** moon events within 30 min of local midnight or noon, and the solstices.
   - **Then simple random rows** up to n.
   - **Size by a zero-defect plan:** n = ln(1−C) / ln(1−p₀). That gives 59 units for "below 5% at 95%" and 299 for "below 1%".
   - The report gives the Clopper-Pearson one-sided 95% upper bound for the defects actually seen.

Tier C does not need to find scattered errors: tier B already checks every row. Its job is the fault that tiers A and B share by construction. dark_window.py, astral and the NOAA solar equations all follow the same textbook algorithms, so they can agree with each other and all be wrong. USNO is the independent reference.

## Calling USNO

The USNO API has no endpoint for several dates at once (`rstt/oneday` takes one date), so the calls cannot be batched. Instead they are spaced and reused:

- **Spacing.** `--pause` seconds after every network call (default 2 s).
- **Backoff.** On HTTP 429, a 5xx or a timeout the call waits and retries, up to 5 times. The wait is the server's Retry-After when it sends one, otherwise pause × 2, × 4, × 8 and so on.
- **Cache.** Every response is saved in `data/external/usno_cache/` (gitignored), keyed by locale, date and the exact URL. A rerun, or a larger sample drawn with the same seed, reuses earlier calls, and an interrupted run resumes where it stopped. The 59-unit and 299-unit samples with the same seed start alike, so the 299 run reuses most of the 59 run's calls.
- **Bias flags need numbers.** A locale is tested for bias only with at least 10 residuals, so the few USNO units per locale give no z score.

## Tiers

| Tier | What | Rows | Oracle |
|---|---|---|---|
| A | Invariants | all | the table itself: date sequence, doy and month-day, time format; days_after_full = (age − SYN/2) mod SYN; illumination agrees with age; age steps by about 1 day; sunrise and sunset continuity; photoperiod = sunset − previous row's sunrise; dusk 45–140 min after sunset; full_dark ≤ astronomical night; SST range and day-to-day step, including the Dec→Jan wrap; watch = season AND moon; watch_season and watch_moon recomputed from the profile arcs (±1 day or ±0.15 d at an arc edge); profile SST mean, minimum and maximum |
| B | Independent recompute | all | astral 3.2 for the six sun and moon times and a coarse moon age; sst_clim_c re-derived from the raw OISST file (day-of-year mean, 15-day circular running mean) |
| C | External reference | sample (`--usno N`, 2 calls per unit) | USNO one-day API: sunrise, sunset, moonrise, moonset |

## Generator conventions the oracles must copy

- **Window.** Each rise and set column is the first event in the local noon-to-noon window that starts on the row's date. So "sunrise" is the next morning's sunrise.
- **Moon age.** Taken at the window's end.
- **Minutes.** Times are floored to the minute. USNO and astral moon times are rounded, so their residuals have a mean of about −0.5 min by design.

## Oracle holes, counted as `B:oracle_gap` rather than as defects

- **Hour 24.** astral rounds an event in the last half minute of a UTC day to hour 24 and raises an error.
- **Lost sun events.** astral's sun functions drop an event within seconds of 00:00 UTC. For those, the audit instead checks that the sun crosses the threshold within the tolerance of the table's time.

## Tolerances

| Check | Tolerance |
|---|---|
| Sun times | 2 min |
| Astronomical twilight | 3 min |
| Moon times | 6 min (different horizon and parallax models) |
| Photoperiod | 2 min |
| Daily age step | ±0.3 d (the moon's speed varies by about ±20%) |
| Illumination | 4 percentage points |
| SST recompute | 0.011 C (rounding) |
| SST daily step | 0.25 C |

## Baseline, 2026-11-10

- 0 defects in 10,585 rows, 28 s.
- 19 oracle gaps.
- No locale flagged for bias.
- Residual spread: sun mean +0.02 min, sd 0.45; moon −0.49 / 0.50; SST 0.000 / 0.003 C.

## Not covered

- The spawn calendar (`spawn_calendar_*.csv`), the light ladder and the temperature ladder files. They need their own invariants, the same way.
- Whether the observed windows in the profile are right. That is a check on the source records, not on the tables.

## Pinned at container start

After a clean audit the audited state is pinned in `data/data_manifest.json` with `scripts/data_manifest.py pin --audit-report <report.json>`. The pin step refuses a report that has defects or bias flags. The manifest holds a sha256 and size for each file, taken over the bytes with CRLF folded to LF, and it records the audit that passed.

**What is pinned (93 files on 2026-11-10, commit 54e23bf, after the 299-unit run):**
- the live spawn calendar and its meta file;
- `scripts/cue_params.json`;
- the 29 locale cue tables;
- `locale_profiles.csv`;
- the raw OISST files behind the tables;
- the temperature and light ladder files. These are pinned but not audited.

**At startup:** the tank service's command runs `data_manifest.py verify` before `conductor.py loop` and writes `data/data_manifest_check.json` (gitignored). `DATA_MANIFEST_MODE` in the compose environment sets what a mismatch does:
- `warn`, the default: the controller starts anyway. The mismatch is logged and comes back on every tick as the calendar problem `data_manifest_mismatch`, which raises the usual calendar alert.
- `enforce`: the service refuses to start, with exit 3.

After a deliberate change to any pinned file, run the audit again and re-pin.

