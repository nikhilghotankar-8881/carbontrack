import os
import streamlit as st
from backend.extractor import process_document_file, parse_electricity_bill_text
from backend.calculator import calculate_activity_emission
from database.db import save_document, save_extracted_items, update_verified_items, save_calculation, get_emission_factor


def render_upload_bill():
    st.markdown("## ⚡ Upload Electricity Bill")
    st.markdown("Upload your electricity bill (PDF, JPG, or PNG) to extract consumption data and calculate your carbon footprint.")

    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Choose an electricity bill file", type=["pdf", "jpg", "jpeg", "png"], key="bill_uploader")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        use_sample = st.button("📄 Load Sample Bill", use_container_width=True)

    file_to_process = None
    filename = ""

    if use_sample:
        sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents", "electricity_bill.pdf")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                file_to_process = f
                filename = "electricity_bill.pdf"
            st.info("Loaded sample electricity bill: `sample_documents/electricity_bill.pdf`")
        else:
            st.error("Sample electricity bill not found.")
    elif uploaded_file is not None:
        file_to_process = uploaded_file
        filename = uploaded_file.name

    if file_to_process:
        with st.spinner("Extracting bill data via OCR/PDF parser..."):
            extracted = process_document_file(file_to_process, filename, document_type="electricity_bill")

        st.success("✅ Extraction complete! Please review and verify the extracted details below.")

        st.markdown("### 🔍 Human Verification")
        st.markdown("*OCR raw extraction isolated from calculation. Verify and edit fields before running calculation.*")

        with st.form("verify_bill_form"):
            c1, c2 = st.columns(2)
            with c1:
                consumer_name = st.text_input("Consumer Name", value=extracted.get("consumer_name", ""))
                bill_date = st.text_input("Bill Date (YYYY-MM-DD)", value=extracted.get("bill_date", ""))
            with c2:
                units_consumed = st.number_input("Units Consumed (kWh)", value=float(extracted.get("units_consumed", 0.0)), min_value=0.0, step=1.0)
                bill_amount = st.number_input("Bill Amount (₹)", value=float(extracted.get("bill_amount", 0.0)), min_value=0.0, step=10.0)

            # Lookup factor to display transparency preview
            factor_info = get_emission_factor("Electricity", method="activity-based", unit="kWh")
            if factor_info:
                st.caption(f"ℹ️ **Factor preview**: {factor_info['factor_value']} {factor_info['factor_unit']} | Source: {factor_info['source']} ({factor_info['version']})")

            submitted = st.form_submit_button("⚡ Calculate Carbon Footprint", use_container_width=True, type="primary")

        if submitted:
            if units_consumed <= 0:
                st.warning("⚠️ Units consumed must be greater than 0 to calculate footprint.")
                return

            with st.spinner("Calculating footprint..."):
                # Save Document
                doc_id = save_document(filename, filename.split('.')[-1], "electricity_bill", extracted.get("raw_text", ""))

                # Save Extracted Items
                items_dict = {
                    "consumer_name": consumer_name,
                    "bill_date": bill_date,
                    "units_consumed": units_consumed,
                    "bill_amount": bill_amount
                }
                save_extracted_items(doc_id, items_dict)

                # Calculate
                calc_res = calculate_activity_emission(units_consumed, "kWh", "Electricity")

                calc_record = {
                    "document_id": doc_id,
                    "date": bill_date,
                    "category": "Electricity",
                    "activity_value": units_consumed,
                    "activity_unit": "kWh",
                    "factor_id": calc_res["factor_id"],
                    "factor_value": calc_res["factor_value"],
                    "method": calc_res["method"],
                    "source": calc_res["source"],
                    "version": calc_res["version"],
                    "result_co2e": calc_res["result_co2e"]
                }

                save_calculation(calc_record)

            st.balloons()
            st.markdown("---")
            st.markdown("### 📊 Emission Result")

            res_col1, res_col2 = st.columns([2, 1])
            with res_col1:
                st.metric("Estimated CO₂e Emission", f"{calc_res['result_co2e']:.2f} kg CO₂e")
                st.markdown(f"**Calculation Formula**: `{units_consumed} kWh × {calc_res['factor_value']} kg CO₂e/kWh` = **{calc_res['result_co2e']:.2f} kg CO₂e**")
            with res_col2:
                st.info(f"**Method**: {calc_res['method']}\n\n**Source**: {calc_res['source']}\n\n**Version**: {calc_res['version']}")

            with st.expander("📖 View Raw Extracted Text"):
                st.code(extracted.get("raw_text", "No text extracted"))
