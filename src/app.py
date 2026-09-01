"""
Vrinda - Day 4 (main dashboard owner): connected to Garima's LOCKED final
spatial dataset.

Data sources (both real, both locked — see Garima_Day4_Completion_Summary.md):
  - data/processed/final_wards_static.geojson  (48 wards: geometry + real
    vulnerability, from WorldPop population density + Sentinel-2 NDVI, D8/D10)
  - data/processed/final_ward_daily.csv        (26,208 rows: real UTCI/NCTL/
    CTBI, D2-D6; real priority_v2, D10; real HAP-grounded recommended
    actions, Day 4 Action Engine)

This replaces the earlier version that read priority_rubric_v1_full_test.csv
(flagged as stale by Shweta's Day 4 validation — see
Shweta_Day4_Validation_Report.md). No more "vulnerability pending" message:
vulnerability is real now, so the sidebar/detail-card language below reflects
that.

response_capacity is still honestly "Pending" (healthcare-access/OSM not yet
built) — shown as such in the detail card, not hidden or faked.

Deliberately NOT fancy: real data + working ward-click interaction + clean
screenshot is the Day 4 bar, per the playbook. Polish is Day 5's job, if time
allows.
"""
import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import json

st.set_page_config(page_title="Ahmedabad Heat-Health Early Warning", layout="wide")

TIER_COLORS = {"LOW": "#2ecc71", "MODERATE": "#f1c40f", "HIGH": "#e67e22", "CRITICAL": "#c0392b"}
TIER_ICONS = {"LOW": "🟢", "MODERATE": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}


@st.cache_data
def load_data():
    wards_static = gpd.read_file("data/processed/final_wards_static.geojson")
    daily = pd.read_csv("data/processed/final_ward_daily.csv", parse_dates=["date"])
    return wards_static, daily


wards_static, daily = load_data()

available_dates = sorted(daily["date"].dt.date.unique())
peak_date = daily.loc[daily["CTBI"].idxmax(), "date"].date()

if "selected_ward" not in st.session_state:
    st.session_state.selected_ward = wards_static["Ward_Name"].iloc[0]
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

    ward_names = sorted(wards_static["Ward_Name"].tolist())
    dropdown_choice = st.selectbox(
        "Ward", ward_names,
        index=ward_names.index(st.session_state.selected_ward)
    )
    if dropdown_choice != st.session_state.selected_ward:
        st.session_state.selected_ward = dropdown_choice

    st.markdown("---")
    st.caption("🟢 **Real:** ward boundaries, CTBI/NCTL/UTCI (546 days, 2021–2026), "
               "vulnerability (WorldPop population density + Sentinel-2 NDVI)")
    st.caption("🟡 **Pending:** response capacity (healthcare-access data not yet built) "
               "— priority is capped below CRITICAL until this is added")

# ---------------------------------------------------------------
# DATA FOR SELECTED DATE
# ---------------------------------------------------------------
day_data = daily[daily["date"].dt.date == st.session_state.selected_date].copy()
# NOTE: both final_wards_static.geojson and final_ward_daily.csv carry a
# 'vulnerability' column (static file: Garima's ward-level classification;
# daily file: Khushi's priority_rubric_v2 recomputed it per-row for its own
# use). They agree in value but merging both would create vulnerability_x/
# vulnerability_y instead of a clean column. The static file is authoritative
# (vulnerability doesn't change day-to-day) — drop the daily copy before merging.
day_data = day_data.drop(columns=["vulnerability"])
gdf_day = wards_static.merge(day_data, on=["Ward_ID", "Ward_Name"], how="left")

# ---------------------------------------------------------------
# LAYOUT: map + detail card
# ---------------------------------------------------------------
col_map, col_detail = st.columns([2, 1])

with col_map:
    st.subheader(f"Ward Heat-Health Priority Map — {st.session_state.selected_date}")
    geojson_dict = json.loads(gdf_day.to_json())

    fig = px.choropleth_map(
        gdf_day,
        geojson=geojson_dict,
        locations=gdf_day.index,
        color="tier",
        hover_name="Ward_Name",
        hover_data={"CTBI": ":.3f", "NCTL": ":.2f", "UTCI_mean": ":.1f", "vulnerability": True},
        color_discrete_map=TIER_COLORS,
        category_orders={"tier": ["LOW", "MODERATE", "HIGH", "CRITICAL"]},
        map_style="carto-positron",
        center={"lat": 23.02, "lon": 72.57},
        zoom=9.5,
        opacity=0.75,
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

    tier_counts = day_data["tier"].value_counts()
    st.caption(
        f"On this date: {tier_counts.get('LOW',0)} Low · {tier_counts.get('MODERATE',0)} Moderate · "
        f"{tier_counts.get('HIGH',0)} High · {tier_counts.get('CRITICAL',0)} Critical"
    )

with col_detail:
    st.subheader(f"Ward Detail: {st.session_state.selected_ward}")
    row = gdf_day[gdf_day["Ward_Name"] == st.session_state.selected_ward]

    if len(row) == 0 or pd.isna(row.iloc[0]["CTBI"]):
        st.warning("No data for this ward on this date.")
    else:
        row = row.iloc[0]
        tier = row["tier"]
        st.markdown(f"### {TIER_ICONS.get(tier,'')} Priority: **{tier}**")
        st.caption(row["priority_v2"])

        st.metric("CTBI (Cumulative Thermal Burden)", f"{row['CTBI']:.3f}")
        st.metric("NCTL (Nighttime Load)", f"{row['NCTL']:.2f} degree-hours")
        st.metric("UTCI (daily mean)", f"{row['UTCI_mean']:.1f} °C")

        st.markdown("---")
        st.markdown("**Vulnerability & Response Capacity**")
        vuln_icon = "🔴" if row["vulnerability"] == "High" else "🟢"
        st.write(f"{vuln_icon} Vulnerability: **{row['vulnerability']}**")
        st.caption(f"Population density: {row['population_density']:,.0f}/km² · "
                    f"NDVI (green cover): {row['ndvi_green_cover']:.3f}")
        st.write(f"⏳ Response Capacity: **{row['response_capacity']}** "
                  f"(healthcare-access data not yet built)")
        if row["drivers"] != "none" and pd.notna(row["drivers"]):
            st.caption(f"Vulnerability drivers: {row['drivers']}")

        st.markdown("---")
        st.markdown("**Recommended Actions**")
        actions = str(row["recommended_actions"]).split(" | ")
        for a in actions:
            st.write(f"- {a}")

st.markdown("---")
st.caption(
    "🟢 Demonstrated: real ward boundaries (48) + real CTBI/NCTL/UTCI (546 days, 2021-2026) "
    "+ real vulnerability (WorldPop + Sentinel-2 NDVI) + HAP-grounded action recommendations "
    "| 🟡 Prototype/Pending: response capacity (healthcare access), full CRITICAL tier"
)
