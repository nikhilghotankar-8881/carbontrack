import streamlit as st

def inject_custom_css():
    """Injects high-end, modern CSS styling across the CarbonTrack app."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* App container background */
        .stApp {
            background-color: #f8fafc;
        }

        /* Custom Header Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #064e3b 0%, #047857 60%, #10b981 100%);
            border-radius: 20px;
            padding: 28px 36px;
            color: #ffffff;
            margin-bottom: 24px;
            box-shadow: 0 12px 28px -6px rgba(6, 78, 59, 0.25);
            position: relative;
            overflow: hidden;
        }
        
        .hero-banner::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -10%;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        .hero-title {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin: 0 0 6px 0;
            color: #ffffff !important;
        }

        .hero-subtitle {
            font-size: 15px;
            font-weight: 400;
            color: #d1fae5;
            margin: 0;
            max-width: 650px;
        }

        /* Premium Glass/Elevated Card */
        .custom-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 24px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.03), 0 2px 6px -1px rgba(0, 0, 0, 0.02);
            margin-bottom: 20px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .custom-card:hover {
            box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.06), 0 4px 10px -2px rgba(0, 0, 0, 0.03);
        }

        /* Metric Pill Container */
        .metric-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 20px 24px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.03);
            text-align: left;
            position: relative;
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.5px;
            margin-top: 4px;
        }
        
        .metric-label {
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748b;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
            border-right: 1px solid #1e293b;
        }

        section[data-testid="stSidebar"] * {
            color: #f1f5f9 !important;
        }

        section[data-testid="stSidebar"] .stButton > button {
            background-color: #047857 !important;
            color: #ffffff !important;
            border-radius: 10px;
            border: none;
            font-weight: 600;
        }

        /* Custom Form Input Fields */
        div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
            border-radius: 10px !important;
            border-color: #cbd5e1 !important;
        }
        
        div[data-baseweb="input"]:focus-within > div, div[data-baseweb="select"]:focus-within > div {
            border-color: #059669 !important;
            box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.15) !important;
        }

        /* Custom Streamlit Buttons */
        .stButton > button {
            border-radius: 12px !important;
            font-weight: 600 !important;
            padding: 10px 20px !important;
            transition: all 0.2s ease !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
            border: none !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(4, 120, 87, 0.25) !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(4, 120, 87, 0.35) !important;
        }

        /* Streamlit Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f1f5f9;
            padding: 6px;
            border-radius: 14px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 8px 18px;
            font-weight: 600;
            color: #475569;
        }

        .stTabs [aria-selected="true"] {
            background-color: #ffffff !important;
            color: #047857 !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        }

        /* Status Pills */
        .badge-high {
            background-color: #dcfce7;
            color: #15803d;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .badge-medium {
            background-color: #ffedd5;
            color: #c2410c;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        </style>
    """, unsafe_allow_html=True)

def render_hero(title: str, subtitle: str, icon: str = "🌱"):
    """Renders a stunning hero banner at the top of pages."""
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-title">{icon} {title}</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)
