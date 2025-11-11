import streamlit as st

st.sidebar.title("User Role")

OPTIONS = ["Driver", "Government", "Police/Hospital", "Researcher"]

# 1) Set a default ONCE, before drawing the widget
if "role" not in st.session_state:
    st.session_state.role = "Driver"

# 2) Draw the widget; DO NOT assign to session_state afterwards
role = st.sidebar.selectbox(
    "Select your role:",
    OPTIONS,
    index=OPTIONS.index(st.session_state.role),
    key="role",
)

# Use `role` or `st.session_state.role` below; don't write to it.
import random

# --- Page setup ---
st.set_page_config(page_title="Prediction", layout="wide")

# --- Global role selector ---
if "role" not in st.session_state:
    st.session_state["role"] = st.sidebar.selectbox(
        "Select your role:",
        ["Driver", "Government", "Police/Hospital", "Researcher"]
    )
role = st.session_state["role"]

st.title("🤖 Accident Risk Prediction")
st.caption(f"Customized prediction view for: **{role}**")

# Utility: simple simulation of probability (no real model)
def simulate_probability(base=0.4):
    return round(min(0.95, max(0.05, base + random.uniform(-0.1, 0.3))), 2)

# =========================================================
# DRIVER VIEW
# =========================================================
if role == "Driver":
    st.subheader("🚗 Driver Risk Estimation")

    time_of_day = st.slider("Select time of travel (24-hour)", 0, 23, 22)
    road_type = st.selectbox("Road type", ["Highway", "Urban", "Rural"])
    weather = st.selectbox("Weather condition", ["Clear", "Rainy", "Foggy"])
    alcohol_bac = st.slider("Your alcohol level (BAC %)", 0.0, 0.3, 0.0, step=0.01)

    if st.button("Predict my risk"):
        base = 0.25
        if 20 <= time_of_day or time_of_day <= 4: base += 0.2
        if weather != "Clear": base += 0.2
        if road_type == "Highway": base += 0.15
        base += alcohol_bac * 2
        prob = simulate_probability(base)

        st.metric("Predicted accident risk", f"{int(prob*100)}%")
        if prob > 0.7:
            st.warning("⚠️ High risk: Avoid driving late or in bad weather.")
        elif prob > 0.4:
            st.info("Moderate risk: Stay alert and maintain safe distance.")
        else:
            st.success("Low risk: Drive safe and stay focused!")

# =========================================================
# GOVERNMENT VIEW
# =========================================================
elif role == "Government":
    st.subheader("🏛️ Road Safety Planning Simulation")

    region = st.selectbox("Region", ["Klang", "Petaling", "Gombak", "Hulu Langat"])
    lighting = st.select_slider("Lighting quality (1=Poor, 5=Excellent)", [1,2,3,4,5], 3)
    avg_speed = st.slider("Average vehicle speed (km/h)", 30, 120, 80)
    budget = st.slider("Budget allocated (RM, thousands)", 100, 2000, 500, step=50)

    if st.button("Simulate hotspot risk"):
        base = 0.3 + (5 - lighting)*0.1 + (avg_speed - 70)/200
        prob = simulate_probability(base)
        reduction = round(budget/4000, 2)

        st.metric("Hotspot Risk Index", f"{int(prob*100)}%")
        st.metric("Potential Reduction with Current Budget", f"{int(reduction*100)}%")
        st.info("🛠 Recommendation: Improve lighting and enforce lower speed limits.")

# =========================================================
# POLICE / HOSPITAL VIEW
# =========================================================
elif role == "Police/Hospital":
    st.subheader("🚓 Emergency Incident Forecast")

    shift = st.selectbox("Shift", ["Day (6–14)", "Evening (14–22)", "Night (22–6)"])
    rain_forecast = st.checkbox("Rain expected during shift")
    events = st.checkbox("Nearby event / festival ongoing")

    if st.button("Simulate incident forecast"):
        base_calls = {"Day (6–14)": 15, "Evening (14–22)": 22, "Night (22–6)": 28}[shift]
        if rain_forecast: base_calls += 5
        if events: base_calls += 4
        prob = simulate_probability(base_calls/50)

        st.metric("Predicted incidents this shift", int(base_calls))
        st.metric("Severity probability", f"{int(prob*100)}%")
        st.warning("Prepare extra units for high-severity night incidents.")

# =========================================================
# RESEARCHER VIEW
# =========================================================
elif role == "Researcher":
    st.subheader("🎓 Research Simulation Panel")

    model_type = st.selectbox("Model type", ["Logistic Regression", "Random Forest", "XGBoost"])
    threshold = st.slider("Decision threshold", 0.1, 0.9, 0.5)
    features = st.multiselect("Selected features", 
        ["time_of_day", "weather", "road_type", "alcohol_bac", "speed", "visibility"],
        default=["time_of_day", "weather", "road_type"]
    )

    if st.button("Simulate model metrics"):
        base_auc = {"Logistic Regression": 0.82, "Random Forest": 0.87, "XGBoost": 0.90}[model_type]
        adj = random.uniform(-0.02, 0.03)
        auc = round(base_auc + adj, 2)
        precision = round(0.75 + random.uniform(-0.1, 0.1), 2)
        recall = round(0.72 + random.uniform(-0.1, 0.1), 2)

        st.metric("AUC", auc)
        st.metric("Precision", precision)
        st.metric("Recall", recall)
        st.info("🔍 Simulation only — replace with actual metrics later.")

# =========================================================
st.divider()
st.caption("All results shown are simulated for demonstration purposes only.")
