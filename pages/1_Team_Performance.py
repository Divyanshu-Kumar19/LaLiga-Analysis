import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(page_title="Team Performance", layout="wide")

st.title("Team Performance Analysis")

df_perf = pd.read_csv("Analysis/CleanedDatasets/Analysis/performance_metrics.csv")
df_xg = pd.read_csv("Analysis/CleanedDatasets/Analysis/xg_metrics.csv")

st.subheader("Key Performance Metrics")
teams = df_perf["Team"].unique()
selected_teams = st.sidebar.multiselect("Select Teams", teams, default=teams[:5])

if selected_teams:
    df_filtered = df_perf[df_perf["Team"].isin(selected_teams)]
else:
    df_filtered = df_perf

st.markdown("### Top 10 Teams by Total Points")
top_10_points = df_filtered.sort_values(by="TotalPoints", ascending=False).head(10)
fig_points = px.bar(
    top_10_points, 
    x="TotalPoints", 
    y="Team", 
    orientation='h',
    title="Top 10 Teams by Total Points",
    color="TotalPoints",
    color_continuous_scale="Viridis",
    text="TotalPoints"
)
fig_points.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_points, use_container_width=True)

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Win Rate vs Loss Rate")
    fig_win_loss = px.scatter(
        df_filtered, 
        x="WinRate", 
        y="LossRate", 
        text="Team", 
        size="TotalMatches",
        color="Team",
        title="Win Rate vs Loss Rate"
    )
    st.plotly_chart(fig_win_loss, use_container_width=True)

with col2:
    st.markdown("### Goals Breakdown")
    fig_goals = px.bar(
        df_filtered, 
        x="Team", 
        y=["TotalGoalsFor", "TotalGoalsAgainst"], 
        barmode="group",
        title="Goals For vs Goals Against"
    )
    fig_goals.update_layout(xaxis_tickangle=-90)
    st.plotly_chart(fig_goals, use_container_width=True)

st.markdown("### Expected Goals (xG) Analysis")
xg_filtered = df_xg[df_xg["Team"].isin(selected_teams)] if selected_teams else df_xg

fig_xg = px.bar(
    xg_filtered,
    x="Team",
    y=["AvgxG", "AvgxGA"],
    barmode="group",
    title="Average xG vs xAG (Expected Goals vs Assisted Goals)"
)
fig_xg.update_layout(xaxis_tickangle=-90)
st.plotly_chart(fig_xg, use_container_width=True)

st.markdown("### Detailed Metrics Table")
st.dataframe(df_filtered)
