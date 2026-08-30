"""
Garima - Day 2: Spatial pipeline continuation
- Cleans/validates ward geometries
- Builds the demographic join schema (no fabricated values)
- Provides a merge function for when real ward-wise data is manually downloaded
"""
import geopandas as gpd
import pandas as pd

gdf = gpd.read_file("data/spatial/ahmedabad_wards_clean.geojson")

# --- Geometry validation ---
assert gdf.geometry.is_valid.all(), "Invalid geometries found - fix before proceeding"
assert not gdf.geometry.is_empty.any(), "Empty geometries found"
print(f"{len(gdf)} ward geometries validated - all valid, no empty shapes")

# --- Demographic join schema (columns only - NO fabricated numbers) ---
demographic_template = gdf[["Ward_ID", "Ward_Name"]].copy()
demographic_template["population_total"] = pd.NA
demographic_template["population_density"] = pd.NA
demographic_template["elderly_pct"] = pd.NA            # NEEDS VERIFICATION at ward level
demographic_template["sc_st_pct"] = pd.NA               # confirmed available (Census 2011)
demographic_template["literacy_pct"] = pd.NA            # confirmed available (Census 2011)
demographic_template["outdoor_worker_density"] = pd.NA  # likely unavailable at ward level
demographic_template["slum_density"] = pd.NA            # city total known; ward split unconfirmed
demographic_template["healthcare_access"] = pd.NA       # needs separate hospital/PHC dataset
demographic_template["ndvi_green_cover"] = pd.NA        # computable independently via Sentinel-2

demographic_template.to_csv("data/spatial/demographic_join_template.csv", index=False)
print(f"Demographic schema saved -> data/spatial/demographic_join_template.csv ({len(demographic_template)} wards)")


def merge_real_demographics(real_data_path: str, name_column: str):
    """
    Once Garima manually downloads the real AMC/Census ward-wise file:
    call this with the path to that file and the column name that holds
    ward names, to join it against our Ward_ID scheme by matching names.

    NOTE: ward names in the AMC source may not exactly match Ward_Name here
    (spelling/formatting differences are common) - manual review of the
    merge result is required before trusting it.
    """
    real_df = pd.read_csv(real_data_path)
    merged = demographic_template.merge(
        real_df, left_on="Ward_Name", right_on=name_column, how="left"
    )
    unmatched = merged[merged[name_column].isna()]
    if len(unmatched) > 0:
        print(f"WARNING: {len(unmatched)} wards did not match - check name spelling differences")
    return merged
