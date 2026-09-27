import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from modules.database import init_db, get_all_transactions
from modules.recommendations import get_recommendation_for_category
from modules.ui_components import CATEGORY_ICONS

init_db()

st.set_page_config(page_title="Dashboard — CarbonTrack", page_icon="📊", layout="wide")

st.title("📊 Carbon Footprint Dashboard")
st.caption("Comprehensive personal carbon emission insights, category breakdowns, trends, and targeted reduction tips.")

df = get_all_transactions()

if df.empty:
    st.info("ℹ️ No transactions logged yet. Upload a bill, import a purchase CSV, or add a manual entry to view your dashboard insights!")
    st.markdown("""
    ### Getting Started
    1. Go to **Upload & Manual Entry** to enter electricity/fuel bills or manual transactions.
    2. Go to **Purchases CSV** to bulk import online shopping history.
    3. Return here to track your total CO₂e footprint and reduction insights.
    """)
else:
    # 1. KPI Cards
    total_co2e = df['co2e'].sum()
    total_tx = len(df)
    
    # Calculate current month CO2e
    df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')
    current_month_str = datetime.now().strftime("%Y-%m")
    df_month = df[df['date_dt'].dt.strftime("%Y-%m") == current_month_str]
    month_co2e = df_month['co2e'].sum() if not df_month.empty else total_co2e

    # Highest emitting category
    cat_summary = df.groupby('category')['co2e'].sum().reset_index()
    highest_cat_row = cat_summary.loc[cat_summary['co2e'].idxmax()]
    highest_cat = highest_cat_row['category']
    highest_cat_co2e = highest_cat_row['co2e']

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total CO₂e Footprint", f"{total_co2e:.2f} kg", help="Total calculated CO₂e across all logged transactions")
    with c2:
        st.metric("This Month CO₂e", f"{month_co2e:.2f} kg", help=f"Total CO₂e logged in {datetime.now().strftime('%B %Y')}")
    with c3:
        st.metric("Logged Transactions", f"{total_tx}", help="Total number of logged records")
    with c4:
        st.metric("Top Contributor", f"{CATEGORY_ICONS.get(highest_cat, '')} {highest_cat}", f"{highest_cat_co2e:.2f} kg")

    st.markdown("---")

    # 2. Charts section
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Category Breakdown")
        cat_summary['display_name'] = cat_summary['category'].apply(lambda c: f"{CATEGORY_ICONS.get(c, '📦')} {c}")
        fig_cat = px.bar(
            cat_summary.sort_values('co2e', ascending=True),
            x='co2e',
            y='display_name',
            orientation='h',
            text_auto='.2f',
            labels={'co2e': 'CO₂e (kg)', 'display_name': 'Category'},
            color='co2e',
            color_continuous_scale='Greens'
        )
        fig_cat.update_layout(showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_right:
        st.subheader("Daily Emission Trend")
        daily_df = df.groupby('date')['co2e'].sum().reset_index().sort_values('date')
        fig_daily = px.line(
            daily_df,
            x='date',
            y='co2e',
            markers=True,
            labels={'date': 'Date', 'co2e': 'CO₂e (kg)'},
            line_shape='linear'
        )
        fig_daily.update_traces(line_color='#2e7d32', line_width=3)
        fig_daily.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_daily, use_container_width=True)

    # 3. Monthly Trend Chart
    df['year_month'] = df['date_dt'].dt.strftime("%Y-%m")
    monthly_df = df.groupby('year_month')['co2e'].sum().reset_index().sort_values('year_month')
    
    st.subheader("Monthly Footprint Overview")
    fig_monthly = px.bar(
        monthly_df,
        x='year_month',
        y='co2e',
        text_auto='.2f',
        labels={'year_month': 'Month', 'co2e': 'Total CO₂e (kg)'},
        color_discrete_sequence=['#4caf50']
    )
    fig_monthly.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_monthly, use_container_width=True)

    # 4. Actionable Recommendation Section (Phase 11)
    st.markdown("---")
    st.subheader("🌱 Actionable Reduction Recommendation")
    rec_text = get_recommendation_for_category(highest_cat)
    
    st.markdown(f"""
    <div style="
        border-left: 6px solid #2e7d32; 
        background-color: #e8f5e9; 
        padding: 18px 24px; 
        border-radius: 8px;
        margin: 10px 0 25px 0;
    ">
        <h4 style="margin: 0 0 8px 0; color: #1b5e20;">Highest Impact Area: {highest_cat} ({highest_cat_co2e:.2f} kg CO₂e)</h4>
        <div style="font-size: 15px; color: #2e7d32; line-height: 1.5;">{rec_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # 5. Export CSV Report
    st.markdown("### 📥 Download Carbon Report")
    csv_report = df[['date', 'vendor', 'item', 'category', 'amount', 'quantity', 'unit', 'co2e', 'calculation_method', 'source_type']].to_csv(index=False)
    st.download_button(
        label="📄 Download Transaction Report (CSV)",
        data=csv_report,
        file_name=f"carbontrack_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
