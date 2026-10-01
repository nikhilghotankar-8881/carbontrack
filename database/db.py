import os
import sqlite3
import pandas as pd

DB_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(DB_DIR, "carbon.db")
EMISSION_FACTORS_CSV = os.path.join(os.path.dirname(DB_DIR), "emission_factors", "emission_factors.csv")


def get_connection():
    """Returns a connection to the SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite schema for 5 tables and seeds default user and emission factors."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT DEFAULT 'Local User',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Seed default user if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name) VALUES ('Local User')")

    # 2. documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        document_type TEXT NOT NULL,
        upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        raw_text TEXT,
        status TEXT DEFAULT 'uploaded',
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # 3. extracted_items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS extracted_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        field_name TEXT NOT NULL,
        extracted_value TEXT,
        verified_value TEXT,
        confidence REAL,
        FOREIGN KEY (document_id) REFERENCES documents(id)
    )
    """)

    # 4. emission_factors table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emission_factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        activity_type TEXT NOT NULL,
        unit TEXT NOT NULL,
        factor_value REAL NOT NULL,
        factor_unit TEXT NOT NULL,
        country TEXT NOT NULL,
        region TEXT NOT NULL,
        source TEXT NOT NULL,
        source_url TEXT,
        year INTEGER NOT NULL,
        version TEXT NOT NULL,
        boundary TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """)

    # 5. calculations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        document_id INTEGER,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        activity_value REAL NOT NULL,
        activity_unit TEXT NOT NULL,
        factor_id INTEGER,
        factor_value REAL NOT NULL,
        method TEXT NOT NULL,
        source TEXT NOT NULL,
        version TEXT NOT NULL,
        result_co2e REAL NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (document_id) REFERENCES documents(id),
        FOREIGN KEY (factor_id) REFERENCES emission_factors(id)
    )
    """)

    conn.commit()

    # Seed emission factors if empty
    cursor.execute("SELECT COUNT(*) FROM emission_factors")
    if cursor.fetchone()[0] == 0 and os.path.exists(EMISSION_FACTORS_CSV):
        df = pd.read_csv(EMISSION_FACTORS_CSV)
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
        df.to_sql('emission_factors', conn, if_exists='append', index=False)
        conn.commit()

    conn.close()


def get_all_emission_factors():
    """Retrieves all active emission factors as a DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM emission_factors WHERE is_active = 1", conn)
    conn.close()
    return df


def get_emission_factor(category, method=None, unit=None, activity=None):
    """
    Looks up specific active emission factor row matching category and method (or unit).
    Method can be 'activity-based' or 'spend-based'.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if activity:
        cursor.execute("""
            SELECT * FROM emission_factors 
            WHERE category = ? AND LOWER(activity_type) LIKE ? AND is_active = 1
            LIMIT 1
        """, (category, f"%{activity.lower()}%"))
        row = cursor.fetchone()
        if row:
            conn.close()
            return dict(row)

    if unit:
        cursor.execute("""
            SELECT * FROM emission_factors 
            WHERE category = ? AND unit = ? AND is_active = 1
            LIMIT 1
        """, (category, unit))
        row = cursor.fetchone()
        if row:
            conn.close()
            return dict(row)

    if method == "activity-based":
        cursor.execute("""
            SELECT * FROM emission_factors 
            WHERE category = ? AND unit != 'INR' AND is_active = 1
            LIMIT 1
        """, (category,))
    else:
        cursor.execute("""
            SELECT * FROM emission_factors 
            WHERE category = ? AND unit = 'INR' AND is_active = 1
            LIMIT 1
        """, (category,))

    row = cursor.fetchone()

    # Fallback to category 'Other' spend-based factor if category not found
    if not row and method == "spend-based":
        cursor.execute("""
            SELECT * FROM emission_factors 
            WHERE category = 'Other' AND unit = 'INR' AND is_active = 1
            LIMIT 1
        """)
        row = cursor.fetchone()

    conn.close()
    return dict(row) if row else None


def save_document(filename, file_type, document_type, raw_text=""):
    """Inserts a new document record and returns its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO documents (user_id, filename, file_type, document_type, raw_text, status)
        VALUES (1, ?, ?, ?, ?, 'uploaded')
    """, (filename, file_type, document_type, raw_text))
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return doc_id


def update_document_status(doc_id, status):
    """Updates document processing status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET status = ? WHERE id = ?", (status, doc_id))
    conn.commit()
    conn.close()


def save_extracted_items(document_id, items_dict, confidence=1.0):
    """Saves key-value field extractions for a document."""
    conn = get_connection()
    cursor = conn.cursor()
    # Remove old extractions for this document if re-running
    cursor.execute("DELETE FROM extracted_items WHERE document_id = ?", (document_id,))
    for field_name, value in items_dict.items():
        val_str = str(value) if value is not None else ""
        cursor.execute("""
            INSERT INTO extracted_items (document_id, field_name, extracted_value, verified_value, confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (document_id, field_name, val_str, val_str, confidence))
    conn.commit()
    conn.close()


def update_verified_items(document_id, verified_dict):
    """Updates verified values for extracted items."""
    conn = get_connection()
    cursor = conn.cursor()
    for field_name, verified_val in verified_dict.items():
        cursor.execute("""
            UPDATE extracted_items 
            SET verified_value = ?
            WHERE document_id = ? AND field_name = ?
        """, (str(verified_val), document_id, field_name))
    conn.commit()
    conn.close()


def save_calculation(calc_dict):
    """Saves a calculation result dictionary into the calculations table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO calculations (
            user_id, document_id, date, category, activity_value, activity_unit,
            factor_id, factor_value, method, source, version, result_co2e
        )
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        calc_dict.get('document_id'),
        calc_dict.get('date'),
        calc_dict.get('category'),
        calc_dict.get('activity_value', 0.0),
        calc_dict.get('activity_unit', ''),
        calc_dict.get('factor_id'),
        calc_dict.get('factor_value', 0.0),
        calc_dict.get('method', ''),
        calc_dict.get('source', ''),
        calc_dict.get('version', ''),
        calc_dict.get('result_co2e', 0.0)
    ))
    conn.commit()
    calc_id = cursor.lastrowid
    conn.close()

    if calc_dict.get('document_id'):
        update_document_status(calc_dict['document_id'], 'calculated')

    return calc_id


def get_all_calculations():
    """Retrieves all calculations ordered by date DESC."""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT c.*, ef.factor_unit, ef.source_url
        FROM calculations c
        LEFT JOIN emission_factors ef ON c.factor_id = ef.id
        ORDER BY c.date DESC, c.id DESC
    """, conn)
    conn.close()
    return df


def get_calculation_by_id(calc_id):
    """Retrieves a single calculation record by ID with emission factor metadata."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, ef.factor_unit, ef.source_url, ef.boundary, ef.country, ef.region, ef.activity_type
        FROM calculations c
        LEFT JOIN emission_factors ef ON c.factor_id = ef.id
        WHERE c.id = ?
    """, (calc_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
