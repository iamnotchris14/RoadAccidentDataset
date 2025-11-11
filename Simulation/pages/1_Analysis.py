import streamlit as st

st.sidebar.title("User Role")
role = st.sidebar.selectbox(
    "Select your role:",
    ["Driver", "Government", "Police/Hospital", "Researcher"]
)

st.title("📈 Accident Analysis")

if role == "Driver":
    st.write("Here’s an overview of risky times and locations for daily commuters.")
elif role == "Government":
    st.write("These charts highlight areas needing better road safety measures.")
elif role == "Police/Hospital":
    st.write("Analyze when and where most accidents occur to plan better resource allocation.")
elif role == "Researcher":
    st.write("Explore datasets for correlation and regression analysis.")

# Example shared visualization
st.bar_chart({"Morning": [20], "Afternoon": [35], "Night": [50]})
