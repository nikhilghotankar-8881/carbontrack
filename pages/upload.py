import streamlit as st
from datetime import datetime
from modules.database import init_db, save_transaction
from modules.calculator import calculate_activity_emission, calculate_spend_emission
from modules.validators import validate_amount, validate_quantity, validate_date
from modules.classifier import classify_text
from modules.extractor import process_bill_file
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
                        res = calculate_spend_emission(amount=amt, category=category)
                        data_used_str = f"₹{amt:.2f}"
                else:
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
    st.subheader("Bill / Receipt Extraction & Verification")
    st.caption("Upload a bill PDF or image scan (JPG/PNG). System extracts details for your verification.")

    uploaded_bill = st.file_uploader("Upload Bill (PDF, JPG, PNG)", type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_bill is not None:
        with st.spinner("🔍 Reading bill & extracting transaction fields..."):
            extracted = process_bill_file(uploaded_bill, uploaded_bill.name)

        st.success("✅ Extraction complete! Please verify and edit extracted fields below.")

        with st.expander("📄 View Raw Extracted Text", expanded=False):
            st.code(extracted.get("raw_text") or "No text could be extracted.", language="text")

        st.markdown("### 🛠️ Verify Extracted Information")
        st.warning("⚠️ Always review extracted fields before confirming. Missing or low-confidence fields are left editable below.")

        with st.form("verify_bill_form"):
            b_col1, b_col2 = st.columns(2)

            # Default fallback values for form controls
            extracted_date_str = extracted.get("date")
            try:
                def_date = datetime.strptime(extracted_date_str, "%Y-%m-%d") if extracted_date_str else datetime.today()
            except Exception:
                def_date = datetime.today()

            detected_item = extracted.get("item") or "Electricity Bill"
            auto_category = classify_text(detected_item)
            cat_list = list(CATEGORY_ICONS.keys())
            cat_index = cat_list.index(auto_category) if auto_category in cat_list else 0

            with b_col1:
                v_date = st.date_input("Date", value=def_date, key="b_date")
                v_category = st.selectbox(
                    "Category", 
                    options=cat_list, 
                    index=cat_index,
                    format_func=lambda c: f"{CATEGORY_ICONS[c]} {c}",
                    key="b_cat"
                )
                v_item = st.text_input("Item Description", value=detected_item, key="b_item")
                v_vendor = st.text_input("Vendor / Provider", value=extracted.get("vendor") or "", placeholder="e.g. BESCOM, HPCL", key="b_vendor")

            with b_col2:
                v_amount = st.number_input("Amount (₹)", min_value=0.0, value=float(extracted.get("amount") or 0.0), key="b_amt")
                v_quantity = st.number_input("Physical Quantity (e.g. 185)", min_value=0.0, value=float(extracted.get("quantity") or 0.0), key="b_qty")
                v_unit = st.text_input("Unit", value=extracted.get("unit") or "kWh", key="b_unit")

            confirm_bill_btn = st.form_submit_button("🌱 Confirm Verification & Save Transaction", use_container_width=True)

        if confirm_bill_btn:
            try:
                # If quantity > 0 -> Activity based
                if v_quantity > 0:
                    try:
                        res = calculate_activity_emission(
                            quantity=v_quantity,
                            unit=v_unit,
                            category=v_category,
                            item=v_item
                        )
                        data_used_str = f"{v_quantity} {v_unit or 'units'}"
                    except ValueError:
                        res = calculate_spend_emission(amount=v_amount, category=v_category)
                        data_used_str = f"₹{v_amount:.2f}"
                else:
                    res = calculate_spend_emission(amount=v_amount, category=v_category)
                    data_used_str = f"₹{v_amount:.2f}"

                tx_record = {
                    "date": v_date.strftime("%Y-%m-%d"),
                    "vendor": v_vendor,
                    "item": v_item,
                    "category": v_category,
                    "amount": v_amount,
                    "quantity": v_quantity if v_quantity > 0 else None,
                    "unit": v_unit if v_unit else None,
                    "co2e": res["co2e"],
                    "calculation_method": res["calculation_method"],
                    "source_type": "bill"
                }

                save_transaction(tx_record)

                st.success("🎉 Bill transaction verified and saved to history!")
                render_result_card(
                    co2e=res["co2e"],
                    method=res["calculation_method"],
                    data_used=data_used_str,
                    factor_info=f"{res['source']} ({res['source_year']})",
                    quality=res["data_quality"]
                )

            except Exception as e:
                st.error(f"Error processing verified bill: {str(e)}")
