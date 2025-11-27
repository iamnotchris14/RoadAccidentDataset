import streamlit as st
import pandas as pd
import base64

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

        /* Make text readable */
        .block-container {{
            background: rgba(255, 255, 255, 0.8);
            padding: 2rem;
            border-radius: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
driver_bg = "https://images.wallpaperscraft.com/image/single/roads_bridge_crossroads_345975_1280x720.jpg"
gov_bg = "https://images7.alphacoders.com/742/thumb-1920-742786.jpg"
emergency_bg = "https://t4.ftcdn.net/jpg/07/07/02/79/360_F_707027965_o1Nawl8IUYvBowX2BWbJBO8lAyHtkuIa.jpg"

# ==============================Centred Title Function===============================
def center_text(text, size=30, weight="bold"):
    st.markdown(
        f"<h1 style='text-align:center; font-size:{size}px; font-weight:{weight};'>{text}</h1>",
        unsafe_allow_html=True
    )

# --- Remember selected role in session_state ---
if "role" not in st.session_state:
    st.session_state["role"] = "Driver"   # default role

# (Optional) keep a sidebar label, but use session_state
st.sidebar.title("User Role")
# Sidebar role selector
role = st.sidebar.selectbox(
    "Select your role:",
    ["Driver", "Government", "Emergency Responder"]
)
st.session_state["role"] = role

# Use this everywhere below
role = st.session_state["role"]

# --- Page Title ---
center_text("", size=20)
center_text("🚦Traffic Accident Risk Dashboard", size=50)
center_text("Home", size=30)
st.write(f"Welcome, **{role}** 👋")

# --- Intro content (lightly tailored) ---
if role == "Driver":
    set_bg(driver_bg)
    st.info("This dashboard helps you understand accident risk on your routes and time of travel.")
elif role == "Government":
    st.info("Visualize accident hotspots and long-term safety patterns to support policy decisions.")
elif role == "Emergency Responder":
    st.info("Monitor high-risk hours and zones to optimize patrols and emergency response.")

st.write("Use the sidebar to navigate to other pages: Analysis or Prediction.")

# ====================================================Load Dataset=============================================================
df = pd.read_csv("road_accident_dataset.csv")


# Driver variables
driver_peak_time = df["Time of Day"].value_counts().idxmax()
driver_risky_weather = df["Weather Conditions"].value_counts().idxmax()
driver_common_age_group = df["Driver Age Group"].value_counts().idxmax()

# Government variables
gov_top_region = df["Region"].value_counts().idxmax()
gov_common_road_type = df["Road Type"].value_counts().idxmax()
gov_area_type = df["Urban/Rural"].value_counts().idxmax()

# Police/Hospital variables
resp_peak_time = df["Time of Day"].value_counts().idxmax()
severity_counts = df["Accident Severity"].value_counts(normalize=True)
severe_share = float(severity_counts.get("Severe", 0))
resp_severity_pattern = f"{severe_share * 100:.1f}% severe crashes"
resp_fatal_hotspot = df.groupby("Region")["Number of Fatalities"].sum().idxmax()


#========================================================driver page=============================================================
if role == "Driver":
    
    st.image("images/omw.gif", caption="Your POV on the road", width="stretch")
    # 📊 Interactive chart area
    st.markdown("#### What our dataset shows?")
    st.markdown(
        "Use the selector below to explore how accident counts change by **time of day**, "
        "**weather**, and **driver age group**."
    )

    driver_dim_label = st.selectbox(
        "Explore accidents by:",
        ["Time of Day", "Weather Conditions", "Driver Age Group"],
        key="driver_dim"
    )

    driver_chart_data = (
        df[driver_dim_label].value_counts().reset_index()
    )
    driver_chart_data.columns = [driver_dim_label, "Accident Count"]
    driver_chart_data = driver_chart_data.sort_values("Accident Count", ascending=False)

    st.bar_chart(driver_chart_data.set_index(driver_dim_label)["Accident Count"])

    # expander (balanced)
    with st.expander("Here's why our dataset looks balanced"):
        st.markdown(
            """
            **This dataset has been intentionally balanced across weather, time of day, and driver age groups.**

            For drivers, this matters because:
            - You can explore accident patterns **without one factor dominating** the charts  
            - Clear weather, bad weather, day, night — all show up fairly  
            - You can understand how *each* condition affects risk independently  

            Real accident data is usually skewed (e.g., more night crashes, more young drivers).  
            But this balanced dataset is meant to help us **learn the patterns**, not overwhelm us with noisy real data.

            👉 Our dataset is balanced so you can clearly see how different conditions affect risk — without the data being skewed by one dominant factor.*
            """
        )
    #expander (insights)
    with st.expander("What's found in the dataset"):
    
        # Metrics section
        st.markdown("### 📊 Key Insights")
        col1, col2, col3 = st.columns(3)
        col1.metric("Peak accident time", driver_peak_time)
        col2.metric("Most common weather", driver_risky_weather)
        col3.metric("Top age group in crashes", driver_common_age_group)

    # Explanation section
        st.markdown("---")
        st.markdown("### 🧩 What this means for Drivers")
        st.markdown(
            f"Even when the road looks normal, **{driver_peak_time}** tends to have more crashes because "
            "drivers are tired, rushing, or less focused. Additionally, those times are when many people "
            "go out drinking, and careless individuals may choose to drink and drive — which significantly "
            "increases the danger on the road.\n\n"
            f"Combined with conditions like **{driver_risky_weather}**, even small mistakes like hard braking, "
            "misjudging distance, or glancing at your phone can become serious very quickly.\n\n"
            "If you recognise yourself in the patterns shown above, it's a signal to be extra cautious on the road."
    )

    #educational purposes
    st.markdown("### 🎓 Learn: Understand Your Risk Better")

    st.info(
        "Even though this dataset is balanced, it still shows how different conditions "
        "— time of day, weather, and age group — relate to accident patterns. "
        "Use this section to test your intuition and learn how small choices change your risk."
    )

    st.markdown("#### ❓ Quick Quiz for Drivers")
    driver_quiz = st.radio(
        "Based on the dataset, which time of day has the highest accident count?",
        ["Morning", "Afternoon", "Evening", "Night"],
        key="driver_quiz"
    )

    if st.button("Check my answer", key="driver_quiz_button"):
        if driver_quiz == driver_peak_time:
            st.success(
                f"✅ Correct! In this dataset, **{driver_peak_time}** has the most recorded accidents.\n\n"
                "This often overlaps with commuting times or late-day fatigue, when drivers are more tired or distracted."
            )
        else:
            st.warning(
                f"⚠️ Not quite. In this dataset, **{driver_peak_time}** actually has the highest accident count.\n\n"
                "This is a good reminder that the times we *feel* most relaxed on the road may still carry more risk."
            )

    st.markdown("#### 💡 Practical Tip")
    st.markdown(
        f"- Treat **{driver_peak_time}** as a **high-alert window**, even if the weather seems fine, as some drivers tend to speed in main roads. \n"
        f"- In conditions like **{driver_risky_weather}**, add extra following distance and reduce your speed slightly. For example, dont tailgate and be too close to the car in front of you.\n"
        "- If your age group appears often in the chart above, use that as a signal to be extra intentional about safe driving habits."
    )

    st.markdown("---")
    st.image("images/friends-hug.gif", use_container_width=True)
    st.markdown(
    "**❤️ Why this matters:**\n"
    "Every decision you make on the road—whether to accelerate, check your phone, or push through fatigue—"
    "can influence not just your safety, but the lives of passengers, pedestrians, and other drivers. "
    "Seeing the patterns in this data helps you recognise moments when you may unknowingly be at higher risk. "
    "Understanding these risks empowers you to adjust your driving habits, stay alert during peak danger periods, "
    "and protect yourself and the people waiting for you at home."
)


#--------------------------------------------------------------------government page----------------------------------------------------------------------
elif role == "Government":
    set_bg(gov_bg)
    st.image("images/government.gif", use_container_width=True)
    st.markdown("#### What our dataset shows?")
    st.markdown(
        "Use the selector below to see how crashes are distributed by **region**, **road type**, "
        "or **urban vs rural areas**."
    )

    gov_dim_label = st.selectbox(
        "Explore crashes by:",
        ["Region", "Road Type", "Urban/Rural"],
        key="gov_dim"
    )

    gov_chart_data = (
        df[gov_dim_label].value_counts().reset_index()
    )
    gov_chart_data.columns = [gov_dim_label, "Accident Count"]
    gov_chart_data = gov_chart_data.sort_values("Accident Count", ascending=False)

    st.bar_chart(gov_chart_data.set_index(gov_dim_label)["Accident Count"])

    #expander (balanced)
    with st.expander("Here's why our dataset looks balanced"):
        st.markdown(
            """
            **This dataset has been intentionally balanced across regions, road types, and area types (urban/rural).**

            For policymakers, this is important because:
            - It allows **unbiased comparisons** across different regions  
            - It avoids one large state/region from dominating the statistics  
            - You can evaluate infrastructure or policy conditions fairly  
            - It helps isolate *relationships* instead of raw volume dominance  

            Real government crash datasets are heavily skewed. For example, big cities dominate the chart.  
            Here, the balance creates a **neutral analytics sandbox** for exploring policy ideas.

            👉 Overall, this dataset is balanced to ensure fair, unbiased comparisons across regions and conditions, making it easier for us to evaluate potential policy interventions.
            """
        )

    # expander (insights)
    with st.expander("What's found in the dataset"):

        st.markdown("### 📊 Key Insights")
        col1, col2, col3 = st.columns(3)
        col1.metric("Fatality hotspot region", resp_fatal_hotspot)
        col2.metric("Most common road type", gov_common_road_type)
        col3.metric("Dominant area type", gov_area_type)

    # Explanation below the graph
        st.markdown("---")
        st.markdown("#### 🧩 What this means for planning")
        st.markdown(
            f"The chart above shows where crashes cluster in the dataset — whether by **{gov_dim_label}**, "
            f"road type, or area type. Regions like **{resp_fatal_hotspot}** with repeated fatalities "
            f"are strong candidates for targeted interventions."
    )
    
    #educational
    st.markdown("### 🎓 Learn: Turning Data into Policy Insight")

    st.info(
        "This dataset is balanced so that regions, road types, and area types all appear clearly. "
        "That makes it easier to see **where** risk concentrates and think about which policies "
        "or infrastructure changes could make the biggest difference."
    )

    st.markdown("#### ❓ Quick Quiz for Policymakers")
    gov_quiz = st.radio(
        "In this dataset, which region has the highest total number of fatalities?",
        df['Region'].unique().tolist(),
        key="gov_quiz"
    )

    if st.button("Check my answer", key="gov_quiz_button"):
        if gov_quiz == resp_fatal_hotspot:
            st.success(
                f"✅ Correct! **{resp_fatal_hotspot}** has the highest total fatalities in this dataset.\n\n"
                "In a real setting, this kind of region would be a prime candidate for targeted safety interventions."
            )
        else:
            st.warning(
                f"⚠️ Not quite. In this dataset, **{resp_fatal_hotspot}** has the highest total fatalities.\n\n"
                "Balanced data like this lets you see such patterns clearly and ask: "
                "\"What combination of design, enforcement, and education is needed there?\""
            )

    st.markdown("#### 💡 Policy Reflection")
    st.markdown(
        f"- If a region like **{resp_fatal_hotspot}** repeatedly appears as a high-fatality area, it may justify:\n"
        "  - Junction redesign or traffic-calming measures\n"
        "  - Improved lighting, signage, or speed management\n"
        "  - Targeted enforcement or public education campaigns\n\n"
        "- Comparing **road types** in the chart above can reveal whether highways, main roads, or streets "
        "contribute most to serious outcomes.\n"
        "- Balanced data ensures these comparisons are **fair**, not dominated by just one large or busy region."
    )

    st.markdown("---")

    st.markdown(    
    "**❤️ Why this matters:**\n"
    "Every crash has economic, social, and human consequences. A single high-risk road segment can silently accumulate "
    "millions in medical costs, lost productivity, and emergency response burdens. More importantly, it represents "
    "lives disrupted or lost. By identifying where risk concentrates—whether by region, road type, or urban design—you "
    "can prioritize interventions that create the greatest positive impact. Data-driven planning ensures that every "
    "budget decision, road redesign, or safety policy translates into a safer, more resilient transport system for "
    "entire communities."
)

#--------------------------------------------------------------------------emergency responder page-------------------------------------------------------------------
elif role == "Emergency Responder":
    
    set_bg(emergency_bg)

    st.image("images/ambulance.gif", use_container_width=True)
    st.markdown("#### What our dataset shows?")
    st.markdown(
        "Use the selector below to explore how incidents vary by **time of day**, **severity**, or **region**."
    )

    resp_dim_label = st.selectbox(
        "Explore incidents by:",
        ["Time of Day", "Accident Severity", "Region"],
        key="resp_dim"
    )

    resp_chart_data = (
        df[resp_dim_label].value_counts().reset_index()
    )
    resp_chart_data.columns = [resp_dim_label, "Accident Count"]
    resp_chart_data = resp_chart_data.sort_values("Accident Count", ascending=False)

    st.bar_chart(resp_chart_data.set_index(resp_dim_label)["Accident Count"])

    # expander (balanced)
    with st.expander("📘 Here's why our dataset looks balanced"):
        st.markdown(
            """
            **This dataset has been intentionally balanced across time, severity, and regions.**

            For police and medical teams, this helps because:
            - It reveals patterns **without volume bias**  
            - Every region appears equally, so no hotspot hides others  
            - Severity levels are evenly shown, helping practice triage logic  
            - Time-of-day comparisons become easier to interpret  

            In real crash data, certain hours, days, and regions dominate incident counts.  
            A balanced dataset allows responders to **train pattern recognition** without skew.

            👉 In summary, our dataset is balanced so every risk factor is visible. It aids in helping responders train, analyse patterns, and plan resources without natural data imbalance hiding important trends.
            """
        )

    #expander (insights)
    with st.expander("What's found in the dataset"):
        st.markdown("### 📊 Key Insights")
        col1, col2, col3 = st.columns(3)
        col1.metric("Peak incident time", resp_peak_time)
        col2.metric("Severity share", resp_severity_pattern)
        col3.metric("Fatality hotspot", resp_fatal_hotspot)

    # Explanation below
        st.markdown("#### 🧩 What this means for operations")
        st.markdown(
            f"The chart above shows how incidents cluster in terms of **{resp_dim_label}**. "
            f"Patterns around **{resp_peak_time}** and regions like **{resp_fatal_hotspot}** can guide smarter deployment."
    )

    #educational
    st.markdown("### 🎓 Learn: Improving Readiness and Response")

    st.info(
        "For emergency services, patterns in time, location, and severity are crucial. "
        "This balanced dataset helps highlight those patterns without one busy region or hour hiding the others."
    )

    st.markdown("#### ❓ Quick Quiz for Responders")
    resp_quiz = st.radio(
        "According to this dataset, when do accidents most commonly happen?",
        ["Morning", "Afternoon", "Evening", "Night"],
        key="resp_quiz"
    )

    if st.button("Check my answer", key="resp_quiz_button"):
        if resp_quiz == resp_peak_time:
            st.success(
                f"✅ Correct! **{resp_peak_time}** is the peak accident time in this dataset.\n\n"
                "In real operations, this kind of information can guide shift planning, vehicle staging, "
                "and hospital preparedness."
            )
        else:
            st.warning(
                f"⚠️ Not quite. In this dataset, **{resp_peak_time}** has the highest number of accidents.\n\n"
                "Knowing these peaks helps emergency teams anticipate demand instead of only reacting to it."
            )

    st.markdown("#### 💡 Operational Insight")
    st.markdown(
        f"- If **{resp_peak_time}** is a high-demand period, consider:\n"
        "  - Increasing patrol visibility or ambulance coverage during that window\n"
        "  - Ensuring key hospitals are prepared for a possible surge of trauma cases\n"
        f"- Regions like **{resp_fatal_hotspot}** with more fatalities may benefit from:\n"
        "  - Closer ambulance staging points\n"
        "  - Faster routing protocols\n"
        "  - Coordination drills between police, EMS, and hospitals\n\n"
        "Balanced data lets you practice reading these patterns and imagining how deployment could adapt."
    )

    st.markdown("---")
    
    st.markdown(    
    "**❤️ Why this matters:**\n"
    "For first responders, minutes and even seconds can determine whether an accident results in recovery or tragedy. "
    "Understanding when and where incidents spike allows emergency teams to position resources more strategically, "
    "reduce response times, and improve survival outcomes. Balanced data like this helps reveal patterns without the "
    "noise of real-world bias, enabling better shift planning, patrol routing, and hospital readiness. Ultimately, "
    "smarter preparation means more lives saved and less pressure on emergency systems."
)