import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from modules.styles import inject_custom_css, render_hero
from modules.database import init_db, get_all_transactions
from modules.recommendations import get_recommendation_for_category
from modules.ui_components import CATEGORY_ICONS

init_db()

st.set_page_config(page_title="Dashboard — CarbonTrack", page_icon="📊", layout="wide")

# Inject Custom CSS
inject_custom_css()

render_hero(
    title="Carbon Footprint Analytics Dashboard",
    subtitle="Interactive personal carbon emission insights, category breakdowns, daily/monthly trends, and actionable reduction tips.",
    icon="📊"
)

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
    
    df['date_dt'] = pd.to_datetime(df['date'], errors='coerce')
    current_month_str = datetime.now().strftime("%Y-%m")
    df_month = df[df['date_dt'].dt.strftime("%Y-%m") == current_month_str]
    month_co2e = df_month['co2e'].sum() if not df_month.empty else total_co2e

    cat_summary = df.groupby('category')['co2e'].sum().reset_index()
    highest_cat_row = cat_summary.loc[cat_summary['co2e'].idxmax()]
    highest_cat = highest_cat_row['category']
    highest_cat_co2e = highest_cat_row['co2e']

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Footprint</div>
            <div class="metric-value" style="color: #047857;">{total_co2e:.2f} <span style="font-size: 16px; font-weight: 500;">kg CO₂e</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">This Month CO₂e</div>
            <div class="metric-value" style="color: #0d9488;">{month_co2e:.2f} <span style="font-size: 16px; font-weight: 500;">kg CO₂e</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Logged Records</div>
            <div class="metric-value" style="color: #0284c7;">{total_tx}</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Top Contributor</div>
            <div class="metric-value" style="color: #c2410c; font-size: 22px;">
                {CATEGORY_ICONS.get(highest_cat, '')} {highest_cat}
                <div style="font-size: 14px; font-weight: 600; color: #64748b;">{highest_cat_co2e:.2f} kg</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

    # 2. Charts section
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("<h4 style='color: #0f172a; margin-bottom: 12px;'>Category Breakdown</h4>", unsafe_allow_html=True)
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
        fig_cat.update_layout(
            showlegend=False, 
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_right:
        st.markdown("<h4 style='color: #0f172a; margin-bottom: 12px;'>Daily Emission Trend</h4>", unsafe_allow_html=True)
        daily_df = df.groupby('date')['co2e'].sum().reset_index().sort_values('date')
        fig_daily = px.line(
            daily_df,
            x='date',
            y='co2e',
            markers=True,
            labels={'date': 'Date', 'co2e': 'CO₂e (kg)'},
            line_shape='linear'
        )
        fig_daily.update_traces(line_color='#047857', line_width=3, marker=dict(size=8, color='#065f46'))
        fig_daily.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_daily, use_container_width=True)

    # 3. Monthly Trend Chart
    df['year_month'] = df['date_dt'].dt.strftime("%Y-%m")
    monthly_df = df.groupby('year_month')['co2e'].sum().reset_index().sort_values('year_month')
    
    st.markdown("<h4 style='color: #0f172a; margin-top: 16px; margin-bottom: 12px;'>Monthly Footprint Overview</h4>", unsafe_allow_html=True)
    fig_monthly = px.bar(
        monthly_df,
        x='year_month',
        y='co2e',
        text_auto='.2f',
        labels={'year_month': 'Month', 'co2e': 'Total CO₂e (kg)'},
        color_discrete_sequence=['#10b981']
    )
    fig_monthly.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    # 4. Actionable Recommendation Section
    st.markdown("---")
    rec_text = get_recommendation_for_category(highest_cat)
    
    st.markdown(f"""
    <div style="
        border-left: 6px solid #047857; 
        background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%); 
        padding: 20px 26px; 
        border-radius: 12px;
        margin: 10px 0 25px 0;
        box-shadow: 0 4px 12px rgba(4, 120, 87, 0.06);
    ">
        <h4 style="margin: 0 0 6px 0; color: #064e3b; font-weight: 800;">
            🌱 Top Targeted Reduction Tip: {highest_cat} ({highest_cat_co2e:.2f} kg CO₂e)
        </h4>
        <div style="font-size: 15px; color: #047857; line-height: 1.6; font-weight: 500;">
            {rec_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5. Export CSV Report
    col_rep_text, col_rep_btn = st.columns([3, 1])
    with col_rep_text:
        st.markdown("##### 📄 Export Transaction Data")
        st.caption("Download full calculated carbon transaction dataset in standard CSV format.")
    with col_rep_btn:
        csv_report = df[['date', 'vendor', 'item', 'category', 'amount', 'quantity', 'unit', 'co2e', 'calculation_method', 'source_type']].to_csv(index=False)
        st.download_button(
            label="📥 Download CSV Report",
            data=csv_report,
            file_name=f"carbontrack_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
