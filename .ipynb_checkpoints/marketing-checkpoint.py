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
    .metric-value { font-size: 2rem; font-weight: 700; color: #1e293b; }
    .metric-label { font-size: 0.85rem; color: #6b7280; margin-top: 4px; }
    .section-title {
        font-size: 1.3rem; font-weight: 700;
        color: #ffffff; margin: 1.2rem 0 0.8rem 0;
        border-left: 4px solid #1e293b;
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
    csv_path = os.path.join(base_dir, "Final_dataset.csv")
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
    st.title("Filters")
    st.markdown("---")

    # Education
    edu_options = ["All"] + sorted(df_full["Education"].dropna().unique().tolist())
    selected_edu = st.multiselect("Education", edu_options, default=["All"])

    # Marital Status
    mar_options = ["All"] + sorted(df_full["Marital_Status"].dropna().unique().tolist())
    selected_mar = st.multiselect("Marital Status", mar_options, default=["All"])

    # Country
    cty_options = ["All"] + sorted(df_full["Country"].dropna().unique().tolist())
    selected_cty = st.multiselect("Country", cty_options, default=["All"])

    # Age Group
    age_order = ["Teen", "Young Adult", "Middle Aged", "Senior", "Elderly"]
    age_options = ["All"] + [a for a in age_order if a in df_full["Age_Group"].unique()]
    selected_age = st.multiselect("Age Group", age_options, default=["All"])

    # Income Group
    inc_order = ["Low", "Lower Middle", "Middle", "Upper Middle", "High"]
    inc_options = ["All"] + [i for i in inc_order if i in df_full["Income_Group"].unique()]
    selected_inc = st.multiselect("Income Group", inc_options, default=["All"])

    # Response Filter
    response_filter = st.radio("Campaign Response", ["All", "Responded", "Not Responded"])

    st.markdown("---")


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

#df = df[(df["Income"] >= income_range[0]) & (df["Income"] <= income_range[1])]

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
st.title("Marketing Campaign Dashboard")
st.markdown("Interactive exploration of Customer Details")
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "KPI Overview",
    "Customer Segments",
    "Campaign Performance",
    "Channel & Products"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — KPI OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">Key Performance Indicators</div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Customers",   f"{len(df):,}")
    k2.metric("Avg Income",        f"{df['Income'].mean():,.0f}")
    k3.metric("Avg Spending",      f"{df['Total_Amt'].mean():,.0f}")
    k4.metric("Response Rate",     f"{df['Response'].mean()*100:.2f}%")
    k5.metric("Avg Purchases",     f"{df['Total_Purchases'].mean():.1f}")


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
                           title="Recency Distribution")
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
                     title="Average Spending",
                     color="Is_Parent",
                     color_discrete_sequence=["#2563EB", "#16A34A"],
                     labels={"Total_Amt": "Avg Spent", "Is_Parent": ""})
        fig.update_layout(plot_bgcolor="#1a1f2e", paper_bgcolor="#1a1f2e", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        parent_resp = df.groupby("Is_Parent")["Response"].mean().reset_index()
        parent_resp["Response"] = parent_resp["Response"] * 100
        fig = px.bar(parent_resp, x="Is_Parent", y="Response",
                     title="Response Rate",
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
                 title="Average Spending by Country",
                 color="Avg_Spent", color_continuous_scale="Teal",
                 labels={"Avg_Spent": "Avg Spent"})
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
                     labels={"Total_Accepted": "Total"})
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
                     labels={"Response": "Response"})
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
                     labels={"Response": "Response"})
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

