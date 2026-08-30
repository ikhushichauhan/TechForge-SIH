"""
Shweta - Day 1: Raw weather (ERA5) -> Cleaned weather pipeline
Input : data/processed/era5_merged.nc (Dev's real ERA5 download)
Output: data/processed/cleaned_weather.csv
"""
import xarray as xr
import pandas as pd
import numpy as np

ds = xr.open_dataset("data/processed/era5_merged.nc")
df = ds[["t2m", "d2m", "u10", "v10"]].to_dataframe().reset_index()

# Temperature: Kelvin -> Celsius
df["temp_C"] = df["t2m"] - 273.15
df["dewpoint_C"] = df["d2m"] - 273.15

# Wind speed from u/v components
df["wind_speed"] = np.sqrt(df["u10"]**2 + df["v10"]**2)

# Relative Humidity (Magnus formula)
def calc_rh(temp_c, dewpoint_c):
    a, b = 17.625, 243.04
    numerator = np.exp((a * dewpoint_c) / (b + dewpoint_c))
    denominator = np.exp((a * temp_c) / (b + temp_c))
    return 100 * (numerator / denominator)

df["RH"] = calc_rh(df["temp_C"], df["dewpoint_C"])

# Sanity checks
assert (df["wind_speed"] >= 0).all(), "Negative wind speed found!"
assert df[["temp_C","dewpoint_C","wind_speed","RH"]].isna().sum().sum() == 0, "Missing values found!"
assert ((df["RH"] >= 0) & (df["RH"] <= 100)).all(), "RH out of valid range!"

df_clean = df[["time", "latitude", "longitude", "temp_C", "dewpoint_C", "wind_speed", "RH"]]
df_clean.to_csv("data/processed/cleaned_weather.csv", index=False)
print(f"Cleaned weather saved -> data/processed/cleaned_weather.csv ({len(df_clean)} rows)")
