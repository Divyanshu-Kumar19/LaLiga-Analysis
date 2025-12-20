import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="LaLiga Teams Analysis", layout="wide", initial_sidebar_state="expanded"
)

st.title("LaLiga Teams Analysis Dashboard")

st.markdown(
    """
#### Project Overview
This dashboard provides a professional, data-driven analysis of LaLiga football teams from 2019 to 2026. It integrates match performance, financial metrics, and squad characteristics to deliver actionable insights for analysts, investors, and football enthusiasts.

**Key Features:**
- **Team Performance:** Explore match results, goal statistics, and advanced performance metrics.
- **Financial Analysis:** Review revenue, attendance, and financial health indicators.
- **Squad Analysis:** Assess player market values, age profiles, squad depth, and quality.
- **Predictions:** Access machine learning-based forecasts and legacy prediction tools.
- **Modelling Insights:** Compare investment and sporting models, and simulate match outcomes.
"""
)