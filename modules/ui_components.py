import streamlit as st

CATEGORY_ICONS = {
    "Electricity": "⚡",
    "Fuel": "⛽",
    "Transport": "🚗",
    "Food": "🍎",
    "Clothing": "👕",
    "Electronics": "📱",
    "Household": "🏠",
    "Other": "📦"
}

def render_result_card(co2e: float, method: str, data_used: str, factor_info: str, quality: str):
    """
    Renders the standardized result display card with rich visual design.
    """
    badge_class = "badge-high" if quality == "High" else "badge-medium"
    dot_color = "🟢" if quality == "High" else "🟠"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0; 
        border-radius: 18px; 
        padding: 24px; 
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        margin-top: 18px;
        margin-bottom: 24px;
    ">
        <div style="font-size: 12px; text-transform: uppercase; color: #64748b; font-weight: 700; letter-spacing: 0.8px;">
            Estimated CO₂e Footprint
        </div>
        <div style="font-size: 40px; font-weight: 800; color: #047857; margin: 8px 0 16px 0; letter-spacing: -1px;">
            {co2e:.4f} <span style="font-size: 20px; font-weight: 600; color: #334155;">kg CO₂e</span>
        </div>
        
        <div style="
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
            gap: 12px; 
            background: #ffffff;
            border-radius: 12px;
            padding: 16px;
            border: 1px solid #f1f5f9;
        ">
            <div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Method</div>
                <div style="font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 2px;">{method.title()}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Data Used</div>
                <div style="font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 2px;">{data_used}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Factor Source</div>
                <div style="font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 2px;">{factor_info}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Data Quality</div>
                <div style="margin-top: 4px;">
                    <span class="{badge_class}">{dot_color} {quality} Quality</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
