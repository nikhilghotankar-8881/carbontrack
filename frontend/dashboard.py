from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import get_all_calculations, get_calculation_by_id


def render_dashboard():
    st.markdown("## 📊 Carbon Footprint Dashboard")
    st.markdown("Overview of your overall, monthly, and daily carbon emissions with full calculation auditability.")

    df = get_all_calculations()

    if df.empty:
        st.info("ℹ️ No calculation records found yet. Upload an electricity bill or shopping invoice to get started!")
        return

    # Filter dates
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    today_str = datetime.today().strftime("%Y-%m-%d")
    current_month_str = datetime.today().strftime("%Y-%m")

    total_co2e = df['result_co2e'].sum()
    today_co2e = df[df['date'].dt.strftime('%Y-%m-%d') == today_str]['result_co2e'].sum()
    monthly_co2e = df[df['date'].dt.strftime('%Y-%m') == current_month_str]['result_co2e'].sum()
    total_records = len(df)

    # 1. KPI Cards
    st.markdown("### 📈 Key Metrics")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Emissions", f"{total_co2e:.2f} kg", help="Lifetime calculated footprint")
    with k2:
        st.metric("Monthly Emissions", f"{monthly_co2e:.2f} kg", help="Current month total footprint")
    with k3:
        st.metric("Today's Emissions", f"{today_co2e:.2f} kg", help="Calculated footprint today")
    with k4:
        st.metric("Calculations", f"{total_records}", help="Total document calculations")

    st.markdown("---")

    # 2. Charts
    c_col1, c_col2 = st.columns([1, 1])

    with c_col1:
        st.markdown("#### 🍩 Category Breakdown")
        cat_df = df.groupby('category')['result_co2e'].sum().reset_index()
        fig_donut = px.pie(
            cat_df,
            names='category',
            values='result_co2e',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_donut.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_donut, use_container_width=True)

    with c_col2:
        st.markdown("#### 📅 Emissions Over Time")
        daily_df = df.groupby(df['date'].dt.strftime('%Y-%m-%d'))['result_co2e'].sum().reset_index()
        daily_df = daily_df.sort_values('date')
        fig_line = px.bar(
            daily_df,
            x='date',
            y='result_co2e',
            labels={'date': 'Date', 'result_co2e': 'kg CO₂e'},
            color_discrete_sequence=['#10B981']
        )
        fig_line.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=300)
        st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # 3. Calculation Records Table
    st.markdown("### 📋 Calculation History")
    display_df = df[['id', 'date', 'category', 'activity_value', 'activity_unit', 'result_co2e', 'method', 'source', 'version']].copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df.columns = ['ID', 'Date', 'Category', 'Activity', 'Unit', 'CO₂e (kg)', 'Method', 'Source', 'Version']

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 4. "How was this calculated?" Audit Transparency Inspector
    st.markdown("### ❓ How was this calculated?")
    st.markdown("Select any calculation record below to see the complete mathematical formula, factor source, version, and boundary details.")

    calc_options = {f"Record #{row['ID']} - {row['Category']} ({row['CO₂e (kg)']:.2f} kg CO₂e on {row['Date']})": row['ID'] for _, row in display_df.iterrows()}

    if calc_options:
        selected_label = st.selectbox("Choose a calculation to inspect:", list(calc_options.keys()))
        selected_id = calc_options[selected_label]

        calc_detail = get_calculation_by_id(selected_id)
        if calc_detail:
            with st.container():
                st.info(f"🔍 **Calculation Audit Details for Record #{selected_id}**")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f"**Activity Input**: {calc_detail['activity_value']} {calc_detail['activity_unit']}")
                    st.markdown(f"**Category**: `{calc_detail['category']}`")
                    st.markdown(f"**Method**: `{calc_detail['method']}`")
                with m2:
                    st.markdown(f"**Factor Value**: {calc_detail['factor_value']} {calc_detail.get('factor_unit', '')}")
                    st.markdown(f"**Result**: **{calc_detail['result_co2e']:.4f} kg CO₂e**")
                    st.markdown(f"**Source**: {calc_detail['source']}")
                with m3:
                    st.markdown(f"**Version**: `{calc_detail['version']}`")
                    st.markdown(f"**Boundary**: `{calc_detail.get('boundary', 'Scope 2')}`")
                    st.markdown(f"**Region/Country**: {calc_detail.get('region', 'National')}, {calc_detail.get('country', 'India')}")

                if calc_detail.get('source_url'):
                    st.markdown(f"🔗 [View Government/Official Source Document]({calc_detail['source_url']})")

                st.markdown("#### 📐 Mathematical Formula Breakdown")
                if calc_detail['method'] == 'activity-based':
                    st.code(f"CO₂e (kg) = Input Activity ({calc_detail['activity_value']} {calc_detail['activity_unit']}) × Emission Factor ({calc_detail['factor_value']} {calc_detail.get('factor_unit', '')})\n"
                            f"          = {calc_detail['activity_value']} × {calc_detail['factor_value']}\n"
                            f"          = {calc_detail['result_co2e']:.4f} kg CO₂e")
                else:
                    st.code(f"CO₂e (kg) = Spend Amount (₹{calc_detail['activity_value']}) × EEIO Spend Factor ({calc_detail['factor_value']} {calc_detail.get('factor_unit', '')})\n"
                            f"          = ₹{calc_detail['activity_value']} × {calc_detail['factor_value']}\n"
                            f"          = {calc_detail['result_co2e']:.4f} kg CO₂e")
