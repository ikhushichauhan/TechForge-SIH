"""
Dev - Day 4: Reproducible End-to-End Pipeline (Frozen)
========================================================
Raw ERA5 data -> UTCI -> NCTL -> CTBI, in one script.

This consolidates logic that was previously scattered across src/*.py
files AND the day3 notebook (where the timezone/NCTL/baseline/normalization
fixes were made but never extracted into a reusable script). Running this
file end-to-end regenerates every processed output from the raw ERA5 file.

USAGE:
    python src/pipeline_end_to_end.py

INPUT:
    data/raw/era5_raw.grib          (or re-download via src/download_era5.py)

OUTPUTS (all in data/processed/):
    cleaned_weather.csv
    utci_hourly.csv
    daystress.csv
    nctl.csv
    CTBI.csv                        (alpha=0.7, per-year reset)
    ctbi_sensitivity.csv            (alpha=0.6/0.7/0.8)

CONFIRMED FIXES INCLUDED (see Decision Log D5-D7 for history):
    1. UTC -> IST timezone conversion applied BEFORE any day/night hour split
    2. NCTL = single night's excess sum only (no carry-forward between nights)
    3. Baseline = fixed 90th percentile of nighttime UTCI (not median/expanding-window)
    4. Normalization = min-max (x-min)/(max-min), not divide-by-max
    5. CTBI resets to 0 at the start of each year (years are not one continuous series)
"""
import xarray as xr
import pandas as pd
import numpy as np

# Reuses the team's own already-validated functions - no logic is
# reimplemented here, to avoid the pipeline drifting from what's
# actually been tested (this was itself one of the Day 3 lessons).
from process_weather import weather_processing, radiation_processing
from cos_solar import calculate_cos_solar_zenith
from mrt import calculate_mrt
from utci import calculate_utci

# NOTE: input is the pre-merged NetCDF (data/processed/era5_merged.nc),
# not the raw .grib file - process_weather.py's weather_processing()
# expects the netcdf4 engine. To regenerate era5_merged.nc itself from
# a fresh .grib download, see src/read_era5.py.
MERGED_NC_PATH = "data/processed/era5_merged.nc"
DAY_START, DAY_END = 6, 18
NIGHT_START, NIGHT_END = 20, 6
BASELINE_PERCENTILE = 0.90


# ---------------------------------------------------------------
# STEP 1+2: Load ERA5, clean weather variables, compute MRT + UTCI
# (all via the team's existing validated functions)
# ---------------------------------------------------------------
def compute_utci_dataset(nc_path):
    ds = weather_processing(nc_path)
    ds["cos_theta"] = calculate_cos_solar_zenith(ds)
    ds = radiation_processing(ds)
    ds = calculate_mrt(ds)
    ds = calculate_utci(ds)
    return ds


# ---------------------------------------------------------------
# STEP 3: FIX 1 - timezone correction, applied before any hour classification
# ---------------------------------------------------------------
def to_utci_dataframe_with_ist(ds):
    df = ds[["tdb", "mrt", "v", "rh", "utci"]].to_dataframe().reset_index()
    df["local_time"] = (
        df["time"].dt.tz_localize("UTC").dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
    )
    df["hour"] = df["local_time"].dt.hour
    df["date"] = df["local_time"].dt.date
    df["is_day"] = df["hour"].between(DAY_START, DAY_END - 1)
    df["is_night"] = (df["hour"] >= NIGHT_START) | (df["hour"] < NIGHT_END)
    return df


# ---------------------------------------------------------------
# STEP 4: FIX 2 + FIX 3 - per-night NCTL, fixed 90th-percentile baseline
# ---------------------------------------------------------------
def assign_night_date(row):
    if row["hour"] >= 20:
        return row["date"]
    elif row["hour"] < 6:
        return row["date"] - pd.Timedelta(days=1)
    return None


def compute_baseline_and_nctl(df):
    baseline = df[df["is_night"]]["utci"].quantile(BASELINE_PERCENTILE)

    night_df = df[df["is_night"]].copy()
    night_df["night_date"] = night_df.apply(assign_night_date, axis=1)
    night_df["excess"] = (night_df["utci"] - baseline).clip(lower=0)  # per-night, no carry-forward

    nctl = night_df.groupby("night_date")["excess"].sum().reset_index()
    nctl.columns = ["date", "NCTL"]
    nctl["date"] = pd.to_datetime(nctl["date"])
    return baseline, nctl


# ---------------------------------------------------------------
# STEP 5: FIX 4 - min-max normalization
# ---------------------------------------------------------------
def normalize_min_max(series):
    return (series - series.min()) / (series.max() - series.min())


# ---------------------------------------------------------------
# STEP 6: FIX 5 - CTBI, reset per year
# ---------------------------------------------------------------
def compute_ctbi_per_year(df, alpha, beta_gamma_split=0.5):
    beta = (1 - alpha) * beta_gamma_split
    gamma = (1 - alpha) * (1 - beta_gamma_split)
    result = []
    for year, group in df.groupby("year"):
        group = group.sort_values("date").reset_index(drop=True)
        ctbi_prev = 0.0
        vals = []
        for _, row in group.iterrows():
            c = alpha * ctbi_prev + beta * row["DayStress_norm"] + gamma * row["NCTL_norm"]
            vals.append(c)
            ctbi_prev = c
        group["CTBI"] = vals
        result.append(group)
    return pd.concat(result, ignore_index=True)


# ---------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------
if __name__ == "__main__":
    print("Step 1-2/6: Loading ERA5, computing weather variables + MRT + UTCI...")
    ds = compute_utci_dataset(MERGED_NC_PATH)

    print("Step 3/6: Converting to IST, classifying day/night hours...")
    df = to_utci_dataframe_with_ist(ds)
    df.to_csv("data/processed/utci_hourly.csv", index=False)

    print("Step 4/6: Computing nighttime baseline + NCTL...")
    baseline, nctl = compute_baseline_and_nctl(df)
    print(f"  Baseline (90th percentile, IST-corrected): {baseline:.2f}")
    nctl.to_csv("data/processed/nctl.csv", index=False)

    daystress = df[df["is_day"]].groupby("date")["utci"].mean().reset_index()
    daystress.columns = ["date", "DayStress"]
    daystress["date"] = pd.to_datetime(daystress["date"])
    daystress.to_csv("data/processed/daystress.csv", index=False)

    print("Step 5/6: Normalizing and computing CTBI (alpha=0.7)...")
    merged = pd.merge(daystress, nctl, on="date", how="inner").sort_values("date").reset_index(drop=True)
    merged["DayStress_norm"] = normalize_min_max(merged["DayStress"])
    merged["NCTL_norm"] = normalize_min_max(merged["NCTL"])
    merged["year"] = merged["date"].dt.year

    ctbi_main = compute_ctbi_per_year(merged, alpha=0.7)
    ctbi_main.to_csv("data/processed/CTBI.csv", index=False)
    print(f"  CTBI range: {ctbi_main['CTBI'].min():.3f} to {ctbi_main['CTBI'].max():.3f}")

    print("Step 6/6: Running alpha sensitivity test (0.6/0.7/0.8)...")
    sensitivity = merged[["date", "year", "DayStress_norm", "NCTL_norm"]].copy()
    for a in [0.6, 0.7, 0.8]:
        result = compute_ctbi_per_year(merged, alpha=a)
        sensitivity[f"CTBI_alpha_{a}"] = result["CTBI"].values
    sensitivity.to_csv("data/processed/ctbi_sensitivity.csv", index=False)
    corr = sensitivity["CTBI_alpha_0.6"].corr(sensitivity["CTBI_alpha_0.8"])
    print(f"  Sensitivity correlation (0.6 vs 0.8): {corr:.3f}")

    print("\nPipeline complete. All outputs regenerated in data/processed/.")
