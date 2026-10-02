import streamlit as st
import pandas as pd
from database.db import get_all_calculations, get_calculation_by_id, get_extracted_items


def render_audit():
    st.markdown("## 🔬 Scientific Calculation Audit Trail")
    st.markdown("Dedicated transparency ledger for hackathon judges to trace every calculation step back to raw activity inputs and cited emission factors.")

    df = get_all_calculations()

    if df.empty:
        st.info("ℹ️ No calculation audit records available. Process a document or run Demo Data to populate the ledger.")
        return

    # Key Ledger Stats
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.metric("Audit Ledger Records", f"{len(df)}")
    with a2:
        activity_cnt = len(df[df['method'] == 'activity-based'])
        st.metric("Activity-Based Audits", f"{activity_cnt}")
    with a3:
        spend_cnt = len(df[df['method'] == 'spend-based'])
        st.metric("Spend-Based Audits", f"{spend_cnt}")
    with a4:
        st.metric("Audited CO₂e Total", f"{df['result_co2e'].sum():.2f} kg")

    st.markdown("---")

    st.markdown("### 📜 Audit Ledger Table")
    audit_table = []
    for _, row in df.iterrows():
        calc_id_str = f"CALC-{row['id']:05d}"
        doc_str = row['filename'] if pd.notnull(row['filename']) else ("Electricity Bill" if row['category'] == "Electricity" else "Shopping Invoice")
        status_str = "VERIFIED" if row['method'] == "activity-based" else "ESTIMATED"
        formula_str = f"{row['activity_value']} {row['activity_unit']} × {row['factor_value']} {row.get('factor_unit','')}"

        audit_table.append({
            "Calculation ID": calc_id_str,
            "Date": str(row['date'])[:10],
            "Input Document": doc_str,
            "Activity Input": f"{row['activity_value']} {row['activity_unit']}",
            "Category": row['category'],
            "Emission Factor": f"{row['factor_value']} {row.get('factor_unit','')}",
            "Source": row['source'],
            "Version": row['version'],
            "Method": row['method'].title(),
            "Formula": formula_str,
            "CO₂e (kg)": f"{row['result_co2e']:.4f}",
            "Status": status_str,
            "raw_id": row['id']
        })

    audit_df = pd.DataFrame(audit_table)
    st.dataframe(
        audit_df.drop(columns=["raw_id"]),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # Deep Audit Inspector Card
    st.markdown("### 🔬 Judge Audit Inspector")
    calc_options = {f"{row['Calculation ID']} — {row['Category']} ({row['CO₂e (kg)']} kg CO₂e)": row['raw_id'] for _, row in audit_df.iterrows()}

    if calc_options:
        sel_key = st.selectbox("Select Calculation ID to inspect complete scientific breakdown:", list(calc_options.keys()))
        target_id = calc_options[sel_key]
        calc = get_calculation_by_id(target_id)

        if calc:
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 2px solid #10B981; border-radius: 12px; padding: 20px; margin-top: 10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <h3 style="margin:0; color:#064E3B;">CALCULATION AUDIT TRACE: CALC-{calc['id']:05d}</h3>
                    <span style="background:#10B981; color:white; padding:4px 12px; border-radius:12px; font-weight:700; font-size:0.8rem;">{calc['method'].upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 1. Input & Document Metadata")
                st.markdown(f"- **Document File**: `{calc.get('filename', 'N/A')}`")
                st.markdown(f"- **Document Type**: `{calc.get('document_type', 'N/A')}`")
                st.markdown(f"- **Transaction Date**: {calc['date']}")
                st.markdown(f"- **Extracted Activity**: `{calc['activity_value']} {calc['activity_unit']}`")
                st.markdown(f"- **Assigned Category**: `{calc['category']}`")

            with c2:
                st.markdown("#### 2. Cited Emission Factor Metadata")
                st.markdown(f"- **Emission Factor ID**: `EF-{calc['factor_id']:03d}`")
                st.markdown(f"- **Factor Value**: `{calc['factor_value']} {calc.get('factor_unit','')}`")
                st.markdown(f"- **Cited Source**: {calc['source']}")
                st.markdown(f"- **Source Version**: `{calc['version']}`")
                st.markdown(f"- **System Boundary**: `{calc.get('boundary','Scope 2')}`")
                st.markdown(f"- **Geographic Scope**: {calc.get('region','National')}, {calc.get('country','India')}")

            st.markdown("#### 3. Mathematical Formula & Step Execution")
            if calc['method'] == 'activity-based':
                st.code(f"""
INPUT ACTIVITY QUANTITY  = {calc['activity_value']} {calc['activity_unit']}
EMISSION FACTOR          = {calc['factor_value']} {calc.get('factor_unit','')}
CITED SOURCE             = {calc['source']} ({calc['version']})

FORMULA:
  Result CO₂e (kg) = Input Quantity ({calc['activity_value']}) × Factor ({calc['factor_value']})
                   = {calc['activity_value']} × {calc['factor_value']}
                   = {calc['result_co2e']:.4f} kg CO₂e
                """)
            else:
                st.code(f"""
INPUT SPEND AMOUNT       = ₹{calc['activity_value']}
EEIO SPEND FACTOR        = {calc['factor_value']} {calc.get('factor_unit','')}
CITED SOURCE             = {calc['source']} ({calc['version']})

FORMULA:
  Result CO₂e (kg) = Spend Amount (₹{calc['activity_value']}) × EEIO Factor ({calc['factor_value']})
                   = ₹{calc['activity_value']} × {calc['factor_value']}
                   = {calc['result_co2e']:.4f} kg CO₂e
                """)

            if calc.get('source_url'):
                st.markdown(f"🔗 **Government / Official Source Link**: [{calc['source_url']}]({calc['source_url']})")
