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
    st.markdown("---")
    center_text("Accident Distribution by Time of Day", size=30)


    

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
    st.markdown("---")

    # ================================================================
    # 2. Injuries vs Fatalities – Pictogram
    # ================================================================
    center_text("Injuries vs Fatalities", size=30)

    injuries = int(df["Number of Injuries"].sum())
    fatalities = int(df["Number of Fatalities"].sum())
    total_people = injuries + fatalities if injuries + fatalities > 0 else 1

    p_inj = round(injuries / total_people * 100, 1)
    p_fat = round(fatalities / total_people * 100, 1)

    left, mid1, mid2, right = st.columns([1.5, 2, 2, 1])

    with mid1:
        st.metric("**Total Injuries**", f"{injuries:,}")

    with mid2:
        st.metric("**Total Fatalities**", f"{fatalities:,}")

    
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

    with st.expander("**Interpretation**"):
         st.write(
                f"- **{p_inj}%** injured survivors.\n"
                f"- **{p_fat}%** fatalities.\n"
                "- Small percentage changes = big real-world impact."
            )

    center_text("Simple truth: Small percentage changes mean big real-world impact.", size=20)
    st.markdown("---")

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
    
    with st.expander("**Interpretation**"):
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
    st.markdown("---")



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

            "\n- **Streets** contribute the smallest portion, likely due to lower traffic volume and speed.\n"

            "\nOverall: **Main Roads** and **Highways** should be prioritised for safety improvements.")
        

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
    
    st.info(
        "This view is designed for **emergency responders and dispatch teams**. "
        "It focuses on how quickly help arrives (Emergency Response Time, ERT) "
        "and where accidents are more severe across countries.\n\n"
        "Use this page to:\n"
        "- Compare **Urban vs Rural** response times\n"
        "- Identify countries with **higher average accident severity**\n"
        "- Support resource planning and prioritisation"
    )
    st.markdown("---")
    ert_col = next(
        (c for c in df.columns if "response" in c.lower() or "ert" in c.lower()),
        None
    )
    severity_col = next(
        (c for c in df.columns if "severity" in c.lower()),
        None
    )

    if ert_col is None:
        st.error(
            "⚠️ Could not detect the Emergency Response Time (ERT) column.\n\n"
            "Please rename your ERT column to include 'response' or 'ERT', "
            "or manually set `ert_col` inside `emergency_page()`."
        )
        return

    if severity_col is None:
        st.error(
            "⚠️ Could not detect any severity column.\n\n"
            "Please rename your severity column to include 'severity', "
            "or manually set `severity_col` inside `emergency_page()`."
        )
        return

    country_col = "Country"
    area_col = "Urban/Rural"
    year_col = "Year"
    ert_col = "Emergency Response Time"
    severity_col = "Accident Severity"

    # Make sure key columns exist
    missing_cols = [c for c in [country_col, area_col, year_col] if c not in df.columns]
    if missing_cols:
        st.error(
            f"Missing required column(s): {', '.join(missing_cols)}. "
            "Please check your dataset."
        )
        return
    
    center_text("Emergency Response Time: Urban vs Rural", size=30)

    # ================== FILTERS (Shared) ==================
    st.markdown("### Filters")

    left, right = st.columns(2)

    with left:
        years = sorted(df[year_col].dropna().unique())
        selected_years = st.multiselect(
            "Year(s) to include",
            options=years,
            default=years,
        )

    with right:
        areas = df[area_col].dropna().unique().tolist()
        selected_areas = st.multiselect(
            "Area type(s)",
            options=areas,
            default=areas,
        )

    filtered = df.copy()
    if selected_years:
        filtered = filtered[filtered[year_col].isin(selected_years)]
    if selected_areas:
        filtered = filtered[filtered[area_col].isin(selected_areas)]

    if filtered.empty:
        st.warning("No data for the selected filters. Try widening your selection.")
        return

    # ================================================================
    # 1. Dumbbell Chart – ERT vs Urban/Rural by Country
    # ================================================================

    agg_choice = st.radio(
        "Summary statistic for ERT:",
        ["Mean", "Median"],
        horizontal=True,
    )
    agg_func = "mean" if agg_choice == "Mean" else "median"

    ert_grouped = (
        filtered.groupby([country_col, area_col])[ert_col]
        .agg(agg_func)
        .reset_index()
        .rename(columns={ert_col: "ERT_Value"})
    )

    # Pivot to wide format: one column for Urban, one for Rural
    pivot = ert_grouped.pivot(
        index=country_col,
        columns=area_col,
        values="ERT_Value"
    ).reset_index()

    # Drop countries where we don't have at least one ERT value
    pivot = pivot.dropna(how="all", subset=pivot.columns[1:])

    if pivot.empty:
        st.warning(
            "Not enough data to draw the dumbbell chart. "
            "Try including more area types or years."
        )
    else:
        # Sort countries by overall average ERT (for nicer y-axis ordering)
        pivot["AverageERT"] = pivot[pivot.columns[1:]].mean(axis=1)
        pivot = pivot.sort_values("AverageERT", ascending=True)

        fig_dumbbell = go.Figure()

        # Add connecting lines (one per country)
        for _, row in pivot.iterrows():
            # Collect non-null area values for this country
            xs = []
            ys = []
            for area in pivot.columns[1:-1]:  # skip country + AverageERT
                val = row[area]
                if pd.notna(val):
                    xs.append(val)
                    ys.append(row[country_col])
            
            if len(xs) >= 2:
                fig_dumbbell.add_trace(
                    go.Scatter(
                        x=xs,
                        y=ys,
                        mode="lines",
                        line=dict(width=2),
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )


        area_types = [c for c in pivot.columns[1:-1]]  
        colors = px.colors.qualitative.Set2

        for i, area_value in enumerate(area_types):
            fig_dumbbell.add_trace(
                go.Scatter(
                    x=pivot[area_value],
                    y=pivot[country_col],
                    mode="markers",
                    name=str(area_value),
                    marker=dict(size=12, symbol="circle"),
                    hovertemplate = (
                                      "Country: %{y}<br>"
                                      f"Area: {area_value}<br>"
                                      f"{agg_choice} ERT: %{{x:.2f}} minutes<extra></extra>"
                                    )
                            )
                                    )
            
        fig_dumbbell.update_layout(
            xaxis_title=f"{agg_choice} Emergency Response Time (minutes)",
            yaxis_title="Country",
            margin=dict(t=40, l=0, r=0, b=0),
            legend_title_text="Area Type",
        )

        st.plotly_chart(fig_dumbbell, use_container_width=True)

        with st.expander("**Interpretation**"):
            st.write(
                "- Each **horizontal line** shows one country.\n"
                "- The markers show **Urban vs Rural** average response time.\n"
                "- A **wide gap** between the markers means big Urban–Rural disparity.\n"
                "- Countries with **shorter ERT on the left** are responding faster overall.\n"
                "- This helps identify where **Rural support needs to be boosted**."
            )

    st.markdown("---")

    # ================================================================
    # 2. Choropleth – Average Severity Level by Country
    # ================================================================
    center_text("Average Accident Severity by Country", size=30)

    severity_map = {
        "minor": 1,
        "moderate": 2,
        "severe": 3,
    }

    sev_clean = (
        filtered[severity_col]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(severity_map)
    )

    if sev_clean.isna().all():
        st.error(
            "Cannot compute average severity – severity values could not be mapped. "
            "Expected labels: minor, moderate, severe."
        )
        return

    filtered_sev = filtered.copy()
    filtered_sev["_SeverityNum"] = sev_clean

    # static vs animated
    mode = st.radio(
        "Map mode:",
        ["Overall average", "Animated by year"],
        horizontal=True,
    )

    if mode == "Overall average":
        sev_grouped = (
            filtered_sev.groupby(country_col)["_SeverityNum"]
            .mean()
            .reset_index()
            .rename(columns={"_SeverityNum": "Average Severity"})
        )

        fig_choro = px.choropleth(
            sev_grouped,
            locations=country_col,
            locationmode="country names",
            color="Average Severity",
            hover_name=country_col,
            color_continuous_scale=["#00cc00", "#ffff00", "#ff9900", "#ff0000"],
            labels={"Average Severity": "Avg Severity"},
        )

        fig_choro.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=40, l=0, r=0, b=0),
            coloraxis_colorbar=dict(
                title="Avg Severity (1=Minor, 3=Severe)",
            ),
        )

        st.plotly_chart(fig_choro, use_container_width=True)

    else:
        sev_year = (
            filtered_sev.groupby([country_col, year_col])["_SeverityNum"]
            .mean()
            .reset_index()
            .rename(columns={"_SeverityNum": "Average Severity"})
        )

        fig_choro = px.choropleth(
            sev_year,
            locations=country_col,
            locationmode="country names",
            color="Average Severity",
            hover_name=country_col,
            animation_frame=year_col,
             color_continuous_scale=["#00cc00", "#ffff00", "#ff9900", "#ff0000"],
            labels={"Average Severity": "Avg Severity"},
        )

        fig_choro.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=40, l=0, r=0, b=0),
            coloraxis_colorbar=dict(
                title="Avg Severity (1=Minor, 3=Severe)",
            ),
        )

        st.plotly_chart(fig_choro, use_container_width=True)
        
    with st.expander("**Interpretation**"):
        st.write(
                "- The map visualises the **average accident severity** across countries using a clear colour gradient.\n"
                "- **Green areas** represent **low average severity**, where most accidents are minor.\n"
                "- **Yellow areas** indicate **moderate severity**, suggesting a mix of minor and more serious crashes.\n"
                "- **Red areas** highlight **high average severity**, meaning crashes are more severe and may need stronger emergency response resources.\n"
                "- In the **animated view**, you can observe how severity changes **year by year**, helping identify improving or worsening regions.\n"
                "- This map helps emergency responders and policymakers prioritise **ambulance deployment, trauma care capacity, and road-safety interventions**."
            )



# =====================================================================
# ROLE ROUTING
# =====================================================================

if role == "Driver":
    driver_page(df)

elif role == "Government":
    government_page(df)

else:
    emergency_page(df)






