#  Heat-Health Early Warning & Human Thermal Stress Index

### PS 26083 - Extreme Heatwave Early Warning and Human Thermal Stress Index

> **From predicting how hot it will be → understanding cumulative human heat burden → identifying vulnerable areas → prioritizing action.**

---

##  Overview

Extreme heat does not affect every location equally.

Traditional heatwave warnings often rely heavily on ambient temperature thresholds. However, the actual thermal stress experienced by humans also depends on factors such as humidity, wind speed, and the surrounding radiative environment.

Our project proposes a localized **Heat-Health Decision Support System** that transforms meteorological data into human-centric thermal stress information and combines cumulative heat burden with spatial vulnerability and response capacity.

The core prototype follows:

**Weather → Human Thermal Stress → Nighttime Thermal Load → Cumulative Thermal Burden → Spatial Vulnerability → Priority → Action**

The system is designed to support municipal corporations, disaster-management authorities, and public-health agencies in identifying areas where heat-health interventions should be prioritized.

---

##  Problem Statement

**Problem Statement ID:** 26083

**Title:** Extreme Heatwave Early Warning and Human Thermal Stress Index

The problem statement highlights that conventional temperature-based heatwave warnings may not adequately represent the combined effects of temperature, humidity, wind, and radiation on human health.

The proposed system aims to move from:

> **"How hot will it be?"**

towards:

> **"What will this heat do to people, where will the burden persist, and where should authorities act first?"**

---

##  Our Core Idea

Our prototype introduces a cumulative thermal-burden workflow built around three key components:

### UTCI — Human Thermal Stress

We use the **Universal Thermal Climate Index (UTCI)** to convert meteorological conditions into a human-centric thermal stress metric.

UTCI incorporates:

* Air temperature
* Relative humidity
* Wind speed
* Mean Radiant Temperature (MRT)

### NCTL — Nighttime Cumulative Thermal Load

We quantify persistent nighttime thermal load by measuring nighttime UTCI above a local historical baseline.

Conceptually:

```text
NCTL(t) =
Σ max(0, UTCI_night(h) − UTCI_baseline) × Δt
```

NCTL captures both:

**Magnitude + Duration**

of elevated nighttime thermal stress.

We use NCTL as a **proxy for reduced recovery opportunity**, rather than claiming it is a clinically validated physiological recovery index.

### CTBI — Cumulative Thermal Burden Index

We accumulate daytime thermal stress and nighttime thermal load over multiple days.

```text
CTBI(t) =
α × CTBI(t−1)
+
β × DayStress_norm(t)
+
γ × NCTL_norm(t)
```

Here, α, β, and γ are prototype parameters.

They are **not treated as scientifically validated physiological constants**. Sensitivity testing is used to examine whether qualitative patterns remain stable across reasonable parameter ranges.

---

##  System Architecture

```text
                 HISTORICAL WEATHER
                       │
                    ERA5 / CDS
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
 Temperature       Dewpoint          Wind U/V
       │               │                │
       └───────────────┴────────────────┘
                       +
                  Radiation
                       │
                       ↓
              RH + Wind Speed + MRT
                       │
                       ↓
                     UTCI
                       │
              ┌────────┴────────┐
              ↓                 ↓
       DAYTIME STRESS      NIGHTTIME UTCI
              │                 │
              │             Baseline
              │                 │
              │                NCTL
              │                 │
              └────────┬────────┘
                       ↓
                     CTBI
                       │
                       ↓
              SPATIAL ENRICHMENT
                       │
              ┌────────┼─────────┐
              ↓        ↓         ↓
            WARD   VULNERABILITY  RESPONSE
            DATA      DATA       CAPACITY
              └────────┼─────────┘
                       ↓
                PROTOTYPE PRIORITY
                       │
                Low / Moderate /
                  High / Critical
                       │
                       ↓
                ACTION ENGINE
                       │
                       ↓
               GIS DASHBOARD
                  (Streamlit)
```

---

##  Methodology

### 1. Historical Weather Data

The prototype uses **ERA5 reanalysis data** accessed through the **Copernicus Climate Data Store (CDS)**.

Relevant meteorological variables include:

* 2m air temperature
* 2m dewpoint temperature
* 10m U/V wind components
* Relevant radiation variables

The hourly data enables both daytime and nighttime thermal-load analysis.

---

### 2. Data Preprocessing

Raw ERA5 data is cleaned and transformed.

```text
Temperature:
Kelvin → °C

Wind:
Wind Speed = √(u10² + v10²)

Dewpoint + Temperature:
→ Relative Humidity

Radiation Variables:
→ Mean Radiant Temperature estimate
```

The processed dataset becomes the input for human thermal stress calculations.

---

### 3. UTCI Calculation

The **Universal Thermal Climate Index (UTCI)** is calculated using an established thermal-comfort implementation such as `pythermalcomfort`.

Conceptually:

```text
Air Temperature
       +
Relative Humidity
       +
Wind Speed
       +
Mean Radiant Temperature
       ↓
      UTCI
```

UTCI provides a human-centric representation of thermal stress instead of relying only on air temperature.

---

### 4. Daytime Thermal Stress

Hourly UTCI values are separated into daytime and nighttime periods.

Daytime UTCI is used to derive a daytime thermal-stress measure:

```text
Hourly UTCI
     ↓
Daytime Window
     ↓
DayStress
     ↓
Normalization
```

---

### 5. Nighttime Cumulative Thermal Load

Nighttime UTCI is compared against a local historical baseline.

For the prototype, the baseline can be derived using a reproducible historical percentile-based method such as the **90th percentile of nighttime UTCI**, provided the available historical period supports that interpretation.

```text
Nighttime UTCI
      ↓
Historical Baseline
      ↓
Excess Thermal Load
      ↓
Duration × Magnitude
      ↓
NCTL
```

NCTL is expressed in degree-hours.

---

### 6. Cumulative Thermal Burden

Daytime stress and nighttime thermal load are combined over time.

```text
Previous CTBI
     +
Daytime Stress
     +
Nighttime Thermal Load
     ↓
    CTBI
```

This allows repeated heat exposure to be represented rather than treating every hot day as an isolated event.

---

##  Spatial Enrichment

ERA5 meteorological grids are spatially coarser than individual administrative wards.

Therefore, the prototype spatially enriches the thermal indicators.

```text
ERA5 Grid
    ↓
Spatial Assignment
    ↓
Ward / Zone / Grid
    ↓
CTBI + NCTL + UTCI
```

If official ward boundaries are available, the prototype operates at ward level.

If ward-level data is unavailable, the architecture supports:

**Ward → Zone → Regular Spatial Grid**

The system does not represent a spatial grid as a ward.

---

##  Vulnerability

The same thermal exposure can produce different levels of risk in different populations.

Potential vulnerability indicators include:

* Elderly population
* Population density
* Outdoor-worker presence
* Informal settlements
* Other reliable locally available demographic indicators

Only features supported by reliable data are included in the prototype.

---

##  Response Capacity

Thermal exposure alone does not determine intervention priority.

The prototype also considers the ability of an area to respond to heat stress.

Potential indicators include:

* Healthcare accessibility
* Cooling infrastructure
* Healthcare resources
* Green infrastructure
* Other locally available response-capacity indicators

These indicators are initially kept separate rather than being combined using arbitrary multipliers.

---

##  Prototype Priority Engine

The current one-week prototype does **not** claim to predict mortality percentages without real health outcome labels.

Instead, it uses a transparent prototype decision framework.

```text
Thermal Burden
      +
Vulnerability
      +
Response Capacity
      ↓
Priority
      ↓
Low / Moderate / High / Critical
```

For example:

```text
High CTBI
+
High Vulnerability
+
Low Response Capacity
        ↓
     CRITICAL
```

The exact thresholds are documented and designed to remain transparent.

---

##  Action Recommendation Engine

The system translates priority into potential intervention categories.

Examples include:

```text
High thermal burden
+
High elderly vulnerability
        ↓
Vulnerable population checks
+
Cooling access prioritization
```

```text
High thermal burden
+
High outdoor-worker exposure
        ↓
Reduce / shift strenuous outdoor activity
during peak heat periods
```

```text
High thermal burden
+
Low response capacity
        ↓
Prioritize cooling and emergency resources
```

Recommendations are intended as **decision-support guidance** and should be aligned with official heat-health guidance.

---

##  GIS Dashboard

The prototype dashboard is built using **Streamlit**.

The dashboard provides:

### Map View

```text
🟢 Low
🟡 Moderate
🟠 High
🔴 Critical
```

### Area Detail View

A selected area can display:

```text
UTCI
NCTL
CTBI

Vulnerability
Response Capacity

Priority Level

Recommended Action
```

The dashboard is intended to demonstrate how thermal-burden information can be converted into spatially actionable insights.

---

##  Future AI/ML Extension

Real health-impact prediction requires reliable historical health outcome data.

Once sufficient hospitalization/mortality data becomes available, the system can be extended to:

```text
UTCI
NCTL
CTBI
Vulnerability
Weather Features
Historical Health Outcomes
          ↓
      XGBoost
          ↓
Health-Impact Probability
          ↓
         SHAP
          ↓
Explainable Risk
```

### SHAP

SHAP can explain which features contributed most strongly to an individual prediction.

Example:

```text
High Risk

Major contributing factors:
↑ NCTL
↑ CTBI
↑ Humidity
↑ Elderly population
↓ Healthcare access
```

These outputs will only be presented as SHAP explanations after an actual trained model produces them.

---

##  Future 3–5 Day Forecasting

The current prototype primarily demonstrates the historical thermal-burden pipeline.

A production system can integrate operational forecast sources such as:

**IMD / NCMRWF**

The future architecture becomes:

```text
3–5 Day Weather Forecast
          ↓
         UTCI
          ↓
         NCTL
          ↓
         CTBI
          ↓
Health-Impact Model
          ↓
Risk Probability
          ↓
Priority
          ↓
Action
```

Forecast uncertainty can additionally be estimated using forecast-error statistics, ensemble information, and model uncertainty.

---

##  Future Alert Layer

The production architecture can connect high-priority results to:

* SMS
* WhatsApp
* Email
* Authority notification systems
* Heat Action Plan triggers

These integrations are considered future extensions rather than core requirements of the current prototype.

---

## 🟢🟡🔵 Project Maturity

### 🟢 DEMONSTRATED

Real data and implemented calculations:

```text
ERA5
 ↓
Data Processing
 ↓
UTCI
 ↓
DayStress
 ↓
NCTL
 ↓
CTBI
 ↓
Real Graphs
```

###  PROTOTYPE

Decision-support components:

```text
Thermal Indicators
+
Vulnerability
+
Response Capacity
 ↓
Priority
 ↓
Action Recommendations
 ↓
GIS Dashboard
```

###  FUTURE / PRODUCTION

Components requiring additional real-world data/infrastructure:

```text
IMD / NCMRWF Forecast
+
Historical Hospitalization / Mortality Data
 ↓
XGBoost
 ↓
Health-Impact Probability
 ↓
SHAP
 ↓
Uncertainty
 ↓
3–5 Day Early Warning
 ↓
Automated Alerts
```

---

##  Technology Stack

### Data & Scientific Computing

* Python
* Pandas
* NumPy
* xarray
* NetCDF
* cdsapi

### Thermal Comfort

* pythermalcomfort

### GIS / Spatial Processing

* GeoPandas
* GeoJSON / Shapefile
* Folium / Plotly

### Dashboard

* Streamlit

### Machine Learning — Future

* Scikit-learn
* XGBoost
* SHAP

### Development

* VS Code
* Git
* GitHub
* Google Colab for experimentation when required

---

##  Suggested Repository Structure

```text
heat-health-early-warning/
│
├── README.md
│
├── data/
│   ├── sample/
│   └── processed/
│
├── src/
│   ├── data_processing.py
│   ├── utci.py
│   ├── nctl.py
│   ├── ctbi.py
│   ├── spatial.py
│   └── priority.py
│
├── dashboard/
│   └── app.py
│
├── notebooks/
│   ├── era5_exploration.ipynb
│   ├── utci_analysis.ipynb
│   └── ctbi_analysis.ipynb
│
├── outputs/
│   ├── graphs/
│   ├── maps/
│   └── screenshots/
│
├── docs/
│   ├── decision_log.md
│   └── methodology.md
│
└── requirements.txt
```

---

##  Development Workflow

The project is developed using parallel workstreams with controlled handoffs.

```text
Dev
ERA5 → UTCI → NCTL → CTBI
          ↓
        Shweta
   Validation + Graphs
          ↓
        Leader
      PPT / Proof


Garima
Ward / Spatial Data
          ↓
       Vrinda
    GIS Dashboard


Khushi
Risk + Priority + Actions
          ↓
       Vrinda
    Action Dashboard


Everyone
    ↓
Leader
    ↓
Final Integration
    ↓
PPT + GitHub + Screenshots + Demo
```

Team members develop locally in VS Code/Colab and push stable outputs to GitHub.

---

##  Validation Strategy

The current prototype focuses on validating the computational pipeline and logical behavior.

### Thermal Pipeline

Check:

* Temperature/unit conversions
* Wind calculations
* Relative humidity
* MRT inputs
* UTCI outputs

### NCTL

Check:

* Nighttime window
* Historical baseline
* Magnitude × duration behavior

### CTBI

Sensitivity testing:

```text
α = 0.6
α = 0.7
α = 0.8
```

The goal is to check whether qualitative patterns remain stable.

### Future Health Model

Once real health outcomes are available:

* AUROC
* Precision
* Recall
* F1
* Calibration
* Backtesting against historical heat events

will be considered.

---

##  Limitations

The current prototype does not claim:

* Clinically validated mortality prediction
* A scientifically validated CTBI parameter set
* Clinically validated NCTL recovery measurement
* Ward-level weather directly from ERA5
* Real SHAP explanations without a trained model
* Fabricated mortality percentages
* Fabricated confidence intervals
* Production-grade automated SMS/WhatsApp alerts

These limitations are intentionally documented to maintain scientific and technical credibility.

---

##  What Is Novel About This Approach?

We are **not** claiming to have invented UTCI, nighttime heat stress, or heatwave alerts.

The proposed contribution is the operational combination of:

```text
Human Thermal Stress
        +
Persistent Nighttime Thermal Load
        +
Multi-Day Cumulative Burden
        +
Spatial Vulnerability
        +
Response Capacity
        ↓
Heat-Health Priority
        ↓
Action
```

The goal is to move from:

> **Predicting heat**

to:

> **Understanding cumulative human heat burden and deciding where intervention should happen first.**

---

##  Current Prototype Goal

The immediate objective is to demonstrate a working proof-of-concept using real historical weather data.

### By Day 3

```text
Real ERA5
   ↓
UTCI
   ↓
NCTL
   ↓
CTBI
   ↓
Real Graphs
```

### By Day 4

```text
CTBI
 ↓
Spatial Areas
 ↓
Vulnerability
 ↓
Priority
 ↓
Dashboard
```

### By Day 5

```text
Working Prototype
+
Real Proof-of-Work
+
GitHub
+
Screenshots
+
PPT
+
Demo Story
```

---

##  One-Sentence Pitch

> **We transform real weather data into human thermal stress, quantify persistent nighttime and multi-day heat burden, identify vulnerable and low-response areas, and translate those insights into actionable heat-health priorities.**

---

##  Team

**Dev** — AI/ML & Thermal Science Pipeline
**Khushi** — AI/ML Support, Risk & Action Logic
**Shweta** — Data Analysis, Validation & Visualization
**Garima** — GIS & Spatial Data
**Vrinda** — Full-Stack & Streamlit Dashboard
**Leader** — Integration, Research, Planning, Documentation & Technical Coordination

---

##  Disclaimer

This project is a prototype developed for the **PS 26083 — Extreme Heatwave Early Warning and Human Thermal Stress Index** problem statement.

The current prototype is intended for research, demonstration, and decision-support purposes. It does not replace official meteorological forecasts, medical advice, or government heat-health protocols.

---

##  Future Vision

```text
ONE CITY
   ↓
MULTIPLE CITIES
   ↓
WARD-LEVEL HEAT-HEALTH INTELLIGENCE
   ↓
3–5 DAY FORECASTING
   ↓
HEALTH-IMPACT PREDICTION
   ↓
EXPLAINABLE AI
   ↓
AUTOMATED EARLY WARNING
   ↓
NATIONAL HEAT-HEALTH DECISION SUPPORT SYSTEM
```
