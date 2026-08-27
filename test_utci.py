from pythermalcomfort.models import utci

# Sample weather conditions
tdb = 40.0   # Air temperature (°C)
tr = 45.0    # Mean radiant temperature (°C)
v = 2.0      # Wind speed (m/s)
rh = 40.0    # Relative humidity (%)

# Calculate UTCI
result = utci(
    tdb=tdb,
    tr=tr,
    v=v,
    rh=rh
)

print("UTCI calculation successful!")
print("Air temperature:", tdb, "°C")
print("Mean radiant temperature:", tr, "°C")
print("Wind speed:", v, "m/s")
print("Relative humidity:", rh, "%")
print("UTCI:", result)