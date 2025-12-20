import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Squad Analysis", layout="wide")

st.title("Squad Analysis")

DATA_DIR = "Analysis/CleanedDatasets/SquadAnalysis"


df_squad = pd.read_csv(f"{DATA_DIR}/squad_value_scores.csv")
df_players = pd.read_csv(f"{DATA_DIR}/TopPlayersPerTeam.csv")
df_age = pd.read_csv(f"{DATA_DIR}/AgeProfilePerTeam.csv")
league_pos = pd.read_csv("Analysis/CleanedDatasets/Analysis/league_positions.csv")

st.header("League Trend ")

teams_trend = league_pos["Team"].unique()
selected_trend_teams = st.multiselect(
    "Select Teams for League Position Trend",
    options=list(teams_trend),
    default=list(teams_trend),
)
filtered_league_pos = (
    league_pos[league_pos["Team"].isin(selected_trend_teams)]
    if selected_trend_teams
    else league_pos
)
fig_position_trend = px.line(
    filtered_league_pos,
    x="Season",
    y="Position",
    color="Team",
    title=f"League Position Trend for Selected Teams",
    markers=True,
)
fig_position_trend.update_yaxes(autorange="reversed", title="Position (1=Top)")
st.plotly_chart(fig_position_trend, use_container_width=True)


st.header("Squad Overview")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Squad Value Score")
    fig_val = px.bar(
        df_squad,
        x="SquadValueScore",
        y="Team",
        orientation="h",
        title="Squad Value Score (Ranked)",
        color="SquadValueScore",
        color_continuous_scale="Viridis",
    )
    fig_val.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_val, use_container_width=True)

with col2:
    st.subheader("Age Range & Average")

    df_sorted_age = df_squad.sort_values(by="AvgAge_y", ascending=False)

    fig_age = go.Figure()

    for idx, row in df_sorted_age.iterrows():
        fig_age.add_trace(
            go.Scatter(
                x=[row["MinAge"], row["MaxAge"]],
                y=[row["Team"], row["Team"]],
                mode="lines",
                line=dict(color="lightgray", width=2),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    fig_age.add_trace(
        go.Scatter(
            x=df_sorted_age["MinAge"],
            y=df_sorted_age["Team"],
            mode="markers",
            name="Min Age",
            marker=dict(color="#66c2a5", size=8, symbol="line-ns-open"),
        )
    )

    fig_age.add_trace(
        go.Scatter(
            x=df_sorted_age["MaxAge"],
            y=df_sorted_age["Team"],
            mode="markers",
            name="Max Age",
            marker=dict(color="#8da0cb", size=8, symbol="line-ns-open"),
        )
    )

    fig_age.add_trace(
        go.Scatter(
            x=df_sorted_age["AvgAge_y"],
            y=df_sorted_age["Team"],
            mode="markers",
            name="Average Age",
            marker=dict(color="#fc8d62", size=12),
            text=df_sorted_age["AvgAge_y"].map(lambda x: f"{x:.1f}"),
            hovertemplate="%{x:.1f} years",
        )
    )

    fig_age.update_layout(
        title="Squad Age Range (Min - Avg - Max)",
        xaxis_title="Age (Years)",
        yaxis=dict(title=None, automargin=True),
        height=600 if len(df_sorted_age) > 10 else 400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig_age, use_container_width=True)

st.divider()

st.header("Age Profile Distribution")

df_age_melted = df_age.melt(
    id_vars=["Team"],
    value_vars=["YoungPlayers", "PrimePlayers", "ExperiencedPlayers"],
    var_name="AgeGroup",
    value_name="Count",
)

fig_stack = px.bar(
    df_age_melted,
    x="Team",
    y="Count",
    color="AgeGroup",
    title="Player Age Distribution per Team",
    color_discrete_map={
        "YoungPlayers": "#66c2a5",
        "PrimePlayers": "#fc8d62",
        "ExperiencedPlayers": "#8da0cb",
    },
)
fig_stack.update_layout(xaxis_tickangle=-90)
st.plotly_chart(fig_stack, use_container_width=True)

st.divider()

st.header("About Team")

selected_team = st.selectbox("Select Team for Details", df_squad["Team"].unique())

if selected_team:
    st.subheader(f"Top Key Players: {selected_team}")
    team_players = (
        df_players[df_players["Team"] == selected_team]
        .sort_values(by="PlayerScore", ascending=False)
        .head(5)
    )

    st.dataframe(
        team_players[
            ["Player", "Goals", "Assists", "Expected Goals (xG)", "PlayerScore"]
        ],
        hide_index=True,
        use_container_width=True,
    )

    fig_players = px.bar(
        team_players,
        x="PlayerScore",
        y="Player",
        orientation="h",
        title="Top 5 Players by Player Score",
        color="PlayerScore",
        text_auto=".1f",
    )
    fig_players.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_players, use_container_width=True)

    team_stats = df_squad[df_squad["Team"] == selected_team].iloc[0]
    st.subheader("Team Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Goals", team_stats.get("TotalGoals", 0))
    m2.metric("Total Assists", team_stats.get("TotalAssists", 0))
    m3.metric("xG", f"{team_stats.get('TotalxG', 0):.1f}")
    m4.metric("Unique Used Players", team_stats.get("UniquePlayers", 0))

with st.expander("View Raw Squad Data"):
    st.dataframe(df_squad)
