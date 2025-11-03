from pathlib import Path
import pandas as pd
import requests
from io import StringIO

RAW = Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)
OUT = RAW / "cases.csv"

BASE = "https://data.cdc.gov/resource/2ew6-ywp6.csv"

# Expanded candidates based on your columns
CANDIDATE_METRIC_COLS = [
    "wastewater_percentile",
    "wastewater_viral_activity_level",
    "wastewater_activity_level",
    "wastewater_percentile_15d",
    "percentile",                 # <-- present in your pull
    "ptc_15d",                    # percent change 15d (backup)
]

def main():
    print("Downloading CDC NWSS wastewater metrics (site-level weekly)…")

    # Pull a large page; aggregate locally
    r = requests.get(BASE, params={"$limit": 500000}, timeout=60)
    r.raise_for_status()

    df = pd.read_csv(StringIO(r.text), low_memory=False)
    df.columns = [c.strip().lower() for c in df.columns]

    # pick metric column
    metric_col = next((c for c in CANDIDATE_METRIC_COLS if c in df.columns), None)
    if metric_col is None:
        raise ValueError(f"No expected metric column found. Got columns: {list(df.columns)[:40]}")

    # choose date column
    date_col = "date_end" if "date_end" in df.columns else ("week_end" if "week_end" in df.columns else None)
    if date_col is None:
        raise ValueError(f"No expected date column (date_end/week_end). Columns: {list(df.columns)[:40]}")

    # keep & clean
    df = df[[date_col, metric_col]].copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[metric_col] = pd.to_numeric(df[metric_col], errors="coerce")
    df = df.dropna(subset=[date_col, metric_col])

    # national weekly series = median across reporting sites
    nat = (
        df.groupby(date_col, as_index=False)
          .agg(cases=(metric_col, "median"))
          .sort_values(date_col)
          .rename(columns={date_col: "date"})
    )

    nat.to_csv(OUT, index=False)
    print(f"Saved {len(nat)} weekly rows to {OUT}")
    print(f"ℹUsing metric column: {metric_col}")

if __name__ == "__main__":
    main()
