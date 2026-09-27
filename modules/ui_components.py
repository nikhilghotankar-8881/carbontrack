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
    Renders the standardized result display card defined in DESIGN.md §6.
    """
    quality_color = "#2e7d32" if quality == "High" else "#ed6c02" # Green for High, Amber for Medium
    badge_bg = "#e8f5e9" if quality == "High" else "#fff3e0"
    
    st.markdown(f"""
    <div style="
        border: 2px solid #e0e0e0; 
        border-radius: 12px; 
        padding: 20px; 
        background-color: #fafafa;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    ">
        <div style="font-size: 14px; text-transform: uppercase; color: #666; font-weight: 600; letter-spacing: 0.5px;">Estimated CO₂e Footprint</div>
        <div style="font-size: 38px; font-weight: 700; color: #1b5e20; margin: 8px 0;">{co2e:.4f} <span style="font-size: 20px; font-weight: 500;">kg CO₂e</span></div>
        <hr style="border: none; border-top: 1px solid #eee; margin: 12px 0;">
        <table style="width: 100%; border-collapse: collapse; font-size: 14px; color: #333;">
            <tr>
                <td style="padding: 4px 0; color: #666; width: 140px;"><b>Calculation Method:</b></td>
                <td style="padding: 4px 0;">{method.title()}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; color: #666;"><b>Data Used:</b></td>
                <td style="padding: 4px 0;">{data_used}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; color: #666;"><b>Emission Factor:</b></td>
                <td style="padding: 4px 0;">{factor_info}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; color: #666;"><b>Data Quality:</b></td>
                <td style="padding: 4px 0;">
                    <span style="
                        background-color: {badge_bg}; 
                        color: {quality_color}; 
                        padding: 3px 10px; 
                        border-radius: 12px; 
                        font-weight: 600;
                        font-size: 13px;
                        display: inline-block;
                    ">● {quality}</span>
                </td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
