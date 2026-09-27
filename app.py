import streamlit as st

st.set_page_config(
    page_title="CarbonTrack — Personal Carbon Footprint Estimator",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.sidebar.title("🌱 CarbonTrack")
    st.sidebar.caption("Personal Carbon Footprint Estimator")
    st.sidebar.markdown("---")
    
    st.title("Welcome to CarbonTrack 🌱")
    st.markdown("""
    CarbonTrack helps you estimate your personal carbon footprint from daily bills and online purchase records.
    
    ### Key Features
    - ⚡ **Bill & Receipt Upload**: Activity-based CO₂e calculation from electricity, fuel, and grocery bills.
    - 🛒 **Online Purchases**: Spend-based CO₂e estimation from order history CSVs.
    - 📊 **Interactive Dashboard**: Category breakdown, daily & monthly trends, and reduction tips.
    - 📜 **Transaction History**: Full control to view, edit, or delete logged records.
    
    ---
    *Select a page from the sidebar to get started.*
    """)

if __name__ == "__main__":
    main()
