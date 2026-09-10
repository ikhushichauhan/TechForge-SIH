"""
Vrinda - Day 4 (main dashboard owner): connected to Garima's LOCKED final
spatial dataset.

Data sources:
  - data/spatial/final_wards_static.geojson
  - data/processed/final_ward_daily.csv

The dashboard demonstrates:
  - 48 real ward boundaries
  - real UTCI / NCTL / CTBI
  - real vulnerability context
  - prototype priority levels
  - HAP-grounded recommended actions
"""

import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import json


# ===============================================================
# HELPER TO CLEAN HTML (PREVENTS MARKDOWN CODEBLOCK CONVERSION)
# ===============================================================

def render_html(html_str: str):
    """
    Strips all leading whitespace from every line of HTML.
    This guarantees Markdown will NEVER convert HTML lines with 4+ spaces
    into <pre><code> code blocks with copy buttons.
    """
    cleaned = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


# ===============================================================
# PAGE CONFIGURATION
# ===============================================================

st.set_page_config(
    page_title="Ahmedabad Heat-Health Early Warning",
    page_icon="🌡️",
    layout="wide"
)


# ===============================================================
# SESSION STATE & THEME INITIALIZATION
# ===============================================================

if "dark_theme" not in st.session_state:
    st.session_state.dark_theme = False


# ===============================================================
# LOAD DATA
# ===============================================================

@st.cache_data
def load_data():
    wards_static = gpd.read_file("data/spatial/final_wards_static.geojson")
    daily = pd.read_csv("data/processed/final_ward_daily.csv", parse_dates=["date"])
    return wards_static, daily

wards_static, daily = load_data()


# ===============================================================
# AVAILABLE DATES & SESSION DEFAULTS
# ===============================================================

available_dates = sorted(daily["date"].dt.date.unique())
peak_date = daily.loc[daily["CTBI"].idxmax(), "date"].date()

if "selected_ward" not in st.session_state:
    st.session_state.selected_ward = wards_static["Ward_Name"].iloc[0]

if "selected_date" not in st.session_state:
    st.session_state.selected_date = peak_date


# ===============================================================
# SIDEBAR CONTROLS & THEME TOGGLE
# ===============================================================

with st.sidebar:
    render_html("""
    <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; margin-bottom: 0.8rem; padding-bottom: 0.35rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
        🎛️ Control Center
    </div>
    """)

    # Theme Switcher Toggle
    is_dark = st.toggle(
        "🌙 Dark Theme Mode",
        value=st.session_state.dark_theme,
        key="theme_toggle_widget",
        help="Toggle between Light and Dark Navy Command Dashboard theme"
    )
    st.session_state.dark_theme = is_dark

    st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)

    selected_date = st.select_slider(
        "Date Selection",
        options=available_dates,
        value=st.session_state.selected_date,
        help="6-year real dataset (2021-2026). Defaults to peak CTBI day."
    )
    st.session_state.selected_date = selected_date

    if selected_date == peak_date:
        st.caption("📅 Showing peak CTBI day across 6-year record.")

    ward_names = sorted(wards_static["Ward_Name"].tolist())

    dropdown_choice = st.selectbox(
        "Ward Search & Select",
        ward_names,
        index=ward_names.index(st.session_state.selected_ward)
    )

    if dropdown_choice != st.session_state.selected_ward:
        st.session_state.selected_ward = dropdown_choice

    st.markdown("---")

    render_html("""
    <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #94a3b8; margin-bottom: 0.8rem;">
        📊 Data Pipeline Status
    </div>
    <div class="sidebar-status-card status-real">
        <strong style="color: #4ade80;">🟢 Verified Operational Data</strong><br>
        48 Ward Boundaries, CTBI/NCTL/UTCI (546 days, 2021–2026), WorldPop Population Density, Sentinel-2 NDVI
    </div>
    <div class="sidebar-status-card status-pending">
        <strong style="color: #facc15;">🟡 Pending Module</strong><br>
        Response capacity (healthcare access OSM layer in development) — priority tier capped below CRITICAL
    </div>
    """)


# ===============================================================
# CSS INJECTION (LIGHT VS DEEP NAVY DARK THEME)
# ===============================================================

if st.session_state.dark_theme:
    # Deep Navy Command Center Dark Theme
    css_theme_vars = """
    :root {
        --bg-main: #0a1120;
        --bg-card: #111a2e;
        --bg-header: linear-gradient(135deg, #0b1426 0%, #16243f 100%);
        --bg-sidebar: #070d18;
        --border-color: #1e2c47;
        --border-hover: #3b82f6;
        --text-primary: #ffffff;
        --text-secondary: #e2e8f0;
        --text-muted: #94a3b8;
        --card-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        --card-shadow-hover: 0 10px 25px rgba(59, 130, 246, 0.25);
        --metric-bg: #162238;
        --action-bg: #131d33;
        --footer-bg: #111a2e;
    }
    """
else:
    # Light Theme
    css_theme_vars = """
    :root {
        --bg-main: #f8fafc;
        --bg-card: #ffffff;
        --bg-header: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        --bg-sidebar: #0f172a;
        --border-color: #e2e8f0;
        --border-hover: #3b82f6;
        --text-primary: #0f172a;
        --text-secondary: #334155;
        --text-muted: #64748b;
        --card-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        --card-shadow-hover: 0 10px 25px rgba(59, 130, 246, 0.15);
        --metric-bg: #f1f5f9;
        --action-bg: #f8fafc;
        --footer-bg: #ffffff;
    }
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

{css_theme_vars}

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    transition: background-color 0.25s ease, color 0.25s ease;
}}

[data-testid="stAppViewContainer"] > section > div {{
    padding-top: 0 !important;
}}

header[data-testid="stHeader"] {{
    background: transparent !important;
}}

.main .block-container {{
    padding: 1rem 1.5rem 2rem 1.5rem !important;
    max-width: 1400px;
}}

/* ── Sidebar Styling ── */
[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
}}
[data-testid="stSidebar"] * {{
    color: #f1f5f9 !important;
}}
[data-testid="stSidebar"] label {{
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    color: #94a3b8 !important;
}}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stSlider > div {{
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px;
}}

/* ── Header Bar ── */
.govt-header {{
    background: var(--bg-header);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.2rem 1.6rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--card-shadow);
}}
.govt-header-left {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}
.govt-header-icon {{
    font-size: 2.2rem;
    line-height: 1;
}}
.govt-header h1 {{
    color: #ffffff !important;
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.3px;
}}
.govt-header p {{
    color: #94a3b8 !important;
    font-size: 0.82rem;
    margin: 0.2rem 0 0 0;
}}
.status-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(34, 197, 94, 0.15);
    border: 1px solid rgba(34, 197, 94, 0.4);
    color: #4ade80 !important;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.status-dot {{
    width: 8px; height: 8px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 8px #22c55e;
    animation: pulse-dot 2s ease-in-out infinite;
}}
@keyframes pulse-dot {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.5; transform: scale(0.85); }}
}}

/* ── KPI Cards ── */
.kpi-row {{
    display: flex;
    gap: 0.9rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}}
.kpi-card {{
    flex: 1;
    min-width: 170px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: var(--card-shadow);
    transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
}}
.kpi-card:hover {{
    transform: translateY(-3px);
    border-color: var(--border-hover);
    box-shadow: var(--card-shadow-hover);
}}
.kpi-label {{
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--text-muted);
    margin-bottom: 0.35rem;
}}
.kpi-value {{
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
}}
.kpi-sub {{
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}}

/* ── Panels ── */
.shadcn-panel {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: var(--card-shadow);
    transition: border-color 0.2s ease;
}}
.shadcn-panel:hover {{
    border-color: var(--border-hover);
}}

/* ── Section Titles ── */
.section-title {{
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border-color);
}}

/* ── Tier Badges ── */
.tier-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.8px;
    padding: 0.35rem 0.9rem;
    border-radius: 8px;
    text-transform: uppercase;
    transition: transform 0.15s ease;
}}
.tier-badge:hover {{
    transform: scale(1.04);
}}
.tier-LOW       {{ background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.4); }}
.tier-MODERATE  {{ background: rgba(234,179,8,0.15); color: #facc15; border: 1px solid rgba(234,179,8,0.4); }}
.tier-HIGH      {{ background: rgba(249,115,22,0.15); color: #fb923c; border: 1px solid rgba(249,115,22,0.4); }}
.tier-CRITICAL  {{ background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.4); }}

/* ── Metric Mini Cards (Interactive) ── */
.metric-mini {{
    background: var(--metric-bg);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 0.75rem;
    text-align: center;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}}
.metric-mini:hover {{
    transform: translateY(-2px);
    border-color: var(--border-hover);
    box-shadow: 0 4px 12px rgba(0,0,0,0.12);
}}
.metric-mini-label {{
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--text-muted);
    margin-bottom: 0.25rem;
}}
.metric-mini-value {{
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
}}
.metric-mini-unit {{
    font-size: 0.65rem;
    color: var(--text-muted);
}}

/* ── Vulnerability Rows ── */
.vuln-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0.2rem;
    border-bottom: 1px solid var(--border-color);
    font-size: 0.82rem;
    transition: background 0.15s ease;
}}
.vuln-row:hover {{
    background: rgba(59, 130, 246, 0.05);
}}
.vuln-row:last-child {{ border-bottom: none; }}
.vuln-label {{ color: var(--text-secondary); font-weight: 500; }}
.vuln-value {{ color: var(--text-primary); font-weight: 600; }}

/* ── Action Cards ── */
.action-card {{
    background: var(--action-bg);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 0.75rem 0.95rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    font-size: 0.83rem;
    color: var(--text-primary);
    line-height: 1.45;
}}
.action-card:hover {{
    transform: translateX(4px);
    border-color: var(--border-hover);
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}}
.action-num {{
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    font-weight: 700;
    font-size: 0.72rem;
    min-width: 24px; height: 24px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 0.05rem;
}}

/* ── Map Legend ── */
.map-legend {{
    display: flex;
    gap: 1.2rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
}}
.legend-item {{
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
    transition: background 0.15s ease;
}}
.legend-item:hover {{
    background: var(--metric-bg);
}}
.legend-swatch {{
    width: 14px; height: 14px;
    border-radius: 4px;
    display: inline-block;
}}

/* ── Tier Counts ── */
.tier-count-row {{
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    margin-top: 0.6rem;
}}
.tier-count-badge {{
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.35rem 0.8rem;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    transition: transform 0.15s ease;
    cursor: pointer;
}}
.tier-count-badge:hover {{
    transform: translateY(-2px);
}}

/* ── Footer ── */
.govt-footer {{
    background: var(--footer-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-top: 1.5rem;
    font-size: 0.75rem;
    color: var(--text-muted);
    line-height: 1.6;
    box-shadow: var(--card-shadow);
}}
.govt-footer strong {{
    color: var(--text-primary);
}}

/* ── Sidebar Status Cards ── */
.sidebar-status-card {{
    border-radius: 10px;
    padding: 0.75rem 0.9rem;
    margin-bottom: 0.65rem;
    font-size: 0.78rem;
    line-height: 1.5;
}}
.status-real {{
    background: rgba(34, 197, 94, 0.1) !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
}}
.status-pending {{
    background: rgba(234, 179, 8, 0.1) !important;
    border: 1px solid rgba(234, 179, 8, 0.3) !important;
}}

.subtle-divider {{
    border: none;
    border-top: 1px solid var(--border-color);
    margin: 0.8rem 0;
}}
.ward-name-title {{
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.4rem;
}}
.priority-desc {{
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.45;
    margin-top: 0.35rem;
}}
</style>
""", unsafe_allow_html=True)


# ===============================================================
# HEADER
# ===============================================================

render_html("""
<div class="govt-header">
    <div class="govt-header-left">
        <div class="govt-header-icon">🌡️</div>
        <div>
            <h1>Ahmedabad Extreme Heatwave Early Warning System</h1>
            <p>Human Thermal Stress &amp; Heat-Health Priority Command Center</p>
        </div>
    </div>
    <div class="status-badge">
        <span class="status-dot"></span>
        System Operational
    </div>
</div>
""")


# ===============================================================
# DATA PREPARATION FOR SELECTED DATE
# ===============================================================

day_data = daily[daily["date"].dt.date == st.session_state.selected_date].copy()

if "vulnerability" in day_data.columns:
    day_data = day_data.drop(columns=["vulnerability"])

gdf_day = wards_static.merge(
    day_data,
    on=["Ward_ID", "Ward_Name"],
    how="left"
)


# ===============================================================
# TOP KPI SUMMARY ROW
# ===============================================================

TIER_COLORS = {
    "LOW": "#2ecc71",
    "MODERATE": "#f1c40f",
    "HIGH": "#e67e22",
    "CRITICAL": "#c0392b"
}

tier_order = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "CRITICAL": 3}
tier_reverse = {0: "LOW", 1: "MODERATE", 2: "HIGH", 3: "CRITICAL"}

if len(day_data) > 0 and "tier" in day_data.columns:
    highest_tier_num = day_data["tier"].map(tier_order).max()
    highest_tier = tier_reverse.get(highest_tier_num, "—")
    avg_ctbi = day_data["CTBI"].mean()
    high_crit_count = int(day_data["tier"].isin(["HIGH", "CRITICAL"]).sum())
else:
    highest_tier = "—"
    avg_ctbi = 0.0
    high_crit_count = 0

tier_badge_class = f"tier-{highest_tier}" if highest_tier in TIER_COLORS else ""

formatted_date_str = (
    st.session_state.selected_date.strftime('%d %b %Y')
    if hasattr(st.session_state.selected_date, 'strftime')
    else str(st.session_state.selected_date)
)

render_html(f"""
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-label">Selected Date</div>
        <div class="kpi-value">{formatted_date_str}</div>
        <div class="kpi-sub">6-Year Operational Dataset</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Highest Priority Alert</div>
        <div class="kpi-value"><span class="tier-badge {tier_badge_class}">{highest_tier}</span></div>
        <div class="kpi-sub">Across 48 Ahmedabad Wards</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Average CTBI Index</div>
        <div class="kpi-value">{avg_ctbi:.3f}</div>
        <div class="kpi-sub">Cumulative Thermal Burden</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">High / Critical Wards</div>
        <div class="kpi-value" style="color: {'#ef4444' if high_crit_count > 0 else 'inherit'};">{high_crit_count}</div>
        <div class="kpi-sub">Elevated Action Required</div>
    </div>
</div>
""")


# ===============================================================
# MAIN CONTENT LAYOUT (MAP + INTELLIGENCE PANEL)
# ===============================================================

col_map, col_detail = st.columns([2, 1])


# ===============================================================
# LEFT COLUMN: MAP PANEL
# ===============================================================

with col_map:

    render_html(f"""
    <div class="shadcn-panel" style="margin-bottom: 0.8rem;">
        <div class="section-title">Ward Heat-Health Priority GIS Map — {formatted_date_str}</div>
        <div class="map-legend">
            <div class="legend-item"><span class="legend-swatch" style="background:#2ecc71;"></span> Low Tier</div>
            <div class="legend-item"><span class="legend-swatch" style="background:#f1c40f;"></span> Moderate Tier</div>
            <div class="legend-item"><span class="legend-swatch" style="background:#e67e22;"></span> High Tier</div>
            <div class="legend-item"><span class="legend-swatch" style="background:#c0392b;"></span> Critical Tier</div>
        </div>
    </div>
    """)

    gdf_map = gdf_day.copy()
    if "date" in gdf_map.columns:
        gdf_map["date"] = gdf_map["date"].dt.strftime("%Y-%m-%d")

    geojson_dict = json.loads(gdf_map.to_json())

    map_style_choice = "carto-darkmatter" if st.session_state.dark_theme else "carto-positron"

    fig = px.choropleth_map(
        gdf_day,
        geojson=geojson_dict,
        locations=gdf_day.index,
        color="tier",
        hover_name="Ward_Name",
        hover_data={
            "CTBI": ":.3f",
            "NCTL": ":.2f",
            "UTCI_mean": ":.1f",
            "vulnerability": True
        },
        color_discrete_map=TIER_COLORS,
        category_orders={"tier": ["LOW", "MODERATE", "HIGH", "CRITICAL"]},
        map_style=map_style_choice,
        center={"lat": 23.02, "lon": 72.57},
        zoom=9.6,
        opacity=0.82
    )

    plotly_text_color = "#ffffff" if st.session_state.dark_theme else "#0f172a"

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=530,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=plotly_text_color),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color=plotly_text_color),
            bgcolor="rgba(0,0,0,0)"
        )
    )

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun",
        selection_mode="points",
        key="ward_map"
    )

    # Click handling
    if event and event.selection and event.selection.get("points"):
        clicked_index = event.selection["points"][0]["location"]
        clicked_ward = gdf_day.loc[int(clicked_index), "Ward_Name"]
        st.session_state.selected_ward = clicked_ward

    # Tier counts summary
    tier_counts = day_data["tier"].value_counts()
    low_c = tier_counts.get("LOW", 0)
    mod_c = tier_counts.get("MODERATE", 0)
    high_c = tier_counts.get("HIGH", 0)
    crit_c = tier_counts.get("CRITICAL", 0)

    render_html(f"""
    <div class="tier-count-row">
        <span class="tier-count-badge" style="background:rgba(34,197,94,0.15); color:#4ade80; border:1px solid rgba(34,197,94,0.35);">🟢 Low: {low_c}</span>
        <span class="tier-count-badge" style="background:rgba(234,179,8,0.15); color:#facc15; border:1px solid rgba(234,179,8,0.35);">🟡 Moderate: {mod_c}</span>
        <span class="tier-count-badge" style="background:rgba(249,115,22,0.15); color:#fb923c; border:1px solid rgba(249,115,22,0.35);">🟠 High: {high_c}</span>
        <span class="tier-count-badge" style="background:rgba(239,68,68,0.15); color:#f87171; border:1px solid rgba(239,68,68,0.35);">🔴 Critical: {crit_c}</span>
    </div>
    """)


# ===============================================================
# RIGHT COLUMN: WARD INTELLIGENCE PANEL
# ===============================================================

with col_detail:

    row = gdf_day[gdf_day["Ward_Name"] == st.session_state.selected_ward]

    if len(row) == 0 or pd.isna(row.iloc[0]["CTBI"]):
        render_html(f"""
        <div class="shadcn-panel">
            <div class="section-title">Ward Intelligence Panel</div>
            <div class="ward-name-title">{st.session_state.selected_ward}</div>
            <div style="padding: 1.2rem; background: rgba(234,179,8,0.12); border: 1px solid rgba(234,179,8,0.3); border-radius: 8px; color: #facc15; font-size: 0.85rem;">
                ⚠️ No operational weather or thermal stress data available for this ward on {formatted_date_str}.
            </div>
        </div>
        """)
    else:
        row_data = row.iloc[0]

        tier = row_data["tier"]
        tier_class = f"tier-{tier}" if tier in TIER_COLORS else ""

        vuln_val = row_data["vulnerability"]
        vuln_color = "#f87171" if vuln_val == "High" else "#4ade80"

        response_capacity = row_data.get("response_capacity", "Pending")

        drivers = row_data["drivers"]
        has_drivers = drivers != "none" and pd.notna(drivers)

        actions = str(row_data["recommended_actions"]).split(" | ")

        actions_html = ""
        for i, action in enumerate(actions, 1):
            actions_html += f'<div class="action-card"><div class="action-num">{i}</div><div>{action}</div></div>'

        drivers_html = ""
        if has_drivers:
            drivers_html = f"""
            <div class="section-title" style="margin-top:0.6rem;">Risk Drivers Identified</div>
            <div style="font-size:0.82rem; color:var(--text-secondary); background:var(--metric-bg); border-radius:8px; padding:0.6rem 0.8rem; margin-bottom:0.6rem; border:1px solid var(--border-color);">
                {drivers}
            </div>
            <hr class="subtle-divider">
            """

        render_html(f"""
        <div class="shadcn-panel">
            <div class="section-title">Ward Intelligence Panel</div>
            <div class="ward-name-title">{st.session_state.selected_ward}</div>
            <div style="margin-bottom:0.35rem;">
                <span class="tier-badge {tier_class}">{tier}</span>
            </div>
            <div class="priority-desc">{row_data["priority_v2"]}</div>

            <hr class="subtle-divider">

            <div class="section-title">Thermal Stress Metrics</div>
            <div style="display:flex; gap:0.5rem; margin-bottom:0.2rem;">
                <div class="metric-mini" style="flex:1;">
                    <div class="metric-mini-label">CTBI</div>
                    <div class="metric-mini-value">{row_data["CTBI"]:.3f}</div>
                    <div class="metric-mini-unit">Cumulative</div>
                </div>
                <div class="metric-mini" style="flex:1;">
                    <div class="metric-mini-label">NCTL</div>
                    <div class="metric-mini-value">{row_data["NCTL"]:.2f}</div>
                    <div class="metric-mini-unit">°C·hrs</div>
                </div>
                <div class="metric-mini" style="flex:1;">
                    <div class="metric-mini-label">UTCI Mean</div>
                    <div class="metric-mini-value">{row_data["UTCI_mean"]:.1f}°C</div>
                    <div class="metric-mini-unit">Daily Mean</div>
                </div>
            </div>

            <hr class="subtle-divider">

            <div class="section-title">Vulnerability Profile</div>
            <div class="vuln-row">
                <span class="vuln-label">Vulnerability Level</span>
                <span class="vuln-value" style="color:{vuln_color};">● {vuln_val}</span>
            </div>
            <div class="vuln-row">
                <span class="vuln-label">Population Density</span>
                <span class="vuln-value">{row_data["population_density"]:,.0f} / km²</span>
            </div>
            <div class="vuln-row">
                <span class="vuln-label">NDVI Green Cover</span>
                <span class="vuln-value">{row_data["ndvi_green_cover"]:.3f}</span>
            </div>
            <div class="vuln-row">
                <span class="vuln-label">Response Capacity</span>
                <span class="vuln-value" style="color:#facc15;">⏳ {response_capacity}</span>
            </div>

            <hr class="subtle-divider">

            {drivers_html}

            <div class="section-title">Recommended HAP Action Directives</div>
            {actions_html}
        </div>
        """)


# ===============================================================
# FOOTER / DATA & METHODOLOGY STATUS
# ===============================================================

render_html("""
<div class="govt-footer">
    <div style="font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: var(--text-primary); margin-bottom: 0.4rem;">
        🏛️ Data &amp; Methodology Operational Record
    </div>
    <strong>Coverage:</strong> 48 Wards · 546 Days · 2021–2026 &nbsp;│&nbsp;
    <strong>Demographics:</strong> WorldPop Population Density &nbsp;│&nbsp;
    <strong>Vegetation:</strong> Sentinel-2 NDVI &nbsp;│&nbsp;
    <strong>Thermal Stress:</strong> CTBI / NCTL / UTCI &nbsp;│&nbsp;
    <strong>Action Framework:</strong> HAP-Grounded Directives &nbsp;│&nbsp;
    <span style="color:#facc15;"><strong>Pending:</strong> Healthcare access spatial layer</span>
</div>
""")
