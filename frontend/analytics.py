from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import get_all_calculations, get_documents_list


def render_analytics():
    st.markdown("## 📊 Carbon Intelligence Dashboard")
    st.markdown("Comprehensive analytics based strictly on verified stored calculation records.")

    df = get_all_calculations()
    df_docs = get_documents_list()

    if df.empty:
        st.info("ℹ️ No calculation data available for analytics yet. Process a document or run Demo Data to see charts.")
        return

    df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')
    current_month_str = datetime.today().strftime("%Y-%m")
    today_str = datetime.today().strftime("%Y-%m-%d")

    monthly_total = df[df['date_dt'].dt.strftime('%Y-%m') == current_month_str]['result_co2e'].sum()
    today_total = df[df['date_dt'].dt.strftime('%Y-%m-%d') == today_str]['result_co2e'].sum()

    unique_days = df['date_dt'].dt.strftime('%Y-%m-%d').nunique()
    daily_avg = (df['result_co2e'].sum() / unique_days) if unique_days > 0 else 0.0
    doc_count = len(df_docs) if not df_docs.empty else len(df)

    # 1. Top KPI Cards
    st.markdown("### 📈 Key Metric Highlights")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("TOTAL THIS MONTH", f"{monthly_total:.2f} kg CO₂e", help="Emissions for current month")
    with k2:
        st.metric("TODAY", f"{today_total:.2f} kg CO₂e", help="Emissions for today")
    with k3:
        st.metric("AVERAGE / DAY", f"{daily_avg:.2f} kg CO₂e", help="Daily average footprint across active days")
    with k4:
        st.metric("DOCUMENTS PROCESSED", f"{doc_count}", help="Total documents analyzed")

    st.markdown("---")

    # 2. Charts Section
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("#### 📈 CHART 1: Daily Carbon Footprint")
        daily_df = df.groupby(df['date_dt'].dt.strftime('%Y-%m-%d'))['result_co2e'].sum().reset_index()
        daily_df = daily_df.sort_values('date_dt')
        fig_line = px.line(
            daily_df,
            x='date_dt',
            y='result_co2e',
            labels={'date_dt': 'Date', 'result_co2e': 'kg CO₂e'},
            markers=True,
            color_discrete_sequence=['#10B981']
        )
        fig_line.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        st.markdown("#### 🍩 CHART 2: Category Contribution")
        cat_df = df.groupby('category')['result_co2e'].sum().reset_index()
        fig_pie = px.pie(
            cat_df,
            names='category',
            values='result_co2e',
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
        st.plotly_chart(fig_pie, use_container_width=True)

    c3, c4 = st.columns([1, 1])

    with c3:
        st.markdown("#### 📅 CHART 3: Monthly Footprint Trend")
        df['month_str'] = df['date_dt'].dt.strftime('%Y-%m')
        monthly_df = df.groupby('month_str')['result_co2e'].sum().reset_index()
        fig_bar = px.bar(
            monthly_df,
            x='month_str',
            y='result_co2e',
            labels={'month_str': 'Month', 'result_co2e': 'kg CO₂e'},
            color_discrete_sequence=['#047857']
        )
        fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c4:
        st.markdown("#### 🏆 TOP EMISSION SOURCES")
        total_co2e_sum = df['result_co2e'].sum()
        if total_co2e_sum > 0:
            cat_percent = df.groupby('category')['result_co2e'].sum().reset_index()
            cat_percent['percent'] = (cat_percent['result_co2e'] / total_co2e_sum) * 100
            cat_percent = cat_percent.sort_values('percent', ascending=False)

            for _, row in cat_percent.iterrows():
                st.markdown(f"**{row['category']}**: `{row['percent']:.1f}%` ({row['result_co2e']:.2f} kg CO₂e)")
                st.progress(min(int(row['percent']), 100))
        else:
            st.caption("No emissions recorded.")

    st.markdown("---")

    # 3. Recent Calculations Table
    st.markdown("### 📋 Recent Calculations Table")
    recent_display = df[['id', 'date', 'category', 'activity_value', 'activity_unit', 'method', 'source', 'result_co2e']].head(10).copy()
    recent_display['id'] = recent_display['id'].apply(lambda x: f"CALC-{x:05d}")
    recent_display['date'] = pd.to_datetime(recent_display['date']).dt.strftime('%Y-%m-%d')
    recent_display.columns = ['ID', 'Date', 'Category', 'Activity Value', 'Unit', 'Method', 'Source', 'CO₂e Result (kg)']
    st.dataframe(recent_display, use_container_width=True, hide_index=True)
