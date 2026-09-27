import os
import sqlite3
import pandas as pd

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
DB_PATH = os.path.join(DB_DIR, "carbon.db")
EMISSION_FACTORS_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "emission_factors.csv")

def get_connection():
    """Returns a connection to the SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes SQLite schema and seeds emission factors from CSV if table is empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create emission_factors table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emission_factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        activity TEXT NOT NULL,
        unit TEXT NOT NULL,
        factor REAL NOT NULL,
        method TEXT NOT NULL,
        source TEXT NOT NULL,
        source_year INTEGER NOT NULL,
        region TEXT NOT NULL
    )
    """)

    # Create transactions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        vendor TEXT NOT NULL,
        item TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        quantity REAL,
        unit TEXT,
        co2e REAL NOT NULL,
        calculation_method TEXT NOT NULL,
        source_type TEXT NOT NULL
    )
    """)

    conn.commit()

    # Check if emission_factors table is empty and seed it
    cursor.execute("SELECT COUNT(*) FROM emission_factors")
    count = cursor.fetchone()[0]
    if count == 0 and os.path.exists(EMISSION_FACTORS_CSV):
        df = pd.read_csv(EMISSION_FACTORS_CSV)
        # Drop id if present so SQLite handles AUTOINCREMENT cleanly
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
        df.to_sql('emission_factors', conn, if_exists='append', index=False)
        conn.commit()

    conn.close()

def get_all_emission_factors():
    """Retrieves all emission factors as a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM emission_factors", conn)
    conn.close()
    return df

def get_emission_factor(category, method, activity=None):
    """
    Looks up specific emission factor row matching category and method.
    If activity is provided, tries exact/substring match on activity first.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if activity:
        cursor.execute("""
            SELECT * FROM emission_factors 
            WHERE category = ? AND method = ? AND LOWER(activity) LIKE ?
            LIMIT 1
        """, (category, method, f"%{activity.lower()}%"))
        row = cursor.fetchone()
        if row:
            conn.close()
            return dict(row)
            
    cursor.execute("""
        SELECT * FROM emission_factors 
        WHERE category = ? AND method = ? 
        LIMIT 1
    """, (category, method))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_transaction(transaction_dict):
    """Saves a transaction dictionary into SQLite transactions table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (date, vendor, item, category, amount, quantity, unit, co2e, calculation_method, source_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        transaction_dict.get('date'),
        transaction_dict.get('vendor', ''),
        transaction_dict.get('item', ''),
        transaction_dict.get('category'),
        transaction_dict.get('amount', 0.0),
        transaction_dict.get('quantity'),
        transaction_dict.get('unit'),
        transaction_dict.get('co2e'),
        transaction_dict.get('calculation_method'),
        transaction_dict.get('source_type')
    ))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_all_transactions():
    """Retrieves all transactions as a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC, id DESC", conn)
    conn.close()
    return df

def update_transaction(trans_id, transaction_dict):
    """Updates an existing transaction by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions 
        SET date=?, vendor=?, item=?, category=?, amount=?, quantity=?, unit=?, co2e=?, calculation_method=?, source_type=?
        WHERE id=?
    """, (
        transaction_dict.get('date'),
        transaction_dict.get('vendor', ''),
        transaction_dict.get('item', ''),
        transaction_dict.get('category'),
        transaction_dict.get('amount', 0.0),
        transaction_dict.get('quantity'),
        transaction_dict.get('unit'),
        transaction_dict.get('co2e'),
        transaction_dict.get('calculation_method'),
        transaction_dict.get('source_type'),
        trans_id
    ))
    conn.commit()
    conn.close()

def delete_transaction(trans_id):
    """Deletes a transaction by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
    conn.commit()
    conn.close()
