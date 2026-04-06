import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import os
import warnings
warnings.filterwarnings("ignore")

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Marketing Campaign Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #2563EB; }
    .metric-label { font-size: 0.85rem; color: #6b7280; margin-top: 4px; }
    .section-title {
        font-size: 1.3rem; font-weight: 700;
        color: #1e293b; margin: 1.2rem 0 0.8rem 0;
        border-left: 4px solid #2563EB;
        padding-left: 10px;
    }
    .sidebar .sidebar-content { background-color: #1e293b; }
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA LAYER — Load CSV + Build SQL Layer
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "Cleaned_marketing_data.csv")
    df = pd.read_csv(csv_path)

    # Ensure derived columns exist
    if "Total_Amt" not in df.columns:
        df["Total_Amt"] = (df["MntWines"] + df["MntFruits"] + df["MntMeatProducts"]
                         + df["MntFishProducts"] + df["MntSweetProducts"] + df["MntGoldProds"])
    if "Age" not in df.columns:
        df["Age"] = 2024 - df["Year_Birth"]
    if "Childrens" not in df.columns:
        df["Childrens"] = df["Kidhome"] + df["Teenhome"]
    if "Total_Purchases" not in df.columns:
        df["Total_Purchases"] = (df["NumWebPurchases"] + df["NumStorePurchases"]
                                + df["NumCatalogPurchases"] + df["NumDealsPurchases"])
    if "Campaigns_Accepted" not in df.columns:
        df["Campaigns_Accepted"] = (df["AcceptedCmp1"] + df["AcceptedCmp2"] + df["AcceptedCmp3"]
                                  + df["AcceptedCmp4"] + df["AcceptedCmp5"])
    if "Is_Parent" not in df.columns:
        df["Is_Parent"] = (df["Childrens"] > 0).map({True: "Parent", False: "Non-Parent"})

    df["Age_Group"]    = df["Age_Group"].astype(str)
    df["Income_Group"] = df["Income_Group"].astype(str)
    return df


@st.cache_resource
def get_sql_connection(df):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df.to_sql("market_data", conn, index=False, if_exists="replace")
    return conn


def run_query(conn, query):
    return pd.read_sql(query, conn)


# ── Load ──────────────────────────────────────────────────────────────────────
df_full = load_data()
conn    = get_sql_connection(df_full)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Filters
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
    st.title("📊 Dashboard Filters")
    st.markdown("---")

    # Education
    edu_options = ["All"] + sorted(df_full["Education"].dropna().unique().tolist())
    selected_edu = st.multiselect("🎓 Education", edu_options, default=["All"])

    # Marital Status
    mar_options = ["All"] + sorted(df_full["Marital_Status"].dropna().unique().tolist())
    selected_mar = st.multiselect("💍 Marital Status", mar_options, default=["All"])

    # Country
    cty_options = ["All"] + sorted(df_full["Country"].dropna().unique().tolist())
    selected_cty = st.multiselect("🌍 Country", cty_options, default=["All"])

    # Age Group
    age_order = ["Teen", "Young Adult", "Middle Aged", "Senior", "Elderly"]
    age_options = ["All"] + [a for a in age_order if a in df_full["Age_Group"].unique()]
    selected_age = st.multiselect("👤 Age Group", age_options, default=["All"])

    # Income Group
    inc_order = ["Low", "Lower Middle", "Middle", "Upper Middle", "High"]
    inc_options = ["All"] + [i for i in inc_order if i in df_full["Income_Group"].unique()]
    selected_inc = st.multiselect("💰 Income Group", inc_options, default=["All"])

    # Income Range Slider
    st.markdown("---")
    inc_min = int(df_full["Income"].min())
    inc_max = int(df_full["Income"].max())
    income_range = st.slider("💵 Income Range", inc_min, inc_max, (inc_min, inc_max), step=1000)

    # Response Filter
    st.markdown("---")
    response_filter = st.radio("📣 Campaign Response", ["All", "Responded", "Not Responded"])

    st.markdown("---")
    st.caption("Marketing Campaign Analysis Dashboard")


# ── Apply Filters ─────────────────────────────────────────────────────────────
df = df_full.copy()

if "All" not in selected_edu and selected_edu:
    df = df[df["Education"].isin(selected_edu)]
if "All" not in selected_mar and selected_mar:
    df = df[df["Marital_Status"].isin(selected_mar)]
if "All" not in selected_cty and selected_cty:
    df = df[df["Country"].isin(selected_cty)]
if "All" not in selected_age and selected_age:
    df = df[df["Age_Group"].isin(selected_age)]
if "All" not in selected_inc and selected_inc:
    df = df[df["Income_Group"].isin(selected_inc)]

df = df[(df["Income"] >= income_range[0]) & (df["Income"] <= income_range[1])]

if response_filter == "Responded (1)":
    df = df[df["Response"] == 1]
elif response_filter == "Not Responded (0)":
    df = df[df["Response"] == 0]

# Push filtered data to SQL
conn_filtered = sqlite3.connect(":memory:", check_same_thread=False)
df.to_sql("market_data", conn_filtered, index=False, if_exists="replace")


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.title("📊 Marketing Campaign Intelligence Dashboard")
st.markdown("Interactive exploration of customer segments, spending behavior, and campaign performance.")
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "KPI Overview",
    "Customer Segments",
    "Campaign Performance",
    "Channel & Products",
    "SQL Explorer"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — KPI OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Key Performance Indicators</div>', unsafe_allow_html=True)

    # KPI Row 1
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("👥 Total Customers",   f"{len(df):,}")
    k2.metric("💰 Avg Income",        f"{df['Income'].mean():,.0f}")
    k3.metric("🛍️ Avg Spending",      f"{df['Total_Amt'].mean():,.0f}")
    k4.metric("📣 Response Rate",     f"{df['Response'].mean()*100:.2f}%")
    k5.metric("📦 Avg Purchases",     f"{df['Total_Purchases'].mean():.1f}")

    st.markdown("")

    # KPI Row 2
    k6, k7, k8, k9, k10 = st.columns(5)
    k6.metric("🍷 Avg Wine Spend",    f"{df['MntWines'].mean():,.0f}")
    k7.metric("🥩 Avg Meat Spend",    f"{df['MntMeatProducts'].mean():,.0f}")
    k8.metric("🥇 Avg Gold Spend",    f"{df['MntGoldProds'].mean():,.0f}")
    k9.metric("🌐 Avg Web Visits",    f"{df['NumWebVisitsMonth'].mean():.1f}")
    k10.metric("📅 Avg Recency",      f"{df['Recency'].mean():.0f} days")

    st.markdown("---")

    # Income & Age Distribution
    st.markdown('<div class="section-title">Customer Demographics</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(df, x="Income", nbins=40, color_discrete_sequence=["#2563EB"],
                           title="Income Distribution", labels={"Income": "Income", "count": "Frequency"})
        fig.update_layout(bargap=0.05, plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(df, x="Age", nbins=30, color_discrete_sequence=["#EA580C"],
                           title="Age Distribution", labels={"Age": "Age", "count": "Frequency"})
        fig.update_layout(bargap=0.05, plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    # Total Spent & Recency
    col3, col4 = st.columns(2)
    with col3:
        fig = px.histogram(df, x="Total_Amt", nbins=40, color_discrete_sequence=["#16A34A"],
                           title="Total Spending Distribution")
        fig.update_layout(bargap=0.05, plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = px.histogram(df, x="Recency", nbins=30, color_discrete_sequence=["#7C3AED"],
                           title="Recency Distribution (Days since last purchase)")
        fig.update_layout(bargap=0.05, plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CUSTOMER SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">Segment Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Education breakdown
    with col1:
        edu_data = df.groupby("Education")["Total_Amt"].mean().reset_index().sort_values("Total_Amt", ascending=False)
        fig = px.bar(edu_data, x="Education", y="Total_Amt",
                     title="Avg Spending by Education",
                     color="Total_Amt", color_continuous_scale="Blues",
                     labels={"Total_Amt": "Avg Spent"})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Marital Status breakdown
    with col2:
        mar_data = df.groupby("Marital_Status")["Total_Amt"].mean().reset_index().sort_values("Total_Amt", ascending=False)
        fig = px.bar(mar_data, x="Marital_Status", y="Total_Amt",
                     title="Avg Spending by Marital Status",
                     color="Total_Amt", color_continuous_scale="Oranges",
                     labels={"Total_Amt": "Avg Spent"})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    # Age Group breakdown
    with col3:
        age_order = ["Teen", "Young Adult", "Middle Aged", "Senior", "Elderly"]
        age_data  = df.groupby("Age_Group")["Total_Amt"].mean().reset_index()
        age_data["Age_Group"] = pd.Categorical(age_data["Age_Group"], categories=age_order, ordered=True)
        age_data  = age_data.sort_values("Age_Group")
        fig = px.line(age_data, x="Age_Group", y="Total_Amt", markers=True,
                      title="Avg Spending by Age Group",
                      color_discrete_sequence=["#2563EB"],
                      labels={"Total_Amt": "Avg Spent", "Age_Group": "Age Group"})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    # Income Group breakdown
    with col4:
        inc_order = ["Low", "Lower Middle", "Middle", "Upper Middle", "High"]
        inc_data  = df.groupby("Income_Group")["Total_Amt"].mean().reset_index()
        inc_data["Income_Group"] = pd.Categorical(inc_data["Income_Group"], categories=inc_order, ordered=True)
        inc_data  = inc_data.sort_values("Income_Group")
        fig = px.bar(inc_data, x="Income_Group", y="Total_Amt",
                     title="Avg Spending by Income Group",
                     color="Income_Group",
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     labels={"Total_Amt": "Avg Spent"})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Parent vs Non-Parent Analysis</div>', unsafe_allow_html=True)

    col5, col6 = st.columns(2)
    with col5:
        parent_data = df.groupby("Is_Parent")["Total_Amt"].mean().reset_index()
        fig = px.bar(parent_data, x="Is_Parent", y="Total_Amt",
                     title="Avg Spending: Parent vs Non-Parent",
                     color="Is_Parent",
                     color_discrete_sequence=["#2563EB", "#16A34A"],
                     labels={"Total_Amt": "Avg Spent", "Is_Parent": ""})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        parent_resp = df.groupby("Is_Parent")["Response"].mean().reset_index()
        parent_resp["Response"] = parent_resp["Response"] * 100
        fig = px.bar(parent_resp, x="Is_Parent", y="Response",
                     title="Response Rate: Parent vs Non-Parent",
                     color="Is_Parent",
                     color_discrete_sequence=["#EA580C", "#7C3AED"],
                     labels={"Response": "Response Rate (%)", "Is_Parent": ""})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Country breakdown
    st.markdown('<div class="section-title">Country Level Analysis</div>', unsafe_allow_html=True)
    country_data = df.groupby("Country").agg(
        Total_Customers=("ID", "count"),
        Avg_Income=("Income", "mean"),
        Avg_Spent=("Total_Amt", "mean"),
        Response_Rate=("Response", "mean")
    ).reset_index()
    country_data["Response_Rate"] = (country_data["Response_Rate"] * 100).round(2)
    country_data = country_data.sort_values("Avg_Spent", ascending=False)

    fig = px.bar(country_data, x="Country", y="Avg_Spent",
                 hover_data=["Total_Customers", "Avg_Income", "Response_Rate"],
                 title="Avg Spending by Country",
                 color="Avg_Spent", color_continuous_scale="Teal",
                 labels={"Avg_Spent": "Avg Total Spent"})
    fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CAMPAIGN PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">Campaign Acceptance Rates</div>', unsafe_allow_html=True)

    campaigns = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5", "Response"]
    labels    = ["Campaign 1", "Campaign 2", "Campaign 3", "Campaign 4", "Campaign 5", "Final Response"]
    rates     = [df[c].mean() * 100 for c in campaigns]
    totals    = [df[c].sum() for c in campaigns]

    camp_df = pd.DataFrame({"Campaign": labels, "Acceptance_Rate": rates, "Total_Accepted": totals})

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(camp_df, x="Campaign", y="Acceptance_Rate",
                     title="Campaign Acceptance Rate (%)",
                     color="Acceptance_Rate", color_continuous_scale="RdYlGn",
                     text=camp_df["Acceptance_Rate"].apply(lambda x: f"{x:.2f}%"),
                     labels={"Acceptance_Rate": "Rate (%)"})
        fig.update_traces(textposition="outside")
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(camp_df, x="Campaign", y="Total_Accepted",
                     title="Total Customers Accepted per Campaign",
                     color="Total_Accepted", color_continuous_scale="Blues",
                     text="Total_Accepted",
                     labels={"Total_Accepted": "Total Accepted"})
        fig.update_traces(textposition="outside")
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Response Rate by Segment</div>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    # Response by Education
    with col3:
        resp_edu = df.groupby("Education")["Response"].mean().reset_index()
        resp_edu["Response"] = resp_edu["Response"] * 100
        resp_edu = resp_edu.sort_values("Response", ascending=False)
        fig = px.bar(resp_edu, x="Education", y="Response",
                     title="Response Rate by Education (%)",
                     color="Response", color_continuous_scale="Greens",
                     text=resp_edu["Response"].apply(lambda x: f"{x:.1f}%"),
                     labels={"Response": "Response Rate (%)"})
        fig.update_traces(textposition="outside")
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    # Response by Income Group
    with col4:
        resp_inc = df.groupby("Income_Group")["Response"].mean().reset_index()
        resp_inc["Response"] = resp_inc["Response"] * 100
        inc_order = ["Low", "Lower Middle", "Middle", "Upper Middle", "High"]
        resp_inc["Income_Group"] = pd.Categorical(resp_inc["Income_Group"], categories=inc_order, ordered=True)
        resp_inc = resp_inc.sort_values("Income_Group")
        fig = px.bar(resp_inc, x="Income_Group", y="Response",
                     title="Response Rate by Income Group (%)",
                     color="Response", color_continuous_scale="Purples",
                     text=resp_inc["Response"].apply(lambda x: f"{x:.1f}%"),
                     labels={"Response": "Response Rate (%)"})
        fig.update_traces(textposition="outside")
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    # Response vs Spending Boxplot
    st.markdown('<div class="section-title">Response vs Spending Behavior</div>', unsafe_allow_html=True)
    col5, col6 = st.columns(2)

    with col5:
        fig = px.box(df, x="Response", y="Total_Amt",
                     color="Response",
                     title="Response vs Total Spending",
                     color_discrete_sequence=["#2563EB", "#EA580C"],
                     labels={"Total_Amt": "Total Spent", "Response": "Response"})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        fig = px.box(df, x="Response", y="Income",
                     color="Response",
                     title="Response vs Income",
                     color_discrete_sequence=["#16A34A", "#DC2626"],
                     labels={"Income": "Income", "Response": "Response"})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Campaigns accepted summary table
    st.markdown('<div class="section-title">Campaign Summary Table</div>', unsafe_allow_html=True)
    st.dataframe(camp_df.style.format({"Acceptance_Rate": "{:.2f}%", "Total_Accepted": "{:,}"}),
                 use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CHANNEL & PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">Purchase Channel Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Channel totals
    with col1:
        channels = {
            "Web":     df["NumWebPurchases"].sum(),
            "Store":   df["NumStorePurchases"].sum(),
            "Catalog": df["NumCatalogPurchases"].sum(),
            "Deals":   df["NumDealsPurchases"].sum()
        }
        ch_df = pd.DataFrame({"Channel": list(channels.keys()), "Total": list(channels.values())})
        fig = px.bar(ch_df, x="Channel", y="Total",
                     title="Total Purchases by Channel",
                     color="Channel",
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     text="Total")
        fig.update_traces(textposition="outside")
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Channel pie
    with col2:
        fig = px.pie(ch_df, names="Channel", values="Total",
                     title="Channel Share (%)",
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     hole=0.4)
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    # Web visits vs purchases
    st.markdown('<div class="section-title">Web Conversion Analysis</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    with col3:
        fig = px.scatter(df.sample(min(3000, len(df))),
                         x="NumWebVisitsMonth", y="NumWebPurchases",
                         color="Income_Group",
                         title="Web Visits vs Web Purchases",
                         opacity=0.5,
                         labels={"NumWebVisitsMonth": "Web Visits/Month",
                                 "NumWebPurchases": "Web Purchases"})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        conv_rate = df["NumWebPurchases"].mean() / df["NumWebVisitsMonth"].mean() * 100
        channel_resp = df.groupby("Response").agg(
            Web=("NumWebPurchases", "mean"),
            Store=("NumStorePurchases", "mean"),
            Catalog=("NumCatalogPurchases", "mean"),
            Deals=("NumDealsPurchases", "mean")
        ).reset_index()
        channel_resp["Response"] = channel_resp["Response"].map({0: "Not Responded", 1: "Responded"})
        channel_melt = channel_resp.melt(id_vars="Response", var_name="Channel", value_name="Avg_Purchases")
        fig = px.bar(channel_melt, x="Channel", y="Avg_Purchases", barmode="group",
                     color="Response", title="Channel Usage by Response",
                     color_discrete_sequence=["#2563EB", "#EA580C"],
                     labels={"Avg_Purchases": "Avg Purchases"})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    # Product Spending
    st.markdown('<div class="section-title">Product Spending Analysis</div>', unsafe_allow_html=True)
    col5, col6 = st.columns(2)

    with col5:
        products = {
            "Wine":   df["MntWines"].sum(),
            "Fruits": df["MntFruits"].sum(),
            "Meat":   df["MntMeatProducts"].sum(),
            "Fish":   df["MntFishProducts"].sum(),
            "Sweets": df["MntSweetProducts"].sum(),
            "Gold":   df["MntGoldProds"].sum()
        }
        prod_df = pd.DataFrame({"Product": list(products.keys()), "Total": list(products.values())})
        fig = px.pie(prod_df, names="Product", values="Total",
                     title="Product Spending Mix",
                     color_discrete_sequence=px.colors.qualitative.Pastel,
                     hole=0.3)
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        prod_inc = df.groupby("Income_Group")[
            ["MntWines", "MntMeatProducts", "MntGoldProds", "MntFruits", "MntFishProducts", "MntSweetProducts"]
        ].mean().reset_index()
        inc_order = ["Low", "Lower Middle", "Middle", "Upper Middle", "High"]
        prod_inc["Income_Group"] = pd.Categorical(prod_inc["Income_Group"], categories=inc_order, ordered=True)
        prod_inc = prod_inc.sort_values("Income_Group")
        prod_melt = prod_inc.melt(id_vars="Income_Group", var_name="Product", value_name="Avg_Spend")
        prod_melt["Product"] = prod_melt["Product"].str.replace("Mnt", "").str.replace("Products", "").str.replace("Prods", "")
        fig = px.bar(prod_melt, x="Income_Group", y="Avg_Spend", color="Product",
                     title="Product Mix by Income Group (Stacked)",
                     color_discrete_sequence=px.colors.qualitative.Set3,
                     labels={"Avg_Spend": "Avg Spend", "Income_Group": "Income Group"})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e", barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

    # Correlation Heatmap
    st.markdown('<div class="section-title">Correlation Heatmap</div>', unsafe_allow_html=True)
    corr_cols = ["Age", "Income", "Total_Amt", "Recency",
                 "NumWebPurchases", "NumStorePurchases", "NumCatalogPurchases",
                 "Total_Purchases", "Campaigns_Accepted", "Response"]
    corr_matrix = df[corr_cols].corr().round(2)
    fig = px.imshow(corr_matrix, text_auto=True, color_continuous_scale="RdBu_r",
                    title="Feature Correlation Heatmap", aspect="auto")
    fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e")
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SQL EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">🔍 Live SQL Query Explorer</div>', unsafe_allow_html=True)
    st.info("Write any SQL query on the **market_data** table and explore results interactively.")

    # Preset queries
    preset = st.selectbox("📋 Load a Preset Query", [
        "Custom Query",
        "Overall KPIs",
        "Avg Spending by Education",
        "Campaign Acceptance Rates",
        "Response Rate by Income Group",
        "Top 10 Highest Spenders",
        "Channel Preference by Age Group",
        "Spending by Marital Status",
        "Parent vs Non-Parent Response",
        "Least Engaged Customers"
    ])

    preset_queries = {
        "Overall KPIs": """SELECT 
    COUNT(*) AS Total_Customers,
    ROUND(AVG(Income), 2) AS Avg_Income,
    ROUND(AVG(Total_Amt), 2) AS Avg_Spent,
    ROUND(AVG(Response) * 100, 2) AS Response_Rate,
    ROUND(AVG(Recency), 2) AS Avg_Recency,
    ROUND(AVG(Total_Purchases), 2) AS Avg_Purchases
FROM market_data""",

        "Avg Spending by Education": """SELECT Education,
    COUNT(*) AS Total_Customers,
    ROUND(AVG(Income), 2) AS Avg_Income,
    ROUND(AVG(Total_Amt), 2) AS Avg_Spent,
    ROUND(AVG(Response) * 100, 2) AS Response_Rate
FROM market_data
GROUP BY Education
ORDER BY Avg_Spent DESC""",

        "Campaign Acceptance Rates": """SELECT 
    ROUND(AVG(AcceptedCmp1) * 100, 2) AS Campaign1_Rate,
    ROUND(AVG(AcceptedCmp2) * 100, 2) AS Campaign2_Rate,
    ROUND(AVG(AcceptedCmp3) * 100, 2) AS Campaign3_Rate,
    ROUND(AVG(AcceptedCmp4) * 100, 2) AS Campaign4_Rate,
    ROUND(AVG(AcceptedCmp5) * 100, 2) AS Campaign5_Rate,
    ROUND(AVG(Response) * 100, 2) AS Final_Response_Rate
FROM market_data""",

        "Response Rate by Income Group": """SELECT Income_Group,
    COUNT(*) AS Total_Customers,
    SUM(Response) AS Responders,
    ROUND(AVG(Response) * 100, 2) AS Response_Rate,
    ROUND(AVG(Total_Amt), 2) AS Avg_Spent
FROM market_data
GROUP BY Income_Group
ORDER BY Response_Rate DESC""",

        "Top 10 Highest Spenders": """SELECT ID, Age, Age_Group, Education, Marital_Status,
    Income, Income_Group, Total_Amt, Campaigns_Accepted, Response
FROM market_data
ORDER BY Total_Amt DESC
LIMIT 10""",

        "Channel Preference by Age Group": """SELECT Age_Group,
    ROUND(AVG(NumWebPurchases), 2) AS Avg_Web,
    ROUND(AVG(NumStorePurchases), 2) AS Avg_Store,
    ROUND(AVG(NumCatalogPurchases), 2) AS Avg_Catalog,
    ROUND(AVG(NumDealsPurchases), 2) AS Avg_Deals,
    ROUND(AVG(Total_Purchases), 2) AS Avg_Total
FROM market_data
GROUP BY Age_Group
ORDER BY Avg_Total DESC""",

        "Spending by Marital Status": """SELECT Marital_Status,
    COUNT(*) AS Total_Customers,
    ROUND(AVG(Total_Amt), 2) AS Avg_Spent,
    ROUND(AVG(Income), 2) AS Avg_Income,
    ROUND(AVG(Response) * 100, 2) AS Response_Rate
FROM market_data
GROUP BY Marital_Status
ORDER BY Avg_Spent DESC""",

        "Parent vs Non-Parent Response": """SELECT 
    CASE WHEN Childrens > 0 THEN 'Parent' ELSE 'Non-Parent' END AS Customer_Type,
    COUNT(*) AS Total_Customers,
    ROUND(AVG(Total_Amt), 2) AS Avg_Spent,
    ROUND(AVG(Response) * 100, 2) AS Response_Rate
FROM market_data
GROUP BY Customer_Type""",

        "Least Engaged Customers": """SELECT ID, Age, Income, Total_Amt, Recency, Total_Purchases
FROM market_data
WHERE Recency > 80 AND Total_Amt < 100
ORDER BY Recency DESC
LIMIT 10"""
    }

    default_query = preset_queries.get(preset, "SELECT * FROM market_data LIMIT 10")
    query_input = st.text_area("✏️ SQL Query", value=default_query, height=200)

    col_run, col_clear = st.columns([1, 5])
    with col_run:
        run_btn = st.button("▶ Run Query", type="primary")

    if run_btn:
        try:
            result = run_query(conn_filtered, query_input)
            st.success(f"✅ Query returned {len(result):,} rows")
            st.dataframe(result, use_container_width=True)

            # Auto chart if result has 2 columns
            if len(result.columns) == 2:
                col_a, col_b = result.columns
                if result[col_b].dtype in [np.float64, np.int64]:
                    fig = px.bar(result, x=col_a, y=col_b,
                                 title=f"{col_b} by {col_a}",
                                 color=col_b, color_continuous_scale="Blues")
                    fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
                    st.plotly_chart(fig, use_container_width=True)

            # Download button
            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Result as CSV", csv,
                               file_name="query_result.csv", mime="text/csv")
        except Exception as e:
            st.error(f"❌ Query Error: {e}")

    # Raw Data Preview
    st.markdown("---")
    st.markdown('<div class="section-title">📄 Raw Data Preview</div>', unsafe_allow_html=True)
    st.caption(f"Showing filtered data: {len(df):,} rows × {df.shape[1]} columns")
    st.dataframe(df.head(100), use_container_width=True)

    csv_full = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Filtered Dataset", csv_full,
                       file_name="filtered_marketing_data.csv", mime="text/csv")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><sub>Marketing Campaign Intelligence Dashboard | Built with Streamlit & Plotly</sub></center>",
    unsafe_allow_html=True
)
