#!/usr/bin/env python3
"""cue_schema.py -- the reef cue-table format, version 1 (stdlib only).

    python cue_schema.py validate <dir>        check a cue-table repo against its index.json
    python cue_schema.py index <dir> [--source-commit SHA]
                                               (re)write <dir>/index.json from the files in it

A cue-table repo (for example reef-cue-tables) is a folder with an index.json at
its root. The index names every file, the kind of file it is, its sha256 and
size, and where a controller installs it (always under data/). The controller's
importer (cue_import.py) refuses a repo whose index does not validate, whose
hashes do not match, or whose major schema version it does not know.

index.json, schema "reef-cue-tables", schema_version "1.0":

    {"schema": "reef-cue-tables", "schema_version": "1.0",
     "generated_utc": "...", "source_commit": "...",
     "locales": [{"id": "gbr", "name": "...", "grade": "rich", "table": "locales/gbr/cue_table_2027.csv"}],
     "files": [{"path": "locales/gbr/cue_table_2027.csv", "kind": "cue_table",
                "install": "data/locales/gbr/cue_table_2027.csv",
                "sha256": "...", "bytes": 12345}]}

Hashes are over the bytes with CRLF folded to LF (as data_manifest.py does), so
a Windows checkout that flips line endings still matches. Kinds and the columns
each must have are in KINDS below (a file may have more columns, not fewer);
SCHEMA.md in the cue-table repo explains each column.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import posixpath
import re
import sys

SCHEMA = "reef-cue-tables"
SCHEMA_VERSION = "1.0"
SUPPORTED_MAJOR = 1

# kind -> (path pattern in the repo, install pattern, required CSV columns or JSON keys)
KINDS = {
    "cue_table": (r"^locales/([a-z0-9_]+)/cue_table_(\d{4})\.csv$", "data/locales/{0}/cue_table_{1}.csv",
                  ["date", "doy", "month_day", "sunrise", "sunset", "astro_dusk", "astro_dawn", "moonrise",
                   "moonset", "moon_illum_pct", "moon_age_d", "days_after_full", "photoperiod_min",
                   "full_dark_min", "temp_clim_c", "sst_clim_c", "watch_season", "watch_moon", "watch",
                   "watch_start_after_sunset_min", "watch_end_after_sunset_min"]),
    "temp_ladder": (r"^locales/([a-z0-9_]+)/temp_ladder_(\d{4})\.csv$", "data/locales/{0}/temp_ladder_{1}.csv",
                    ["date", "doy", "month_day", "sst_clim_c", "temp_l1_c"]),
    "light_ladder": (r"^locales/([a-z0-9_]+)/light/([a-z0-9_]+)_light_ladder_daily\.csv$",
                     "data/locales/{0}/light/{1}_light_ladder_daily.csv",
                     ["date", "par_clear_surface", "kd_par", "par_depth_l1"]),
    "light_model": (r"^locales/([a-z0-9_]+)/light/([a-z0-9_.-]+\.(?:json|csv))$", "data/locales/{0}/light/{1}", []),
    "profiles": (r"^locales/locale_profiles\.csv$", "data/locales/locale_profiles.csv",
                 ["locale_id", "name", "grade", "focus", "ref_lat", "ref_lon", "ref_tz_h", "season_start",
                  "season_end", "daf_lo", "daf_hi", "table"]),
    "genus_windows": (r"^locales/locale_genus_windows\.csv$", "data/locales/locale_genus_windows.csv",
                      ["locale_id", "genus", "grade", "n_nights", "season_start", "season_end", "daf_lo", "daf_hi"]),
    "species_windows": (r"^locales/locale_species_windows\.csv$", "data/locales/locale_species_windows.csv",
                        ["locale_id", "species", "genus", "grade", "n_nights", "season_start", "season_end",
                         "daf_lo", "daf_hi"]),
    "locale_defs": (r"^locales/locales\.csv$", "data/pseudosync/locales.csv", ["locale_id", "name"]),
    "records": (r"^locales/added_records\.csv$", "data/locales/added_records.csv",
                ["locale_id", "date_local", "species", "source_citation"]),
    "locale_meta": (r"^locales/([a-z0-9_]+)\.csv$", "data/locales/{0}.csv", ["locale_id"]),
    "sst": (r"^sst/([a-z0-9_]+)\.csv$", "data/external/oisst_locales/{0}.csv", ["date", "sst_c"]),
    "sst_meta": (r"^sst/([a-z0-9_]+)\.json$", "data/external/oisst_locales/{0}.json",
                 ["locale_id", "dataset", "period"]),
    "reference_params": (r"^reference/([a-z0-9_]+)/cue_params\.json$", "data/reference/cue_params.json",
                         ["reference_site", "sst_fit", "safety_band_c", "max_step_c_per_day", "watch",
                          "offset_schedule"]),
    "calendar": (r"^reference/([a-z0-9_]+)/(spawn_calendar_[0-9-]+)\.csv$", "data/{1}.csv",
                 ["date", "cue_date", "offset_days", "target_c", "photoperiod_min", "moon_illum_pct",
                  "days_after_full"]),
    "calendar_meta": (r"^reference/([a-z0-9_]+)/(spawn_calendar_[0-9-]+)\.meta\.json$", "data/{1}.meta.json",
                      ["columns"]),
    "arc_selection": (r"^reference/([a-z0-9_]+)/arc_selection\.json$", "data/arc_selection.json", []),
    "light_series": (r"^reference/([a-z0-9_]+)/([a-z0-9_]+_10min)\.csv$", "data/okinawa_light/{1}.csv",
                     ["sun_alt_deg", "moon_alt_deg", "moon_illum_pct", "full_dark", "total_lux_clear"]),
    "arc_catalog": (r"^arc_catalog\.json$", "data/arc_catalog.json", []),
    "manifest": (r"^data_manifest\.json$", "data/data_manifest.json", ["files"]),
    "doc": (r"^(?:locales/)?README\.md$", None, []),
}
# Files the index never lists (the repo's own front matter).
UNLISTED = {"index.json", "README.md", "SCHEMA.md", "AUDIT.md", "LICENSE", "LICENSE-CODE", "ATTRIBUTION.md",
            ".gitignore"}
INSTALL_PREFIXES = ("data/locales/", "data/external/oisst_locales/", "data/reference/", "data/okinawa_light/",
                    "data/pseudosync/locales.csv", "data/arc_catalog.json", "data/arc_selection.json",
                    "data/data_manifest.json", "data/spawn_calendar_")


def sha(path: str) -> tuple[str, int]:
    with open(path, "rb") as fh:
        b = fh.read().replace(b"\r\n", b"\n")
    return hashlib.sha256(b).hexdigest(), len(b)


def classify(rel: str):
    """(kind, install path) for a repo-relative path, or (None, None)."""
    for kind, (pat, inst, _cols) in KINDS.items():
        m = re.match(pat, rel)
        if m:
            return kind, (inst.format(*m.groups()) if inst else None)
    return None, None


def safe_install(path: str) -> bool:
    if not path or path.startswith("/") or "\\" in path or ":" in path:
        return False
    norm = posixpath.normpath(path)
    return norm == path and ".." not in norm.split("/") and norm.startswith(INSTALL_PREFIXES)


def _check_columns(path: str, kind: str, need: list) -> list[str]:
    errs = []
    if not need:
        return errs
    if path.endswith(".json"):
        try:
            with open(path, encoding="utf-8") as fh:
                obj = json.load(fh)
        except ValueError as e:
            return [f"not valid JSON: {e}"]
        missing = [k for k in need if not isinstance(obj, dict) or k not in obj]
        if missing:
            errs.append("missing keys: " + ", ".join(missing))
        return errs
    with open(path, encoding="utf-8", newline="") as fh:
        rd = csv.reader(fh)
        header = next(rd, [])
        rows = list(rd)
    missing = [c for c in need if c not in header]
    if missing:
        errs.append("missing columns: " + ", ".join(missing))
    if not rows:
        errs.append("no rows")
    if kind == "cue_table" and not missing and rows:
        di = header.index("date")
        try:
            dates = [dt.date.fromisoformat(r[di]) for r in rows]
        except ValueError as e:
            return errs + [f"bad date: {e}"]
        if any((b - a).days != 1 for a, b in zip(dates, dates[1:])):
            errs.append("dates are not one per day without gaps")
        if len(dates) not in (365, 366):
            errs.append(f"{len(dates)} rows, expected a full year")
    if kind in ("cue_table", "sst", "temp_ladder") and not missing and rows:
        col = "sst_c" if kind == "sst" else "sst_clim_c"
        ci = header.index(col)
        for r in rows:
            v = r[ci].strip() if ci < len(r) else ""
            if v:
                try:
                    f = float(v)
                except ValueError:
                    errs.append(f"{col} not a number: {v!r}")
                    break
                if not -2.0 <= f <= 40.0:
                    errs.append(f"{col} out of range: {f}")
                    break
    return errs


def validate(root: str) -> tuple[dict | None, list[str]]:
    """(index, problems). An empty problem list means the repo is usable."""
    errs = []
    ip = os.path.join(root, "index.json")
    if not os.path.exists(ip):
        return None, ["no index.json"]
    try:
        with open(ip, encoding="utf-8") as fh:
            idx = json.load(fh)
    except ValueError as e:
        return None, [f"index.json is not valid JSON: {e}"]
    if idx.get("schema") != SCHEMA:
        errs.append(f"schema is {idx.get('schema')!r}, expected {SCHEMA!r}")
    ver = str(idx.get("schema_version", ""))
    if not re.match(r"^\d+\.\d+$", ver) or int(ver.split(".")[0]) != SUPPORTED_MAJOR:
        errs.append(f"schema_version {ver!r} not supported (this reader knows {SUPPORTED_MAJOR}.x)")
        return idx, errs
    seen_install = {}
    listed = set()
    for e in idx.get("files", []):
        rel, kind, inst = e.get("path", ""), e.get("kind"), e.get("install")
        listed.add(rel)
        if kind not in KINDS:
            errs.append(f"{rel}: unknown kind {kind!r}")
            continue
        if inst is not None and not safe_install(inst):
            errs.append(f"{rel}: unsafe install path {inst!r}")
            continue
        if inst in seen_install:
            errs.append(f"{rel}: install path {inst} also used by {seen_install[inst]}")
        seen_install[inst] = rel
        p = os.path.join(root, *rel.split("/"))
        if posixpath.normpath(rel) != rel or rel.startswith("/") or ".." in rel.split("/"):
            errs.append(f"{rel}: unsafe path")
            continue
        if not os.path.isfile(p):
            errs.append(f"{rel}: listed but missing")
            continue
        h, n = sha(p)
        if h != e.get("sha256"):
            errs.append(f"{rel}: sha256 does not match the index")
            continue
        errs += [f"{rel}: {m}" for m in _check_columns(p, kind, KINDS[kind][2])]
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x != ".git"]
        for f in files:
            rel = os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
            if rel not in listed and rel not in UNLISTED and not rel.startswith("tools/"):
                errs.append(f"{rel}: in the repo but not in index.json")
    tables = {e["path"] for e in idx.get("files", []) if e.get("kind") == "cue_table"}
    for loc in idx.get("locales", []):
        if loc.get("table") and loc["table"] not in tables:
            errs.append(f"locale {loc.get('id')}: table {loc['table']} is not a listed cue_table")
    return idx, errs


def build_index(root: str, source_commit: str = "", locales: list | None = None) -> dict:
    files = []
    for d, dirs, fs in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in (".git", "tools"))
        for f in sorted(fs):
            rel = os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
            if rel in UNLISTED:
                continue
            kind, inst = classify(rel)
            if kind is None:
                raise SystemExit(f"cue_schema: no kind for {rel}")
            h, n = sha(os.path.join(d, f))
            files.append({"path": rel, "kind": kind, "install": inst, "sha256": h, "bytes": n})
    idx = {"schema": SCHEMA, "schema_version": SCHEMA_VERSION,
           "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "source_commit": source_commit, "locales": locales or [], "files": files}
    with open(os.path.join(root, "index.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(idx, fh, indent=1)
        fh.write("\n")
    return idx


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="reef cue-table format v1")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("dir")
    i = sub.add_parser("index")
    i.add_argument("dir")
    i.add_argument("--source-commit", default="")
    a = ap.parse_args(argv)
    if a.cmd == "index":
        idx = build_index(a.dir, a.source_commit)
        print(f"index.json: {len(idx['files'])} files")
        return 0
    idx, errs = validate(a.dir)
    for e in errs:
        print("  " + e)
    n = len(idx.get("files", [])) if idx else 0
    print(f"{'OK' if not errs else 'FAILED'}: {n} files, {len(errs)} problems")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
