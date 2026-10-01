import os
import streamlit as st
from backend.extractor import process_document_file
from backend.classifier import classify_text
from backend.calculator import calculate_spend_emission
from database.db import save_document, save_extracted_items, save_calculation, get_emission_factor

ALLOWED_CATEGORIES = ["Clothing", "Electronics", "Grocery", "Fuel", "Household", "Other"]


def render_upload_invoice():
    st.markdown("## 🛒 Upload Online Shopping Invoice")
    st.markdown("Upload your shopping invoice (PDF, JPG, or PNG) to extract purchase details and calculate your carbon footprint.")

    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("Choose a shopping invoice file", type=["pdf", "jpg", "jpeg", "png"], key="invoice_uploader")
    with col2:
        st.markdown("<br>", unsafe_allow_dict=True)
        use_sample = st.button("📄 Load Sample Invoice", use_container_width=True)

    file_to_process = None
    filename = ""

    if use_sample:
        sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents", "shopping_invoice.pdf")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                file_to_process = f
                filename = "shopping_invoice.pdf"
            st.info("Loaded sample shopping invoice: `sample_documents/shopping_invoice.pdf`")
        else:
            st.error("Sample shopping invoice not found.")
    elif uploaded_file is not None:
        file_to_process = uploaded_file
        filename = uploaded_file.name

    if file_to_process:
        with st.spinner("Extracting invoice data via OCR/PDF parser..."):
            extracted = process_document_file(file_to_process, filename, document_type="shopping_invoice")

        st.success("✅ Extraction complete! Please review and verify the extracted details below.")

        product_name = extracted.get("product_name", "")
        auto_category = classify_text(product_name)
        category_index = ALLOWED_CATEGORIES.index(auto_category) if auto_category in ALLOWED_CATEGORIES else ALLOWED_CATEGORIES.index("Other")

        st.markdown("### 🔍 Human Verification")
        st.markdown("*OCR raw extraction isolated from calculation. Verify and edit fields before running calculation.*")

        with st.form("verify_invoice_form"):
            c1, c2 = st.columns(2)
            with c1:
                verified_product = st.text_input("Product / Item Name", value=product_name)
                inv_date = st.text_input("Invoice Date (YYYY-MM-DD)", value=extracted.get("date", ""))
                selected_category = st.selectbox("Category (Auto-classified)", ALLOWED_CATEGORIES, index=category_index)
            with c2:
                quantity = st.number_input("Quantity", value=float(extracted.get("quantity", 1.0)), min_value=1.0, step=1.0)
                amount = st.number_input("Total Amount (₹)", value=float(extracted.get("amount", 0.0)), min_value=0.0, step=10.0)

            factor_info = get_emission_factor(selected_category, method="spend-based")
            if factor_info:
                st.caption(f"ℹ️ **Factor preview**: {factor_info['factor_value']} {factor_info['factor_unit']} | Source: {factor_info['source']} ({factor_info['version']})")

            submitted = st.form_submit_button("🛒 Calculate Carbon Footprint", use_container_width=True, type="primary")

        if submitted:
            if amount <= 0:
                st.warning("⚠️ Total amount must be greater than ₹0 to calculate footprint.")
                return

            with st.spinner("Calculating footprint..."):
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
            st.markdown("### 📊 Emission Result")

            res_col1, res_col2 = st.columns([2, 1])
            with res_col1:
                st.metric("Estimated CO₂e Emission", f"{calc_res['result_co2e']:.2f} kg CO₂e")
                st.markdown(f"**Calculation Formula**: `₹{amount} × {calc_res['factor_value']} {calc_res['factor_unit']}` = **{calc_res['result_co2e']:.2f} kg CO₂e**")
            with res_col2:
                st.info(f"**Method**: {calc_res['method']}\n\n**Source**: {calc_res['source']}\n\n**Version**: {calc_res['version']}")

            with st.expander("📖 View Raw Extracted Text"):
                st.code(extracted.get("raw_text", "No text extracted"))
