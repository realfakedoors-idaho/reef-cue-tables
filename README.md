# Spawning Array

Spawning records from every reef on shared season, lunar and after-sunset axes,
in one self-contained page (`index.html`), live at
<https://realfakedoors-idaho.github.io/reef-cue-tables/>. This is the
`gh-pages` branch of the reef-cue-tables repository; GitHub Pages serves it from
the root. The controller downloads only `main`, so the page never reaches a tank.

The reef cue tables built from these records:
[reef-cue-tables](https://github.com/realfakedoors-idaho/reef-cue-tables).

Built from commit `64dfd10` of the project repository by
`scripts/build_master_sync.py`, which refuses to build when any cited source or
data column lacks a licence, terms link or attribution. The page ends with a
"Data, licences and status" footer.

## Licences

* Page code (HTML, CSS, JavaScript): MIT (`LICENSE`).
* Compiled data: CC BY-NC 4.0 (`LICENSE-DATA`). Non-commercial because five
  iNaturalist observations on the page are CC BY-NC.
* Third-party sources: their own terms, `ATTRIBUTION.md` and
  `sources/page_licenses.csv` (licence, terms link, attribution, basis).

## Limits

* Six cited sources have no open licence; the page shows only dates, species
  and sites from them, each with its citation.
* Only four *Stichodactyla gigantea* spawning events exist (JAZA, 2020 to 2022).
* Rows do not carry a per-row verification status.
