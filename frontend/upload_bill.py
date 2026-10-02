import os
from datetime import datetime
import streamlit as st
from backend.extractor import process_document_file
from backend.calculator import calculate_activity_emission
from database.db import save_document, save_extracted_items, save_calculation, get_emission_factor


def render_upload_bill():
    st.markdown("## ⚡ Electricity Bill Carbon Calculator")
    st.markdown("Activity-based CO₂e estimation from monthly electricity bills using Central Electricity Authority (CEA v20.0) grid emission factors.")

    # Step Indicator
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; background:#F8FAFC; border:1px solid #E2E8F0; padding:12px 20px; border-radius:12px; margin-bottom:24px;">
        <div style="font-weight:700; color:#047857; font-size:0.85rem;">01 UPLOAD</div>
        <div style="color:#94A3B8;">→</div>
        <div style="font-weight:700; color:#047857; font-size:0.85rem;">02 EXTRACT</div>
        <div style="color:#94A3B8;">→</div>
        <div style="font-weight:700; color:#047857; font-size:0.85rem;">03 VERIFY</div>
        <div style="color:#94A3B8;">→</div>
        <div style="font-weight:700; color:#047857; font-size:0.85rem;">04 CALCULATE</div>
        <div style="color:#94A3B8;">→</div>
        <div style="font-weight:700; color:#047857; font-size:0.85rem;">05 RESULT</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload your electricity bill (PNG, JPG, JPEG, PDF)", type=["pdf", "jpg", "jpeg", "png"], key="bill_uploader")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        use_sample = st.button("📄 Load Demo Electricity Bill", use_container_width=True)

    file_to_process = None
    filename = ""

    if use_sample:
        sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents", "electricity_bill.pdf")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                file_to_process = f
                filename = "electricity_bill.pdf"
            st.info("Loaded demo electricity bill: `sample_documents/electricity_bill.pdf`")
        else:
            st.error("Sample document not found.")
    elif uploaded_file is not None:
        file_to_process = uploaded_file
        filename = uploaded_file.name

    if file_to_process:
        with st.spinner("Extracting bill data via PyMuPDF text parser & Tesseract OCR..."):
            extracted = process_document_file(file_to_process, filename, document_type="electricity_bill")

        st.success("✅ Document processed! Review extracted values below before confirming calculation.")

        st.markdown("### ✍️ Extracted Information & Human Verification")
        st.caption("OCR raw extraction is isolated from calculation. Confirm or manually correct fields below:")

        with st.form("verify_bill_form"):
            c1, c2 = st.columns(2)
            with c1:
                consumer_name = st.text_input("Consumer Name", value=extracted.get("consumer_name", "Rajesh Sharma"))
                bill_date = st.text_input("Billing Date (YYYY-MM-DD)", value=extracted.get("bill_date", datetime.today().strftime("%Y-%m-%d")))
            with c2:
                units_consumed = st.number_input("Units Consumed (kWh)", value=float(extracted.get("units_consumed", 240.0)), min_value=0.0, step=1.0)
                bill_amount = st.number_input("Bill Amount (₹)", value=float(extracted.get("bill_amount", 2160.0)), min_value=0.0, step=10.0)

            # Look up factor preview
            factor_info = get_emission_factor("Electricity", method="activity-based", unit="kWh")
            if factor_info:
                st.info(f"ℹ️ **Configured Factor Preview**: `{factor_info['factor_value']} {factor_info['factor_unit']}` | Source: {factor_info['source']} ({factor_info['version']})")
            else:
                st.error("⚠️ Factor not configured in emission factor database.")

            submitted = st.form_submit_button("⚡ Confirm & Calculate Footprint", use_container_width=True, type="primary")

        if submitted:
            if units_consumed <= 0:
                st.warning("⚠️ Units consumed must be greater than 0 to calculate footprint.")
                return

            with st.spinner("Executing calculation engine..."):
                doc_id = save_document(filename, filename.split('.')[-1], "electricity_bill", extracted.get("raw_text", ""))

                items_dict = {
                    "consumer_name": consumer_name,
                    "bill_date": bill_date,
                    "units_consumed": units_consumed,
                    "bill_amount": bill_amount
                }
                save_extracted_items(doc_id, items_dict)

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

            # Result Card
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #064E3B 0%, #047857 100%); color: white; padding: 24px; border-radius: 16px; margin-bottom: 20px;">
                <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; opacity: 0.9;">
                    ESTIMATED ELECTRICITY EMISSIONS
                </div>
                <div style="font-size: 2.8rem; font-weight: 800; margin: 8px 0;">
                    {calc_res['result_co2e']:.2f} <span style="font-size: 1.5rem; font-weight: 500;">kg CO₂e</span>
                </div>
                <div style="font-size: 0.95rem; opacity: 0.95;">
                    Activity Input: <strong>{units_consumed} kWh</strong> • Method: <strong>Activity-based estimate</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Calculation Explanation Expander
            with st.expander("❓ How was this calculated?", expanded=True):
                st.markdown("#### Formula Breakdown")
                st.code(f"""
INPUT ACTIVITY         = {units_consumed} kWh
EMISSION FACTOR        = {calc_res['factor_value']} kg CO₂e/kWh
CALCULATION METHOD     = Activity-based

FORMULA:
  Result CO₂e = Input Activity ({units_consumed} kWh) × Factor ({calc_res['factor_value']} kg CO₂e/kWh)
              = {units_consumed} × {calc_res['factor_value']}
              = {calc_res['result_co2e']:.4f} kg CO₂e
                """)

                c_meta1, c_meta2 = st.columns(2)
                with c_meta1:
                    st.markdown(f"- **Factor Source**: {calc_res['source']}")
                    st.markdown(f"- **Version**: `{calc_res['version']}`")
                with c_meta2:
                    st.markdown(f"- **System Boundary**: `Scope 2 (Grid Emissions)`")
                    st.markdown(f"- **Geographic Scope**: `India (National)`")

                if calc_res.get('source_url'):
                    st.markdown(f"🔗 [View Official CEA Source Document]({calc_res['source_url']})")

            with st.expander("📖 View Raw Extracted Text", expanded=False):
                st.code(extracted.get("raw_text", "No text extracted"))
