"""
Vrinda - Day 2: Dashboard skeleton with locked interaction architecture
Map -> Ward click -> Detail card

Real ward boundaries (48 wards, Garima's Day 1 output).
UTCI/NCTL/CTBI/priority values are still dummy placeholders - only the
data-loading section changes once Dev/Garima's real spatial dataset lands.

KEY UPGRADE from Day 1: ward selection now works BOTH ways -
  1. Sidebar dropdown (for accessibility / quick lookup)
  2. Clicking directly on the map (the core "Map -> Ward click -> Detail card" flow)
Both update the same session_state, so the detail card always reflects
whichever selection happened most recently.
"""
import streamlit as st
import geopandas as gpd
import plotly.express as px
import json
import random

st.set_page_config(page_title="Ahmedabad Heat-Health Early Warning", layout="wide")

# ---------------------------------------------------------------
# DATA LOADING (swap this section for real thermal/spatial data later)
# ---------------------------------------------------------------
@st.cache_data
def load_wards():
    gdf = gpd.read_file("data/spatial/ahmedabad_wards_clean.geojson")
    random.seed(42)
    gdf["priority"] = [random.choice(["Low", "Moderate", "High", "Critical"]) for _ in range(len(gdf))]
    gdf["UTCI"] = [round(random.uniform(28, 50), 1) for _ in range(len(gdf))]
    gdf["NCTL"] = [round(random.uniform(0, 15), 1) for _ in range(len(gdf))]
    gdf["CTBI"] = [round(random.uniform(0, 100), 1) for _ in range(len(gdf))]
    gdf["vulnerability"] = [random.choice(["Low", "High"]) for _ in range(len(gdf))]
    gdf["response_capacity"] = [random.choice(["Low", "High"]) for _ in range(len(gdf))]
    return gdf.reset_index(drop=True)

gdf = load_wards()

# ---------------------------------------------------------------
# SESSION STATE - single source of truth for "which ward is selected"
# ---------------------------------------------------------------
if "selected_ward" not in st.session_state:
    st.session_state.selected_ward = gdf["Ward_Name"].iloc[0]

# ---------------------------------------------------------------
# TITLE
# ---------------------------------------------------------------
st.title("🌡️ Ahmedabad Extreme Heatwave Early Warning System")
st.caption("Human Thermal Stress & Heat-Health Priority Dashboard — Prototype")

# ---------------------------------------------------------------
# SIDEBAR (path 1 into selected_ward)
# ---------------------------------------------------------------
with st.sidebar:
    st.header("Select a Ward")
    ward_names = sorted(gdf["Ward_Name"].tolist())
    dropdown_choice = st.selectbox(
        "Ward", ward_names,
        index=ward_names.index(st.session_state.selected_ward)
    )
    if dropdown_choice != st.session_state.selected_ward:
        st.session_state.selected_ward = dropdown_choice

# ---------------------------------------------------------------
# LAYOUT: map + detail card
# ---------------------------------------------------------------
col_map, col_detail = st.columns([2, 1])

with col_map:
    st.subheader("Ward Risk Map — click a ward to select it")
    geojson_dict = json.loads(gdf.to_json())

    fig = px.choropleth_map(
        gdf,
        geojson=geojson_dict,
        locations=gdf.index,
        color="priority",
        hover_name="Ward_Name",
        color_discrete_map={
            "Low": "#2ecc71", "Moderate": "#f1c40f",
            "High": "#e67e22", "Critical": "#e74c3c",
        },
        category_orders={"priority": ["Low", "Moderate", "High", "Critical"]},
        map_style="carto-positron",
        center={"lat": 23.02, "lon": 72.57},
        zoom=9.5,
        opacity=0.7,
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=600)

    # --- PATH 2 into selected_ward: clicking the map itself ---
    event = st.plotly_chart(
        fig, use_container_width=True,
        on_select="rerun", selection_mode="points", key="ward_map"
    )
    if event and event.selection and event.selection.get("points"):
        clicked_index = event.selection["points"][0]["location"]
        clicked_ward = gdf.loc[int(clicked_index), "Ward_Name"]
        st.session_state.selected_ward = clicked_ward

    st.caption("⚠️ Priority levels shown are placeholder values — will be replaced with real CTBI-based priority once Dev/Garima's pipeline output is integrated.")

with col_detail:
    st.subheader(f"Ward Detail: {st.session_state.selected_ward}")
    row = gdf[gdf["Ward_Name"] == st.session_state.selected_ward].iloc[0]

    priority_colors = {"Low": "🟢", "Moderate": "🟡", "High": "🟠", "Critical": "🔴"}
    st.markdown(f"### {priority_colors.get(row['priority'],'')} Priority: **{row['priority']}**")

    st.metric("UTCI", f"{row['UTCI']} °C")
    st.metric("NCTL", f"{row['NCTL']} degree-hours")
    st.metric("CTBI", f"{row['CTBI']}")

    st.write("**Vulnerability:**", row["vulnerability"])
    st.write("**Response Capacity:**", row["response_capacity"])

    st.markdown("---")
    st.markdown("**Recommended Action** *(placeholder — Khushi's action engine will fill this in)*")
    st.info("Activate cooling resources and prioritize vulnerable-population checks.")

st.markdown("---")
st.caption("🟢 Demonstrated: Ward boundaries (real, 48 wards, DataMeet source) | 🟡 Prototype: Priority values shown are placeholders pending real CTBI integration")
