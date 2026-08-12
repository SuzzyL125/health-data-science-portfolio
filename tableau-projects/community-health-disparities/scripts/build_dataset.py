#!/usr/bin/env python3
"""Build county-level CDC PLACES files for a Tableau disparities dashboard."""

from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
DATASET_ID = "swc5-untb"
MEASURES = ["DIABETES", "OBESITY", "CHD", "STROKE", "GHLTH", "ACCESS2", "CHECKUP", "DELAYMED", "LACKTRPT", "FOODSTAMP", "HOUSINSECU", "ISOLATION"]
BURDEN = ["DIABETES", "OBESITY", "CHD", "STROKE", "GHLTH"]
ACCESS = ["ACCESS2", "DELAYMED"]
PROTECTIVE = ["CHECKUP"]
SOCIAL = ["LACKTRPT", "FOODSTAMP", "HOUSINSECU", "ISOLATION"]


def download_places() -> pd.DataFrame:
    endpoint = f"https://data.cdc.gov/resource/{DATASET_ID}.csv"
    where = "data_value_type='Age-adjusted prevalence'"
    params = {
        "$limit": 500000,
        "$where": where,
    }
    url = f"{endpoint}?{urlencode(params)}"
    with urlopen(url, timeout=240) as response:
        content = response.read().decode("utf-8-sig")
    return pd.read_csv(io.StringIO(content), dtype={"locationid": str, "stateabbr": str})


def percentile(series: pd.Series, reverse: bool = False) -> pd.Series:
    ranked = series.rank(method="average", pct=True)
    return 1 - ranked if reverse else ranked


def numeric_or_missing(frame: pd.DataFrame, column: str) -> pd.Series:
    """Return a numeric source column, or a missing-valued aligned Series."""
    if column not in frame:
        return pd.Series(np.nan, index=frame.index)
    return pd.to_numeric(frame[column], errors="coerce")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    retrieved = datetime.now(timezone.utc)
    stamp = retrieved.strftime("%Y%m%dT%H%M%SZ")

    raw = download_places()
    raw.columns = raw.columns.str.strip().str.lower()
    raw.to_csv(RAW / f"places_county_{stamp}.csv", index=False)
    required = {"locationid", "locationname", "stateabbr", "statedesc", "measureid", "data_value", "data_value_type"}
    if not required.issubset(raw.columns):
        raise ValueError(f"Missing expected columns: {sorted(required - set(raw.columns))}")

    work = raw[raw["measureid"].isin(MEASURES)].copy()
    work["data_value"] = pd.to_numeric(work["data_value"], errors="coerce")
    work["low_confidence_limit"] = numeric_or_missing(work, "low_confidence_limit")
    work["high_confidence_limit"] = numeric_or_missing(work, "high_confidence_limit")
    work["totalpopulation"] = numeric_or_missing(work, "totalpopulation")
    work = work.dropna(subset=["data_value"])
    work["source_retrieved_utc"] = retrieved.isoformat()

    duplicates = work.duplicated(["locationid", "measureid"], keep=False)
    if duplicates.any():
        # Keep the latest year if a restored dataset contains more than one release year.
        if "year" not in work:
            raise ValueError("Duplicate county/measure rows found, but no year column is available to resolve them")
        work["year_numeric"] = pd.to_numeric(work["year"], errors="coerce")
        work = work.sort_values("year_numeric").drop_duplicates(["locationid", "measureid"], keep="last")

    identifiers = ["locationid", "locationname", "stateabbr", "statedesc"]
    wide = work.pivot(index=identifiers, columns="measureid", values="data_value").reset_index()
    population = work.groupby(identifiers, as_index=False)["totalpopulation"].max()
    wide = wide.merge(population, on=identifiers, how="left")

    adverse_percentiles = []
    for measure in BURDEN + ACCESS + SOCIAL:
        if measure in wide:
            column = f"pct_{measure.lower()}"
            wide[column] = percentile(wide[measure])
            adverse_percentiles.append(column)
    for measure in PROTECTIVE:
        if measure in wide:
            column = f"pct_{measure.lower()}_gap"
            wide[column] = percentile(wide[measure], reverse=True)
            adverse_percentiles.append(column)

    def mean_available(columns: list[str]) -> pd.Series:
        available = [column for column in columns if column in wide]
        return wide[available].mean(axis=1) if available else pd.Series(np.nan, index=wide.index)

    wide["burden_score"] = mean_available([f"pct_{x.lower()}" for x in BURDEN])
    wide["access_barrier_score"] = mean_available([f"pct_{x.lower()}" for x in ACCESS] + ["pct_checkup_gap"])
    wide["social_needs_score"] = mean_available([f"pct_{x.lower()}" for x in SOCIAL])
    wide["priority_score"] = wide[adverse_percentiles].mean(axis=1)
    wide["priority_percentile"] = percentile(wide["priority_score"])
    wide["priority_quintile"] = pd.cut(
        wide["priority_percentile"],
        bins=[0, .2, .4, .6, .8, 1.000001],
        labels=["Q1 Lower", "Q2", "Q3", "Q4", "Q5 Highest"],
        include_lowest=True,
    ).astype(str)
    wide["high_priority_flag"] = wide["priority_percentile"].ge(.8).astype(int)
    wide["source_retrieved_utc"] = retrieved.isoformat()

    wide_output = PROCESSED / "community_health_tableau.csv"
    long_output = PROCESSED / "indicator_long_tableau.csv"
    wide.to_csv(wide_output, index=False)
    work.to_csv(long_output, index=False)

    qa = {
        "retrieved_utc": retrieved.isoformat(),
        "source_dataset": DATASET_ID,
        "raw_rows": int(len(raw)),
        "selected_indicator_rows": int(len(work)),
        "counties": int(wide["locationid"].nunique()),
        "states": int(wide["stateabbr"].nunique()),
        "high_priority_counties": int(wide["high_priority_flag"].sum()),
        "duplicate_county_measure_rows_after_cleaning": int(work.duplicated(["locationid", "measureid"]).sum()),
        "indicators_present": sorted(work["measureid"].unique().tolist()),
    }
    (PROCESSED / "qa_summary.json").write_text(json.dumps(qa, indent=2) + "\n")
    print(json.dumps(qa, indent=2))
    print(f"Wrote {wide_output} and {long_output}")


if __name__ == "__main__":
    main()
