"""
Day 2 - DayStress + Nighttime Baseline calculation
Input : notebooks/data/processed/utci_hourly.csv (Dev's real UTCI output)
Output: daystress.csv + printed nighttime baseline value
"""
import pandas as pd

DAY_START, DAY_END = 6, 18        # daytime window: 06:00-18:00
NIGHT_START, NIGHT_END = 20, 6    # nighttime window: 20:00-06:00 (wraps midnight)

df = pd.read_csv("notebooks/data/processed/utci_hourly.csv", parse_dates=["time"])
df["hour"] = df["time"].dt.hour
df["date"] = df["time"].dt.date

df["is_day"] = df["hour"].between(DAY_START, DAY_END - 1)
df["is_night"] = (df["hour"] >= NIGHT_START) | (df["hour"] < NIGHT_END)

# --- DayStress: mean UTCI across daytime hours, per date ---
daystress = (
    df[df["is_day"]]
    .groupby("date")["utci"]
    .mean()
    .reset_index()
    .rename(columns={"utci": "DayStress"})
)
daystress.to_csv("data/processed/daystress.csv", index=False)
print(f"DayStress calculated for {len(daystress)} days -> saved to data/processed/daystress.csv")

# --- Nighttime baseline: 90th percentile across full dataset ---
night_utci = df[df["is_night"]]["utci"]
baseline = night_utci.quantile(0.90)
print(f"Nighttime readings used: {len(night_utci)}")
print(f"NIGHTTIME BASELINE (90th percentile) = {baseline:.2f} UTCI")
