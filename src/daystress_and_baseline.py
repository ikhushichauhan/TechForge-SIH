"""
Day 2 - DayStress + Nighttime Baseline calculation

Input:
    notebooks/data/processed/utci_hourly.csv
    (Dev's real UTCI output, timestamps assumed UTC)

Output:
    data/processed/daystress.csv
    Printed nighttime baseline value

Methodology:
    1. Convert ERA5/UTCI timestamps from UTC to IST.
    2. DayStress = mean UTCI during 08:00-20:00 IST.
    3. Nighttime = 20:00-06:00 IST.
    4. Nighttime baseline = fixed 90th percentile of all
       nighttime UTCI values in the available dataset.
"""

import pandas as pd


# ===============================================================
# METHODOLOGY
# ===============================================================

DAY_START = 8
DAY_END = 20

NIGHT_START = 20
NIGHT_END = 6


# ===============================================================
# LOAD UTCI DATA
# ===============================================================

input_file = "notebooks/data/processed/utci_hourly.csv"

df = pd.read_csv(
    input_file,
    parse_dates=["time"]
)

# Make sure timestamps are explicitly treated as UTC
df["time"] = pd.to_datetime(
    df["time"],
    utc=True
)

# ===============================================================
# UTC -> IST
# ===============================================================

df["time"] = df["time"].dt.tz_convert(
    "Asia/Kolkata"
)

# Extract IST hour and IST calendar date
df["hour"] = df["time"].dt.hour
df["date"] = df["time"].dt.normalize()


# ===============================================================
# DAY / NIGHT FLAGS
# ===============================================================

# Daytime: 08:00-19:59 IST
df["is_day"] = (
    (df["hour"] >= DAY_START)
    & (df["hour"] < DAY_END)
)

# Nighttime: 20:00-05:59 IST
df["is_night"] = (
    (df["hour"] >= NIGHT_START)
    | (df["hour"] < NIGHT_END)
)


# ===============================================================
# DAYSTRESS
# ===============================================================

daystress = (
    df[df["is_day"]]
    .groupby("date")["utci"]
    .mean()
    .reset_index()
    .rename(columns={"utci": "DayStress"})
)


# Remove timezone information before saving,
# so the date is stored cleanly as a calendar date.
daystress["date"] = (
    daystress["date"]
    .dt.tz_localize(None)
)

# Save DayStress output
daystress.to_csv(
    "data/processed/daystress.csv",
    index=False
)

print(
    f"DayStress calculated for {len(daystress)} days "
    f"using 08:00-20:00 IST."
)
print("Saved to: data/processed/daystress.csv")

# ===============================================================
# NIGHTTIME BASELINE
# ===============================================================

night_utci = df.loc[
    df["is_night"],
    "utci"
].dropna()


baseline = night_utci.quantile(0.90)


print(
    f"Nighttime readings used: {len(night_utci)}"
)

print(
    f"NIGHTTIME BASELINE (90th percentile) = "
    f"{baseline:.2f} UTCI"
)