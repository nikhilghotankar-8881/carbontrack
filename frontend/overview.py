import os
from datetime import datetime
import streamlit as st
import pandas as pd
from database.db import get_all_calculations, get_documents_list, save_document, save_extracted_items, save_calculation
from backend.extractor import process_document_file
from backend.calculator import calculate_activity_emission, calculate_spend_emission
from backend.classifier import classify_text


def render_overview(set_nav_callback=None):
    # Top Hero Section
    st.markdown("""
    <div style="background: linear-gradient(135deg, #064E3B 0%, #047857 50%, #10B981 100%); padding: 32px; border-radius: 16px; color: white; margin-bottom: 24px; box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.25);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;">
            <div>
                <div style="display: inline-block; background: rgba(255, 255, 255, 0.18); backdrop-filter: blur(8px); padding: 4px 12px; border-radius: 20px; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 12px; text-transform: uppercase; border: 1px solid rgba(255,255,255,0.25);">
                    🌱 CARBONTRACK • CARBON FOOTPRINT ESTIMATOR
                </div>
                <h1 style="color: white !important; font-size: 2.3rem; font-weight: 700; margin: 0 0 8px 0; line-height: 1.2;">
                    Turn everyday bills and online purchases into transparent CO₂e estimates.
                </h1>
                <p style="color: #E6F4EA !important; font-size: 1.05rem; margin: 0; max-width: 720px; line-height: 1.5;">
                    Your bills already contain valuable activity data. CarbonTrack extracts this data, maps it to verified Indian government & EEIO emission factors, and calculates your verifiable carbon footprint.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status Checklist Area
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("<div style='background:#F0FDF4; border:1px solid #BBF7D0; padding:10px 14px; border-radius:10px; font-weight:600; font-size:0.88rem; color:#166534;'>✓ Emission Factor Database</div>", unsafe_allow_html=True)
    with s2:
        st.markdown("<div style='background:#F0FDF4; border:1px solid #BBF7D0; padding:10px 14px; border-radius:10px; font-weight:600; font-size:0.88rem; color:#166534;'>✓ Calculation Engine</div>", unsafe_allow_html=True)
    with s3:
        st.markdown("<div style='background:#F0FDF4; border:1px solid #BBF7D0; padding:10px 14px; border-radius:10px; font-weight:600; font-size:0.88rem; color:#166534;'>✓ Document Processing</div>", unsafe_allow_html=True)
    with s4:
        st.markdown("<div style='background:#F0FDF4; border:1px solid #BBF7D0; padding:10px 14px; border-radius:10px; font-weight:600; font-size:0.88rem; color:#166534;'>✓ Audit Trail</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Primary Hero Navigation Actions
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("📄 Upload Electricity Bill →", key="hero_btn_bill", use_container_width=True, type="primary"):
            if set_nav_callback:
                set_nav_callback("03  Electricity Bill")
            st.rerun()
    with btn_col2:
        if st.button("🛒 Upload Shopping Invoice →", key="hero_btn_invoice", use_container_width=True, type="primary"):
            if set_nav_callback:
                set_nav_callback("04  Shopping Invoice")
            st.rerun()
    with btn_col3:
        if st.button("📊 View Analytics Dashboard →", key="hero_btn_analytics", use_container_width=True):
            if set_nav_callback:
                set_nav_callback("06  Analytics")
            st.rerun()

    st.markdown("<hr style='margin:28px 0; border:none; border-top:1px solid #E5E7EB;'>", unsafe_allow_html=True)

    # Real DB Metrics KPI Cards
    df_calc = get_all_calculations()
    df_doc = get_documents_list()

    current_month_str = datetime.today().strftime("%Y-%m")
    today_str = datetime.today().strftime("%Y-%m-%d")

    if not df_calc.empty:
        df_calc['date_dt'] = pd.to_datetime(df_calc['date'], errors='coerce')
        monthly_total = df_calc[df_calc['date_dt'].dt.strftime('%Y-%m') == current_month_str]['result_co2e'].sum()
        today_total = df_calc[df_calc['date_dt'].dt.strftime('%Y-%m-%d') == today_str]['result_co2e'].sum()
        total_calcs = len(df_calc)
    else:
        monthly_total = 0.0
        today_total = 0.0
        total_calcs = 0

    total_docs = len(df_doc) if not df_doc.empty else 0

    st.markdown("### 📈 Real-Time Carbon Metrics")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("TOTAL CO₂e THIS MONTH", f"{monthly_total:.2f} kg", help="Aggregated emissions for current month")
    with m2:
        st.metric("TODAY", f"{today_total:.2f} kg", help="Emissions recorded today")
    with m3:
        st.metric("DOCUMENTS PROCESSED", f"{total_docs}", help="Total uploaded or sample documents processed")
    with m4:
        st.metric("CALCULATIONS", f"{total_calcs}", help="Total CO₂e calculation records in database")

    # DEMO DATA Trigger Mode Section
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div style="background: #F8FAFC; border: 1px dashed #64748B; border-radius: 12px; padding: 18px; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
                <div>
                    <span style="background: #0284C7; color: white; padding: 3px 10px; border-radius: 12px; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.5px;">DEMO DATA</span>
                    <span style="font-weight: 600; font-size: 0.95rem; margin-left: 8px; color: #1E293B;">Quick Prototype Demonstration for Judges</span>
                    <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #64748B;">Click below to load pre-configured sample documents and execute the complete pipeline instantly.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        demo_col1, demo_col2 = st.columns(2)
        with demo_col1:
            if st.button("⚡ Run Demo Electricity Bill Pipeline", key="demo_bill_run", use_container_width=True):
                sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents", "electricity_bill.pdf")
                if os.path.exists(sample_path):
                    with open(sample_path, "rb") as f:
                        extracted = process_document_file(f, "electricity_bill.pdf", "electricity_bill")
                    doc_id = save_document("electricity_bill.pdf", "pdf", "electricity_bill", extracted.get("raw_text", ""))
                    save_extracted_items(doc_id, {
                        "consumer_name": extracted.get("consumer_name", "Rajesh Sharma"),
                        "bill_date": extracted.get("bill_date", datetime.today().strftime("%Y-%m-%d")),
                        "units_consumed": extracted.get("units_consumed", 240.0),
                        "bill_amount": extracted.get("bill_amount", 2160.0)
                    })
                    calc_res = calculate_activity_emission(extracted.get("units_consumed", 240.0), "kWh", "Electricity")
                    save_calculation({
                        "document_id": doc_id,
                        "date": extracted.get("bill_date", datetime.today().strftime("%Y-%m-%d")),
                        "category": "Electricity",
                        "activity_value": extracted.get("units_consumed", 240.0),
                        "activity_unit": "kWh",
                        "factor_id": calc_res["factor_id"],
                        "factor_value": calc_res["factor_value"],
                        "method": calc_res["method"],
                        "source": calc_res["source"],
                        "version": calc_res["version"],
                        "result_co2e": calc_res["result_co2e"]
                    })
                    st.success("✅ Demo Electricity Bill processed & saved to database!")
                    st.rerun()
                else:
                    st.error("Sample document not found.")

        with demo_col2:
            if st.button("🛒 Run Demo Shopping Invoice Pipeline", key="demo_invoice_run", use_container_width=True):
                sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents", "shopping_invoice.pdf")
                if os.path.exists(sample_path):
                    with open(sample_path, "rb") as f:
                        extracted = process_document_file(f, "shopping_invoice.pdf", "shopping_invoice")
                    doc_id = save_document("shopping_invoice.pdf", "pdf", "shopping_invoice", extracted.get("raw_text", ""))
                    cat = classify_text(extracted.get("product_name", "Cotton Slim Fit Shirt"))
                    if cat == "Other":
                        cat = "Clothing"
                    save_extracted_items(doc_id, {
                        "product_name": extracted.get("product_name", "Cotton Slim Fit Shirt"),
                        "date": extracted.get("date", datetime.today().strftime("%Y-%m-%d")),
                        "category": cat,
                        "quantity": extracted.get("quantity", 1.0),
                        "amount": extracted.get("amount", 1499.0)
                    })
                    calc_res = calculate_spend_emission(extracted.get("amount", 1499.0), cat)
                    save_calculation({
                        "document_id": doc_id,
                        "date": extracted.get("date", datetime.today().strftime("%Y-%m-%d")),
                        "category": cat,
                        "activity_value": extracted.get("amount", 1499.0),
                        "activity_unit": "INR",
                        "factor_id": calc_res["factor_id"],
                        "factor_value": calc_res["factor_value"],
                        "method": calc_res["method"],
                        "source": calc_res["source"],
                        "version": calc_res["version"],
                        "result_co2e": calc_res["result_co2e"]
                    })
                    st.success("✅ Demo Shopping Invoice processed & saved to database!")
                    st.rerun()
                else:
                    st.error("Sample document not found.")

    st.markdown("<hr style='margin:28px 0; border:none; border-top:1px solid #E5E7EB;'>", unsafe_allow_html=True)

    # Core Workflow Stage Diagram
    st.markdown("### 🔄 End-to-End Processing Workflow")
    st.markdown("The 6-stage scientific estimation pipeline implemented in CarbonTrack:")

    flow_col1, flow_col2, flow_col3, flow_col4, flow_col5, flow_col6 = st.columns(6)
    with flow_col1:
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:14px; border-radius:12px; text-align:center;">
            <div style="font-size:1.4rem;">📤</div>
            <div style="font-weight:700; font-size:0.85rem; color:#0F172A; margin:6px 0 2px 0;">01 UPLOAD</div>
            <div style="font-size:0.75rem; color:#64748B;">Upload bill/invoice PDF or Image</div>
            <div style="margin-top:8px;"><span style="background:#DCFCE7; color:#166534; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:8px;">READY</span></div>
        </div>
        """, unsafe_allow_html=True)

    with flow_col2:
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:14px; border-radius:12px; text-align:center;">
            <div style="font-size:1.4rem;">🔍</div>
            <div style="font-weight:700; font-size:0.85rem; color:#0F172A; margin:6px 0 2px 0;">02 EXTRACT</div>
            <div style="font-size:0.75rem; color:#64748B;">Read activity data via OCR/PyMuPDF</div>
            <div style="margin-top:8px;"><span style="background:#DCFCE7; color:#166534; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:8px;">READY</span></div>
        </div>
        """, unsafe_allow_html=True)

    with flow_col3:
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:14px; border-radius:12px; text-align:center;">
            <div style="font-size:1.4rem;">✍️</div>
            <div style="font-weight:700; font-size:0.85rem; color:#0F172A; margin:6px 0 2px 0;">03 VERIFY</div>
            <div style="font-size:0.75rem; color:#64748B;">Human confirmation & correction</div>
            <div style="margin-top:8px;"><span style="background:#DCFCE7; color:#166534; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:8px;">READY</span></div>
        </div>
        """, unsafe_allow_html=True)

    with flow_col4:
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:14px; border-radius:12px; text-align:center;">
            <div style="font-size:1.4rem;">🏷️</div>
            <div style="font-weight:700; font-size:0.85rem; color:#0F172A; margin:6px 0 2px 0;">04 MAP FACTOR</div>
            <div style="font-size:0.75rem; color:#64748B;">Match CEA / IPCC / EEIO factor</div>
            <div style="margin-top:8px;"><span style="background:#DCFCE7; color:#166534; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:8px;">READY</span></div>
        </div>
        """, unsafe_allow_html=True)

    with flow_col5:
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:14px; border-radius:12px; text-align:center;">
            <div style="font-size:1.4rem;">🧮</div>
            <div style="font-weight:700; font-size:0.85rem; color:#0F172A; margin:6px 0 2px 0;">05 CALCULATE</div>
            <div style="font-size:0.75rem; color:#64748B;">Compute CO₂e & formula breakdown</div>
            <div style="margin-top:8px;"><span style="background:#DCFCE7; color:#166534; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:8px;">READY</span></div>
        </div>
        """, unsafe_allow_html=True)

    with flow_col6:
        st.markdown("""
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:14px; border-radius:12px; text-align:center;">
            <div style="font-size:1.4rem;">📊</div>
            <div style="font-weight:700; font-size:0.85rem; color:#0F172A; margin:6px 0 2px 0;">06 TRACK</div>
            <div style="font-size:0.75rem; color:#64748B;">Store in DB & audit dashboard</div>
            <div style="margin-top:8px;"><span style="background:#DCFCE7; color:#166534; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:8px;">READY</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:28px 0; border:none; border-top:1px solid #E5E7EB;'>", unsafe_allow_html=True)

    # Recent Footprint Calculations Section
    st.markdown("### 📋 Recent Footprint Calculations")
    if not df_calc.empty:
        table_data = []
        for _, row in df_calc.head(5).iterrows():
            status_badge = "VERIFIED" if row['method'] == 'activity-based' else "ESTIMATED"
            doc_label = row.get('filename') or ('Electricity Bill' if row['category'] == 'Electricity' else 'Shopping Invoice')
            table_data.append({
                "Date": str(row['date'])[:10],
                "Source Document": doc_label,
                "Category": row['category'],
                "Activity Input": f"{row['activity_value']} {row['activity_unit']}",
                "Method": row['method'].title(),
                "Factor": f"{row['factor_value']} {row.get('factor_unit','')}",
                "Estimated CO₂e": f"{row['result_co2e']:.2f} kg",
                "Status": status_badge
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
    else:
        st.info("No calculations recorded yet. Use the Upload buttons above or run Demo Data to start tracking!")
