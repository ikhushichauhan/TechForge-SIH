import xarray as xr

# Path to your ERA5 GRIB file
file_path = r"data/raw/era5_raw.grib"

# Open the GRIB file
ds = xr.open_dataset(
    file_path,
    engine="cfgrib"
)

# Print the complete dataset
print("\n===== ERA5 DATASET =====")
print(ds)

# Print dimensions
print("\n===== DIMENSIONS =====")
print(ds.dims)

# Print variables available in the file
print("\n===== VARIABLES =====")
print(list(ds.data_vars))

# Print coordinates
print("\n===== COORDINATES =====")
print(list(ds.coords))