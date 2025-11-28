import streamlit as st
import pandas as pd
import base64
import altair as alt

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

# --- Intro content (lightly tailored) ---
if role == "Driver":
    set_bg(driver_bg)
    st.info("**Welcome, Driver!  \nYou’re on the road every day.**  \n This dashboard highlights when and where risk increases, helping you stay alert during moments when drivers are most vulnerable. Use these insights to protect yourself and everyone sharing the road with you.")
elif role == "Government":
    st.info("**Welcome, Government!  \nYou shape the roads people depend on.**  \n This dashboard shows where risks concentrate across regions and road types. Use the patterns here to guide smarter policies, infrastructure upgrades, and safer city planning.")
elif role == "Emergency Responder":
    st.info("**Welcome, Emergency Responders!  \nYou’re the first to respond when something goes wrong.**  \n This dashboard reveals when and where incidents peak so you can strengthen deployment, reduce response times, and improve survival outcomes when every minute matters.")

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
    
    def load_gif(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    gif_data = load_gif("images/omw.gif")

    st.markdown(
        f"""
        <div style="text-align:center;">
            <img src="data:image/gif;base64,{gif_data}" width="500">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
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

    #  different colors for each bar
    chart = alt.Chart(driver_chart_data).mark_bar().encode(
    x=alt.X(driver_dim_label, sort=None),
    y='Accident Count',
        color=alt.Color(
        driver_dim_label,
        scale=alt.Scale(scheme="oranges"),   # <--- single-hue orange palette
        legend=None
    )
    ).properties(
    width=600,
    height=400
    )

    st.altair_chart(chart, use_container_width=True)

    # expander (balanced)
    with st.expander("Here's why our dataset looks balanced"):
        st.markdown(
            """
            1. You can explore accident patterns **without one factor dominating** the charts  
            2. Clear weather, bad weather, day, night — all show up fairly  
            3. You can understand how *each* condition affects risk independently  

            Real accident data is usually skewed (e.g., more night crashes, more young drivers).  
            But this balanced dataset is meant to help us **learn the patterns**, not overwhelm us with noisy real data.

            👉 Our dataset is balanced so you can clearly see how different conditions affect risk without the data being skewed by one dominant factor.*
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

    #expander(educational purposes)
    with st.expander("🎓 Learning: Understand Your Risk Better"):

        st.info(
        "Even though this dataset is balanced, it still shows how different conditions "
        "like time of day, weather, and age group. These relate to accident patterns. "
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


    st.markdown("---")
    st.markdown("#### News Report for Awareness")
    st.markdown("""
    Between **1913 and 2023**, the number of motor-vehicle deaths in the United States  
    (which include passenger cars, trucks, buses, and motorcycles) **increased by 966%** —  
    from **4,200 deaths** in 1913 to **44,762 deaths** in 2023.

    However, the role of cars in daily life has changed drastically:

    - In **1913**, there were only **1.3 million vehicles** and **2 million drivers**.  
    Miles driven annually was not yet estimated.
    - In **2023**, the U.S. recorded:
    - **284.6 million vehicles**
    - **238 million licensed drivers**
    - **3,247 billion miles** driven annually

    Despite the increase in total fatalities, **exposure levels** (vehicles, drivers, miles driven) have changed so dramatically that the **risk per mile, per driver, and per vehicle has dropped significantly** over time.
    """)

    st.image("images/deathandpop.JPG", use_container_width=False)
    st.image("images/deathMVrates.JPG", use_container_width=False)

    st.markdown("""
    By all measures, motor-vehicle safety has vastly improved since the early 1900s. Driver attitudes and behaviors have changed substantially, as has vehicle safety technology, which makes car travel safer.

    The population motor-vehicle death rate reached its peak in **1937** with **30.8 deaths per 100,000 population**.  
    The current rate is **13.4 per 100,000**, representing a **56% improvement**.

    In **1913**, **33.38 people** died for every **10,000 vehicles** on the road.  
    In **2023**, the death rate was **1.57 per 10,000 vehicles** — a **95% improvement**.

    In **1923**, the first year miles driven was estimated, the motor-vehicle death rate was **18.65 deaths per 100 million miles driven**.  
    Since 1923, the mileage death rate has decreased **93%** and now stands at **1.38 deaths per 100 million miles driven**.
    """)
    st.markdown("""
    <style>
    /* Make expander background white */
    .streamlit-expanderHeader, .streamlit-expanderContent {
        background-color: white !important;
        color: black !important;
        border-radius: 8px;
        padding: 10px;
    }

    /* Optional: remove grey shadows */
    details {
        background-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    with st.expander("Death Rates from 2019-2023"):
        st.markdown(
    """
    Despite these historic drops, we cannot remain complacent.

    ### Changes from 2019 to 2023:
    - **Vehicle death rate:** Increased by **11.3%**
    - **Mileage death rate:** Increased by **15.0%**
    - **Population death rate:** Increased by **12.6%**
    """
    )
    st.markdown("""
    **Source:**  
    Deaths are from the *National Center for Health Statistics (NCHS)*, except 1964, which are *National Safety Council (NSC)* estimates based on data from the *National Highway Traffic Safety Administration’s (NHTSA) Fatality Analysis Reporting System (FARS)*.  

    See Technical Appendix for comparability. Motor-vehicle registrations, mileage, and drivers are estimated by the *Federal Highway Administration*.

    [Read more here](https://injuryfacts.nsc.org/motor-vehicle/historical-fatality-trends/deaths-and-rates/)
    """)


    st.markdown("---")
    st.markdown("#### 💡 Key Takeaways")
    st.markdown(
        f"- Treat **{driver_peak_time}** as a **high-alert window**, even if the weather seems fine, as some drivers tend to speed in main roads. \n"
        f"- In conditions like **{driver_risky_weather}**, add extra following distance and reduce your speed slightly. For example, dont tailgate and be too close to the car in front of you.\n"
        "- If your age group appears often in the chart above, use that as a signal to be extra intentional about safe driving habits."
    )
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

    def load_gif(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    gif_data = load_gif("images/government.gif")

    st.markdown(
        f"""
        <div style="text-align:center;">
            <img src="data:image/gif;base64,{gif_data}" width="500">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
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

    # Altair bar chart with orange gradient shades
    chart = alt.Chart(gov_chart_data).mark_bar().encode(
        x=alt.X(gov_dim_label, sort=None),
        y="Accident Count",
        color=alt.Color(
            gov_dim_label,
            scale=alt.Scale(scheme="oranges"),   # same orange gradient
            legend=None
        )
    ).properties(
        width=600,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)

    #expander (balanced)
    with st.expander("Here's why our dataset looks balanced"):
        st.markdown(
            """
            1. It allows **unbiased comparisons** across different regions  
            2. It avoids one large state/region from dominating the statistics  
            3. You can evaluate infrastructure or policy conditions fairly  
            4. It helps isolate *relationships* instead of raw volume dominance  

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
    
    #expander(educational)
    with st.expander("🎓 Learning: Turning Data into Policy Insight"):

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



    st.markdown("---")
    st.markdown("#### News Report for Awareness")
    st.markdown("""
    **Asia Pacific Road Safety Conference (9–11 September 2025, Manila)**  
    The conference was held at the Asian Development Bank Headquarters in Manila, Philippines.  
    It was jointly organized by the **Asian Development Bank (ADB)**, **Global Road Safety Partnership (GRSP)**, **Asia-Pacific Road Safety Observatory (APRSO)**, **Bridgestone Asia Pacific**, and the **International Road Assessment Programme (iRAP)**.
    """)

    st.image("images/governmentnews.jpg", use_container_width=False)

    st.markdown("""
    Attended by 260+ participants from more than 20 countries, the Asia Pacific Road Safety Conference brought together representatives from government, international organizations, the private sector, academia, and civil society. The 3-day event explored how investing in road safety can support sustainable transport, public health, and economic development.
    """)
    with st.expander("Highligts from the Event"):
        st.markdown(
        """
    **Featured:**
    1. A **high-level ministerial roundtable**
    2. **Panel discussions**
    3. **Workshops**
    4. **Networking sessions** for road safety practitioners

    **84 speakers** from organizations such as:
    1. Asian Development Bank (ADB)
    2. FIA Foundation
    3. United Nations ESCAP
    4. iRAP
    5. World Health Organization (WHO)
    6. Bridgestone
    7. GRSP
        """
    )

    with st.expander("Main Themes Discussed"):
        st.markdown("""
        1. Increasing **road safety investments** and securing financial commitments.
        2. Strengthening understanding of **funding models** aligned with youth, climate, health, and economic priorities.
        3. Encouraging collaboration across **road safety**, **finance**, and **health** sectors.
        4. Building **capacity** in developing member countries to prepare stronger business cases for road safety funding.
        5. Addressing key priority issues:
            - **Powered two-wheeler safety**
            - **Vulnerable road users**
        6. Exploring multi-sector partnerships with **APRSO** to support long-term, sustainable road safety action.
        """)

    st.markdown("""
    <style>
    /* Make expander background white */
    .streamlit-expanderHeader, .streamlit-expanderContent {
        background-color: white !important;
        color: black !important;
        border-radius: 8px;
        padding: 10px;
    }

    /* Optional: remove grey shadows */
    details {
        background-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    **Source:** https://www.grsproadsafety.org/asia-pacific-road-safety-conference-2025-in-manila-philippines/
    
    See the Event Social Media Video [here](https://www.youtube.com/watch?v=zOwBmzbDmlA)
    """)
    st.markdown("---")
    st.markdown("#### 💡 Key Takeaways for Government")
    st.markdown(
        f"- Regions like **{resp_fatal_hotspot}** with repeated high fatality counts should be treated as "
        "priority zones for safety improvements, including:\n"
        "  - Junction redesign or traffic-calming infrastructure\n"
        "  - Better lighting, clearer signage, and stricter speed control\n"
        "  - Focused law enforcement and behaviour-change campaigns\n\n"
        "- Reviewing **road type patterns** helps identify where the most severe outcomes occur — whether on "
        "highways, main roads, or smaller streets — guiding where to direct limited budget and manpower.\n\n"
    )
    with st.expander("What You (Goverment) Should Do Next"):
        st.markdown("Use these patterns to prioritise one high-risk region and one "
        "high-severity road type for targeted upgrades or enforcement planning."
    )

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

    def load_gif(path):
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    gif_data = load_gif("images/ambulance.gif")

    st.markdown(
        f"""
        <div style="text-align:center;">
            <img src="data:image/gif;base64,{gif_data}" width="500">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")
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

    # Altair bar chart with orange gradient shades
    chart = alt.Chart(resp_chart_data).mark_bar().encode(
        x=alt.X(resp_dim_label, sort=None),
        y="Accident Count",
        color=alt.Color(
            resp_dim_label,
            scale=alt.Scale(scheme="oranges"),   # unified color family
            legend=None
        )
    ).properties(
        width=600,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)

    # expander (balanced)
    with st.expander("Here's why our dataset looks balanced"):
        st.markdown(
            """
            1. It reveals patterns **without volume bias**  
            2. Every region appears equally, so no hotspot hides others  
            3. Severity levels are evenly shown, helping practice triage logic  
            4. Time-of-day comparisons become easier to interpret  

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

    #expander(educational)
    with st.expander("🎓 Learning: Improving Readiness and Response"):
    
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


    st.markdown("---")
    st.markdown("#### News Report for Awareness")
    st.markdown("""
    Emergency medical services (EMS) have several responsibilities at the crash site, whether involving an automobile, aircraft, boat, or other types of vehicles. The key responsibilities of EMS covered in this resource include scene safety evaluation, triage coordination, prehospital medical treatment, and crash site investigation.
    """)

    st.image("images/crashsites.jpg", use_container_width=False)

    with st.expander("Issues of Concern"):
        st.markdown("""
##  **EMS Responsibilities at a Crash Site**

### **1. Scene Safety Evaluation**
- Begins **before** EMS arrives by assessing whether it is safe to proceed.
- Crash sites can become unsafe quickly → **continuous monitoring** required.
- Common hazards include:
  - Wreckage, hazardous materials, fire, fumes
  - Environmental hazards (urban, marine, mountain, desert, winter, night)
- Proper **protective gear** is essential; selection depends on crash scale and environment.
- Large crash areas (e.g., aircraft crashes) may require:
  - Radios, fire suppression tools, machinery, casualty transport equipment
- EMS also protects:
  - Firefighters, police, bystanders, and media personnel


### **2. Triage**
- Most crash sites are **mass casualty incidents**.
- Purpose: quickly prioritize patients to avoid overwhelming resources.
- Common issue: transporting **uninjured** first → leaves critical victims untreated.
- No universal triage system, but **consistency within an incident is essential**.
- Triage categories may be based on:
  - Glasgow Coma Scale, vital signs, visible injuries
- Categories must be **clearly marked** (colors, letters, numbers).
- EMS leaders designate **collection points** for easier transport.
- Patients must be **continuously monitored** as conditions may worsen.
- Without training or a unified system:
  - Response becomes chaotic
  - Critically injured patients face delays


### **3. Prehospital Medical Treatment**
- Begins at first contact → continues until arrival at the medical facility.
- Life-threatening injuries treated **first** (ATLS protocol).
- Aircraft crash injury patterns:
  - Most common: **lower extremity fractures**
  - Also: head injuries, open wounds, organ damage, burns
- Rotary aircraft crashes often cause **spinal injuries** → consider **c-spine immobilization**.
- Trauma victims may have multiple injuries → requires:
  - Thorough assessment  
  - Stabilization for transport  
  - Correct prioritization based on triage


### **4. Crash Site Investigation**
- Investigations vary by type of crash.
- In aircraft crashes:
  - Investigators assess events leading up to and immediately after the crash.
  - EMS responders may provide eyewitness accounts.
- Deceased victims are generally **left in place** unless minimal movement is required.
- Investigators document:
  - Passenger locations
  - Debris movement
  - Injury patterns
- Findings help improve:
  - Safety procedures  
  - Materials  
  - Training  
  - Crash prevention strategies  

""")


    st.markdown("""
    <style>
    /* Make expander background white */
    .streamlit-expanderHeader, .streamlit-expanderContent {
        background-color: white !important;
        color: black !important;
        border-radius: 8px;
        padding: 10px;
    }

    /* Optional: remove grey shadows */
    details {
        background-color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    **Emergency Medical Services (EMS)** has several key responsibilities at a crash site. These include triage, patient care, and preparing victims for transport.  
    When performed effectively, EMS response can **maximize lives saved** and **reduce injury severity (morbidity)**.
    """)

    st.markdown("""
    **Source:** https://www.ncbi.nlm.nih.gov/books/NBK537069/
    """)
    
    st.markdown("---")
    st.markdown("#### 💡 Key Takeaways for EMS")
    st.markdown(
        f"- The peak incident time, **{resp_peak_time}**, represents a predictable surge in service demand. "
        "Shift planning, patrol timing, and ambulance staging should be aligned with this pattern to reduce "
        "response delays.\n"
        f"- Regions like **{resp_fatal_hotspot}** with high fatality counts may require closer ambulance "
        "posts, dedicated trauma-capable routing, and stronger police visibility.\n"
        f"- The share of severe crashes (**{resp_severity_pattern}**) highlights the importance of trauma "
        "readiness, rapid transport, and coordinated communication between police, EMS, and hospitals.\n\n"
    )
    with st.expander("What You (EMS) Should Do Next"):
        st.markdown("Review deployment plans for peak-risk hours, strengthen coordination "
        "protocols in high-fatality regions, and ensure that hospital and EMS teams are prepared for a potential "
        "surge during the time windows where severe crashes are most likely.")

    st.markdown(    
    "**❤️ Why this matters:**\n"
    "For first responders, minutes and even seconds can determine whether an accident results in recovery or tragedy. "
    "Understanding when and where incidents spike allows emergency teams to position resources more strategically, "
    "reduce response times, and improve survival outcomes. Balanced data like this helps reveal patterns without the "
    "noise of real-world bias, enabling better shift planning, patrol routing, and hospital readiness. Ultimately, "
    "smarter preparation means more lives saved and less pressure on emergency systems."
)