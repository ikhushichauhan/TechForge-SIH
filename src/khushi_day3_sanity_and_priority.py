"""
Khushi — Day 3 deliverable
1. Independent sanity-check of Dev's CTBI output (city-wide series).
2. Priority Rubric v1 — transparent, rule-based, documented in Decision Log.
3. Test the rubric on real ward-level CTBI (from Garima's ward_thermal_daily.csv).

IMPORTANT / HONESTY NOTE:
Vulnerability and Response Capacity ward-level data are NOT yet available
(demographic_join_template.csv is still empty — blocked, see team discussion
on 2011 census ward-delimitation mismatch: 57 old wards vs 48 current wards).

So this script:
  - Runs the CTBI sanity checks on REAL data (fully valid, no blocker).
  - Builds the priority rubric logic (fully valid, rule-based, not ML).
  - Tests the rubric using REAL thermal burden (CTBI) only.
  - Vulnerability and response-capacity inputs are left as None/NaN in the
    test run, and the priority level is reported as "Thermal-only priority
    (partial)" instead of a full Low/Moderate/High/Critical, so we never
    imply a vulnerability signal that does not exist yet.
"""

import pandas as pd
import numpy as np
import os

RAW_DIR = "data/processed"
OUT_DIR = "data/processed"
DOCS_DIR = "docs"
PROOF_DIR = "proof_of_work"

os.makedirs(PROOF_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# PART 1 — CTBI SANITY CHECK (city-wide series, from Dev's CTBI.csv)
# ---------------------------------------------------------------------------

ctbi = pd.read_csv(os.path.join(RAW_DIR, "CTBI.csv"), parse_dates=["date"])

sanity_report_lines = []
sanity_report_lines.append("# Khushi — Day 3 CTBI Sanity Check\n")
sanity_report_lines.append(
    "Independent verification of Dev's CTBI.csv (city-wide, 6 heatwave "
    "seasons, 91 days/year, 2021-2026). This is NOT a re-derivation of the "
    "formula — it is a behavioural check: does CTBI move the way physical "
    "reasoning says it should?\n"
)

all_pass = True

for y in sorted(ctbi["year"].unique()):
    sub = ctbi[ctbi["year"] == y].reset_index(drop=True)
    first_ctbi = sub.iloc[0]["CTBI"]
    peak_row = sub.loc[sub["CTBI"].idxmax()]
    last_ctbi = sub.iloc[-1]["CTBI"]
    max_nctl = sub["NCTL"].max()
    early_nctl = sub.iloc[:5]["NCTL"].sum()  # first 5 days, early April

    # Check 1: CTBI should rise from a low starting point as the season
    # progresses into peak heat (accumulation behaviour).
    check1 = peak_row["CTBI"] > first_ctbi
    # Check 2: CTBI should decline again after the seasonal peak has passed
    # (recovery behaviour) rather than staying pinned at the peak.
    check2 = last_ctbi < peak_row["CTBI"]
    # Check 3: Early season (first 5 days of April) should show ~zero NCTL,
    # since nighttime heat load hasn't built up yet.
    check3 = early_nctl < 1.0

    status = "PASS" if (check1 and check2 and check3) else "CHECK"
    if status == "CHECK":
        all_pass = False

    sanity_report_lines.append(
        f"## {y} season\n"
        f"- Start CTBI: {first_ctbi:.3f} | Peak CTBI: {peak_row['CTBI']:.3f} "
        f"on {peak_row['date'].date()} | End CTBI: {last_ctbi:.3f}\n"
        f"- Max NCTL this season: {max_nctl:.2f} degree-hours\n"
        f"- Check 1 (CTBI rises from start to peak): {'✅' if check1 else '❌'}\n"
        f"- Check 2 (CTBI declines after peak, i.e. recovery): {'✅' if check2 else '❌'}\n"
        f"- Check 3 (near-zero NCTL in first 5 days of April): {'✅' if check3 else '❌'}\n"
        f"- **Result: {status}**\n"
    )

# Check 4 (cross-year): higher max NCTL in a season should generally
# correlate with a higher CTBI peak that season (nighttime load is a direct
# CTBI input via NCTL_norm).
yearly = ctbi.groupby("year").agg(peak_ctbi=("CTBI", "max"), max_nctl=("NCTL", "max"))
corr = yearly["peak_ctbi"].corr(yearly["max_nctl"])
sanity_report_lines.append(
    f"## Cross-year check\n"
    f"- Correlation between a season's max NCTL and its peak CTBI: **{corr:.3f}**\n"
    f"- Expected: positive and reasonably strong, since NCTL directly feeds "
    f"CTBI via the γ·NCTL_norm term.\n"
    f"- **Result: {'✅ PASS' if corr > 0.3 else '❌ CHECK'}**\n"
)
if corr <= 0.3:
    all_pass = False

sanity_report_lines.append(
    f"\n## Overall sanity verdict: {'✅ ALL CHECKS PASS' if all_pass else '⚠️ SOME CHECKS NEED REVIEW'}\n"
)

with open(os.path.join(DOCS_DIR, "Khushi_Day3_CTBI_Sanity_Check.md"), "w") as f:
    f.writelines(sanity_report_lines)

print("".join(sanity_report_lines))

# ---------------------------------------------------------------------------
# PART 2 — PRIORITY RUBRIC v1 (transparent, rule-based — not ML)
# ---------------------------------------------------------------------------
#
# Rule (as locked in the playbook):
#   High thermal burden + High vulnerability + Low response capacity = CRITICAL
#
# Because vulnerability and response-capacity are not yet available at ward
# level, this function is written to accept them as OPTIONAL. When they are
# None, the rubric explicitly returns a "thermal-only, partial" tier instead
# of pretending to have a full Critical/High/Moderate/Low verdict.


def classify_thermal_tier(ctbi_value, low_thr, high_thr):
    """Bins CTBI alone into Low / Moderate / High thermal burden."""
    if ctbi_value < low_thr:
        return "Low"
    elif ctbi_value < high_thr:
        return "Moderate"
    else:
        return "High"


def priority_rubric_v1(ctbi_value, vulnerability=None, response_capacity=None,
                        ctbi_low_thr=None, ctbi_high_thr=None):
    """
    Priority Rubric v1.

    thermal tier  : Low / Moderate / High   (from CTBI, always available)
    vulnerability : "Low" / "High" / None   (None = not yet available)
    response_cap  : "Low" / "High" / None   (None = not yet available, "Low" = poor capacity)

    Full rule (used once vulnerability + response capacity are real):
        High thermal + High vulnerability + Low response capacity -> CRITICAL
        High thermal + (High vulnerability OR Low response capacity)  -> HIGH
        Moderate thermal + High vulnerability                          -> MODERATE
        Everything else with full data                                 -> LOW

    Partial rule (current state — vulnerability/response capacity missing):
        Returns "Thermal-only: <tier> (partial — vulnerability/response
        capacity pending)" so we never claim a Critical/High verdict we
        cannot yet justify.
    """
    thermal_tier = classify_thermal_tier(ctbi_value, ctbi_low_thr, ctbi_high_thr)

    if vulnerability is None or response_capacity is None:
        return f"Thermal-only: {thermal_tier} (partial — vulnerability/response capacity pending)"

    high_vuln = vulnerability == "High"
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
# PART 3 — TEST the rubric on REAL ward-level CTBI (Garima's Day 3 output)
# ---------------------------------------------------------------------------

ward_thermal = pd.read_csv(os.path.join(RAW_DIR, "ward_thermal_daily.csv"))

# Use city-wide CTBI distribution (from Dev's sensitivity-tested series) to
# set thermal-tier thresholds, since ward-level CTBI here is currently a
# single city-wide series repeated across wards (documented limitation from
# Day 3 — Garima's spatial join uses one city-wide CTBI value per date, not
# per-grid-point CTBI, because CTBI.csv itself is a single time series).
ctbi_low_thr = ctbi["CTBI"].quantile(0.33)
ctbi_high_thr = ctbi["CTBI"].quantile(0.66)

print(f"\nThermal tier thresholds derived from real CTBI distribution: "
      f"Low < {ctbi_low_thr:.3f} <= Moderate < {ctbi_high_thr:.3f} <= High\n")

# Take the most recent date available per ward for a snapshot test
latest_date = ward_thermal["date"].max()
snapshot = ward_thermal[ward_thermal["date"] == latest_date].copy()

snapshot["priority_v1"] = snapshot["CTBI"].apply(
    lambda c: priority_rubric_v1(c, ctbi_low_thr=ctbi_low_thr, ctbi_high_thr=ctbi_high_thr)
)

snapshot_out = snapshot[["Ward_ID", "Ward_Name", "date", "CTBI", "priority_v1"]]
snapshot_out.to_csv(os.path.join(OUT_DIR, "priority_rubric_v1_test_snapshot.csv"), index=False)

print(f"Snapshot date used for test: {latest_date}")
print(snapshot_out.head(10).to_string(index=False))
print(f"\nSaved: {OUT_DIR}/priority_rubric_v1_test_snapshot.csv ({len(snapshot_out)} wards)")

# Also run the rubric across ALL dates (not just snapshot) to prove the tier
# distribution behaves sensibly over the full season (should shift toward
# High as the season progresses through peak heat, then back toward Low).
full_test = ward_thermal.copy()
full_test["priority_v1"] = full_test["CTBI"].apply(
    lambda c: priority_rubric_v1(c, ctbi_low_thr=ctbi_low_thr, ctbi_high_thr=ctbi_high_thr)
)
full_test["thermal_tier_only"] = full_test["priority_v1"].str.extract(r"Thermal-only: (\w+)")

tier_by_month = (
    full_test.assign(month=pd.to_datetime(full_test["date"]).dt.month)
    .groupby("month")["thermal_tier_only"]
    .value_counts(normalize=True)
    .unstack()
    .fillna(0)
    .round(3)
)
print("\nThermal-tier share by month (across all 48 wards, all days):")
print(tier_by_month)

full_test.to_csv(os.path.join(OUT_DIR, "priority_rubric_v1_full_test.csv"), index=False)
print(f"\nSaved: {OUT_DIR}/priority_rubric_v1_full_test.csv ({len(full_test)} rows)")
