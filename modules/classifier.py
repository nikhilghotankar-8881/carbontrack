import os
import re
import pandas as pd

CATEGORY_RULES_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "category_rules.csv")

def load_category_rules():
    """Loads category keyword rules from CSV."""
    if not os.path.exists(CATEGORY_RULES_CSV):
        return []
    df = pd.read_csv(CATEGORY_RULES_CSV)
    rules = []
    for _, row in df.iterrows():
        kw = str(row['keyword']).strip().lower()
        cat = str(row['category']).strip()
        rules.append((kw, cat))
    return rules

def classify_text(text: str) -> str:
    """
    Classifies a product/item/vendor text fragment into one of 8 categories using keyword rules.
    Normalizes text (lowercase, strip extra spaces).
    Falls back to 'Other' if no rule matches.
    """
    if not text or pd.isnull(text):
        return "Other"

    # Normalize text
    normalized = re.sub(r'[^a-zA-Z0-9\s]', '', str(text)).lower().strip()
    
    rules = load_category_rules()
    for kw, category in rules:
        # Match as word or substring boundary
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, normalized) or kw in normalized:
            return category
            
    return "Other"

def classify_dataframe(df: pd.DataFrame, text_column: str = "product") -> pd.DataFrame:
    """
    Adds or updates 'category' column in a DataFrame using keyword classification.
    """
    df_copy = df.copy()
    if 'category' not in df_copy.columns or df_copy['category'].isnull().any():
        df_copy['category'] = df_copy[text_column].apply(classify_text)
    else:
        # Fill missing categories only
        df_copy['category'] = df_copy.apply(
            lambda r: r['category'] if pd.notnull(r['category']) and str(r['category']).strip() != '' else classify_text(r[text_column]),
            axis=1
        )
    return df_copy
