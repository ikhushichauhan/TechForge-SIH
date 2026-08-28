"""
Vrinda - Day 1: Streamlit dashboard skeleton
Connected to REAL Ahmedabad ward boundaries (not dummy shapes).
Risk/UTCI/NCTL/CTBI values are still dummy placeholders - Dev/Garima will
supply the real spatial dataset on Day 3-4, at which point only the data
loading section below needs to change (map/UI code stays the same).
"""
import streamlit as st
import geopandas as gpd
import plotly.express as px
import json
import random

st.set_page_config(page_title="Ahmedabad Heat-Health Early Warning", layout="wide")

# ---------------------------------------------------------------
# DATA LOADING (this section gets swapped for real thermal data later)
# ---------------------------------------------------------------
@st.cache_data
def load_wards():
    gdf = gpd.read_file("data/spatial/ahmedabad_wards_clean.geojson")
    # --- DUMMY DATA (placeholder until Dev/Garima's real CTBI/priority join) ---
    random.seed(42)
    gdf["priority"] = [random.choice(["Low", "Moderate", "High", "Critical"]) for _ in range(len(gdf))]
    gdf["UTCI"] = [round(random.uniform(28, 50), 1) for _ in range(len(gdf))]
    gdf["NCTL"] = [round(random.uniform(0, 15), 1) for _ in range(len(gdf))]
    gdf["CTBI"] = [round(random.uniform(0, 100), 1) for _ in range(len(gdf))]
    gdf["vulnerability"] = [random.choice(["Low", "High"]) for _ in range(len(gdf))]
    gdf["response_capacity"] = [random.choice(["Low", "High"]) for _ in range(len(gdf))]
    return gdf

gdf = load_wards()

# ---------------------------------------------------------------
# TITLE
# ---------------------------------------------------------------
st.title("🌡️ Ahmedabad Extreme Heatwave Early Warning System")
st.caption("Human Thermal Stress & Heat-Health Priority Dashboard — Prototype")

# ---------------------------------------------------------------
# LAYOUT: sidebar selection + map + detail card
# ---------------------------------------------------------------
col_map, col_detail = st.columns([2, 1])

with st.sidebar:
    st.header("Select a Ward")
    ward_names = sorted(gdf["Ward_Name"].tolist())
    selected_ward = st.selectbox("Ward", ward_names)

with col_map:
    st.subheader("Ward Risk Map")
    geojson_dict = json.loads(gdf.to_json())

    fig = px.choropleth_map(
        gdf,
        geojson=geojson_dict,
        locations=gdf.index,
        color="priority",
        hover_name="Ward_Name",
        color_discrete_map={
            "Low": "#2ecc71",
            "Moderate": "#f1c40f",
            "High": "#e67e22",
            "Critical": "#e74c3c",
        },
        category_orders={"priority": ["Low", "Moderate", "High", "Critical"]},
        map_style="carto-positron",
        center={"lat": 23.02, "lon": 72.57},
        zoom=9.5,
        opacity=0.7,
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("⚠️ Priority levels shown are placeholder values — will be replaced with real CTBI-based priority once Dev/Garima's pipeline output is integrated.")

with col_detail:
    st.subheader(f"Ward Detail: {selected_ward}")
    row = gdf[gdf["Ward_Name"] == selected_ward].iloc[0]

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
