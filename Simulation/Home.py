import streamlit as st

# --- Global Role Selector (Sidebar) ---
st.sidebar.title("User Role")
role = st.sidebar.selectbox(
    "Select your role:",
    ["Driver", "Government", "Police/Hospital", "Researcher"]
)

# --- Page Title ---
st.title("🚦 Traffic Accident Dashboard - Home")
st.write(f"Welcome, **{role}** 👋")

# --- Intro content (lightly tailored) ---
if role == "Driver":
    st.info("This dashboard helps you understand accident risk on your routes and time of travel.")
elif role == "Government":
    st.info("Visualize accident hotspots and long-term safety patterns to support policy decisions.")
elif role == "Police/Hospital":
    st.info("Monitor high-risk hours and zones to optimize patrols and emergency response.")
elif role == "Researcher":
    st.info("Explore traffic datasets, trends, and model performance for deeper insights.")

st.write("Use the sidebar to navigate to other pages: Analysis or Prediction.")
