"""
Khushi — Priority Rubric v2 (update to v1)

WHAT CHANGED FROM v1:
v1 could only return "Thermal-only: <tier> (partial)" because vulnerability
data was blocked (2011 Census ward-delimitation mismatch — see Decision Log D7).

v2 plugs in REAL vulnerability, now available via GEE (Decision Log D8):
    - population_density (WorldPop 100m, 2020)
    - ndvi_green_cover (Sentinel-2, Mar-May 2024)

Vulnerability classification rule (documented, not fabricated):
    High vulnerability = population_density in the top tercile (busiest,
    hardest to evacuate/cool) OR ndvi_green_cover in the bottom tercile
    (least natural cooling). Either condition alone is enough to flag High,
    since both are independent heat-vulnerability pathways.

response_capacity is STILL NOT available (healthcare-access via OSM was
never built). So v2 cannot yet return a full CRITICAL verdict, because the
locked rule requires all three factors:
    "High thermal + High vulnerability + Low response capacity = CRITICAL"

Instead, v2 introduces an honest intermediate state:
    "<tier> (partial — response capacity pending)"
which uses REAL thermal + REAL vulnerability, but is capped below CRITICAL
until response_capacity is real too.
"""

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# PART 1 — Classify vulnerability from real GEE data
# ---------------------------------------------------------------------------

demo = pd.read_csv("data/spatial/demographic_join_template.csv")

pop_density_high_thr = demo["population_density"].quantile(2 / 3)
ndvi_low_thr = demo["ndvi_green_cover"].quantile(1 / 3)

print(f"Population density top-tercile threshold: {pop_density_high_thr:.1f} people/km²")
print(f"NDVI bottom-tercile threshold: {ndvi_low_thr:.4f}")


def classify_vulnerability(pop_density, ndvi):
    high_density = pop_density >= pop_density_high_thr
    low_green = ndvi <= ndvi_low_thr
    return "High" if (high_density or low_green) else "Low"


demo["vulnerability"] = demo.apply(
    lambda r: classify_vulnerability(r["population_density"], r["ndvi_green_cover"]), axis=1
)

print(f"\nVulnerability distribution across 48 wards:")
print(demo["vulnerability"].value_counts())
print(f"\nHigh-vulnerability wards:")
print(demo[demo["vulnerability"] == "High"][["Ward_Name", "population_density", "ndvi_green_cover"]]
      .sort_values("population_density", ascending=False).to_string(index=False))

demo[["Ward_ID", "Ward_Name", "vulnerability"]].to_csv(
    "data/processed/ward_vulnerability_v2.csv", index=False
)

# ---------------------------------------------------------------------------
# PART 2 — Priority Rubric v2 function
# ---------------------------------------------------------------------------


def classify_thermal_tier(ctbi_value, low_thr, high_thr):
    if ctbi_value < low_thr:
        return "Low"
    elif ctbi_value < high_thr:
        return "Moderate"
    else:
        return "High"


def priority_rubric_v2(ctbi_value, vulnerability=None, response_capacity=None,
                        ctbi_low_thr=None, ctbi_high_thr=None):
    """
    Full rule (once response_capacity is real too):
        High thermal + High vulnerability + Low response capacity -> CRITICAL
        High thermal + (High vulnerability OR Low response capacity) -> HIGH
        Moderate thermal + High vulnerability -> MODERATE
        Everything else -> LOW

    v2 partial rule (vulnerability real, response_capacity still None):
        Same tiering logic, but the verdict is suffixed
        "(partial — response capacity pending)" and CRITICAL is never
        returned, since that requires low response capacity to be
        genuinely confirmed, not assumed.
    """
    thermal_tier = classify_thermal_tier(ctbi_value, ctbi_low_thr, ctbi_high_thr)

    if vulnerability is None:
        return f"Thermal-only: {thermal_tier} (partial — vulnerability/response capacity pending)"

    high_vuln = vulnerability == "High"

    if response_capacity is None:
        # Real thermal + real vulnerability, response capacity still missing.
        if thermal_tier == "High" and high_vuln:
            return "HIGH (partial — response capacity pending)"
        if thermal_tier == "High" or (thermal_tier == "Moderate" and high_vuln):
            return "MODERATE (partial — response capacity pending)"
        return "LOW (partial — response capacity pending)"

    # Full rule — only reachable once response_capacity is real.
    low_capacity = response_capacity == "Low"
    if thermal_tier == "High" and high_vuln and low_capacity:
        return "CRITICAL"
    if thermal_tier == "High" and (high_vuln or low_capacity):
        return "HIGH"
    if thermal_tier == "Moderate" and high_vuln:
        return "MODERATE"
    if thermal_tier == "Low":
        return "LOW"
    return "MODERATE"


# ---------------------------------------------------------------------------
# PART 3 — Re-run the full test with REAL vulnerability plugged in
# ---------------------------------------------------------------------------

ward_thermal = pd.read_csv("data/processed/ward_thermal_daily.csv")
ctbi_city = pd.read_csv("data/processed/CTBI.csv")

ctbi_low_thr = ctbi_city["CTBI"].quantile(0.33)
ctbi_high_thr = ctbi_city["CTBI"].quantile(0.66)

merged = ward_thermal.merge(demo[["Ward_ID", "vulnerability"]], on="Ward_ID", how="left")

merged["priority_v2"] = merged.apply(
    lambda r: priority_rubric_v2(
        r["CTBI"], vulnerability=r["vulnerability"], response_capacity=None,
        ctbi_low_thr=ctbi_low_thr, ctbi_high_thr=ctbi_high_thr
    ), axis=1
)

merged.to_csv("data/processed/priority_rubric_v2_full_test.csv", index=False)

latest_date = merged["date"].max()
snapshot = merged[merged["date"] == latest_date][
    ["Ward_ID", "Ward_Name", "date", "CTBI", "vulnerability", "priority_v2"]
]
snapshot.to_csv("data/processed/priority_rubric_v2_test_snapshot.csv", index=False)

print(f"\nSnapshot date: {latest_date}")
print(snapshot.to_string(index=False))
print(f"\nSaved: data/processed/priority_rubric_v2_full_test.csv ({len(merged)} rows)")
print(f"Saved: data/processed/priority_rubric_v2_test_snapshot.csv ({len(snapshot)} wards)")
print(f"Saved: data/processed/ward_vulnerability_v2.csv (48 wards)")
