
import pyodbc
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def handle_sql_variant(value):
    return str(value) if value is not None else None
    
@st.cache_resource
def get_db_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_DATABASE')};"
        f"UID={os.getenv('DB_USERNAME')};"
        f"PWD={os.getenv('DB_PASSWORD')};"
        f"MARS_Connection=Yes;"
    )
    # ensure no transaction attempts on simple reads
    conn.autocommit = True

    # Register a converter for sql_variant columns (type -150)
    conn.add_output_converter(-150, handle_sql_variant)
    conn.add_output_converter(-155, handle_sql_variant)

    return conn