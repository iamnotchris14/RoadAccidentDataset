import pandas as pd
import streamlit as st
import joblib
import plotly.graph_objects as go
import math
import numpy as np
# -------------------------------
# FUNCTION: Set Background Image
# -------------------------------
def set_bg(url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .block-container {{
            background: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def add_vertical_space(lines=3):
    st.markdown("<br>" * lines, unsafe_allow_html=True)

# Role-based backgrounds
driver_bg = "https://images.wallpaperscraft.com/image/single/roads_bridge_crossroads_345975_1280x720.jpg"
gov_bg = "https://images7.alphacoders.com/742/thumb-1920-742786.jpg"
emergency_bg = "https://t4.ftcdn.net/jpg/07/07/02/79/360_F_707027965_o1Nawl8IUYvBowX2BWbJBO8lAyHtkuIa.jpg"

# ==============================Centred Title Function===============================
def center_text(text, size=30, weight="bold"):
    st.markdown(
        f"<h1 style='text-align:center; font-size:{size}px; font-weight:{weight};'>{text}</h1>",
        unsafe_allow_html=True
    )

# Load raw data (for dropdown options)
@st.cache_data
def load_dataset():
    chunks = pd.read_csv(
        "road_accident_dataset.csv",
        engine="python",
        on_bad_lines="skip",
        chunksize=50000
    )
    return pd.concat(chunks, ignore_index=True)

df = load_dataset()

# ================== ROLE HANDLING (FOLLOW HOME LOGIC) ==================
if "role" not in st.session_state:
    st.session_state["role"] = "Driver"

st.sidebar.title("User Role")
role = st.sidebar.selectbox(
    "Select your role:",
    ["Driver", "Government", "Emergency Responder"],
    index=["Driver", "Government", "Emergency Responder"].index(st.session_state["role"])
)
st.session_state["role"] = role

# -----------------------------------------------
# Load global role (from sidebar in Home.py)
# -----------------------------------------------
role = st.session_state.get("role", "Driver")

# Apply background based on role
if role == "Driver":
    set_bg(driver_bg)
elif role == "Government":
    set_bg(gov_bg)
elif role == "Emergency Responder":
    set_bg(emergency_bg)
# ==================== DRIVER ==========================
# Cached
@st.cache_resource
def load_driver_model():
    return joblib.load("Simulation/trainedModel/driver_model_compressed.pkl")
@st.cache_resource
def load_driver_encoders():
    return joblib.load("Simulation/trainedModel/driver_encoders_compressed.pkl")
@st.cache_resource
def load_driver_features():
    return joblib.load("Simulation/trainedModel/driver_features_compressed.pkl")


def driver_prediction(df):
    model = load_driver_model()
    encoders = load_driver_encoders()
    features = load_driver_features()
    # --- Page Title ---
    center_text("", size=20)
    center_text("🚦Traffic Accident Risk Dashboard", size=50)
    center_text("Accident Severity Prediction 🚗", size=30)
    center_text("By : Syahirah binti Shamsudin (0137475)", size=20)

    with st.form("driver_form", clear_on_submit=False):
        target = "Accident Severity"
        user_input = {}
        # -------------------------
        # Emoji-enhanced dropdowns
        # -------------------------
        # Weather Conditions
        weather_dict = {
            "Clear": "☀️ Clear",
            "Rainy": "🌧️ Rainy",
            "Snowy": "🌨️ Snowy",
            "Foggy": "🌫️ Foggy",
            "Windy": "💨 Windy"
        }
        user_input["Weather Conditions"] = st.selectbox(
            "Weather Conditions", list(weather_dict.values())
        )
        # Map back for encoding
        reverse_weather = {v: k for k, v in weather_dict.items()}
        user_input["Weather Conditions"] = reverse_weather[user_input["Weather Conditions"]]

        # Time of Day
        time_dict = {
            "Morning": "🌅 Morning",
            "Afternoon": "🌞 Afternoon",
            "Evening": "🌇 Evening",
            "Night": "🌙 Night"
        }
        user_input["Time of Day"] = st.selectbox("Time of Day", list(time_dict.values()))
        reverse_time = {v: k for k, v in time_dict.items()}
        user_input["Time of Day"] = reverse_time[user_input["Time of Day"]]

        # Road Type
        road_dict = {
            "Main Road": "🛣️ Main Road",
            "Highway": "🛤️ Highway",
            "Street": "🏘️ Street"
        }
        user_input["Road Type"] = st.selectbox("Road Type", list(road_dict.values()))
        reverse_road = {v: k for k, v in road_dict.items()}
        user_input["Road Type"] = reverse_road[user_input["Road Type"]]

        # Urban/Rural
        urban_dict = {
            "Urban": "🏙️ Urban",
            "Rural": "🌾 Rural"
        }
        user_input["Urban/Rural"] = st.selectbox("Urban/Rural", list(urban_dict.values()))
        reverse_urban = {v: k for k, v in urban_dict.items()}
        user_input["Urban/Rural"] = reverse_urban[user_input["Urban/Rural"]]

        # Vehicle Condition
        vehicle_dict = {
            "Good": "✅ Good",
            "Moderate": "⚠️ Moderate",
            "Poor": "❌ Poor"
        }
        user_input["Vehicle Condition"] = st.selectbox("Vehicle Condition", list(vehicle_dict.values()))
        reverse_vehicle = {v: k for k, v in vehicle_dict.items()}
        user_input["Vehicle Condition"] = reverse_vehicle[user_input["Vehicle Condition"]]

        # Driver Age Group
        age_dict = {
            "<18": "🧒 <18",
            "18-25": "👩‍🎓 18-25",
            "26-40": "👨‍💼 26-40",
            "41-60": "👴 41-60",
            "61+": "👵 61+"
        }
        user_input["Driver Age Group"] = st.selectbox("Driver Age Group", list(age_dict.values()))
        reverse_age = {v: k for k, v in age_dict.items()}
        user_input["Driver Age Group"] = reverse_age[user_input["Driver Age Group"]]

        # --- submit button ---
        submit = st.form_submit_button("Predict Accident Severity")
    
        # -------------------------
        # Predict Button
        # -------------------------
        
        if submit:
                # -------------------------
                # Conditional defaults for hidden features
                # -------------------------
                subset = df[
                    (df["Time of Day"] == user_input["Time of Day"]) &
                    (df["Road Type"] == user_input["Road Type"]) &
                    (df["Urban/Rural"] == user_input["Urban/Rural"]) &
                    (df["Weather Conditions"] == user_input["Weather Conditions"])
                ]

                # Use mean values from filtered subset
                user_input["Traffic Volume"] = subset["Traffic Volume"].mean()
                user_input["Visibility Level"] = subset["Visibility Level"].mean()

                input_df = pd.DataFrame([user_input])
                #encode categorical features
                for col in input_df.columns:
                    if col in encoders:
                        input_df[col] = encoders[col].transform(input_df[col])

                input_df = input_df[features]  # Reorder columns

                # --- probabilities (internal, not displayed) ---
                probs = model.predict_proba(input_df)[0]
                class_names = driver_encoders[target].inverse_transform(model.classes_)

                top_idx = probs.argmax()
                top_severity = class_names[top_idx]

                st.subheader(f"Predicted Accident Severity: **{top_severity}**")

                # --- map severity to mockup gauge ---
                severity_mapping = {"Minor": "Low Risk ✅", "Moderate": "Medium Risk ⚠️", "Severe": "High Risk 🚨"}
                color_mapping = {"Minor": "green", "Moderate": "yellow", "Severe": "red"}
                gauge_value = {"Minor": 25, "Moderate": 55, "Severe": 85}[top_severity]
                risk_label = severity_mapping[top_severity]
                color = color_mapping[top_severity]

                # Display gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=gauge_value,
                    number={'suffix': "%", 'font': {'size': 100}},
                    title= {'text': "<b>Accident Risk Level<b>", 
                    'font': {'size': 30, 'color': 'black'}  # increase title font size and set color
                    },
                    gauge={
                        'axis': {'range': [0, 100]},
                        'steps': [
                            {'range': [0, 33], 'color': "green"},
                            {'range': [33, 66], 'color': "yellow"},
                            {'range': [66, 100], 'color': "red"}
                        ],
                        'bar': {'color': "black"},
                        'threshold': {'line': {'color': "black", 'width': 4}, 'value': gauge_value}
                    }
                ))
                # Add the risk label as annotation
                fig.add_annotation(
                    x=0.5,              # horizontal center
                    y=0.0001,              # vertical position (adjust 0.05-0.15)
                    text=f"<b>{risk_label}</b>",
                    showarrow=False,
                    font=dict(size=27, color="black"),
                    xref="paper",
                    yref="paper"
                )
                # Move the number slightly up
                fig.update_layout(
                    margin=dict(t=50, b=50, l=50, r=50),  # optional padding
                )
                st.plotly_chart(fig, use_container_width=True)
             # -------------------------
            # Scenario-based Driver Insights
            # -------------------------
                st.markdown("### 🚗 Driver Insights & Recommendations")
                if top_severity == "Minor":
                    st.info(
                        "✅ Risk is low. You can proceed with your trip safely.\n\n"
                        "💡 Tips:\n- Stay aware of changing road and weather conditions\n- Maintain safe speed and distance\n- Track your risk trends over time to learn safer patterns"
                    )
                elif top_severity == "Moderate":
                    st.warning(
                        "⚠️ Moderate risk detected. Consider taking precautions before driving.\n\n"
                        "💡 Tips:\n- Delay the trip until conditions improve if possible\n- Use alternative, safer routes\n- Reduce speed and increase alertness"
                    )
                else:
                    st.error(
                        "🚨 High risk! Driving now is not recommended.\n\n"
                        "💡 Tips:\n- Postpone travel if possible\n- Avoid risky roads\n- Ensure your vehicle is in top condition and plan for emergencies"
                    )
                st.markdown("**🎯 Value:** Helps you make informed, safer driving decisions using real-time scenario inputs.")
                # ========================
                # Disclaimer (bottom)
                # ========================
                st.markdown(
                    """
                    <p style='font-size: 15px; color: rgba(0,0,0,0.6);'>
                    ⚠️ <strong>Disclaimer:</strong> This prediction is generated by a machine learning model and may not be 100% accurate.  
                    Please use it as a supportive insight, not a definitive assessment.
                    </p>
                    """,
                    unsafe_allow_html=True
                )





# ================= GOVERNMENT ==========================
# Cached
@st.cache_resource
def load_government_model():
    return joblib.load("Simulation/trainedModel/government_model_compressed.pkl")
@st.cache_resource
def load_government_encoders():
    return joblib.load("Simulation/trainedModel/government_encoders_compressed.pkl")
@st.cache_resource
def load_government_features():
    return joblib.load("Simulation/trainedModel/government_features_compressed.pkl")

def government_prediction(df):
    model = load_government_model()
    encoders = load_government_encoders()
    features = load_government_features()
    # --- Page Title ---
    center_text("", size=20)
    center_text("🚦Traffic Accident Risk Dashboard", size=50)
    center_text("Economic Loss Prediction💰", size=30)
    center_text("By : Syahirah binti Shamsudin (0137475)", size=20)

    with st.form("government_form", clear_on_submit=False):
        # Features expected by the model
        # -------------------------
        # Dropdowns
        # -------------------------
        user_input = {}
        # -------------------------
        # Country selection
        # -------------------------
        country_list = list(df['Country'].unique())
        selected_country = st.selectbox("Country🌍", country_list)
        user_input["Country"] = selected_country

    
        # -----------------------------------------------------------------------
        # IGNORE THIS REGION PART, CANT DELETE SINCE REGION USED IN TRAINING MODEL
        # -------------------------------------------------------------------------
        if selected_country == "Other / Not Listed":
            region_list = list(df['Region'].unique())
            selected_region = st.selectbox("Region🗺️", region_list)
            user_input["Region"] = selected_region

            # Map "Other" country to the most frequent country in the selected region
            valid_countries = df[df['Region'] == selected_region]['Country']
            mapped_country = valid_countries.mode()[0]  # most frequent country
            user_input["Country"] = mapped_country
        else:
            user_input["Country"] = selected_country
            # Set Region as the most frequent region for this country
            region_default = df[df['Country'] == selected_country]['Region'].mode()[0]
            user_input["Region"] = region_default
        # -------------------------
        # Dropdowns with emojis
        # -------------------------
        # Time of Day
        time_dict = {
            "Morning": "🌅 Morning",
            "Afternoon": "🌞 Afternoon",
            "Evening": "🌇 Evening",
            "Night": "🌙 Night"
        }
        selected_time = st.selectbox("Time of Day", list(time_dict.values()))
        user_input["Time of Day"] = {v:k for k,v in time_dict.items()}[selected_time]

        # Road Type
        road_dict = {
            "Main Road": "🛣️ Main Road",
            "Highway": "🛤️ Highway",
            "Street": "🏘️ Street"
        }
        selected_road = st.selectbox("Road Type", list(road_dict.values()))
        user_input["Road Type"] = {v:k for k,v in road_dict.items()}[selected_road]

        # Weather Conditions
        weather_dict = {
            "Clear": "☀️ Clear",
            "Rainy": "🌧️ Rainy",
            "Snowy": "🌨️ Snowy",
            "Foggy": "🌫️ Foggy",
            "Windy": "💨 Windy"
        }
        selected_weather = st.selectbox("Weather Conditions", list(weather_dict.values()))
        user_input["Weather Conditions"] = {v:k for k,v in weather_dict.items()}[selected_weather]

        # -------------------------
        # Sliders
        # -------------------------
        # Month as select slider
        months_ordered = ["January","February","March","April","May","June",
                        "July","August","September","October","November","December"]
        user_input["Month"] = st.select_slider("Month 📅", options=months_ordered, value="January")
        
        min_traffic = int(df["Traffic Volume"].min())
        max_traffic = int(df["Traffic Volume"].max())
        user_input["Traffic Volume"] = st.slider("Traffic Volume🚦(vehicles/hour)", min_value=min_traffic, max_value=max_traffic, value=(min_traffic+max_traffic)//2)

        min_pop = int(df["Population Density"].min())
        max_pop = int(df["Population Density"].max())
        user_input["Population Density"] = st.slider("Population Density🏙️(people/km²)", min_value=min_pop, max_value=max_pop, value=(min_pop+max_pop)//2)

        # -------------------------
        # Internal/default values
        # -------------------------
        internal = [
            "Number of Injuries", "Number of Fatalities", "Medical Cost",
            "Insurance Claims", "Number of Vehicles Involved",
            "Pedestrians Involved", "Cyclists Involved"
        ]
        for f in internal:
            user_input[f] = df[f].mean()

        # --- submit button ---
        submit = st.form_submit_button("Predict Economic Loss")
        # -------------------------
        # Predict button
        # -------------------------
        if submit:
            input_df = pd.DataFrame([user_input])
            for col in input_df.columns:
                if col in encoders:
                    input_df[col] = encoders[col].transform(input_df[col])
            input_df = input_df[features]
            pred = government_model.predict(input_df)[0]
            st.subheader(f"Estimated Economic Loss per Accident: **${pred:,.2f}💸**")
            # -------------------------
            # Scenario-based Government Insights
            # -------------------------
            st.markdown("### 💰 Government Insights & Recommendations")
            if pred < 5000:
                st.info("✅ Economic impact per accident is low.\n\n💡 Suggested Actions:\n- Monitor accident trends\n- Apply minor preventive measures in this region")
            elif pred < 20000:
                st.warning("⚠️ Moderate economic impact expected.\n\n💡 Suggested Actions:\n- Strengthen road safety campaigns\n- Consider targeted infrastructure improvements\n- Allocate budget for emergency services and insurance coverage adjustments")
            else:
                st.error("🚨 High economic impact predicted!\n\n💡 Suggested Actions:\n- Prioritize funding for high-risk areas\n- Invest in road maintenance, public awareness, and emergency preparedness\n- Adjust insurance and compensation policies proactively")
            st.markdown("**🎯 Value:** Turns accident data into financial impact insights, making budgeting and policy-making more strategic.")
            # ========================
            # Disclaimer (bottom)
            # ========================
            st.markdown(
            """
            <p style='font-size: 15px; color: rgba(0,0,0,0.6);'>
            ⚠️ <strong>Disclaimer:</strong> This prediction is generated by a machine learning model and may not be 100% accurate.  
            Please use it as a supportive insight, not a definitive assessment.
            </p>
            """,
            unsafe_allow_html=True
            )


# ================== RESPONDER ==========================
@st.cache_resource
def load_responder_model():
    return joblib.load("Simulation/trainedModel/responder_model_compressed.pkl")

@st.cache_resource
def load_responder_encoders():
    return joblib.load("Simulation/trainedModel/responder_encoders_compressed.pkl")

@st.cache_resource
def load_responder_features():
    return joblib.load("Simulation/trainedModel/responder_features_compressed.pkl")

def responder_prediction(df):
    model = load_responder_model()
    encoders = load_responder_encoders()
    features = load_responder_features()
    # --- Page Title ---
    center_text("", size=20)
    center_text("🚦Traffic Accident Risk Dashboard", size=50)
    center_text("Emergency Response Time Prediction 🚑", size=30)
    center_text("By : Syahirah binti Shamsudin (0137475)", size=20)
    
    user_input = {}
    # -------------------------
    # Country selection
    # -------------------------
    country_list = list(df['Country'].unique())
    country_list.append("Other / Not Listed")
    selected_country = st.selectbox("Country🌍", country_list)
    user_input["Country"] = selected_country
    # -------------------------
    # Conditional Region input
    # -------------------------
    if selected_country == "Other / Not Listed":
        region_list = list(df['Region'].unique())
        selected_region = st.selectbox("Region🗺️", region_list)
        user_input["Region"] = selected_region

        # Map "Other" country to the most frequent country in the selected region
        valid_countries = df[df['Region'] == selected_region]['Country']
        mapped_country = valid_countries.mode()[0]  # most frequent country
        user_input["Country"] = mapped_country
    else:
        user_input["Country"] = selected_country
        # Set Region as the most frequent region for this country
        region_default = df[df['Country'] == selected_country]['Region'].mode()[0]
        user_input["Region"] = region_default    
    
    with st.form("responder_form", clear_on_submit=False):
        
        # -------------------------
        # Urban/Rural selection
        # -------------------------
        urban_dict = {
            "Urban": "Urban🌆",
            "Rural": "Rural🌾"
        }
        selected = st.radio("Urban or Rural", list(urban_dict.values()))
        # Map back to the label seen by the encoder
        user_input["Urban/Rural"] = {v:k for k,v in urban_dict.items()}[selected]
        # -------------------------
        # Month and Day sliders
        # -------------------------
        months_ordered = [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ]
        user_input["Month"] = st.select_slider("Month 📅", options=months_ordered, value="January")
        
        weekdays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        user_input["Day of Week"] = st.select_slider("Day of Week 📆", options=weekdays, value="Monday")

        # Time of Day
        time_dict = {
            "Morning": "🌅 Morning",
            "Afternoon": "🌞 Afternoon",
            "Evening": "🌇 Evening",
            "Night": "🌙 Night"
        }
        selected_time = st.selectbox("Time of Day", list(time_dict.values()))
        user_input["Time of Day"] = {v:k for k,v in time_dict.items()}[selected_time]
        # -------------------------
        # Weather Conditions dropdown
        # -------------------------
        weather_dict = {
            "Clear": "☀️ Clear",
            "Rainy": "🌧️ Rainy",
            "Snowy": "❄️ Snowy",
            "Foggy": "🌫️ Foggy",
            "Windy": "💨 Windy"
        }
        selected_weather = st.selectbox("Weather Conditions", list(weather_dict.values()))
        reverse_weather = {v: k for k, v in weather_dict.items()}
        user_input["Weather Conditions"] = reverse_weather[selected_weather]

        # -------------------------
        # Road Type dropdown
        # -------------------------
        road_dict = {
            "Main Road": "🛣️ Main Road",
            "Highway": "🛤️ Highway",
            "Street": "🏘️ Street"
        }
        selected_road = st.selectbox("Road Type", list(road_dict.values()))
        reverse_road = {v: k for k, v in road_dict.items()}
        user_input["Road Type"] = reverse_road[selected_road]

        # -------------------------
        # Internal/default features (hidden)
        # -------------------------
        internal = ["Population Density", "Traffic Volume", "Road Condition"]
        for f in internal:
            if f in ["Population Density", "Traffic Volume"]:
                user_input[f] = df[f].mean()
            else:
                user_input[f] = df[f].mode()[0]

        # --- submit button ---
        submit = st.form_submit_button("Predict Emergency Response Time")
        # -------------------------
        # Predict button
        # -------------------------
        if submit:
            input_df = pd.DataFrame([user_input])
            for col in input_df.columns:
                if col in encoders:
                    input_df[col] = encoders[col].transform(input_df[col])

            pred = model.predict(input_df)[0]
            st.subheader(f"Predicted Emergency Response Time: **{pred:.2f} minutes** ⏱️")
            # -------------------------
            # Scenario-based Responder Insights
            # -------------------------
            st.markdown("### 🚑 Emergency Response Insights & Recommendations")
            if pred <= 10:
                st.info("✅ Response time is good.\n\n💡 Suggested Actions:\n- Maintain current resource allocation and readiness\n- Track trends to ensure continued performance")
            elif pred <= 20:
                st.warning("⚠️ Moderate response time.\n\n💡 Suggested Actions:\n- Adjust patrol units or station placements\n- Optimize dispatch routes\n- Prepare additional resources during peak hours")
            else:
                st.error("🚨 High response time! Immediate action needed.\n\n💡 Suggested Actions:\n- Reallocate ambulances, officers, and firefighting units\n- Improve routing and coordination\n- Enhance preparedness during adverse weather or high-incident periods")
            st.markdown("**🎯 Value:** Helps allocate resources to reduce life-saving response delays.")
            # ========================
            # Disclaimer (bottom)
            # ========================
            st.markdown(
            """
            <p style='font-size: 15px; color: rgba(0,0,0,0.6);'>
            ⚠️ <strong>Disclaimer:</strong> This prediction is generated by a machine learning model and may not be 100% accurate.  
            Please use it as a supportive insight, not a definitive assessment.
            </p>
            """,
            unsafe_allow_html=True
            )
# =======================================================
# ROUTING BY ROLE
# =======================================================
if role == "Driver":
    driver_prediction(df)
elif role == "Government":
    government_prediction(df)
elif role == "Emergency Responder":
    responder_prediction(df)
else:
    st.error(f"Unknown role: {role}")
