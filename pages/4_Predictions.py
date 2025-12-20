import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Predictions", layout="wide")
st.title("Model Predictions")
st.markdown(
    "Predict a team's **Target Score** based on their performance, financial, and squad metrics using a trained Random Forest model."
)

MODEL_PATH = "Analysis/src/laliga_rf_model.pkl"
DATASETS_DIR = "Analysis/CleanedDatasets"

model_data = joblib.load(MODEL_PATH)

perf_metrics = pd.read_csv(f"{DATASETS_DIR}/Analysis/performance_metrics.csv")
xg_metrics = pd.read_csv(f"{DATASETS_DIR}/Analysis/xg_metrics.csv")
squad_scores = pd.read_csv(f"{DATASETS_DIR}/SquadAnalysis/squad_value_scores.csv")
financial_scores = pd.read_csv(f"{DATASETS_DIR}/Financial/attendance_metrics.csv")

df_data = pd.merge(perf_metrics, squad_scores, on="Team", how="left")
df_data = pd.merge(df_data, financial_scores, on="Team", how="left")
df_data = pd.merge(df_data, xg_metrics, on="Team", how="left")

model = model_data
input_features = [
    "AvgLeaguePosition",
    "GoalDifference",
    "xGDifference",
    "PointsPerGame",
    "WinRate",
    "SquadValueScore",
    "AvgAttendance",
    "AvgAge_x",
]

if isinstance(model_data, dict):
    model = model_data.get("model")
    input_features = model_data.get("features", input_features)

st.sidebar.header("Prediction Inputs")
mode = st.sidebar.radio("Mode", ["Existing Team", "Custom Team"])

if mode == "Existing Team":
    teams = df_data["Team"].unique()
    selected_team = st.sidebar.selectbox("Select Team", teams)

    team_data = df_data[df_data["Team"] == selected_team].iloc[0]

    st.subheader(f"Current Stats for {selected_team}")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg League Position", f"{team_data['AvgLeaguePosition']:.1f}")
    col2.metric("Win Rate", f"{team_data['WinRate']:.2%}")
    col3.metric("Goal Difference", f"{team_data['GoalDifference']}")
    col4.metric("Squad Value Score", f"{team_data['SquadValueScore']:.2f}")
    input_data = {feat: team_data[feat] for feat in input_features}

    prediction = model.predict(pd.DataFrame([input_data]))[0]

    st.divider()
    st.subheader("Predicted Target Score")
    st.metric("Score", f"{prediction:.2f}")
    st.info("More the score, better the overall team investment prediction.")

    st.divider()
    st.markdown(f"Adjust values to see how the score changes for **{selected_team}**.")

    col_a, col_b = st.columns(2)
    with col_a:
        new_squad_value = st.slider(
            "New Squad Value Score",
            min_value=0.0,
            max_value=float(df_data["SquadValueScore"].max()),
            value=float(input_data["SquadValueScore"]),
        )
        new_attendance = st.slider(
            "New Avg Attendance",
            min_value=0.0,
            max_value=float(df_data["AvgAttendance"].max()),
            value=float(input_data["AvgAttendance"]),
        )

    with col_b:
        new_win_rate = st.slider(
            "New Win Rate",
            min_value=0.0,
            max_value=1.0,
            value=float(input_data["WinRate"]),
        )
        new_goal_diff = st.number_input(
            "New Goal Difference", value=float(input_data["GoalDifference"])
        )

    modified_input = input_data.copy()
    modified_input.update(
        {
            "SquadValueScore": new_squad_value,
            "AvgAttendance": new_attendance,
            "WinRate": new_win_rate,
            "GoalDifference": new_goal_diff,
        }
    )

    new_pred = model.predict(pd.DataFrame([modified_input]))[0]
    st.metric(
        "New Predicted Score",
        f"{new_pred:.2f}",
        delta=f"{new_pred - prediction:.2f}",
    )

elif mode == "Custom Team":
    st.subheader("Custom Team Prediction")

    col1, col2 = st.columns(2)
    with col1:
        i_pos = st.number_input(
            "Avg League Position", min_value=1.0, max_value=20.0, value=10.0
        )
        i_gd = st.number_input("Goal Difference", value=0.0)
        i_xgd = st.number_input("xG Difference", value=0.0)
        i_ppg = st.number_input("Points Per Game", value=1.0)
    with col2:
        i_win = st.slider("Win Rate", 0.0, 1.0, 0.3)
        i_squad = st.number_input("Squad Value Score", value=50.0)
        i_att = st.number_input("Avg Attendance", value=20000.0)
        i_age = st.number_input("Avg Age", value=26.0)

    custom_input = {
        "AvgLeaguePosition": i_pos,
        "GoalDifference": i_gd,
        "xGDifference": i_xgd,
        "PointsPerGame": i_ppg,
        "WinRate": i_win,
        "SquadValueScore": i_squad,
        "AvgAttendance": i_att,
        "AvgAge_x": i_age,
    }

    if st.button("Predict"):
        pred = model.predict(pd.DataFrame([custom_input]))[0]
        st.success(f"Predicted Target Score: **{pred:.2f}**")
