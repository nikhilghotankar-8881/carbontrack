import streamlit as st
from datetime import datetime
from modules.database import init_db, save_transaction
from modules.calculator import calculate_activity_emission, calculate_spend_emission
from modules.validators import validate_amount, validate_quantity
from modules.ui_components import render_result_card, CATEGORY_ICONS

# Ensure database tables exist
init_db()

st.set_page_config(page_title="Upload & Manual Entry — CarbonTrack", page_icon="📝", layout="wide")

st.title("📝 Add Bill or Manual Entry")
st.caption("Upload a bill receipt or manually enter transaction details to calculate carbon emissions.")

tab_manual, tab_bill = st.tabs(["✍️ Manual Entry", "📄 Bill / Receipt Upload"])

with tab_manual:
    st.subheader("Manual Transaction Entry")
    
    with st.form("manual_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            trans_date = st.date_input("Transaction Date", value=datetime.today())
            category_options = list(CATEGORY_ICONS.keys())
            category = st.selectbox(
                "Category", 
                options=category_options, 
                format_func=lambda c: f"{CATEGORY_ICONS[c]} {c}"
            )
            item = st.text_input("Item / Product Name", placeholder="e.g. Electricity Bill, Petrol, Cotton Shirt")
            vendor = st.text_input("Vendor / Provider", placeholder="e.g. BESCOM, HPCL, Amazon")
            
        with col2:
            amount_val = st.number_input("Purchase Amount (₹)", min_value=0.0, step=10.0, value=0.0)
            quantity_val = st.number_input("Physical Quantity (Optional for Activity-based)", min_value=0.0, step=1.0, value=0.0)
            unit_val = st.text_input("Unit (e.g. kWh, litre, kg, km)", placeholder="kWh")
            
        submit_btn = st.form_submit_button("🌱 Calculate & Save Transaction", use_container_width=True)

    if submit_btn:
        valid_amt, amt, amt_err = validate_amount(amount_val)
        valid_qty, qty, qty_err = validate_quantity(quantity_val if quantity_val > 0 else None)

        if not valid_amt or amt_err:
            st.error(amt_err or "Invalid amount entered.")
        else:
            try:
                # If quantity > 0, attempt activity-based calculation
                if qty and qty > 0:
                    try:
                        res = calculate_activity_emission(
                            quantity=qty,
                            unit=unit_val,
                            category=category,
                            item=item
                        )
                        data_used_str = f"{qty} {unit_val or 'units'}"
                    except ValueError:
                        # Fallback to spend-based if activity factor not found
                        res = calculate_spend_emission(amount=amt, category=category)
                        data_used_str = f"₹{amt:.2f}"
                else:
                    # Spend-based calculation
                    res = calculate_spend_emission(amount=amt, category=category)
                    data_used_str = f"₹{amt:.2f}"

                # Save transaction
                tx_record = {
                    "date": trans_date.strftime("%Y-%m-%d"),
                    "vendor": vendor,
                    "item": item or category,
                    "category": category,
                    "amount": amt,
                    "quantity": qty if qty and qty > 0 else None,
                    "unit": unit_val if unit_val else None,
                    "co2e": res["co2e"],
                    "calculation_method": res["calculation_method"],
                    "source_type": "manual"
                }

                save_transaction(tx_record)

                st.success("✅ Transaction calculated and saved to history!")
                render_result_card(
                    co2e=res["co2e"],
                    method=res["calculation_method"],
                    data_used=data_used_str,
                    factor_info=f"{res['source']} ({res['source_year']})",
                    quality=res["data_quality"]
                )

            except Exception as e:
                st.error(f"Error performing calculation: {str(e)}")

with tab_bill:
    st.subheader("Bill / Receipt Upload")
    st.info("Bill PDF and OCR Extraction will be wired in Phase 7 & 8.")
