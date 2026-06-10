import streamlit as st
import pandas as pd
import plotly.express as px

# ========== Page Config ==========
st.set_page_config(
    page_title="Middle East for Trading",
    page_icon="📊",
    layout="wide"
)

# ========== Load Data ==========
@st.cache_data
def load_data():
    df = pd.read_excel("Middle East for Trading.xlsx", sheet_name="Sheet1")
    df.columns = [str(col).strip() for col in df.columns]
    for col in ["Product price", "Settled amount", "Discount amount", "Financed amount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", "").str.replace("(", "-").str.replace(")", ""),
                errors="coerce"
            ).fillna(0)
    return df

df = load_data()

# ========== Title ==========
st.title("📊 Middle East for Trading - Dashboard")
st.markdown("---")

# ========== Filters ==========
col1, col2, col3 = st.columns(3)

with col1:
    branches = ["All"] + sorted(df["Branch Clean"].dropna().unique().tolist())
    selected_branch = st.selectbox("Branch", branches)

with col2:
    months = ["All"] + sorted(df["Month"].dropna().unique().tolist())
    selected_month = st.selectbox("Month", months)

with col3:
    types = ["All"] + sorted(df["Type of transaction"].dropna().unique().tolist())
    selected_type = st.selectbox("Transaction Type", types)

# ========== Filter Data ==========
filtered = df.copy()
if selected_branch != "All":
    filtered = filtered[filtered["Branch Clean"] == selected_branch]
if selected_month != "All":
    filtered = filtered[filtered["Month"] == selected_month]
if selected_type != "All":
    filtered = filtered[filtered["Type of transaction"] == selected_type]

# ========== KPI Cards ==========
st.markdown("### Key Performance Indicators")
k1, k2, k3, k4 = st.columns(4)

total_sales = filtered[filtered["Type of transaction"] == "Sale"]["Product price"].sum()
net_settled = filtered[filtered["Type of transaction"] == "Sale"]["Settled amount"].sum()
total_discount = filtered["Discount amount"].sum()
total_transactions = filtered[filtered["Type of transaction"] == "Sale"].shape[0]

k1.metric("Total Sales", f"{total_sales:,.0f} EGP")
k2.metric("Net Settled", f"{net_settled:,.0f} EGP")
k3.metric("Total Discounts", f"{total_discount:,.0f} EGP")
k4.metric("Total Transactions", f"{total_transactions:,}")

st.markdown("---")

# ========== Charts Row 1 ==========
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### Sales by Branch")
    branch_data = filtered[filtered["Type of transaction"] == "Sale"].groupby("Branch Clean")["Product price"].sum().reset_index()
    branch_data = branch_data.sort_values("Product price", ascending=False)
    fig1 = px.bar(branch_data, x="Branch Clean", y="Product price",
                  color="Branch Clean", text_auto=True)
    fig1.update_layout(showlegend=False, xaxis_title="Branch", yaxis_title="Sales")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown("#### Sales by Month")
    month_order = ["Dec-2025", "Jan-2026", "Feb-2026", "Mar-2026", "Apr-2026"]
    month_data = filtered[filtered["Type of transaction"] == "Sale"].groupby("Month")["Product price"].sum().reset_index()
    month_data["Month"] = pd.Categorical(month_data["Month"], categories=month_order, ordered=True)
    month_data = month_data.sort_values("Month")
    fig2 = px.line(month_data, x="Month", y="Product price", markers=True)
    fig2.update_layout(xaxis_title="Month", yaxis_title="Sales")
    st.plotly_chart(fig2, use_container_width=True)

# ========== Charts Row 2 ==========
c3, c4 = st.columns(2)

with c3:
    st.markdown("#### Transaction Types")
    type_data = filtered.groupby("Type of transaction")["Product price"].sum().reset_index()
    fig3 = px.pie(type_data, names="Type of transaction", values="Product price")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown("#### Top 10 Customers")
    top_customers = filtered[filtered["Type of transaction"] == "Sale"].groupby("Customer name")["Product price"].sum().reset_index()
    top_customers = top_customers.sort_values("Product price", ascending=False).head(10)
    fig4 = px.bar(top_customers, x="Product price", y="Customer name",
                  orientation="h", text_auto=True)
    fig4.update_layout(yaxis_title="", xaxis_title="Sales")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
st.caption("Middle East for Trading © 2026")