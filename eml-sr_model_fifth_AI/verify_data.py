#!/usr/bin/env python3
"""Verify data/age_cheetah inputs without loading the full MCDB beta matrix."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "age_cheetah"
GEO = DATA / "GSE310779_series_matrix.txt"
MCDB = DATA / "GSE223748_datBetaNormalized.csv"

MCDB_CHEETAH_BLOOD = [
    "205128010039_R03C02",
    "205128010039_R02C02",
    "205128010045_R05C01",
    "205128010045_R04C01",
    "205128010045_R03C01",
    "204529320103_R02C01",
    "204529320041_R04C02",
    "204529320032_R04C01",
    "204529320039_R06C01",
    "204529320031_R04C02",
    "204529320040_R04C02",
    "204551090023_R06C01",
    "204551090016_R06C01",
    "203867110006_R04C01",
]


def parse_geo_field(lines: list[str], tag: str) -> list[str]:
    for line in lines:
        if line.startswith(tag + "\t"):
            return [p.strip('"') for p in line.split("\t")[1:]]
    return []


def main() -> None:
    assert GEO.exists(), GEO
    assert MCDB.exists(), MCDB

    header_lines = GEO.read_text(encoding="utf-8", errors="replace").splitlines()[:80]
    gsm = parse_geo_field(header_lines, "!Sample_geo_accession")
    titles = parse_geo_field(header_lines, "!Sample_title")
    tissues = parse_geo_field(header_lines, "!Sample_source_name_ch1")

    print("GSE310779 samples:", len(gsm))
    print("tissues:", Counter(t.lower() for t in tissues))

    with MCDB.open("r", encoding="utf-8", errors="replace") as f:
        mcdb_header = f.readline()
    found = [cid for cid in MCDB_CHEETAH_BLOOD if cid in mcdb_header]
    print("MCDB cheetah blood in header:", len(found), "/", len(MCDB_CHEETAH_BLOOD))
    if len(found) != len(MCDB_CHEETAH_BLOOD):
        missing = set(MCDB_CHEETAH_BLOOD) - set(found)
        raise SystemExit(f"Missing MCDB IDs: {missing}")

    print("OK: data/age_cheetah layout matches paper sources.")


if __name__ == "__main__":
    main()
