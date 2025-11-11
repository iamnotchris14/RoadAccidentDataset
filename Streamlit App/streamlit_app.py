import streamlit as st
import pandas as pd
import plotly.express as px


df = pd.read_csv("road_accident_dataset.csv")  

# Convert Accident Severity to numeric
sev_map = {"Minor": 0, "Moderate": 1, "Severe": 2}
df["Severity_Num"] = df["Accident Severity"].map(sev_map)

# Sidebar menu
page = st.sidebar.selectbox("Select Page", ["Introduction", "Analysis", "Prediction"])

# ================= Introduction Page =================
if page == "Introduction":
    st.title("Accident Severity Dashboard")
    st.write("""
        Welcome to the Accident Severity Dashboard!  
        Here, you can explore accident data, analyze patterns by country, and even predict severity.
    """)

# ================= Analysis Page =================
elif page == "Analysis":
    st.title("Geographic Heatmap of Accident Severity by Country")

    # Calculate average severity per country
    country_avg = (
        df.groupby("Country")["Severity_Num"]
        .mean()
        .reset_index()
        .rename(columns={"Severity_Num": "Avg_Severity"})
    )

    # Create choropleth
    fig = px.choropleth(
        country_avg,
        locations="Country",
        locationmode="country names",
        color="Avg_Severity",
        color_continuous_scale=["#00B050", "#FFD700", "#C00000"],  
        title="Average Accident Severity by Country",
        projection="natural earth",
    )
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True),
        coloraxis_colorbar=dict(title="Avg Severity<br>(0=Minor, 2=Severe)")
    )

    st.plotly_chart(fig, use_container_width=True)

# ================= Prediction Page =================
elif page == "Prediction":
    st.title("Accident Severity Prediction")
    st.write("Here you can add a model input form to predict accident severity.")
    
    country_input = st.text_input("Country")
    weather_input = st.selectbox("Weather Conditions", df["Weather Conditions"].unique())
    severity_btn = st.button("Predict Severity")

    if severity_btn:
        st.write("Prediction logic goes here!")  # Replace with your model prediction
