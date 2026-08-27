import numpy as np
import xarray as xr

from pythermalcomfort.models import utci


def calculate_utci(ds: xr.Dataset) -> xr.Dataset:
    """
    Calculate UTCI from:

    tdb : air temperature [°C]
    mrt : mean radiant temperature [°C]
    v   : wind speed at 10 m [m/s]
    rh  : relative humidity [%]
    """

    # Use one consistent dimension order for every UTCI input.
    target_dims = ("latitude", "longitude", "time")

    tdb = ds["tdb"].transpose(*target_dims).values
    tr = ds["mrt"].transpose(*target_dims).values
    v = ds["v"].transpose(*target_dims).values
    rh = ds["rh"].transpose(*target_dims).values

    # Calculate UTCI
    result = utci(
        tdb=tdb,
        tr=tr,
        v=v,
        rh=rh,
        units="SI",
        limit_inputs=False,
        round_output=False,
    )

    # Put result back into xarray using the same dimensions
    ds["utci"] = xr.DataArray(
        np.asarray(result.utci),
        coords={
            "latitude": ds.latitude,
            "longitude": ds.longitude,
            "time": ds.time,
        },
        dims=target_dims,
        name="utci",
    )

    ds["utci"].attrs["units"] = "°C"
    ds["utci"].attrs["description"] = (
        "Universal Thermal Climate Index"
    )

    return ds