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
# HELPER: case-insensitive column finder
# --------------------------------------------------
# FIX: the original script looked for exact names like "rh" and "t2m_C",
# but the actual files use "RH" and "temp_C" - since column lookups were
# case-sensitive, those checks were silently never running. This helper
# finds a column regardless of case, and works even if naming conventions
# change slightly in the future.
def find_column(df, candidates):
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None

# --------------------------------------------------
# TEMPERATURE CHECK
# --------------------------------------------------
temp_column = find_column(weather, ["t2m_C", "temp_C", "temperature"])

if temp_column:
    print("\n========== TEMPERATURE ==========")
    print("Column used:", temp_column)
    print("Minimum:", weather[temp_column].min())
    print("Maximum:", weather[temp_column].max())
else:
    print("\n========== TEMPERATURE ==========")
    print("WARNING: no temperature column found - check not run")

# --------------------------------------------------
# RH CHECK
# --------------------------------------------------
rh_column = find_column(weather, ["rh", "RH", "relative_humidity"])

if rh_column:
    print("\n========== RELATIVE HUMIDITY ==========")
    invalid_rh = ((weather[rh_column] < 0) | (weather[rh_column] > 100)).sum()
    print("Column used:", rh_column)
    print("Minimum:", weather[rh_column].min())
    print("Maximum:", weather[rh_column].max())
    print("Invalid RH values:", invalid_rh)
else:
    print("\n========== RELATIVE HUMIDITY ==========")
    print("WARNING: no RH column found - check not run")

# --------------------------------------------------
# WIND CHECK
# --------------------------------------------------
wind_column = find_column(weather, ["wind_speed", "windspeed", "wind"])

if wind_column:
    print("\n========== WIND SPEED ==========")
    negative_wind = (weather[wind_column] < 0).sum()
    print("Column used:", wind_column)
    print("Minimum:", weather[wind_column].min())
    print("Maximum:", weather[wind_column].max())
    print("Negative wind values:", negative_wind)
else:
    print("\n========== WIND SPEED ==========")
    print("WARNING: no wind speed column found - check not run")

# --------------------------------------------------
# UTCI CHECK
# --------------------------------------------------
utci_column = find_column(utci, ["utci", "UTCI", "utci_c", "utci_C"])

if utci_column:
    print("\n========== UTCI ==========")
    print("UTCI column:", utci_column)
    print("Minimum:", utci[utci_column].min())
    print("Maximum:", utci[utci_column].max())
    print("Missing UTCI:", utci[utci_column].isna().sum())
else:
    print("\n========== UTCI ==========")
    print("WARNING: no UTCI column found - check not run")

# --------------------------------------------------
# TIMESTAMP CHECK
# --------------------------------------------------
print("\n========== TIMESTAMP ==========")

time_column = find_column(weather, ["time", "timestamp", "datetime", "date"])

if time_column:
    parsed_time = pd.to_datetime(weather[time_column], errors="coerce")
    print("Timestamp column:", time_column)
    print("Invalid timestamps:", parsed_time.isna().sum())
    print("Start:", parsed_time.min())
    print("End:", parsed_time.max())
else:
    print("WARNING: no timestamp column found - check not run")

# --------------------------------------------------
# FINAL STATUS
# --------------------------------------------------
checks_run = sum([
    temp_column is not None,
    rh_column is not None,
    wind_column is not None,
    utci_column is not None,
    time_column is not None,
])

print("\n===================================")
print(f"DATA VALIDATION COMPLETED - {checks_run}/5 checks actually ran")
if checks_run < 5:
    print("WARNING: not all checks ran - see WARNING messages above")
print("===================================")
