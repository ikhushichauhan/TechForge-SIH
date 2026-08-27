import pandas as pd
import numpy as np
import xarray as xr
from pvlib.solarposition import get_solarposition


def calculate_cos_solar_zenith(ds):
    """
    Calculate cos(solar zenith angle) for every
    time * latitude * longitude point.
    """

    times = pd.DatetimeIndex(ds.time.values).tz_localize("UTC")

    cos_theta = np.empty(
        (ds.sizes["time"], ds.sizes["latitude"], ds.sizes["longitude"]),
        dtype=np.float32
    )

    for i, lat in enumerate(ds.latitude.values):
        for j, lon in enumerate(ds.longitude.values):

            solar_position = get_solarposition(
                times,
                latitude=float(lat),
                longitude=float(lon),
                method="nrel_numpy"
            )

            zenith = solar_position["zenith"].to_numpy()

            cos_values = np.cos(np.deg2rad(zenith))

            # Sun below horizon → no direct solar contribution
            cos_values = np.clip(cos_values, 0, 1)

            cos_theta[:, i, j] = cos_values

    return xr.DataArray(
        cos_theta,
        coords={
            "time": ds.time,
            "latitude": ds.latitude,
            "longitude": ds.longitude
        },
        dims=("time", "latitude", "longitude"),
        name="cos_theta"
    )