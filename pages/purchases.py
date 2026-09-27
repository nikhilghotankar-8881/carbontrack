import streamlit as st
import pandas as pd
from modules.styles import inject_custom_css, render_hero
from modules.database import init_db, save_transaction
from modules.validators import validate_csv_columns, validate_date, validate_amount
from modules.classifier import classify_text
from modules.calculator import calculate_spend_emission
from modules.ui_components import CATEGORY_ICONS

init_db()

st.set_page_config(page_title="Purchases CSV — CarbonTrack", page_icon="🛒", layout="wide")

# Inject Custom Styling
inject_custom_css()

render_hero(
    title="Online Purchase CSV Import",
    subtitle="Import order history CSVs from Amazon, Flipkart, BigBasket, etc., to estimate spend-based carbon emissions.",
    icon="🛒"
)

# Sample CSV download section
col_info, col_dl = st.columns([3, 1])

with col_info:
    st.markdown("""
    <div style="background: #ffffff; border-radius: 14px; padding: 18px 24px; border: 1px solid #e2e8f0;">
        <div style="font-weight: 700; color: #0f172a; font-size: 15px;">CSV Requirement</div>
        <div style="font-size: 13px; color: #64748b; margin-top: 4px;">
            Required columns: <code>date</code>, <code>vendor</code>, <code>product</code>, <code>amount</code>.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_dl:
    sample_csv = "date,vendor,product,amount\n2026-09-20,Amazon,Cotton T-Shirt,799\n2026-09-21,Flipkart,Wireless Earbuds,1499\n2026-09-22,BigBasket,Weekly Grocery,650\n2026-09-23,Uber,Cab Ride,450"
    st.download_button(
        label="📥 Sample Purchase CSV",
        data=sample_csv,
        file_name="sample_purchases.csv",
        mime="text/csv",
        use_container_width=True
    )

st.markdown("---")

uploaded_file = st.file_uploader("Upload Purchase CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file)
        valid, err_msg = validate_csv_columns(df_raw)
        
        if not valid:
            st.error(f"❌ Invalid CSV file format: {err_msg}")
        else:
            st.success(f"✅ CSV uploaded successfully! {len(df_raw)} records found.")
            
            df_norm = df_raw.copy()
            df_norm.columns = [c.strip().lower() for c in df_norm.columns]

            if 'category' not in df_norm.columns or df_norm['category'].isnull().all():
                df_norm['category'] = df_norm['product'].apply(classify_text)

            st.markdown("### 🔍 Preview & Verify Import Data")
            st.caption("Verify or edit assigned categories below before confirming import.")

            category_list = list(CATEGORY_ICONS.keys())
            
            edited_df = st.data_editor(
                df_norm[['date', 'vendor', 'product', 'amount', 'category']],
                column_config={
                    "date": st.column_config.TextColumn("Date (YYYY-MM-DD)", required=True),
                    "vendor": st.column_config.TextColumn("Vendor", required=True),
                    "product": st.column_config.TextColumn("Product / Item", required=True),
                    "amount": st.column_config.NumberColumn("Amount (₹)", min_value=0.0, format="₹%.2f", required=True),
                    "category": st.column_config.SelectboxColumn("Category", options=category_list, required=True)
                },
                use_container_width=True,
                num_rows="dynamic"
            )

            if st.button("🚀 Confirm & Process Import", type="primary", use_container_width=True):
                saved_count = 0
                total_co2e = 0.0

                for _, row in edited_df.iterrows():
                    d_valid, d_str = validate_date(str(row['date']))
                    a_valid, amt_val, _ = validate_amount(row['amount'])
                    
                    if not d_valid or not a_valid:
                        continue

                    cat = str(row['category']).strip()
                    if cat not in category_list:
                        cat = classify_text(str(row['product']))

                    res = calculate_spend_emission(amount=amt_val, category=cat)

                    tx_record = {
                        "date": d_str,
                        "vendor": str(row['vendor']).strip(),
                        "item": str(row['product']).strip(),
                        "category": cat,
                        "amount": amt_val,
                        "quantity": None,
                        "unit": None,
                        "co2e": res["co2e"],
                        "calculation_method": res["calculation_method"],
                        "source_type": "csv"
                    }

                    save_transaction(tx_record)
                    saved_count += 1
                    total_co2e += res["co2e"]

                st.success(f"🎉 Successfully imported {saved_count} transactions! Total added CO₂e: **{total_co2e:.4f} kg**")
                st.info("View all imported records in the **Transaction History** or **Dashboard** page.")

    except Exception as e:
        st.error(f"Error reading CSV file: {str(e)}")
