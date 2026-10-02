import os
from datetime import datetime
import streamlit as st
from backend.extractor import process_document_file
from backend.classifier import classify_text
from backend.calculator import calculate_spend_emission
from database.db import save_document, save_extracted_items, save_calculation, get_emission_factor

ALLOWED_CATEGORIES = ["Clothing", "Electronics", "Grocery", "Fuel", "Household", "Other"]


def render_upload_invoice():
    st.markdown("## 🛒 Shopping Invoice Carbon Estimator")
    st.markdown("Estimate spending-based CO₂e carbon emissions from online purchase invoices using GHG Protocol EEIO category factors.")

    # 6-Step Workflow Bar
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; background:#F8FAFC; border:1px solid #E2E8F0; padding:12px 16px; border-radius:12px; margin-bottom:24px; flex-wrap:wrap;">
        <div style="font-weight:700; color:#047857; font-size:0.8rem;">01 UPLOAD</div>
        <div style="color:#94A3B8;">→</div>
        <div style="font-weight:700; color:#047857; font-size:0.8rem;">02 EXTRACT</div>
        <div style="color:#94A3B8;">→</div>
        <div style="font-weight:700; color:#047857; font-size:0.8rem;">03 VERIFY</div>
        <div style="color:#94A3B8;">→</div>
        <div style="font-weight:700; color:#047857; font-size:0.8rem;">04 CATEGORIZE</div>
        <div style="color:#94A3B8;">→</div>
        <div style="font-weight:700; color:#047857; font-size:0.8rem;">05 MAP FACTOR</div>
        <div style="color:#94A3B8;">→</div>
        <div style="font-weight:700; color:#047857; font-size:0.8rem;">06 CALCULATE</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload your online shopping invoice (PNG, JPG, JPEG, PDF)", type=["pdf", "jpg", "jpeg", "png"], key="invoice_uploader")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        use_sample = st.button("📄 Load Demo Shopping Invoice", use_container_width=True)

    file_to_process = None
    filename = ""

    if use_sample:
        sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents", "shopping_invoice.pdf")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                file_to_process = f
                filename = "shopping_invoice.pdf"
            st.info("Loaded demo shopping invoice: `sample_documents/shopping_invoice.pdf`")
        else:
            st.error("Sample document not found.")
    elif uploaded_file is not None:
        file_to_process = uploaded_file
        filename = uploaded_file.name

    if file_to_process:
        with st.spinner("Extracting invoice data via PyMuPDF text parser & Tesseract OCR..."):
            extracted = process_document_file(file_to_process, filename, document_type="shopping_invoice")

        st.success("✅ Extraction complete! Review and verify the extracted details below.")

        product_name = extracted.get("product_name", "Cotton Slim Fit Shirt")
        auto_category = classify_text(product_name)
        if auto_category not in ALLOWED_CATEGORIES:
            auto_category = "Clothing"
        category_index = ALLOWED_CATEGORIES.index(auto_category)

        st.markdown("### ✍️ Product Verification & Category Mapping")
        st.caption("Auto-classification uses rule-based keyword mapping. Select category override if needed:")

        with st.form("verify_invoice_form"):
            c1, c2 = st.columns(2)
            with c1:
                verified_product = st.text_input("Product / Item Name", value=product_name)
                inv_date = st.text_input("Invoice Date (YYYY-MM-DD)", value=extracted.get("date", datetime.today().strftime("%Y-%m-%d")))
                selected_category = st.selectbox("Category (Auto-classified)", ALLOWED_CATEGORIES, index=category_index)
            with c2:
                quantity = st.number_input("Quantity", value=float(extracted.get("quantity", 1.0)), min_value=1.0, step=1.0)
                amount = st.number_input("Total Amount (₹)", value=float(extracted.get("amount", 1499.0)), min_value=0.0, step=10.0)

            factor_info = get_emission_factor(selected_category, method="spend-based")
            if factor_info:
                st.info(f"ℹ️ **EEIO Spend Factor Preview**: `{factor_info['factor_value']} {factor_info['factor_unit']}` | Source: {factor_info['source']} ({factor_info['version']})")
            else:
                st.error("⚠️ Factor not configured in emission factor database.")

            submitted = st.form_submit_button("🛒 Confirm & Calculate Footprint", use_container_width=True, type="primary")

        if submitted:
            if amount <= 0:
                st.warning("⚠️ Total amount must be greater than ₹0 to calculate footprint.")
                return

            with st.spinner("Executing calculation engine..."):
                doc_id = save_document(filename, filename.split('.')[-1], "shopping_invoice", extracted.get("raw_text", ""))

                items_dict = {
                    "product_name": verified_product,
                    "date": inv_date,
                    "category": selected_category,
                    "quantity": quantity,
                    "amount": amount
                }
                save_extracted_items(doc_id, items_dict)

                calc_res = calculate_spend_emission(amount, selected_category)

                calc_record = {
                    "document_id": doc_id,
                    "date": inv_date,
                    "category": selected_category,
                    "activity_value": amount,
                    "activity_unit": "INR",
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
                    ESTIMATED PURCHASE FOOTPRINT
                </div>
                <div style="font-size: 2.8rem; font-weight: 800; margin: 8px 0;">
                    {calc_res['result_co2e']:.2f} <span style="font-size: 1.5rem; font-weight: 500;">kg CO₂e</span>
                </div>
                <div style="font-size: 0.95rem; opacity: 0.95;">
                    Category: <strong>{selected_category}</strong> • Amount: <strong>₹{amount}</strong> • Method: <strong>Spend-based estimate</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Calculation Explanation Expander
            with st.expander("❓ How was this calculated?", expanded=True):
                st.markdown("#### Method Selection & Formula Breakdown")
                st.info("ℹ️ **Method Used**: `Spend-based estimate` (Method B)\n\n**Reason**: Physical product lifecycle factor unavailable; mapped spend amount to EEIO category factor.")

                st.code(f"""
INPUT SPEND AMOUNT     = ₹{amount}
CATEGORY               = {selected_category}
EEIO SPEND FACTOR      = {calc_res['factor_value']} kg CO₂e/INR
CALCULATION METHOD     = Spend-based

FORMULA:
  Result CO₂e = Spend Amount (₹{amount}) × Factor ({calc_res['factor_value']} kg CO₂e/INR)
              = ₹{amount} × {calc_res['factor_value']}
              = {calc_res['result_co2e']:.4f} kg CO₂e
                """)

                c_meta1, c_meta2 = st.columns(2)
                with c_meta1:
                    st.markdown(f"- **Factor Source**: {calc_res['source']}")
                    st.markdown(f"- **Version**: `{calc_res['version']}`")
                with c_meta2:
                    st.markdown(f"- **System Boundary**: `Cradle-to-gate / Cradle-to-shelf`")
                    st.markdown(f"- **Geographic Scope**: `Global EEIO Standard`")

                if calc_res.get('source_url'):
                    st.markdown(f"🔗 [View Official Source Document]({calc_res['source_url']})")

            with st.expander("📖 View Raw Extracted Text", expanded=False):
                st.code(extracted.get("raw_text", "No text extracted"))
