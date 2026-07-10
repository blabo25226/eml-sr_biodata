#!/usr/bin/env python3
"""Extract MCDB cheetah blood (14) from GSE223748 without loading full matrix."""
from __future__ import annotations

import csv
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "age_cheetah"
MCDB = DATA / "GSE223748_datBetaNormalized.csv"
OUT_BETA = DATA / "cheetah_mamconsortium_betas.csv"
OUT_META = DATA / "mcdb_cheetah_blood_meta.csv"

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


def fetch_mcdb_metadata(chip_ids: list[str]) -> list[dict]:
    """Fetch age/sex from GEO (batch search + per-sample accession)."""
    import json
    import urllib.parse

    term = urllib.parse.quote("GSE223748 AND Cheetah AND Blood")
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=gds&term={term}&retmax=20&retmode=json"
    )
    time.sleep(0.4)
    data = json.loads(urllib.request.urlopen(url, timeout=60).read())
    gids = [x for x in data["esearchresult"]["idlist"] if x != "200223748"]

    url2 = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gds&id="
        + ",".join(gids)
        + "&retmode=json"
    )
    time.sleep(0.4)
    summ = json.loads(urllib.request.urlopen(url2, timeout=60).read())["result"]

    chip_to_gsm: dict[str, str] = {}
    for gid in gids:
        title = summ[gid].get("title", "")
        chip = title.split()[-1]
        chip_to_gsm[chip] = summ[gid].get("accession", "")

    rows: list[dict] = []
    for chip in chip_ids:
        gsm = chip_to_gsm.get(chip)
        if not gsm:
            raise RuntimeError(f"GEO sample not found for chip {chip}")
        url3 = f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={gsm}&form=text&view=full"
        time.sleep(0.35)
        text = urllib.request.urlopen(url3, timeout=60).read().decode("utf-8", errors="replace")
        age = None
        sex_raw = None
        for line in text.splitlines():
            if line.startswith("!Sample_characteristics_ch1") and "age:" in line.lower():
                age = float(line.split(":", 1)[1].strip())
            if line.startswith("!Sample_characteristics_ch1") and "female:" in line.lower():
                sex_raw = line.split(":", 1)[1].strip()
        if age is None:
            raise RuntimeError(f"age missing for {chip} ({gsm})")
        if sex_raw in ("0", "1"):
            sex = "F" if sex_raw == "1" else "M"
        else:
            sex = "NA"
        rows.append(
            {
                "chip_id": chip,
                "SID": f"X{chip}",
                "GSM": gsm,
                "Age": age,
                "Sex": sex,
                "Study": "MammCon",
                "Tissue": "blood",
            }
        )
    return rows


def extract_beta_columns() -> None:
    with MCDB.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        cols = [h.strip('"') for h in header]
        col_idx = {c: i for i, c in enumerate(cols)}
        indices = [col_idx[c] for c in MCDB_CHEETAH_BLOOD]
        missing = [c for c in MCDB_CHEETAH_BLOOD if c not in col_idx]
        if missing:
            raise SystemExit(f"Missing columns: {missing}")

        with OUT_BETA.open("w", encoding="utf-8", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(["X"] + MCDB_CHEETAH_BLOOD)
            for row in reader:
                if not row:
                    continue
                cpg = row[0].strip('"')
                writer.writerow([cpg] + [row[i] for i in indices])
    print("Wrote", OUT_BETA)


def main() -> None:
    extract_beta_columns()
    meta = fetch_mcdb_metadata(MCDB_CHEETAH_BLOOD)
    import pandas as pd

    pd.DataFrame(meta).to_csv(OUT_META, index=False)
    print("Wrote", OUT_META, "n=", len(meta))


if __name__ == "__main__":
    main()
