import streamlit as st
import pandas as pd
from database.db import get_all_calculations, get_calculation_by_id, get_extracted_items


def render_history():
    st.markdown("## 📜 Calculation & Document History")
    st.markdown("Complete repository of all processed documents, extracted values, and verified calculation records.")

    df = get_all_calculations()

    if df.empty:
        st.info("ℹ️ No calculation history recorded yet. Upload a document or run Demo Data on the Overview page.")
        return

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')

    # Filter Section
    with st.expander("🔍 Filter & Search Options", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            categories = ["All"] + sorted(list(df['category'].dropna().unique()))
            selected_cat = st.selectbox("Filter by Category", categories)
        with col2:
            doc_types = ["All"] + sorted(list(df['document_type'].dropna().unique()))
            selected_doc_type = st.selectbox("Filter by Document Type", doc_types)
        with col3:
            methods = ["All"] + sorted(list(df['method'].dropna().unique()))
            selected_method = st.selectbox("Filter by Method", methods)
        with col4:
            search_kw = st.text_input("Search Source / Vendor / Keyword", value="")

    # Apply Filters
    filtered_df = df.copy()

    if selected_cat != "All":
        filtered_df = filtered_df[filtered_df['category'] == selected_cat]
    if selected_doc_type != "All":
        filtered_df = filtered_df[filtered_df['document_type'] == selected_doc_type]
    if selected_method != "All":
        filtered_df = filtered_df[filtered_df['method'] == selected_method]
    if search_kw.strip():
        kw = search_kw.lower().strip()
        filtered_df = filtered_df[
            filtered_df['category'].str.lower().str.contains(kw, na=False) |
            filtered_df['source'].str.lower().str.contains(kw, na=False) |
            filtered_df['filename'].str.lower().str.contains(kw, na=False)
        ]

    st.markdown(f"Showing **{len(filtered_df)}** of **{len(df)}** calculation records:")

    if filtered_df.empty:
        st.warning("No records match the selected filter criteria.")
        return

    # Display Table with Status Badges
    display_rows = []
    for _, row in filtered_df.iterrows():
        status_badge = "VERIFIED" if row['method'] == 'activity-based' else "ESTIMATED"
        doc_type_label = "Electricity Bill" if row['document_type'] == "electricity_bill" else "Shopping Invoice"
        filename_label = row['filename'] if pd.notnull(row['filename']) else doc_type_label

        display_rows.append({
            "ID": f"CALC-{row['id']:05d}",
            "Date": row['date_str'],
            "Document": filename_label,
            "Document Type": doc_type_label,
            "Category": row['category'],
            "Activity Input": f"{row['activity_value']} {row['activity_unit']}",
            "Method": row['method'].title(),
            "Factor Value": f"{row['factor_value']} {row.get('factor_unit', '')}",
            "CO₂e (kg)": f"{row['result_co2e']:.2f}",
            "Status": status_badge,
            "raw_id": row['id']
        })

    display_df = pd.DataFrame(display_rows)
    st.dataframe(
        display_df.drop(columns=["raw_id"]),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.markdown("### 🔍 Record Inspector")

    calc_options = {f"{row['ID']} — {row['Category']} ({row['CO₂e (kg)']} kg CO₂e on {row['Date']})": row['raw_id'] for _, row in display_df.iterrows()}

    if calc_options:
        selected_key = st.selectbox("Select calculation record to inspect full audit details:", list(calc_options.keys()))
        target_id = calc_options[selected_key]
        calc_detail = get_calculation_by_id(target_id)

        if calc_detail:
            st.info(f"📋 **Calculation Record Details — CALC-{calc_detail['id']:05d}**")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Document**: `{calc_detail.get('filename', 'N/A')}`")
                st.markdown(f"**Document Type**: `{calc_detail.get('document_type', 'N/A')}`")
                st.markdown(f"**Transaction Date**: {calc_detail['date']}")
            with c2:
                st.markdown(f"**Category**: `{calc_detail['category']}`")
                st.markdown(f"**Activity Input**: {calc_detail['activity_value']} {calc_detail['activity_unit']}")
                st.markdown(f"**Method**: `{calc_detail['method']}`")
            with c3:
                st.markdown(f"**Factor Value**: {calc_detail['factor_value']} {calc_detail.get('factor_unit', '')}")
                st.markdown(f"**Result**: **{calc_detail['result_co2e']:.4f} kg CO₂e**")
                st.markdown(f"**Cited Source**: {calc_detail['source']} ({calc_detail['version']})")

            # Show Extracted Key-Values if available
            if calc_detail.get('document_id'):
                extracted_items = get_extracted_items(calc_detail['document_id'])
                if extracted_items:
                    with st.expander("📝 Extracted OCR Fields & Verification", expanded=False):
                        st.json(extracted_items)

            # Raw OCR text if present
            if calc_detail.get('raw_text'):
                with st.expander("📄 Raw Document Text", expanded=False):
                    st.code(calc_detail['raw_text'])
