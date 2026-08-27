import numpy as np
import xarray as xr


SIGMA = 5.67e-8
SOLAR_ABSORPTIVITY = 0.7
BODY_EMISSIVITY = 0.97
HEMISPHERE_FACTOR = 0.5


def calculate_mrt(ds: xr.Dataset) -> xr.Dataset:
    """
    Calculate Mean Radiant Temperature (MRT) from
    ERA5 radiation components.

    Expected input variables:
        ssrd_flux : surface solar radiation downwards [W/m²]
        ssr_flux  : surface net solar radiation [W/m²]
        strd_flux : surface thermal radiation downwards [W/m²]
        str_flux  : surface net thermal radiation [W/m²]
        fdir_flux : total-sky direct solar radiation [W/m²]
        cos_theta : cosine of solar zenith angle [dimensionless]

    Returns:
        Dataset with:
            mrt : mean radiant temperature [°C]
    """

    ssrd = ds["ssrd_flux"]
    ssr = ds["ssr_flux"]
    strd = ds["strd_flux"]
    strr = ds["str_flux"]
    fdir = ds["fdir_flux"]
    cossza = ds["cos_theta"]

    # Radiation components

    diffuse_sw = ssrd - fdir
    reflected_sw = ssrd - ssr
    upward_lw = strd - strr

    # Direct solar radiation incident on the person
    # thermofeel / ERA5-HEAT formulation:
    # dsrp = fdir / cos(solar zenith angle)

    threshold = 1e-6

    direct_sw = xr.where(
        cossza > threshold,
        fdir / cossza,
        fdir
    )

    # Body projected-area factor

    gamma = np.degrees(
        np.arcsin(
            np.clip(cossza, 0.0, 1.0)
        )
    )

    fp = (
        0.308
        * np.cos(
            np.deg2rad(
                gamma
                * (
                    0.998
                    - (gamma ** 2) / 50000.0
                )
            )
        )
    )

    # Mean Radiant Temperature [K]

    mrt_kelvin = (
        (
            1.0 / SIGMA
        )
        * (
            HEMISPHERE_FACTOR * strd
            + HEMISPHERE_FACTOR * upward_lw
            + (
                SOLAR_ABSORPTIVITY
                / BODY_EMISSIVITY
            )
            * (
                HEMISPHERE_FACTOR * diffuse_sw
                + HEMISPHERE_FACTOR * reflected_sw
                + fp * direct_sw
            )
        )
    ) ** 0.25

    # Convert Kelvin → Celsius
    ds["mrt"] = mrt_kelvin - 273.15

    return ds