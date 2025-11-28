import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import squarify
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch
import plotly.graph_objects as go
import plotly.express as px

# ================== PAGE CONFIG ==================
left, mid, right = st.columns([1, 2, 1])
with mid:
  st.set_page_config(
    page_title="Traffic Accident Risk Dashboard – Analysis (Driver)",
    layout="wide"
)
  
st.markdown("""
<style>
/* Entire expander box */
div.streamlit-expander {
    background: #FFFFFF;  
    border-radius: 15px !important;
    border: 1px solid rgba(255, 255, 255, 0.45) !important;
    padding: 5px !important;
}

/* Expander header */
div.streamlit-expanderHeader {
    background: #FFFFFF !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    color: #333 !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    padding: 4px 10px !important;
}

</style>
""", unsafe_allow_html=True)


# ================== SHARED STYLES / HELPERS ==================
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
            background: rgba(255, 255, 255, 0.75);
            padding: 2rem;
            border-radius: 12px;
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
def add_vertical_space(lines=3):
    st.markdown("<br>" * lines, unsafe_allow_html=True)
    
driver_bg = "https://images.wallpaperscraft.com/image/single/roads_bridge_crossroads_345975_1280x720.jpg"
gov_bg = "https://images7.alphacoders.com/742/thumb-1920-742786.jpg"
emergency_bg = "https://t4.ftcdn.net/jpg/07/07/02/79/360_F_707027965_o1Nawl8IUYvBowX2BWbJBO8lAyHtkuIa.jpg"

def center_text(text, size=30, weight="bold"):
    st.markdown(
        f"<h1 style='text-align:center; font-size:{size}px; font-weight:{weight}; margin-bottom:0.2rem;'>{text}</h1>",
        unsafe_allow_html=True
    )

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

# ================== LOAD DATA ==================
df = pd.read_csv("road_accident_dataset.csv")

# ================== LAYOUT: HEADER ==================
center_text("", size=20)
center_text("🚦 Traffic Accident Risk Dashboard", size=40)
center_text("Analysis", size=28)
st.markdown("---")

# If user picks other role, gently tell them this page is for drivers only (for now)
if role != "Driver":
    # set appropriate background so whole app still looks consistent
    if role == "Government":
        set_bg(gov_bg)
    else:
        set_bg(emergency_bg)

    st.info(
        "This page currently shows the **Driver** analysis view only. "
        "Please select **Driver** in the sidebar to explore this analysis."
    )
    st.stop()

# If we reach here, role is Driver
set_bg(driver_bg)

# ================== INTRO SECTION ==================

left, mid, right = st.columns([1, 2, 1])
with mid:
    st.info(
        "This section presents key data insights that help you as a driver understand when and why road accidents are most\n "
        "likely to occur. The visualizations highlight patterns in accident timing, fatality and injuries caused by accident, and contributing factors,\n "
        "allowing you to recognize high-risk situations and make better decisions on the road.\n "
        "Each chart is paired with a brief interpretation to guide you in understanding the trends and their practical implications.\n "

        "\n By reviewing these insights, you as a driver can:"

        "\n- **Identify peak accident hours**"
        "\n- **Understand common causes of road incidents**"
        "\n- **Recognize environmental or behavioral conditions linked to higher risk**"
        "\n- **Adjust driving habits to improve safety and awareness**\n"
)
st.markdown("---")

# =====================================================================
# 1️⃣ Accident Distribution by Time of Day – Donut Chart
# =====================================================================

center_text("Accident Distribution by Time of Day", size=30)
def driver_analysis_page(df):
    
# short intro just under the title
   st.markdown(
        "This section analyses traffic accident data to uncover patterns and insights "
)

time_order = ["Morning", "Afternoon", "Evening", "Night"]
df["Time of Day"] = pd.Categorical(df["Time of Day"],
                                       categories=time_order,
                                       ordered=True)

time_counts = (
        df["Time of Day"]
        .value_counts()
        .reindex(time_order)
        .to_frame(name="Count"  )
        .reset_index()
        .rename(columns={"index": "Time of Day"})
    )
total_cases = time_counts["Count"].sum()
# For quick lookup of percentages
emoji_map = (time_counts.set_index("Time of Day")["Count"] / total_cases * 100).to_dict()

    # ---- Plotly donut chart ----
fig = px.pie(
        time_counts,
        names="Time of Day",
        values="Count",
        hole=0.55,                    # makes it a donut
    )

# Colours similar to before (you can tweak)
fig.update_traces(
    labels=["<b>Morning</b>", "<b>Afternoon</b>", "<b>Evening</b>", "<b>Night</b>"],
    textposition="inside",
    textinfo="label+percent",
    textfont=dict(size=16),
    marker=dict(
        colors=["#FF8000", "#FFD447", "#6CD400", "#00D084"]
    )
)
fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", # transparent background
        plot_bgcolor="rgba(0,0,0,0)", # transparent plot area
        title_text= (" "),
        height=500,                  
        margin=dict(t=60, b=40, l=10, r=60),
        showlegend=False,
        title_font=dict(size=26),

    )

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
     st.plotly_chart(fig, use_container_width=True)
     st.markdown(
    """
    <style>
    div[data-testid="stPlotlyChart"] {
        background-color: rgba(255, 236, 179, 0.55);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
left, mid, right = st.columns([1, 2, 1])
with mid:
    with st.expander("**Interpretation**"):
        st.write(
            "\n- Accident percentages are almost the same across Morning, Afternoon, Evening, and Night."
            "\n- Night is slightly higher **(25.2%)**, but the difference is very small."
            "\n- This shows that accident risk is constant throughout the day."
            "\n- **No time period is completely SAFE.**"
            "\n- You as a driver should stay alert at all hours, not just at night. "
     )

center_text("Simple truth: Accident prevention depends more on driver behaviour than the time of day.", size=20)
st.markdown("---")
# ================================
# 2. Injuries vs Fatalities – Pictogram
# ================================
from matplotlib.patches import Circle, FancyBboxPatch

center_text("Injuries vs Fatalities", size=30)

injuries = int(df["Number of Injuries"].sum())
fatalities = int(df["Number of Fatalities"].sum())
total_people = injuries + fatalities if injuries + fatalities > 0 else 1

p_inj = round(injuries / total_people * 100, 1)
p_fat = round(fatalities / total_people * 100, 1)

left, mid, right = st.columns([2.5, 2, 2.05])

with mid:
    m1, m2 = st.columns([1, 1])
    m1.metric("**Total Injuries**", f"{injuries:,}")
    m2.metric("**Total Fatalities**", f"{fatalities:,}")
    
left, mid, right = st.columns([1, 2, 1])
with mid:
    st.caption(
        "**Move the slider to change how many little people are drawn – "
        "this only changes the picture, not the data.**"
    )
left, mid, right = st.columns([1, 2, 1])
with mid:
    N = st.slider(
        "**Number of people icons**",
        min_value=5,
        max_value=20,
        value=10,
        step=1,
    )

inj_people = round(N * (injuries / total_people))
fat_people = N - inj_people

BLACK = "#000000"
RED = "#FF0000"
HEAD_R = 0.14
BODY_W, BODY_H = 0.38, 0.48
SPACING = 1.0

def draw_person(ax, x, y, color):
        ax.add_patch(
            Circle(
                (x, y + BODY_H / 2 + HEAD_R * 1.05),
                HEAD_R,
                facecolor=color,
                edgecolor="none",
            )
        )
        ax.add_patch(
            FancyBboxPatch(
                (x - BODY_W / 2, y - BODY_H / 2),
                BODY_W,
                BODY_H,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor=color,
                edgecolor="none",
            )
        )

fig2, ax2 = plt.subplots(figsize=(6, 1.1))
x0, y0 = 0, 0

for i in range(inj_people):
        draw_person(ax2, x0 + i * SPACING, y0, BLACK)
for i in range(fat_people):
        draw_person(ax2, x0 + (inj_people + i) * SPACING, y0, RED)

center_x = (N - 1) * SPACING / 2
ax2.text(
        center_x - 1.5,
        1.0,
        f"Injuries {p_inj}%",
        color=BLACK,
        fontsize=11,
        weight="semibold",
        ha="right",
    )
ax2.text(
        center_x + 1.5,
        1.0,
        f"Fatalities {p_fat}%",
        color=RED,
        fontsize=11,
        weight="semibold",
        ha="left",
    )

ax2.set_xlim(-0.6, (N - 1) * SPACING + 0.6)
ax2.set_ylim(-0.3, 0.7)
ax2.axis("off")
fig2.patch.set_alpha(0)
ax2.set_facecolor("none")

fig2.tight_layout()

    
st.markdown(

    """
    <style>
    div[data-testid="stPlotlyChart"] {
        background-color: rgba(255, 236, 179, 0.55);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True

)

left, mid, right = st.columns([1, 2, 1])

with mid:
    st.pyplot(fig2)
left, mid, right = st.columns([1, 2, 1])
with mid:
    with st.expander("**Interpretation**"):
        st.write(
            f"""
- About **{p_inj}%** of people in crashes were **injured but survived**.  
- About **{p_fat}%** of cases were **fatal**.  
- Even if fatalities are a smaller share, each red icon still represents a life lost –  
  a small change in percentage can mean a big real-world impact.
            """
        )
        
center_text("Simple truth: A small change in percentage can mean a big real-world impact", size=20)
st.markdown("---")
# =====================================================================
# 3️⃣ Accident Cause Distribution – Treemap
# =====================================================================
center_text("Accident Cause Distribution", size=30)
cause_counts = (
df["Accident Cause"]
    .value_counts()
    .sort_values(ascending=False)
)

cause_data = pd.DataFrame({
    "Cause": cause_counts.index,
    "Count": cause_counts.values
})

# colour palette (5 distinct pastel-ish colours – extend if more causes)
palette = ["#FFB74D", "#FF5252", "#AED581", "#4DD0E1", "#CE93D8", "#FFF176", "#FF8A65"]
color_map = {
    cause: palette[i % len(palette)]
    for i, cause in enumerate(cause_data["Cause"])
}

fig3 = px.treemap(
    cause_data,
    path=["Cause"],           # only one level
    values="Count",
    color="Cause",
    color_discrete_map=color_map,
)

fig3.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=40, l=0, r=0, b=0)
)
fig3.update_traces(
    texttemplate = "<b>%{label}</b><br>Cases: %{value}",
    textfont = dict(size=16, family="Arial"),
    textinfo="label+value",
    hovertemplate="<b>%{label}</b><br>Cases: %{value}<extra></extra>",
)
    
left, mid, right = st.columns([1, 2, 1])
with mid:
    st.markdown("#### Focus on a specific cause")
left, mid, right = st.columns([1, 2, 1])
with mid:
    selected_cause = st.selectbox(
        "Select an accident cause to learn more:",
        cause_data["Cause"].tolist()
    )
    
# Simple explanation dictionary for when user selects a cause
left, mid, right = st.columns([1, 2, 1])
with mid:
    explanations = {
        "Drunk Driving": (
            "Crashes where drivers are under the influence of alcohol or other substances. "
            "Impaired reaction time and poor judgement make even simple situations dangerous."
        ),
    "Distracted Driving": (
        "Cases where drivers are not fully focused on the road—for example, using a phone, "
        "adjusting the radio, or talking to passengers."
    ),
    "Speeding": (
        "Accidents that occur when drivers exceed the speed limit or drive too fast for road conditions. "
        "Higher speed reduces reaction time and increases impact severity."
    ),
    "Mechanical Failure": (
        "Crashes linked to vehicle issues such as brake failure, worn tyres, or faulty lights."
    ),
    "Weather": (
        "Incidents where rain, fog, snow or other adverse conditions reduce visibility or grip."
    )
}
left, mid, right = st.columns([1, 2, 1])    
with mid:
    st.write(f"**{explanations[selected_cause]}**")
    
# center the chart
left, mid, right = st.columns([1, 2, 1])
with mid:
     st.plotly_chart(fig3, use_container_width=True)
    
left, mid, right = st.columns([1, 2, 1])
with mid:
    left, mid, right = st.columns([1, 2, 1])
    with st.expander("**Interpretation**"):
        st.write(   
        "The treemap shows how different **causes of accidents** contribute to the overall number of crashes. "
        "\n- Drunk Driving is the highest contributor, showing the largest block. "
        "\n- Distracted Driving and Speeding also account for a large share of accidents. "
        "\n- Mechanical Failure and Weather-related issues contribute slightly less but still form significant portions of total accidents.\n"
        
         "\n Overall, human-related behaviours (drunk, distracted, speeding) make up the majority of accident causes. "
        )
left, mid, right = st.columns([1, 2, 1])
with mid:
    st.success(
        "In summary, this page helps you as a driver:\n" 
        "\n- See patterns behind when and why accidents happen"

        "\n- Recognize risks linked to behaviour, environment, and timing"

        "\n- Understand your own safety blind spots"

        "\n- Make small driving adjustments that can prevent major accidents\n"
        "\n**These insights help transform everyday driving into a safer, more mindful experience.**"
    )


