import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ==============================Centred Title Function===============================
def center_text(text, size=30, weight="bold"):
    st.markdown(
        f"<h1 style='text-align:center; font-size:{size}px; font-weight:{weight};'>{text}</h1>",
        unsafe_allow_html=True
    )
center_text("", size=20)
st.set_page_config(page_title="Analysis", layout="wide")

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

# -----------------------------------------------
# Load global role (from sidebar in Home.py)
# -----------------------------------------------
role = st.session_state.get("role", "Driver")
df = pd.read_csv("road_accident_dataset.csv")

# =======================================================
# DRIVER ANALYSIS
# =======================================================
def driver_analysis(df: pd.DataFrame):
    st.markdown(
        """
        <h1 style='text-align:center; font-size:36px;'>
            🚗 Driver Accident Risk Analysis
        </h1>
        <p style='text-align:center; font-size:16px; color:gray;'>
            Explore how time of day, crash outcomes and causes relate to driver risk.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ---------- 1) Donut chart: Time of day ----------
    st.subheader("1. Accident Distribution by Time of Day")

    time_counts = df["Time of Day"].value_counts()

    fig, ax = plt.subplots(figsize=(4, 4))
    colors = ["#66b3ff", "#99ff99", "#ffcc99", "#ff9999"]

    wedges, texts, autotexts = ax.pie(
        time_counts,
        labels=time_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        wedgeprops={"width": 0.4},
        textprops={"fontsize": 9},
    )

    # Make it a donut
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    ax.add_artist(centre_circle)
    ax.set(aspect="equal")

    fig.tight_layout()
    st.pyplot(fig)

    st.info(
        f"🔍 **Insight:** The most common accident period is **{time_counts.idxmax()}**, "
        f"with **{time_counts.max()}** crashes in this dataset."
    )

    st.markdown("---")

    # ---------- 2) Injuries vs Fatalities – icon chart with slider ----------
    from matplotlib.patches import Circle, FancyBboxPatch

    st.subheader("2. Injuries vs Fatalities – People Icon View")

    injuries = int(df["Number of Injuries"].sum())
    fatalities = int(df["Number of Fatalities"].sum())
    total_people = injuries + fatalities if injuries + fatalities > 0 else 1

    p_inj = round(injuries / total_people * 100, 1)
    p_fat = round(fatalities / total_people * 100, 1)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Injuries", f"{injuries:,}")
    c2.metric("Total Fatalities", f"{fatalities:,}")
    c3.metric(
        "Injury : Fatality Ratio",
        f"{injuries}:{fatalities}" if fatalities > 0 else "–"
    )

    st.caption(
        "Move the slider to change how many little people are drawn – "
        "this only changes the picture, not the data."
    )

    N = st.slider(
        "Number of people icons",
        min_value=5,
        max_value=20,
        value=10,
        step=1,
    )

    inj_people = round(N * (injuries / total_people))
    fat_people = N - inj_people

    ORANGE = "#FFA726"
    RED = "#EF5350"

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

    fig2, ax2 = plt.subplots(figsize=(7, 2.2))
    x0, y0 = 0, 0

    for i in range(inj_people):
        draw_person(ax2, x0 + i * SPACING, y0, ORANGE)
    for i in range(fat_people):
        draw_person(ax2, x0 + (inj_people + i) * SPACING, y0, RED)

    center_x = (N - 1) * SPACING / 2
    ax2.text(
        center_x - 1.5,
        1.05,
        f"Injuries {p_inj}%",
        color=ORANGE,
        fontsize=11,
        weight="semibold",
        ha="right",
    )
    ax2.text(
        center_x + 1.5,
        1.05,
        f"Fatalities {p_fat}%",
        color=RED,
        fontsize=11,
        weight="semibold",
        ha="left",
    )

    ax2.set_xlim(-0.6, (N - 1) * SPACING + 0.6)
    ax2.set_ylim(-0.6, 1.6)
    ax2.axis("off")
    fig2.tight_layout()
    st.pyplot(fig2)

    with st.expander("What does this mean?"):
        st.write(
            f"""
- About **{p_inj}%** of people in crashes were **injured but survived**.  
- About **{p_fat}%** of cases were **fatal**.  
- Even if fatalities are a smaller share, each red icon still represents a life lost –  
  a small change in percentage can mean a big real-world impact.
            """
        )

    st.markdown("---")

    # ---------- 3) Treemap / bar: Accident cause ----------
    st.subheader("3. Accident Cause Distribution")

    # 👉 adjust this column name if yours is slightly different
    cause_col = "Accident Cause"
    if cause_col not in df.columns:
        st.error(f"Column `{cause_col}` not found in dataset – rename here if needed.")
        return

    causes = df[cause_col].value_counts()

    try:
        import squarify

        fig3, ax3 = plt.subplots(figsize=(6, 4))
        squarify.plot(
            sizes=causes.values,
            label=[f"{c}\n{v}" for c, v in zip(causes.index, causes.values)],
            color=sns.color_palette("Set2", len(causes)),
            alpha=0.9,
            ax=ax3,
            text_kwargs={"fontsize": 9},
        )
        ax3.axis("off")
        ax3.set_title("Treemap: Accident Cause Distribution", fontsize=14)
        fig3.tight_layout()
        st.pyplot(fig3)

    except ImportError:
        st.warning("`squarify` is not installed – showing a normal bar chart instead.")
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        sns.barplot(x=causes.values, y=causes.index, ax=ax3)
        ax3.set_xlabel("Number of accidents")
        ax3.set_ylabel("Cause")
        fig3.tight_layout()
        st.pyplot(fig3)

    st.info(
        "ℹ️ Use this view to see which **driver behaviours or external factors** appear most often. "
        "These are strong candidates for awareness campaigns and enforcement."
    )


# =======================================================
# GOVERNMENT ANALYSIS
# =======================================================
def government_analysis(df: pd.DataFrame):
    st.markdown(
        """
        <h1 style='text-align:center; font-size:36px;'>
            🏛️ Government Accident Overview
        </h1>
        <p style='text-align:center; font-size:16px; color:gray;'>
            Understand which regions, road types and area categories carry the most risk.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # 1) Accidents by region
    st.subheader("1. Accidents by Region")

    region_counts = df["Region"].value_counts()

    fig1, ax1 = plt.subplots(figsize=(7, 4))
    sns.barplot(x=region_counts.index, y=region_counts.values, ax=ax1)
    ax1.set_xlabel("Region")
    ax1.set_ylabel("Number of accidents")
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=30, ha="right")
    fig1.tight_layout()
    st.pyplot(fig1)

    st.caption("Use this to identify **high-volume regions** that may need targeted policies.")

    st.markdown("---")

    # 2) Road type distribution
    st.subheader("2. Accidents by Road Type")

    rt_counts = df["Road Type"].value_counts()

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(y=rt_counts.index, x=rt_counts.values, ax=ax2)
    ax2.set_xlabel("Number of accidents")
    ax2.set_ylabel("Road Type")
    fig2.tight_layout()
    st.pyplot(fig2)

    st.caption(
        "Helps compare whether **highways, main roads or local streets** contribute most to crashes."
    )

    st.markdown("---")

    # 3) Severity by Urban / Rural
    st.subheader("3. Accident Severity in Urban vs Rural Areas")

    if "Urban/Rural" in df.columns and "Accident Severity" in df.columns:
        crosstab = pd.crosstab(df["Urban/Rural"], df["Accident Severity"])

        fig3, ax3 = plt.subplots(figsize=(6, 4))
        crosstab.plot(kind="bar", stacked=True, ax=ax3, colormap="viridis")
        ax3.set_xlabel("Area Type")
        ax3.set_ylabel("Number of accidents")
        ax3.set_title("Severity by Area Type")
        ax3.legend(title="Severity")
        fig3.tight_layout()
        st.pyplot(fig3)

        with st.expander("How to read this chart"):
            st.write(
                """
- Each bar = **Urban or Rural** area.  
- Different colours = severity levels.  
- Taller / darker sections show where **serious crashes concentrate**, useful for infrastructure prioritisation.
                """
            )
    else:
        st.error("Columns `Urban/Rural` or `Accident Severity` not found – adjust names if needed.")


# =======================================================
# EMERGENCY RESPONDER ANALYSIS
# =======================================================
def responder_analysis(df: pd.DataFrame):
    st.markdown(
        """
        <h1 style='text-align:center; font-size:36px;'>
            🚑 Emergency Response Insights
        </h1>
        <p style='text-align:center; font-size:16px; color:gray;'>
            Focused views to support patrol planning and hospital readiness.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # 1) Severity distribution
    st.subheader("1. Distribution of Accident Severity")

    sev_counts = df["Accident Severity"].value_counts()

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.barplot(x=sev_counts.index, y=sev_counts.values, ax=ax1)
    ax1.set_xlabel("Severity")
    ax1.set_ylabel("Number of accidents")
    fig1.tight_layout()
    st.pyplot(fig1)

    st.caption(
        "Shows how many incidents fall into each severity category – "
        "useful for estimating **resource needs** (ambulances, trauma beds, etc.)."
    )

    st.markdown("---")

    # 2) Heatmap Time of Day vs Severity
    st.subheader("2. Time of Day vs Severity Heatmap")

    if "Time of Day" in df.columns and "Accident Severity" in df.columns:
        heat_data = pd.crosstab(df["Time of Day"], df["Accident Severity"])

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.heatmap(
            heat_data,
            annot=True,
            fmt="d",
            cmap="YlOrRd",
            cbar_kws={"label": "Number of accidents"},
            ax=ax2,
        )
        ax2.set_xlabel("Severity")
        ax2.set_ylabel("Time of Day")
        fig2.tight_layout()
        st.pyplot(fig2)

        st.caption(
            "Use this to spot **high-risk time windows** (e.g. severe night crashes) "
            "and align patrols / hospital staffing."
        )
    else:
        st.error("Columns `Time of Day` or `Accident Severity` not found – adjust names if needed.")


# =======================================================
# ROUTING BY ROLE
# =======================================================
if role == "Driver":
    driver_analysis(df)
elif role == "Government":
    government_analysis(df)
elif role == "Emergency Responder":
    responder_analysis(df)
else:
    st.error(f"Unknown role: {role}")
