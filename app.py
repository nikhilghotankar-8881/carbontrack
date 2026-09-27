import streamlit as st
from modules.styles import inject_custom_css, render_hero
from modules.database import init_db, get_all_transactions
from modules.ui_components import CATEGORY_ICONS

# Initialize Database Schema
init_db()

st.set_page_config(
    page_title="CarbonTrack — Personal Carbon Footprint Estimator",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS Styling
inject_custom_css()

def main():
    # Sidebar Header
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <div style="font-size: 40px; margin-bottom: 4px;">🌱</div>
            <div style="font-size: 20px; font-weight: 800; color: #10b981;">CarbonTrack</div>
            <div style="font-size: 12px; color: #94a3b8; font-weight: 500;">Hybrid Footprint Intelligence</div>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # Hero Banner
    render_hero(
        title="Personal Carbon Footprint Estimator",
        subtitle="Transform your daily bills and purchase records into defensible, activity & spend-based CO₂e estimates.",
        icon="🌱"
    )

    # Core Capabilities Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <div style="font-size: 32px; margin-bottom: 8px;">📄</div>
            <div style="font-size: 16px; font-weight: 700; color: #0f172a;">Bill Extraction</div>
            <div style="font-size: 13px; color: #64748b; margin-top: 6px;">
                Direct PDF text parsing & Tesseract OCR for electricity, gas, & fuel bills.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <div style="font-size: 32px; margin-bottom: 8px;">🛒</div>
            <div style="font-size: 16px; font-weight: 700; color: #0f172a;">CSV Order Import</div>
            <div style="font-size: 13px; color: #64748b; margin-top: 6px;">
                Bulk import online purchase history with auto keyword category classification.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <div style="font-size: 32px; margin-bottom: 8px;">⚖️</div>
            <div style="font-size: 16px; font-weight: 700; color: #0f172a;">Dual Methodology</div>
            <div style="font-size: 13px; color: #64748b; margin-top: 6px;">
                Activity-based (High) & Spend-based (Medium) GHG Protocol calculations.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="custom-card" style="text-align: center;">
            <div style="font-size: 32px; margin-bottom: 8px;">📊</div>
            <div style="font-size: 16px; font-weight: 700; color: #0f172a;">Actionable Insights</div>
            <div style="font-size: 13px; color: #64748b; margin-top: 6px;">
                Category breakdowns, trend analytics, & targeted carbon reduction tips.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick Stats Overview
    df = get_all_transactions()
    st.markdown("### 📈 System Status & Quick Summary")

    if not df.empty:
        total_co2e = df['co2e'].sum()
        total_tx = len(df)
        high_cat = df.groupby('category')['co2e'].sum().idxmax()

        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.metric("Total CO₂e Footprint Logged", f"{total_co2e:.2f} kg")
        with sc2:
            st.metric("Total Logged Transactions", f"{total_tx}")
        with sc3:
            st.metric("Top Emitting Category", f"{CATEGORY_ICONS.get(high_cat, '')} {high_cat}")
    else:
        st.info("💡 No transactions logged yet! Navigate to **Upload & Manual Entry** or **Purchases CSV** using the sidebar to start calculating your carbon footprint.")

if __name__ == "__main__":
    main()
