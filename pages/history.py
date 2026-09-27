import streamlit as st
import pandas as pd
from datetime import datetime
from modules.database import init_db, get_all_transactions, update_transaction, delete_transaction
from modules.calculator import calculate_activity_emission, calculate_spend_emission
from modules.ui_components import CATEGORY_ICONS

init_db()

st.set_page_config(page_title="Transaction History — CarbonTrack", page_icon="📜", layout="wide")

st.title("📜 Transaction History")
st.caption("View, edit, or delete logged carbon footprint transactions.")

# Fetch all transactions
df = get_all_transactions()

if df.empty:
    st.info("No transactions logged yet. Use the **Upload & Manual Entry** or **Purchases CSV** page to add records.")
else:
    # KPI summary bar
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Logged Transactions", len(df))
    col2.metric("Total CO₂e Footprint", f"{df['co2e'].sum():.2f} kg")
    col3.metric("Total Spend", f"₹{df['amount'].sum():.2f}")

    st.markdown("---")

    # Table displaying transactions
    for idx, row in df.iterrows():
        cat_icon = CATEGORY_ICONS.get(row['category'], "📦")
        method_badge = "🟢 Activity" if row['calculation_method'] == "activity-based" else "🟠 Spend"
        
        with st.expander(f"{cat_icon} {row['date']} | **{row['item']}** ({row['vendor']}) — {row['co2e']:.2f} kg CO₂e ({method_badge})"):
            c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
            
            with c1:
                st.write(f"**Date:** {row['date']}")
                st.write(f"**Category:** {row['category']}")
                st.write(f"**Vendor:** {row['vendor'] or 'N/A'}")
            
            with c2:
                st.write(f"**Amount:** ₹{row['amount']:.2f}")
                qty_str = f"{row['quantity']} {row['unit']}" if pd.notnull(row['quantity']) and row['quantity'] else "N/A"
                st.write(f"**Quantity:** {qty_str}")
                st.write(f"**Source Type:** {row['source_type'].title()}")

            with c3:
                st.metric("CO₂e Footprint", f"{row['co2e']:.4f} kg")
                st.caption(f"Method: {row['calculation_method']}")

            with c4:
                st.write("**Actions**")
                btn_edit = st.button("✏️ Edit", key=f"edit_{row['id']}")
                btn_delete = st.button("🗑️ Delete", key=f"del_{row['id']}", type="secondary")

            # Edit modal/container
            if btn_edit or st.session_state.get(f"editing_{row['id']}", False):
                st.session_state[f"editing_{row['id']}"] = True
                st.markdown("##### Edit Transaction Details")
                
                with st.form(key=f"edit_form_{row['id']}"):
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        try:
                            init_d = datetime.strptime(str(row['date']), "%Y-%m-%d")
                        except Exception:
                            init_d = datetime.today()
                        e_date = st.date_input("Date", value=init_d, key=f"e_date_{row['id']}")
                        e_cat = st.selectbox("Category", options=list(CATEGORY_ICONS.keys()), index=list(CATEGORY_ICONS.keys()).index(row['category']) if row['category'] in CATEGORY_ICONS else 0, key=f"e_cat_{row['id']}")
                        e_item = st.text_input("Item", value=str(row['item']), key=f"e_item_{row['id']}")
                        e_vendor = st.text_input("Vendor", value=str(row['vendor']), key=f"e_vendor_{row['id']}")

                    with e_col2:
                        e_amount = st.number_input("Amount (₹)", min_value=0.0, value=float(row['amount']), key=f"e_amt_{row['id']}")
                        e_qty = st.number_input("Physical Quantity (0 for none)", min_value=0.0, value=float(row['quantity']) if pd.notnull(row['quantity']) else 0.0, key=f"e_qty_{row['id']}")
                        e_unit = st.text_input("Unit", value=str(row['unit']) if pd.notnull(row['unit']) else "", key=f"e_unit_{row['id']}")

                    sub_update = st.form_submit_button("Save Changes")
                    if sub_update:
                        if e_qty > 0:
                            try:
                                res = calculate_activity_emission(e_qty, e_unit, e_cat, item=e_item)
                            except ValueError:
                                res = calculate_spend_emission(e_amount, e_cat)
                        else:
                            res = calculate_spend_emission(e_amount, e_cat)

                        updated_record = {
                            "date": e_date.strftime("%Y-%m-%d"),
                            "vendor": e_vendor,
                            "item": e_item,
                            "category": e_cat,
                            "amount": e_amount,
                            "quantity": e_qty if e_qty > 0 else None,
                            "unit": e_unit if e_unit else None,
                            "co2e": res["co2e"],
                            "calculation_method": res["calculation_method"],
                            "source_type": row["source_type"]
                        }
                        update_transaction(row['id'], updated_record)
                        st.session_state[f"editing_{row['id']}"] = False
                        st.success("✅ Transaction updated!")
                        st.rerun()

            # Delete confirmation
            if btn_delete:
                st.warning("⚠️ Are you sure you want to delete this transaction?")
                c_del1, c_del2 = st.columns(2)
                if c_del1.button("Yes, Delete", key=f"confirm_del_{row['id']}", type="primary"):
                    delete_transaction(row['id'])
                    st.success("Deleted!")
                    st.rerun()
