#!/usr/bin/env python3
"""Inspect GSE310779 liver samples and outlier mapping."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "age_cheetah" / "GSE310779_series_matrix.txt"

MANUAL = [
    "ET0394TOX00092", "ET0394TOX00094", "ET0394TOX00063", "ET0394TOX00095",
    "ET0394TOX00084", "ET0394TOX00080", "ET0394TOX00069",
]


def parse_field(lines: list[str], tag: str) -> list[str]:
    for line in lines:
        if line.startswith(tag + "\t"):
            return [p.strip('"') for p in line.split("\t")[1:]]
    return []


def main() -> None:
    lines = GEO.read_text(encoding="utf-8", errors="replace").splitlines()[:80]
    gsm = parse_field(lines, "!Sample_geo_accession")
    titles = parse_field(lines, "!Sample_title")
    tissues = parse_field(lines, "!Sample_source_name_ch1")
    supp = parse_field(lines, "!Sample_supplementary_file")

    print("Liver samples:")
    for g, t, ti, s in zip(gsm, titles, tissues, supp):
        if ti.lower() != "liver":
            continue
        hits = [sid for sid in MANUAL if sid in s or sid in t or sid in g]
        print(f"  {g}  age_title={t!r}  sid_hit={hits}  supp_tail={s[-70:]}")

    print("\nSupplementary path contains ET0394:", sum("ET0394" in x for x in supp))


if __name__ == "__main__":
    main()
