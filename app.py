import streamlit as st
from database.db import init_db
from frontend.upload_bill import render_upload_bill
from frontend.upload_invoice import render_upload_invoice
from frontend.dashboard import render_dashboard

# Page Configuration
st.set_page_config(
    page_title="CarbonTrack — Carbon Footprint Estimator",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Emerald Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #064E3B 0%, #047857 50%, #10B981 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.2);
    }

    .main-header h1 {
        color: white !important;
        font-weight: 700;
        margin: 0 0 8px 0;
        font-size: 2.2rem;
    }

    .main-header p {
        color: #E6F4EA !important;
        margin: 0;
        font-size: 1.05rem;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #10B981;
    }

    .card-box {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database
init_db()

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🌱 CarbonTrack")
    st.markdown("*Transparent Carbon Footprint Estimation*")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        options=["🏠 Home", "⚡ Upload Electricity Bill", "🛒 Upload Shopping Invoice", "📊 Analytics Dashboard"],
        index=0
    )

    st.markdown("---")
    st.caption("🇮🇳 Emission Factors based on CEA v20.0 (2024) & IPCC / GHG Protocol")

# Main Content Routing
if page == "🏠 Home":
    st.markdown("""
    <div class="main-header">
        <h1>🌱 Carbon Footprint Estimator</h1>
        <p>Estimate your CO₂e carbon emissions from electricity bills & online shopping invoices using verified Indian government emission factors.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### ⚡ Electricity Bill")
        st.markdown("Upload your monthly electricity bill to calculate activity-based CO₂e emissions (**0.727 kg CO₂/kWh**, CEA v20.0).")
        if st.button("Go to Electricity Bill →", key="btn_bill", use_container_width=True, type="primary"):
            st.session_state["nav"] = "⚡ Upload Electricity Bill"
            st.rerun()

    with c2:
        st.markdown("### 🛒 Shopping Invoice")
        st.markdown("Upload your online purchase invoice to estimate spend-based CO₂e emissions using GHG Protocol EEIO emission factors.")
        if st.button("Go to Shopping Invoice →", key="btn_invoice", use_container_width=True, type="primary"):
            st.session_state["nav"] = "🛒 Upload Shopping Invoice"
            st.rerun()

    with c3:
        st.markdown("### 📊 Analytics Dashboard")
        st.markdown("View daily and monthly total carbon footprints, category breakdowns, and audit every calculation formula.")
        if st.button("Open Dashboard →", key="btn_dash", use_container_width=True):
            st.session_state["nav"] = "📊 Analytics Dashboard"
            st.rerun()

elif page == "⚡ Upload Electricity Bill":
    render_upload_bill()
elif page == "🛒 Upload Shopping Invoice":
    render_upload_invoice()
elif page == "📊 Analytics Dashboard":
    render_dashboard()
