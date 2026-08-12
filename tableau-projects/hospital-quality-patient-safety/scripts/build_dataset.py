#!/usr/bin/env python3
"""Download, validate, and prepare CMS hospital quality data for Tableau."""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

DATASETS = {
    "hospital_general": "xubh-q36u",
    "complications_deaths": "ynj2-r877",
    "unplanned_visits": "632h-zaca",
}


def download(dataset_id: str) -> pd.DataFrame:
    url = (
        "https://data.cms.gov/provider-data/api/1/datastore/query/"
        f"{dataset_id}/0/download?format=csv"
    )
    with urlopen(url, timeout=180) as response:
        content = response.read().decode("utf-8-sig")
    return pd.read_csv(io.StringIO(content), dtype=str, low_memory=False)


def snake_case(columns: pd.Index) -> list[str]:
    return (
        columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
        .tolist()
    )


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.replace({"Not Available": None, "Not Applicable": None, "": None}), errors="coerce")


def numeric_or_zero(frame: pd.DataFrame, column: str) -> pd.Series:
    """Return a numeric source column, or a zero-valued aligned Series."""
    if column not in frame:
        return pd.Series(0.0, index=frame.index)
    return to_numeric(frame[column]).fillna(0)


def national_flag_counts(frame: pd.DataFrame, prefix: str) -> pd.DataFrame:
    required = {"facility_id", "compared_to_national"}
    if not required.issubset(frame.columns):
        return pd.DataFrame(columns=["facility_id", f"{prefix}_better", f"{prefix}_same", f"{prefix}_worse"])
    labels = frame["compared_to_national"].fillna("").str.lower()
    work = pd.DataFrame({
        "facility_id": frame["facility_id"],
        f"{prefix}_better": labels.str.contains("better|lower than|fewer than", regex=True).astype(int),
        f"{prefix}_same": labels.str.contains("no different|same as|average", regex=True).astype(int),
        f"{prefix}_worse": labels.str.contains("worse|higher than|more than", regex=True).astype(int),
    })
    return work.groupby("facility_id", as_index=False).sum()


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    retrieved = datetime.now(timezone.utc)
    stamp = retrieved.strftime("%Y%m%dT%H%M%SZ")

    frames: dict[str, pd.DataFrame] = {}
    for name, dataset_id in DATASETS.items():
        frame = download(dataset_id)
        frame.columns = snake_case(frame.columns)
        frame.to_csv(RAW / f"{name}_{stamp}.csv", index=False)
        frames[name] = frame

    hospital = frames["hospital_general"].copy()
    if "facility_id" not in hospital or hospital["facility_id"].duplicated().any():
        raise ValueError("Hospital General Information must contain one unique row per facility_id")

    numeric_columns = [
        "hospital_overall_rating",
        "count_of_facility_mort_measures", "count_of_mort_measures_better", "count_of_mort_measures_no_different", "count_of_mort_measures_worse",
        "count_of_facility_safety_measures", "count_of_safety_measures_better", "count_of_safety_measures_no_different", "count_of_safety_measures_worse",
        "count_of_facility_readm_measures", "count_of_readm_measures_better", "count_of_readm_measures_no_different", "count_of_readm_measures_worse",
    ]
    for column in numeric_columns:
        if column in hospital:
            hospital[column] = to_numeric(hospital[column])

    hospital["mortality_worse_flag"] = numeric_or_zero(hospital, "count_of_mort_measures_worse").gt(0).astype(int)
    hospital["safety_worse_flag"] = numeric_or_zero(hospital, "count_of_safety_measures_worse").gt(0).astype(int)
    hospital["readmission_worse_flag"] = numeric_or_zero(hospital, "count_of_readm_measures_worse").gt(0).astype(int)
    hospital["domain_worse_flags"] = hospital[["mortality_worse_flag", "safety_worse_flag", "readmission_worse_flag"]].sum(axis=1)

    complications = national_flag_counts(frames["complications_deaths"], "detailed_outcome")
    readmissions = national_flag_counts(frames["unplanned_visits"], "detailed_readmission")
    hospital = hospital.merge(complications, on="facility_id", how="left").merge(readmissions, on="facility_id", how="left")

    rating = hospital["hospital_overall_rating"]
    flags = hospital["domain_worse_flags"]
    hospital["priority_tier"] = "Routine"
    hospital.loc[flags.eq(1), "priority_tier"] = "Monitor"
    hospital.loc[rating.le(2) | flags.ge(2), "priority_tier"] = "Review"
    hospital.loc[rating.le(2) & flags.ge(2), "priority_tier"] = "High priority"
    hospital.loc[rating.isna(), "priority_tier"] = "Not rated"
    hospital["four_five_star_flag"] = rating.ge(4).astype(int)
    hospital["source_retrieved_utc"] = retrieved.isoformat()

    output = PROCESSED / "hospital_quality_tableau.csv"
    hospital.to_csv(output, index=False)

    rated = hospital[rating.notna()]
    qa = {
        "retrieved_utc": retrieved.isoformat(),
        "source_ids": DATASETS,
        "rows": int(len(hospital)),
        "unique_facilities": int(hospital["facility_id"].nunique()),
        "rated_facilities": int(len(rated)),
        "mean_rating": round(float(rated["hospital_overall_rating"].mean()), 3),
        "four_five_star_share": round(float(rated["four_five_star_flag"].mean()), 4),
        "high_priority_facilities": int(hospital["priority_tier"].eq("High priority").sum()),
        "duplicate_facility_ids": int(hospital["facility_id"].duplicated().sum()),
    }
    (PROCESSED / "qa_summary.json").write_text(json.dumps(qa, indent=2) + "\n")
    print(json.dumps(qa, indent=2))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
