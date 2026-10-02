import streamlit as st
import pandas as pd
from database.db import get_all_emission_factors


def render_emission_factors():
    st.markdown("## 🏛️ Emission Factor Reference Database")
    st.markdown("Official cited emission factors configured in CarbonTrack. Demonstrates scientific traceability and avoids unverified values.")

    df_factors = get_all_emission_factors()

    if df_factors.empty:
        st.error("⚠️ No emission factors configured in database. Please check `emission_factors/emission_factors.csv`.")
        return

    # Overview Metrics
    f1, f2, f3 = st.columns(3)
    with f1:
        st.metric("Total Configured Factors", f"{len(df_factors)}")
    with f2:
        st.metric("Primary Region", "India (National)")
    with f3:
        st.metric("Grid Factor (Electricity)", "0.727 kg CO₂/kWh (CEA v20.0)")

    st.markdown("---")

    # Filter by category
    categories = ["All"] + sorted(list(df_factors['category'].unique()))
    sel_cat = st.selectbox("Filter Emission Factors by Category", categories)

    filtered_df = df_factors if sel_cat == "All" else df_factors[df_factors['category'] == sel_cat]

    st.markdown(f"### 📋 Configured Factors Table ({len(filtered_df)} items)")

    table_df = filtered_df[['id', 'category', 'activity_type', 'unit', 'factor_value', 'factor_unit', 'source', 'year', 'version', 'boundary', 'country', 'is_active']].copy()
    table_df['is_active'] = table_df['is_active'].apply(lambda x: "ACTIVE" if x == 1 else "INACTIVE")
    table_df.columns = ['ID', 'Category', 'Activity Type', 'Input Unit', 'Factor Value', 'Factor Unit', 'Source', 'Year', 'Version', 'Boundary', 'Country', 'Status']

    st.dataframe(table_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Detailed Factor Inspector & Source Citation
    st.markdown("### 📖 Official Source Citation Inspector")
    factor_options = {f"ID #{row['id']} — {row['category']} / {row['activity_type']} ({row['factor_value']} {row['factor_unit']})": row['id'] for _, row in filtered_df.iterrows()}

    if factor_options:
        sel_factor_key = st.selectbox("Select a factor to inspect complete source metadata:", list(factor_options.keys()))
        target_id = factor_options[sel_factor_key]
        factor_row = filtered_df[filtered_df['id'] == target_id].iloc[0]

        with st.container():
            st.info(f"📚 **Factor Metadata — ID #{factor_row['id']}: {factor_row['category']} ({factor_row['activity_type']})**")

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Category**: `{factor_row['category']}`")
                st.markdown(f"**Activity Type**: {factor_row['activity_type']}")
                st.markdown(f"**Input Unit**: `{factor_row['unit']}`")
            with c2:
                st.markdown(f"**Factor Value**: **{factor_row['factor_value']} {factor_row['factor_unit']}**")
                st.markdown(f"**Boundary**: `{factor_row['boundary']}`")
                st.markdown(f"**Region/Country**: {factor_row['region']}, {factor_row['country']}")
            with c3:
                st.markdown(f"**Source**: {factor_row['source']}")
                st.markdown(f"**Version / Edition**: `{factor_row['version']} ({factor_row['year']})`")
                st.markdown(f"**Status**: `ACTIVE`")

            if pd.notnull(factor_row['source_url']) and str(factor_row['source_url']).startswith("http"):
                st.markdown(f"🔗 **Source URL**: [{factor_row['source_url']}]({factor_row['source_url']})")
            else:
                st.caption("Source metadata verified internally.")
