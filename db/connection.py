
import os
import pyodbc
import streamlit as st
from dotenv import load_dotenv

def handle_sql_variant(value):
    return str(value) if value is not None else None
    
@st.cache_resource
def get_db_connection():
    load_dotenv()
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER=tcp:{os.getenv('DB_SERVER')},1433;"
        f"DATABASE={os.getenv('DB_DATABASE')};"
        f"UID={os.getenv('DB_USERNAME')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "MARS_Connection=Yes;"
        "Connection Timeout=30;"
    )
    conn = pyodbc.connect(conn_str)
    # Ensure SQL_VARIANT (-150) and DATETIMEOFFSET (-155) are handled
    conn.add_output_converter(-150, handle_sql_variant)
    conn.add_output_converter(-155, handle_sql_variant)
    return conn