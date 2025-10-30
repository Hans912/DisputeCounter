
import os
import pyodbc
import streamlit as st
from dotenv import load_dotenv

def handle_sql_variant(value):
    return str(value) if value is not None else None
    
@st.cache_resource
def get_db_connection():
    load_dotenv()

    # Prefer nested Streamlit Cloud secrets: st.secrets["azure_sql"]
    s = st.secrets.get("azure_sql")
    if s:
        server = s.get("server")
        database = s.get("database")
        username = s.get("username")
        password = s.get("password")
    else:
        # Fallback to flat secrets or local .env
        server = st.secrets.get("DB_SERVER", os.getenv("DB_SERVER"))
        database = st.secrets.get("DB_DATABASE", os.getenv("DB_DATABASE"))
        username = st.secrets.get("DB_USERNAME", os.getenv("DB_USERNAME"))
        password = st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD"))

    if not all([server, database, username, password]):
        raise RuntimeError("Missing DB secrets. Provide azure_sql.server/database/username/password.")

    base = (
        f"SERVER=tcp:{server},1433;"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "MARS_Connection=Yes;"
        "Connection Timeout=30;"
    )

    last_err = None
    for driver in ["ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server"]:
        try:
            conn = pyodbc.connect(f"DRIVER={{{driver}}};{base}")
            conn.autocommit = True
            conn.add_output_converter(-150, handle_sql_variant)
            conn.add_output_converter(-155, handle_sql_variant)
            # Connectivity probe to surface firewall/auth issues
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            return conn
        except pyodbc.Error as e:
            last_err = e

    raise RuntimeError(f"ODBC connect failed for both drivers: {last_err}")