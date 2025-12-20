import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Financial Analysis", layout="wide")

st.title("Financial Analysis")

FILE_PATH = "Analysis/CleanedDatasets/Financial/financial_scores.csv"

def load_data():
    return pd.read_csv(FILE_PATH)

df = load_data()

st.subheader("Financial Metrics & Scores")

teams = df["Team"].unique()
selected_teams = st.sidebar.multiselect("Select Teams", teams, default=teams[:5])

if selected_teams:
    df_filtered = df[df["Team"].isin(selected_teams)]
else:
    df_filtered = df

col1, col2 = st.columns(2)

with col1:
    fig_avg_att = px.bar(
        df_filtered, 
        x="Team", 
        y="AvgAttendance", 
        title="Average Attendance by Team",
        color="AvgAttendance",
        color_continuous_scale="Blues"
    )
    fig_avg_att.update_layout(xaxis_tickangle=-90)
    st.plotly_chart(fig_avg_att, use_container_width=True)
        
with col2:
    fig_rev = px.bar(
        df_filtered, 
        x="Team", 
        y="EstimatedMatchdayRevenue", 
        title="Estimated Matchday Revenue (€)",
        color="EstimatedMatchdayRevenue",
        color_continuous_scale="Greens"
    )
    fig_rev.update_layout(xaxis_tickangle=-90)
    st.plotly_chart(fig_rev, use_container_width=True)

st.markdown("### Financial Data")
st.dataframe(df_filtered)
