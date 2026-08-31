"""
Vrinda - Day 3 (final): Dashboard connected to REAL, complete data.

Data sources (all real, no dummy values):
  - data/spatial/ahmedabad_wards_clean.geojson   (Garima, Day 1 - 48 real ward boundaries)
  - data/processed/priority_rubric_v1_full_test.csv (Khushi, Day 3 - real CTBI/NCTL/UTCI
    per ward per day, 2021-2026, with thermal-tier categorization already applied)

Upgrade over the earlier Day 3 version: since Garima's real output now covers
ALL 546 days (not just one snapshot), the dashboard now has a DATE SELECTOR -
any day in the 6-year record can be viewed, not just one fixed day.

Honesty note (unchanged from before, still accurate): vulnerability and
response-capacity data are still not available (AMC file manual-download
blocker, open since Day 2). Priority is therefore shown as thermal-only,
explicitly labeled as partial - exactly matching Khushi's own labeling in
her Day 3 output, so the whole team is consistent on this point.

Architecture unchanged: Map -> Ward click -> Detail card.
"""
import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import json

st.set_page_config(page_title="Ahmedabad Heat-Health Early Warning", layout="wide")

TIER_COLORS = {"Low": "#2ecc71", "Moderate": "#f1c40f", "High": "#e74c3c"}


@st.cache_data
def load_data():
    gdf = gpd.read_file("data/spatial/ahmedabad_wards_clean.geojson")
    thermal = pd.read_csv("data/processed/priority_rubric_v1_full_test.csv", parse_dates=["date"])
    return gdf, thermal

gdf, thermal = load_data()

available_dates = sorted(thermal["date"].dt.date.unique())
peak_date = thermal.loc[thermal["CTBI"].idxmax(), "date"].date()

if "selected_ward" not in st.session_state:
    st.session_state.selected_ward = gdf["Ward_Name"].iloc[0]
if "selected_date" not in st.session_state:
    st.session_state.selected_date = peak_date

# ---------------------------------------------------------------
# TITLE
# ---------------------------------------------------------------
st.title("🌡️ Ahmedabad Extreme Heatwave Early Warning System")
st.caption("Human Thermal Stress & Heat-Health Priority Dashboard — Prototype")

# ---------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------
with st.sidebar:
    st.header("Controls")

    selected_date = st.select_slider(
        "Date", options=available_dates,
        value=st.session_state.selected_date,
        help="Full 6-year real dataset (2021-2026). Defaults to the peak CTBI day."
    )
    st.session_state.selected_date = selected_date
    if selected_date == peak_date:
        st.caption("📅 Showing the peak CTBI day in the whole 6-year record.")

    ward_names = sorted(gdf["Ward_Name"].tolist())
    dropdown_choice = st.selectbox(
        "Ward", ward_names,
        index=ward_names.index(st.session_state.selected_ward)
    )
    if dropdown_choice != st.session_state.selected_ward:
        st.session_state.selected_ward = dropdown_choice

    st.markdown("---")
    st.caption("🟢 **Real:** ward boundaries, CTBI/NCTL/UTCI (all 546 days, 2021–2026)")
    st.caption("🟡 **Pending:** vulnerability & response capacity data (manual AMC download still needed) — priority is thermal-only until this is added")

# ---------------------------------------------------------------
# DATA FOR SELECTED DATE
# ---------------------------------------------------------------
day_data = thermal[thermal["date"].dt.date == st.session_state.selected_date]
gdf_day = gdf.merge(
    day_data[["Ward_ID", "CTBI", "NCTL", "UTCI_mean", "thermal_tier_only", "priority_v1"]],
    on="Ward_ID", how="left"
)

# ---------------------------------------------------------------
# LAYOUT: map + detail card
# ---------------------------------------------------------------
col_map, col_detail = st.columns([2, 1])

with col_map:
    st.subheader(f"Ward Thermal Burden Map — {st.session_state.selected_date}")
    geojson_dict = json.loads(gdf_day.to_json())

    fig = px.choropleth_map(
        gdf_day,
        geojson=geojson_dict,
        locations=gdf_day.index,
        color="thermal_tier_only",
        hover_name="Ward_Name",
        hover_data={"CTBI": ":.3f", "NCTL": ":.2f", "UTCI_mean": ":.1f"},
        color_discrete_map=TIER_COLORS,
        category_orders={"thermal_tier_only": ["Low", "Moderate", "High"]},
        map_style="carto-positron",
        center={"lat": 23.02, "lon": 72.57},
        zoom=9.5,
        opacity=0.7,
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=560)

    event = st.plotly_chart(
        fig, use_container_width=True,
        on_select="rerun", selection_mode="points", key="ward_map"
    )
    if event and event.selection and event.selection.get("points"):
        clicked_index = event.selection["points"][0]["location"]
        clicked_ward = gdf_day.loc[int(clicked_index), "Ward_Name"]
        st.session_state.selected_ward = clicked_ward

    tier_counts = day_data["thermal_tier_only"].value_counts()
    st.caption(f"On this date: {tier_counts.get('Low',0)} Low · {tier_counts.get('Moderate',0)} Moderate · {tier_counts.get('High',0)} High")

with col_detail:
    st.subheader(f"Ward Detail: {st.session_state.selected_ward}")
    row = gdf_day[gdf_day["Ward_Name"] == st.session_state.selected_ward]

    if len(row) == 0 or row.iloc[0]["CTBI"] != row.iloc[0]["CTBI"]:  # NaN check
        st.warning("No data for this ward on this date.")
    else:
        row = row.iloc[0]
        tier_icons = {"Low": "🟢", "Moderate": "🟡", "High": "🔴"}
        st.markdown(f"### {tier_icons.get(row['thermal_tier_only'],'')} Thermal Tier: **{row['thermal_tier_only']}**")

        st.metric("CTBI", f"{row['CTBI']:.3f}")
        st.metric("NCTL", f"{row['NCTL']:.2f} degree-hours")
        st.metric("UTCI (daily mean)", f"{row['UTCI_mean']:.1f} °C")

        st.markdown("---")
        st.warning("⏳ **Priority: pending.** Vulnerability & response capacity data not yet available (manual AMC download still needed) — this ward's rating reflects thermal exposure only, not overall risk.")

st.markdown("---")
st.caption("🟢 Demonstrated: real ward boundaries (48) + real CTBI/NCTL/UTCI (full 546-day 2021-2026 record, per-ward via nearest-grid spatial join) | 🟡 Prototype/Pending: vulnerability data, final priority engine")
