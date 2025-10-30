
import os
import pyodbc
import streamlit as st
from dotenv import load_dotenv

def handle_sql_variant(value):
    return str(value) if value is not None else None

@st.cache_resource
def get_db_connection():
    load_dotenv()
    server = st.secrets.get("DB_SERVER", os.getenv("DB_SERVER"))
    database = st.secrets.get("DB_DATABASE", os.getenv("DB_DATABASE"))
    username = st.secrets.get("DB_USERNAME", os.getenv("DB_USERNAME"))
    password = st.secrets.get("DB_PASSWORD", os.getenv("DB_PASSWORD"))

    if not all([server, database, username, password]):
        raise RuntimeError("Missing DB secrets. Check DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD.")

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER=tcp:{server},1433;"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "MARS_Connection=Yes;"
        "Connection Timeout=30;"
    )
    try:
        conn = pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        raise RuntimeError(f"ODBC connect failed: {e}")

    # Register converters to avoid -150/-155 type errors
    conn.add_output_converter(-150, handle_sql_variant)
    conn.add_output_converter(-155, handle_sql_variant)

    # Connectivity probe to surface firewall/permissions issues early
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
    except Exception as e:
        raise RuntimeError(f"DB probe failed after connect: {e}")

    return conn