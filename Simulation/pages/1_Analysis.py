import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import squarify
import numpy as np
from matplotlib.patches import Circle, FancyBboxPatch
import plotly.graph_objects as go
import plotly.express as px


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

def add_vertical_space(lines=3):
    st.markdown("<br>" * lines, unsafe_allow_html=True)

driver_bg = "https://images.wallpaperscraft.com/image/single/roads_bridge_crossroads_345975_1280x720.jpg"
gov_bg = "https://images7.alphacoders.com/742/thumb-1920-742786.jpg"
emergency_bg = "https://t4.ftcdn.net/jpg/07/07/02/79/360_F_707027965_o1Nawl8IUYvBowX2BWbJBO8lAyHtkuIa.jpg"

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

# =====================================================================
# DRIVER PAGE
# =====================================================================

def driver_page(df: pd.DataFrame):
    set_bg(driver_bg)

    # ================== INTRO SECTION ==================
    st.info(
            "This section presents key data insights that help you as a driver understand "
            "when and why road accidents are most likely to occur.\n\n"
            "- Identify peak accident hours\n"
            "- Understand common causes\n"
            "- Recognize environmental or behavioural risks\n"
            "- Adjust driving habits for safety\n"
        )


    # ================================================================
    # 1. Accident Distribution by Time of Day – Donut Chart
    # ================================================================
    center_text("Accident Distribution by Time of Day", size=30)
    center_text("This section analyses traffic accident data to uncover patterns.", size=20)


    #st.markdown("This section analyses traffic accident data to uncover patterns.")

    time_order = ["Morning", "Afternoon", "Evening", "Night"]
    df["Time of Day"] = pd.Categorical(df["Time of Day"], categories=time_order, ordered=True)

    time_counts = (
        df["Time of Day"]
        .value_counts()
        .reindex(time_order)
        .to_frame(name="Count")
        .reset_index()
        .rename(columns={"index": "Time of Day"})
    )

    total_cases = time_counts["Count"].sum()
    emoji_map = (time_counts.set_index("Time of Day")["Count"] / total_cases * 100).to_dict()

    fig = px.pie(
        time_counts,
        names="Time of Day",
        values="Count",
        hole=0.55,
    )

    fig.update_traces(
        labels=["<b>Morning</b>", "<b>Afternoon</b>", "<b>Evening</b>", "<b>Night</b>"],
        textposition="inside",
        textinfo="label+percent",
        textfont=dict(size=16),
        marker=dict(colors=["#FF8000", "#FFD447", "#6CD400", "#00D084"])
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=500,
        margin=dict(t=60, b=40, l=10, r=60),
        showlegend=False,
        title_text=" ",
    )

   
    st.plotly_chart(fig, use_container_width=True)

    
    with st.expander("**Interpretation**"):
         st.write(
                "- Accident percentages are similar across all time periods.\n"
                "- Night accidents are slightly higher.\n"
                "- Risk exists at all hours.\n"
                "- Safe behaviour matters more than time of day."
            )

    center_text("Simple truth: Safe driving matters more than time of day.", size=20)
    #st.markdown("---")

    # ================================================================
    # 2. Injuries vs Fatalities – Pictogram
    # ================================================================
    center_text("Injuries vs Fatalities", size=30)

    injuries = int(df["Number of Injuries"].sum())
    fatalities = int(df["Number of Fatalities"].sum())
    total_people = injuries + fatalities if injuries + fatalities > 0 else 1

    p_inj = round(injuries / total_people * 100, 1)
    p_fat = round(fatalities / total_people * 100, 1)

    
    m1, m2 = st.columns([1, 1])
    m1.metric("**Total Injuries**", f"{injuries:,}")
    m2.metric("**Total Fatalities**", f"{fatalities:,}")

    
    st.caption("**Move the slider (visual only, does not change the data).**")

    
    N = st.slider("Number of people icons", 5, 20, 10, 1)
    inj_people = round(N * (injuries / total_people))
    fat_people = N - inj_people

    BLACK = "#000000"
    RED = "#FF0000"
    HEAD_R = 0.14
    BODY_W, BODY_H = 0.38, 0.48
    SPACING = 1.0

    def draw_person(ax, x, y, color):
        ax.add_patch(
            Circle((x, y + BODY_H / 2 + HEAD_R * 1.05), HEAD_R, facecolor=color, edgecolor="none")
        )
        ax.add_patch(
            FancyBboxPatch(
                (x - BODY_W / 2, y - BODY_H / 2), BODY_W, BODY_H,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor=color, edgecolor="none"
            )
        )

    fig2, ax2 = plt.subplots(figsize=(6, 1.1))
    x0, y0 = 0, 0

    for i in range(inj_people):
        draw_person(ax2, x0 + i * SPACING, y0, BLACK)
    for i in range(fat_people):
        draw_person(ax2, x0 + (inj_people + i) * SPACING, y0, RED)

    center_x = (N - 1) * SPACING / 2
    ax2.text(center_x - 1.5, 1.0, f"Injuries {p_inj}%", color=BLACK, fontsize=11, ha="right")
    ax2.text(center_x + 1.5, 1.0, f"Fatalities {p_fat}%", color=RED, fontsize=11, ha="left")

    ax2.set_xlim(-0.6, (N - 1) * SPACING + 0.6)
    ax2.set_ylim(-0.3, 0.7)
    ax2.axis("off")
    fig2.patch.set_alpha(0)
    ax2.set_facecolor("none")
    fig2.tight_layout()

    
    st.pyplot(fig2)

    st.expander("**Interpretation**")
    st.write(
                f"- **{p_inj}%** injured survivors.\n"
                f"- **{p_fat}%** fatalities.\n"
                "- Small percentage changes = big real-world impact."
            )

    center_text("Simple truth: Small percentage changes mean big real-world impact.", size=20)
    #st.markdown("---")

    # ================================================================
    # 3. Accident Cause Distribution – Treemap
    # ================================================================
    center_text("Accident Cause Distribution", size=30)

    cause_counts = df["Accident Cause"].value_counts().sort_values(ascending=False)

    cause_data = pd.DataFrame({
        "Cause": cause_counts.index,
        "Count": cause_counts.values
    })

    palette = ["#FFB74D", "#FF5252", "#AED581", "#4DD0E1", "#CE93D8", "#FFF176", "#FF8A65"]
    color_map = {cause: palette[i % len(palette)] for i, cause in enumerate(cause_data["Cause"])}

    fig3 = px.treemap(
        cause_data,
        path=["Cause"],
        values="Count",
        color="Cause",
        color_discrete_map=color_map,
    )

    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, l=0, r=0, b=0)
    )

    fig3.update_traces(
        texttemplate="<b>%{label}</b><br>Cases: %{value}",
        textfont=dict(size=16),
        textinfo="label+value",
        hovertemplate="<b>%{label}</b><br>Cases: %{value}<extra></extra>",
    )


    st.markdown("#### Focus on a specific cause")

    
    selected_cause = st.selectbox(
            "Select an accident cause to learn more:",
            cause_data["Cause"].tolist()
        )

    explanations = {
        "Drunk Driving": "Crashes caused by impaired reaction time and poor judgement.",
        "Distracted Driving": "Drivers lose focus due to phones, radio, or conversations.",
        "Speeding": "Driving too fast reduces reaction time and increases impact severity.",
        "Mechanical Failure": "Brake failure, worn tyres, or faulty lights.",
        "Weather": "Rain, fog, or snow reduces visibility and grip."
    }

    
    st.write(f"**{explanations.get(selected_cause, 'No explanation available.')}**")

    st.plotly_chart(fig3, use_container_width=True)
    
    with st.expander("Interpretation"):
         st.write(
                "- Treemap shows proportion of accidents by cause.\n"
                "- Human errors (drunk, distracted, speeding) dominate.\n"
                "- Environmental and mechanical factors are secondary."
            )

    
    st.success(
            "This page helps drivers:\n"
            "- Recognize accident patterns\n"
            "- Understand their safety blind spots\n"
            "- Make better driving decisions\n"
            "**Small changes in behaviour = safer roads**"
        )

# ======================================================================================================
# GOVERNMENT PAGE
# =========================================================================================================

def government_page(df: pd.DataFrame):
    set_bg(gov_bg)
    
    st.info(
            "This view is designed for **government and road authorities**. "
            "It highlights **high-risk road types**, differences in **urban/rural crashes**, "
            "and **reveals long-term fatality trends across countries.**\n "
            "\nThese insights help agencies understand "
            "where crashes are most concentrated, identify infrastructure gaps, and prioritize targeted improvements "
            "such as better lighting, road design upgrades, enforcement strategies, and community-level safety initiatives."
        )




    # Column names
    road_col = "Road Type"
    country_col = "Country"
    area_col = "Urban/Rural"
    year_col = "Year"
    fatal_col = "Number of Fatalities"

    # ---------------------------------------------------------------
    # 1. ROAD TYPE WAFFLE
    # ---------------------------------------------------------------
    center_text("Road Type Distribution of Accidents", size=30)

    road_counts = df[road_col].dropna().value_counts()

    n_rows, n_cols = 10, 10
    total_tiles = n_rows * n_cols

    proportions = (road_counts / road_counts.sum() * total_tiles).round().astype(int)
    diff = total_tiles - proportions.sum()
    proportions.iloc[0] += diff

    waffle_list = []
    for road, count in proportions.items():
        waffle_list.extend([road] * int(count))

    waffle_list = waffle_list[:total_tiles]
    waffle_grid = np.array(waffle_list).reshape(n_rows, n_cols)


    # Use a Matplotlib-friendly pastel hex palette
    pastel = [
        "#FFB3BA",  # soft red
        "#FFDFBA",  # soft orange
        "#FFFFBA",  # soft yellow
        "#BAFFC9",  # soft green
        "#BAE1FF",  # soft blue
        "#E2C6FF",  # soft purple
        "#FFD1DC",  # soft pink
    ]

    road_categories = list(road_counts.index)
    color_map = {r: pastel[i % len(pastel)] for i, r in enumerate(road_categories)}

    fig_w, ax_w = plt.subplots(figsize=(5.5, 5.5))

    for i in range(n_rows):
        for j in range(n_cols):
            road = waffle_grid[i, j]
            ax_w.add_patch(
                plt.Rectangle(
                    (j, n_rows - 1 - i),
                    1, 1,
                    facecolor=color_map[road],
                    edgecolor="grey",
                    linewidth=1.5,
                )
            )

    ax_w.set_xlim(0, n_cols)
    ax_w.set_ylim(0, n_rows)
    ax_w.set_xticks([])
    ax_w.set_yticks([])
    ax_w.set_aspect("equal")
    ax_w.set_title("Waffle Chart (1 square ≈ 1% of accidents)", fontsize=9)

    from matplotlib.patches import Patch
    legend_handles = [Patch(facecolor=color_map[r], edgecolor="none", label=r) for r in road_categories]
    ax_w.legend(handles=legend_handles, bbox_to_anchor=(1, 1), loc="upper left")

    fig_w.patch.set_alpha(0)
    ax_w.set_facecolor("none")
    fig_w.tight_layout()

    
    st.pyplot(fig_w)

    with st.expander("**Interpretation**"):
         st.write(
            "\n- Most accidents occur on **Main Roads**, shown by the largest block of squares."

            "\n- **Highways** make up the second-largest share, indicating notable crash risk at higher speeds."

            "\n- **Streets** contribute the smallest portion, likely due to lower traffic volume and speed."

            "Overall: **Main Roads** and **Highways** should be prioritised for safety improvements.")
        

    st.markdown("---")

    # ---------------------------------------------------------------
    # 2. URBAN vs RURAL BAR CHART
    # ---------------------------------------------------------------
    center_text("Accident Cases in Urban vs Rural Area", size=30)

    area_counts = (
        df.groupby([country_col, area_col])
        .size()
        .reset_index(name="Accident Count")
    )

    fig_bar = px.bar(
        area_counts,
        x=country_col,
        y="Accident Count",
        color=area_col,
        barmode="group",
    )

    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, l=0, r=0, b=0),
        legend_title_text="Area Type",
    )

   
    st.plotly_chart(fig_bar, use_container_width=True)

    with st.expander("**Interpretation**"):
         st.write(
            "- Accident counts are **high in both urban and rural areas** across all countries.\n"
            "\n- Urban areas generally show **slightly higher accident numbers**, likely due to heavier traffic, intersections, and congestion.\n"
            "\n- Rural areas remain significant contributors, especially where long-distance travel and limited lighting occur.\n"
            "- **Overall**: Both area types need attention, but urban regions may require stricter"
            " traffic control and enforcement, while rural regions benefit from better lighting, signage, and road maintenance."
        )

    st.markdown("---")

    # ---------------------------------------------------------------
    # 3. FATALITIES OVER YEARS (LINE CHART)
    # ---------------------------------------------------------------
    center_text("Fatalities Over the Years by Country", size=30)

    trend = (
        df.groupby([year_col, country_col])[fatal_col]
        .sum()
        .reset_index()
    )

    fig_line = px.line(
        trend,
        x=year_col,
        y=fatal_col,
        color=country_col,
        markers=True,
    
    )

    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, l=0, r=0, b=0),
        yaxis_title="Total Fatalities",
    )

    
    st.plotly_chart(fig_line, use_container_width=True)

    with st.expander("**Interpretation**"):
         st.write(
            "\n- All countries show **year-to-year fluctuations** in road fatalities rather than a clear upward or downward trend.\n"
            "\n- The fatality levels stay within a **similar range**, indicating that road safety challenges remain consistent over time.\n"
            "\n- Spikes in certain years may reflect **policy changes, seasonal factors, or major incidents.**"
            "\n- **Overall**: Road fatalities do not show a consistent decline, suggesting that continuous" 
            " and sustained safety efforts are needed rather than one-time interventions."
        )

    st.markdown("---")


    st.success(
            "Government insights:\n"
            "- Identify high-risk road types\n"
            "- Understand rural vs urban differences\n"
            "- Track fatality trends over time\n"
            "\nSupports targeted policies & infrastructure upgrades."
        )


# =====================================================================
# EMERGENCY PAGE
# =====================================================================

def emergency_page(df: pd.DataFrame):
    set_bg(emergency_bg)
    center_text("Emergency Responder – Analysis coming soon", size=28)

# =====================================================================
# ROLE ROUTING
# =====================================================================

if role == "Driver":
    driver_page(df)

elif role == "Government":
    government_page(df)

else:
    emergency_page(df)






