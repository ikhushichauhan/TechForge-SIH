"""
Garima - Day 1: Load and clean Ahmedabad ward boundaries
Source: DataMeet India (github.com/datameet/Municipal_Spatial_Data)
Output: data/spatial/ahmedabad_wards_clean.geojson
"""
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Download source (run once, or use `curl` beforehand):
# curl -sL -o Wards.geojson https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Ahmedabad/Wards.geojson

gdf = gpd.read_file("Wards.geojson")
print(f"Loaded {len(gdf)} ward polygons. CRS: {gdf.crs}")

# Clean IDs and names for joining with thermal/demographic data later
gdf["Ward_ID"] = range(1, len(gdf) + 1)
gdf["Ward_Name"] = gdf["Name"].str.extract(r"\d+\s+(.*)")[0].str.strip().str.title()

# Save cleaned version
gdf.to_file("data/spatial/ahmedabad_wards_clean.geojson", driver="GeoJSON")
print("Saved cleaned ward boundaries with stable Ward_ID -> data/spatial/ahmedabad_wards_clean.geojson")

# Proof-of-work plot
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(ax=ax, edgecolor="black", facecolor="lightblue", linewidth=0.5)
ax.set_title(f"Ahmedabad Wards (n={len(gdf)})")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
plt.tight_layout()
plt.savefig("ahmedabad_wards_plot.png", dpi=120)
print("Saved plot -> ahmedabad_wards_plot.png")
