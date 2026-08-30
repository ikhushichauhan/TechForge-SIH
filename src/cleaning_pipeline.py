import xarray as xr
import numpy as np
import pandas as pd


def clean_weather_data(ds: xr.Dataset) -> pd.DataFrame:
    """
    Raw weather xarray Dataset -> Cleaned pandas DataFrame
    Expects variables: t2m, d2m, u10, v10 (jaise ERA5 mein hote hain)
    """
    df = ds.to_dataframe().reset_index()

    # Temperature: Kelvin -> Celsius
    df["t2m_C"] = df["t2m"] - 273.15
    df["d2m_C"] = df["d2m"] - 273.15

    # Wind speed
    df["wind_speed"] = np.sqrt(df["u10"]**2 + df["v10"]**2)

    # Relative Humidity
    a, b = 17.625, 243.04
    numerator = np.exp((a * df["d2m_C"]) / (b + df["d2m_C"]))
    denominator = np.exp((a * df["t2m_C"]) / (b + df["t2m_C"]))
    df["RH"] = 100 * (numerator / denominator)

    return df[["time", "lat", "lon", "t2m_C", "d2m_C", "wind_speed", "RH"]]


if __name__ == "__main__":
    times = pd.date_range("2024-05-01", periods=24, freq="h")
    lat = [23.0]
    lon = [72.5]

    ds = xr.Dataset(
        {
            "t2m": (["time", "lat", "lon"], np.random.uniform(295, 315, (24, 1, 1))),
            "d2m": (["time", "lat", "lon"], np.random.uniform(285, 300, (24, 1, 1))),
            "u10": (["time", "lat", "lon"], np.random.uniform(-5, 5, (24, 1, 1))),
            "v10": (["time", "lat", "lon"], np.random.uniform(-5, 5, (24, 1, 1))),
        },
        coords={"time": times, "lat": lat, "lon": lon}
    )

    cleaned_df = clean_weather_data(ds)
    print("Cleaned Weather DataFrame:")
    print(cleaned_df.head())
    print(f"\nTotal rows: {len(cleaned_df)}")