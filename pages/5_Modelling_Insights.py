import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import pickle
from sklearn.metrics import r2_score

st.set_page_config(page_title="Modelling Insights", layout="wide")
st.title("Future Predictions")

BASE_PATH = "Analysis/CleanedDatasets"
MODEL_PATH = "Analysis/src/laliga_rf_model.pkl"
SPORTING_MODEL_PATH = "Analysis/src/sporting_rf_model.pkl"

perf = pd.read_csv(f"{BASE_PATH}/Analysis/performance_metrics.csv")
squad = pd.read_csv(f"{BASE_PATH}/SquadAnalysis/squad_value_scores.csv")
fin = pd.read_csv(f"{BASE_PATH}/Financial/financial_scores.csv")
xg = pd.read_csv(f"{BASE_PATH}/Analysis/xg_metrics.csv")

df = perf.merge(
    squad[
        [ "Team","SquadValueScore","AvgAge_x","TotalPlayers","YoungPlayers","PrimePlayers","ExperiencedPlayers",]
    ],
    on="Team",
    how="left",
)
df = df.merge(fin[["Team", "AvgAttendance", "FinancialScore"]], on="Team", how="left")
df = df.merge(xg[["Team", "AvgxG", "xGDifference"]], on="Team", how="left")

investment_model_data = joblib.load(MODEL_PATH)
with open(SPORTING_MODEL_PATH, "rb") as f:
    sporting_model_data = pickle.load(f)
tab1, tab2 = st.tabs(["Investment Analysis", "Sporting Performance & Predictions"])
with tab1:
    st.header("Investment Recommendation Engine")
    st.markdown(
        """
        > **Strategic Business Insight**: This model evaluates teams based on a composite **Investment Score**, 
        > blending on-field performance (Win Rate, Points) with financial potential (Revenue, Attendance, Squad Value).
        """
    )

    model = investment_model_data["model"]
    model_features = investment_model_data["features"]

    X_invest = df[model_features].copy()
    df["InvestmentScore"] = model.predict(X_invest)

    investment_rankings = df.sort_values(
        "InvestmentScore", ascending=False
    ).reset_index(drop=True)
    investment_rankings["Rank"] = investment_rankings.index + 1

    top_pick = investment_rankings.iloc[0]
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Top Investment Recommendation",
        top_pick["Team"],
        f"Score: {top_pick['InvestmentScore']:.1f}",
    )
    col2.metric(
        "Median League Investment Score",
        f"{investment_rankings['InvestmentScore'].median():.1f}",
    )
    col3.metric(
        "Model Confidence (R²)", f"{investment_model_data['metrics']['test_r2']:.3f}"
    )

    st.subheader("Top 10 Investment Opportunities")

    def get_color(rank):
        if rank <= 3:
            return "Strong Buy"
        if rank <= 7:
            return "Moderate Buy"
        return "High Risk / Hold"

    investment_rankings["Recommendation"] = investment_rankings["Rank"].apply(get_color)

    fig_invest = px.bar(
        investment_rankings.head(10),
        x="InvestmentScore",
        y="Team",
        orientation="h",
        color="Recommendation",
        color_discrete_map={
            "Strong Buy": "#00CC96",
            "Moderate Buy": "#636EFA",
            "High Risk / Hold": "#EF553B",
        },
        text_auto=".1f",
        title="Investment Scores (Top 10)",
    )
    st.plotly_chart(fig_invest, use_container_width=True)

    st.subheader("Basis of Investment ?")
    fi_data = pd.DataFrame(investment_model_data["feature_importance"])
    fi_data = fi_data.sort_values("Importance", ascending=True)
    fig_fi = px.bar(
        fi_data,
        x="Importance",
        y="Feature",
        orientation="h",
        title="Investment Model: Feature Importance",
    )
    st.plotly_chart(fig_fi, use_container_width=True)


with tab2:
    st.header("Sporting Performance Predictor")
    st.markdown(
        """
        > **Pure Sporting Focus**: This model predicts **Win Probability** based *strictly* on on-field metrics. 
        """
    )

    sporting_model = sporting_model_data["model"]
    sporting_features = sporting_model_data["features"]

    X_sport = df[sporting_features].fillna(0)
    y_sport = df["WinRate"] if "WinRate" in df.columns else None

    df["Sportingstrength"] = sporting_model.predict(X_sport)

    sport_r2 = (
        r2_score(y_sport, df["Sportingstrength"]) if y_sport is not None else None
    )

    col1, col2 = st.columns(2)
    col1.metric("Sporting Model Accuracy (R²)", f"{sport_r2:.3f}")

    fi_sport = pd.DataFrame(
        {
            "Feature": sporting_features,
            "Importance": sporting_model.feature_importances_,
        }
    ).sort_values("Importance", ascending=True)

    fig_sport_fi = px.bar(
        fi_sport,
        x="Importance",
        y="Feature",
        orientation="h",
        title="Sporting Model: Feature Importance",
    )
    col2.plotly_chart(fig_sport_fi, use_container_width=True)

    st.divider()
    st.subheader("Next Match Prediction")
    st.write(
        "Select two teams to predict the match outcome based on their calculated Sporting Strength."
    )

    col_home, col_away = st.columns(2)
    home_team = col_home.selectbox(
        "Select Your Team (Home)", df["Team"].unique(), index=0
    )
    away_team = col_away.selectbox(
        "Select Opponent (Away)", df["Team"].unique(), index=1
    )

    if home_team != away_team:
        home_strength = df.loc[df["Team"] == home_team, "Sportingstrength"].values[0]
        away_strength = df.loc[df["Team"] == away_team, "Sportingstrength"].values[0]
        # Log5 Probability
        denom = home_strength * (1 - away_strength) + away_strength * (
            1 - home_strength
        )
        win_prob_home = (
            (home_strength * (1 - away_strength)) / denom if denom != 0 else 0.5
        )

        st.write("### Predicted Outcome")
        prob_data = pd.DataFrame(
            {
                "Result": [f"{home_team} Win", f"{away_team} Win"],
                "Probability": [win_prob_home, 1 - win_prob_home],
            }
        )

        fig_match = px.pie(
            prob_data,
            names="Result",
            values="Probability",
            color="Result",
            color_discrete_map={
                f"{home_team} Win": "#636EFA",
                f"{away_team} Win": "#EF553B",
            },
            hole=0.4,
        )
        st.plotly_chart(fig_match, use_container_width=True)

        st.write("#### Head-to-Head Stats Comparison")
        h2h_data = (
            df[df["Team"].isin([home_team, away_team])].set_index("Team").transpose()
        )
        st.dataframe(
            h2h_data.loc[sporting_features + ["WinRate"]], use_container_width=True
        )
    else:
        st.warning("Please select different teams.")
