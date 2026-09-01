"""
Khushi — Day 4 deliverable: Action Engine

Maps each ward's priority verdict (from priority_rubric_v2) + its real
drivers (thermal tier from CTBI, vulnerability type from population
density / NDVI) to a CONSERVATIVE, PUBLIC-HEALTH-PREPAREDNESS recommendation
— never a medical/treatment instruction.

Every recommendation category below is grounded in Ahmedabad's own,
real, already-implemented Heat Action Plan (HAP) — not invented. See
citations in the Decision Log entry this script generates (D11).

Sources (paraphrased, not quoted verbatim beyond short attributed phrases):
- Ahmedabad's color-coded alert system (Yellow/Orange/Red) scales actions
  from public awareness -> cooling-center activation -> hospital heat-ward
  readiness as conditions worsen.
- On milder (Yellow-equivalent) days: pamphlets/awareness, water points,
  fans/shade at transit hubs.
- On more severe (Orange/Red-equivalent) days: public buildings/temples/
  malls opened as cooling centers, outdoor work hours shifted, hospitals
  set up dedicated heat wards.
- Outreach to low-income/vulnerable groups works best through community
  health workers and local leaders, not just SMS/media alone.

We do NOT prescribe medical treatment. Every action below is a
preparedness/logistics recommendation for city authorities.
"""

import pandas as pd
import numpy as np

# ---------------------------------------------------------------------------
# PART 1 — Action rule table (documented, not fabricated)
# ---------------------------------------------------------------------------

# Base action set by priority tier (independent of driver).
# Mirrors Ahmedabad HAP's real escalation ladder: awareness -> infrastructure
# readiness -> cooling-center activation -> hospital/resource mobilization.
TIER_ACTIONS = {
    "LOW": [
        "Standard public awareness: heat-safety pamphlets/posters at community spaces",
        "Ensure public drinking-water points are functional and accessible",
    ],
    "MODERATE": [
        "Install/inspect fans and shade at transit hubs (bus stops, markets)",
        "Brief local community health workers on early heat-stress warning signs",
        "Pre-position mobile water/ORS distribution points",
    ],
    "HIGH": [
        "Activate designated cooling centers (public buildings, community halls) in this ward",
        "Advise shifting outdoor work (construction, vending, labour) to cooler hours",
        "Alert nearest hospitals/PHCs to prepare heat-illness triage capacity",
    ],
    "CRITICAL": [
        "Full cooling-center activation + extended hours in this ward",
        "Deploy mobile medical/first-aid teams proactively, not on-call only",
        "Prioritize this ward for emergency resource allocation (water tankers, staff)",
        "Targeted outreach via community leaders/health workers (not SMS alone — reaches low-literacy/low-income groups more reliably per Ahmedabad HAP lessons)",
    ],
}

# Driver-specific ADD-ON actions (only added when that specific vulnerability
# driver is the reason a ward is flagged, so the recommendation stays
# targeted rather than generic).
DRIVER_ADDONS = {
    "high_density": "High population density ward — prioritize crowd-accessible cooling centers and mist-sprinkler points at high-footfall junctions",
    "low_green": "Low green-cover ward — deploy portable shade structures/tents at transit and market areas as an interim measure (longer-term: prioritize for urban tree-cover planning)",
}


def get_vulnerability_drivers(pop_density, ndvi, pop_density_high_thr, ndvi_low_thr):
    """Returns which specific driver(s) triggered High vulnerability, if any."""
    drivers = []
    if pop_density >= pop_density_high_thr:
        drivers.append("high_density")
    if ndvi <= ndvi_low_thr:
        drivers.append("low_green")
    return drivers


def extract_base_tier(priority_v2_string):
    """priority_v2 strings look like 'HIGH (partial — response capacity pending)'
    or 'Thermal-only: Low (partial — ...)'. Extract just the tier word."""
    s = priority_v2_string.upper()
    for tier in ["CRITICAL", "HIGH", "MODERATE", "LOW"]:
        if tier in s:
            return tier
    return "LOW"


def recommend_actions(priority_v2_string, drivers):
    tier = extract_base_tier(priority_v2_string)
    actions = list(TIER_ACTIONS.get(tier, TIER_ACTIONS["LOW"]))
    for d in drivers:
        if d in DRIVER_ADDONS:
            actions.append(DRIVER_ADDONS[d])
    return tier, actions


# ---------------------------------------------------------------------------
# PART 2 — Run on real ward-level priority v2 data
# ---------------------------------------------------------------------------

demo = pd.read_csv("data/spatial/demographic_join_template.csv")
pop_density_high_thr = demo["population_density"].quantile(2 / 3)
ndvi_low_thr = demo["ndvi_green_cover"].quantile(1 / 3)

priority = pd.read_csv("data/processed/priority_rubric_v2_full_test.csv")
demo_small = demo[["Ward_ID", "population_density", "ndvi_green_cover"]]
merged = priority.merge(demo_small, on="Ward_ID", how="left")

results = []
for _, row in merged.iterrows():
    drivers = get_vulnerability_drivers(
        row["population_density"], row["ndvi_green_cover"],
        pop_density_high_thr, ndvi_low_thr
    )
    tier, actions = recommend_actions(row["priority_v2"], drivers)
    results.append({
        "Ward_ID": row["Ward_ID"],
        "Ward_Name": row["Ward_Name"],
        "date": row["date"],
        "CTBI": row["CTBI"],
        "vulnerability": row["vulnerability"],
        "priority_v2": row["priority_v2"],
        "tier": tier,
        "drivers": ", ".join(drivers) if drivers else "none",
        "recommended_actions": " | ".join(actions),
    })

action_df = pd.DataFrame(results)
action_df.to_csv("data/processed/action_engine_full_test.csv", index=False)

# Snapshot for the latest date (for demo/PPT)
latest_date = action_df["date"].max()
snapshot = action_df[action_df["date"] == latest_date]
snapshot.to_csv("data/processed/action_engine_test_snapshot.csv", index=False)

print(f"Thresholds — pop density top-tercile: {pop_density_high_thr:.1f}/km², NDVI bottom-tercile: {ndvi_low_thr:.4f}")
print(f"\nTier distribution across 48 wards, latest date ({latest_date}):")
print(snapshot["tier"].value_counts())
print(f"\nSample (5 wards):")
print(snapshot[["Ward_Name", "tier", "drivers", "recommended_actions"]].head(5).to_string(index=False))

print(f"\nSaved: data/processed/action_engine_full_test.csv ({len(action_df)} rows)")
print(f"Saved: data/processed/action_engine_test_snapshot.csv ({len(snapshot)} wards)")
