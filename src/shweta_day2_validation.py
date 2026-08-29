import pandas as pd
from pathlib import Path

# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

weather_file = BASE_DIR / "data" / "processed" / "cleaned_weather.csv"
utci_file = BASE_DIR / "data" / "processed" / "utci_hourly.csv"

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

weather = pd.read_csv(weather_file)
utci = pd.read_csv(utci_file)

print("\n========== WEATHER DATA ==========")
print("Rows:", len(weather))
print("Columns:", list(weather.columns))

print("\n========== UTCI DATA ==========")
print("Rows:", len(utci))
print("Columns:", list(utci.columns))

# --------------------------------------------------
# MISSING VALUES
# --------------------------------------------------

print("\n========== MISSING VALUES ==========")

weather_missing = weather.isna().sum()
utci_missing = utci.isna().sum()

print("\nWeather:")
print(weather_missing[weather_missing > 0])

print("\nUTCI:")
print(utci_missing[utci_missing > 0])

# --------------------------------------------------
# DUPLICATES
# --------------------------------------------------

print("\n========== DUPLICATES ==========")

print("Weather duplicate rows:", weather.duplicated().sum())
print("UTCI duplicate rows:", utci.duplicated().sum())

# --------------------------------------------------
# TEMPERATURE CHECK
# --------------------------------------------------

if "t2m_C" in weather.columns:
    print("\n========== TEMPERATURE ==========")
    print("Minimum:", weather["t2m_C"].min())
    print("Maximum:", weather["t2m_C"].max())

# --------------------------------------------------
# RH CHECK
# --------------------------------------------------

if "rh" in weather.columns:
    print("\n========== RELATIVE HUMIDITY ==========")

    invalid_rh = ((weather["rh"] < 0) | (weather["rh"] > 100)).sum()

    print("Minimum:", weather["rh"].min())
    print("Maximum:", weather["rh"].max())
    print("Invalid RH values:", invalid_rh)

# --------------------------------------------------
# WIND CHECK
# --------------------------------------------------

if "wind_speed" in weather.columns:
    print("\n========== WIND SPEED ==========")

    negative_wind = (weather["wind_speed"] < 0).sum()

    print("Minimum:", weather["wind_speed"].min())
    print("Maximum:", weather["wind_speed"].max())
    print("Negative wind values:", negative_wind)

# --------------------------------------------------
# UTCI CHECK
# --------------------------------------------------

utci_column = None

for col in ["utci", "UTCI", "utci_c", "utci_C"]:
    if col in utci.columns:
        utci_column = col
        break

if utci_column:

    print("\n========== UTCI ==========")

    print("UTCI column:", utci_column)
    print("Minimum:", utci[utci_column].min())
    print("Maximum:", utci[utci_column].max())

    print(
        "Missing UTCI:",
        utci[utci_column].isna().sum()
    )

# --------------------------------------------------
# TIMESTAMP CHECK
# --------------------------------------------------

print("\n========== TIMESTAMP ==========")

time_column = None

for col in ["time", "timestamp", "datetime", "date"]:
    if col in weather.columns:
        time_column = col
        break

if time_column:

    parsed_time = pd.to_datetime(
        weather[time_column],
        errors="coerce"
    )

    print("Timestamp column:", time_column)
    print("Invalid timestamps:", parsed_time.isna().sum())
    print("Start:", parsed_time.min())
    print("End:", parsed_time.max())

# --------------------------------------------------
# FINAL STATUS
# --------------------------------------------------

print("\n===================================")
print("DATA VALIDATION COMPLETED")
print("===================================")