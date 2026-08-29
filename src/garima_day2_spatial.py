import geopandas as gpd
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "spatial"
    / "ahmedabad_wards_clean.geojson"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "spatial"
    / "ahmedabad_wards_day2.geojson"
)

DEMOGRAPHIC_TEMPLATE = (
    BASE_DIR
    / "data"
    / "spatial"
    / "ward_demographic_template.csv"
)

# --------------------------------------------------
# LOAD
# --------------------------------------------------

gdf = gpd.read_file(INPUT_FILE)

print("Original rows:", len(gdf))
print("Original columns:")
print(gdf.columns.tolist())

# --------------------------------------------------
# IDENTIFY WARD NAME COLUMN
# --------------------------------------------------

possible_name_columns = [
    "ward_name",
    "Ward_Name",
    "WARD_NAME",
    "name",
    "Name",
    "NAME"
]

name_column = None

for col in possible_name_columns:
    if col in gdf.columns:
        name_column = col
        break

if name_column is None:
    raise ValueError(
        "Could not identify ward name column."
    )

# --------------------------------------------------
# CREATE STABLE WARD ID
# --------------------------------------------------

gdf["Ward_ID"] = range(1, len(gdf) + 1)

gdf["Ward_Name"] = (
    gdf[name_column]
    .astype(str)
    .str.strip()
)

# --------------------------------------------------
# GEOMETRY CHECK
# --------------------------------------------------

print("\n========== GEOMETRY ==========")

print(
    "Missing geometry:",
    gdf.geometry.isna().sum()
)

print(
    "Invalid geometry:",
    (~gdf.geometry.is_valid).sum()
)

# Attempt to repair invalid geometries
if (~gdf.geometry.is_valid).any():
    gdf["geometry"] = gdf.geometry.make_valid()

print(
    "Invalid geometry after repair:",
    (~gdf.geometry.is_valid).sum()
)

# --------------------------------------------------
# CRS
# --------------------------------------------------

print("\nCRS:", gdf.crs)

if gdf.crs is None:
    gdf = gdf.set_crs("EPSG:4326")

else:
    gdf = gdf.to_crs("EPSG:4326")

# --------------------------------------------------
# DUPLICATE WARD CHECK
# --------------------------------------------------

print("\n========== WARD CHECK ==========")

print(
    "Duplicate Ward IDs:",
    gdf["Ward_ID"].duplicated().sum()
)

print(
    "Duplicate Ward names:",
    gdf["Ward_Name"].duplicated().sum()
)

# --------------------------------------------------
# KEEP CLEAN STRUCTURE
# --------------------------------------------------

gdf = gdf[
    [
        "Ward_ID",
        "Ward_Name",
        "geometry"
    ]
]

# --------------------------------------------------
# SAVE
# --------------------------------------------------

gdf.to_file(
    OUTPUT_FILE,
    driver="GeoJSON"
)

print("\nSaved:")
print(OUTPUT_FILE)

# --------------------------------------------------
# DEMOGRAPHIC JOIN TEMPLATE
# --------------------------------------------------

template = pd.DataFrame({
    "Ward_ID": gdf["Ward_ID"],
    "Ward_Name": gdf["Ward_Name"],
    "Population": pd.NA,
    "Population_Density": pd.NA,
    "Elderly_Percentage": pd.NA,
    "Outdoor_Worker_Proxy": pd.NA,
    "Healthcare_Access_Proxy": pd.NA
})

template.to_csv(
    DEMOGRAPHIC_TEMPLATE,
    index=False
)

print("\nDemographic template saved:")
print(DEMOGRAPHIC_TEMPLATE)

# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

print("\n================================")
print("GARIMA DAY 2 SPATIAL PIPELINE")
print("================================")
print("Total wards:", len(gdf))
print("CRS:", gdf.crs)
print("Missing geometry:", gdf.geometry.isna().sum())
print("Invalid geometry:", (~gdf.geometry.is_valid).sum())
print("Duplicate Ward IDs:", gdf["Ward_ID"].duplicated().sum())
print("================================")