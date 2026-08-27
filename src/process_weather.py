import xarray as xr
import numpy as np
from pathlib import Path

def kelvin_to_celsius(temp_k):
    """Convert Kelvin to Celsius."""
    return temp_k - 273.15


def calculate_wind_speed(u10, v10):
    """Calculate wind speed from 10 m U/V wind components."""
    return np.sqrt(u10**2 + v10**2)


def calculate_relative_humidity(tdb, tdp):
    """Calculate relative humidity (%) from air temperature and dewpoint."""
    rh = 100 * (
        np.exp((17.625 * tdp) / (243.04 + tdp))
        / np.exp((17.625 * tdb) / (243.04 + tdb))
    )

    return rh.clip(0, 100)

def accumulated_radiation_to_flux(radiation):
    """
    Convert ERA5 hourly accumulated radiation from J/m²
    to average radiation flux in W/m².
    """

    return radiation / 3600.0

def weather_processing(file_path: Path):
    """Process the data set and creates new variable for UTCI"""
    ds = xr.open_dataset(
        file_path,
        engine="netcdf4"
    )

    ds["tdb"] = kelvin_to_celsius(ds["t2m"])

    ds["tdp"] = kelvin_to_celsius(ds["d2m"])

    ds["v"] = calculate_wind_speed(
        ds["u10"],
        ds["v10"]
    )

    ds["rh"] = calculate_relative_humidity(
        ds["tdb"],
        ds["tdp"]
    )

    ds["ssrd_flux"] = accumulated_radiation_to_flux(
        ds["ssrd"]
    )

    ds["strd_flux"] = accumulated_radiation_to_flux(
        ds["strd"]
    )

    ds["ssr_flux"] = accumulated_radiation_to_flux(
        ds["ssr"]
    )

    ds["str_flux"] = accumulated_radiation_to_flux(
        ds["str"]
    )

    ds["fdir_flux"] = accumulated_radiation_to_flux(
        ds["fdir"]
    )
    print("Years:")
    print(np.unique(ds.time.dt.year.values))

    print("\nRaw radiation ranges:")

    for var in ["ssrd", "ssr", "strd", "str", "fdir"]:
        print(
            f"{var}: "
            f"min={float(ds[var].min(skipna=True)):.2f}, "
            f"max={float(ds[var].max(skipna=True)):.2f}"
        )

    print("\nFlux ranges:")

    for var in [
        "ssrd_flux",
        "ssr_flux",
        "strd_flux",
        "str_flux",
        "fdir_flux",
    ]:
        print(
            f"{var}: "
            f"min={float(ds[var].min(skipna=True)):.2f}, "
            f"max={float(ds[var].max(skipna=True)):.2f}"
        )
    sample = ds.isel(
        latitude=1,
        longitude=1,
        time=slice(0, 24)
    )

    print(
        sample[
            [
                "ssrd_flux",
                "ssr_flux",
                "strd_flux",
                "str_flux",
                "fdir_flux",
            ]
        ]
    )

    return ds

def radiation_processing(ds:xr.Dataset) -> xr.Dataset:
    ds["I_sw"] = (
        ds["fdir_flux"] *
        ds["cos_theta"]
    )

    ds["D_sw"] = (
        ds["ssrd_flux"] -
        ds["fdir_flux"]
    )

    ds["R_sw"] = (
        ds["ssrd_flux"] -
        ds["ssr_flux"]
    )

    ds["U_lw"] = (
        ds["strd_flux"] -
        ds["str_flux"]
    )

    ds["D_lw"] = ds["strd_flux"]

    return ds