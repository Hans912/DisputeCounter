from db.queries import get_invoice_by_id, get_dispute_by_id, get_customer_phone_by_id
from db.connection import get_db_connection
import pandas as pd

def get_invoice_data(invoice_id: str) -> pd.DataFrame:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = get_invoice_by_id()
        cursor.execute(query, [invoice_id])
        
        # Get column names
        columns = [column[0] for column in cursor.description]
        # Fetch all rows
        rows = cursor.fetchall()
        # Create DataFrame
        df = pd.DataFrame.from_records(rows, columns=columns)
        cursor.close()
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

def get_dispute_data(dispute_id: str) -> pd.DataFrame:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = get_dispute_by_id()
        cursor.execute(query, [dispute_id])
        
        # Get column names
        columns = [column[0] for column in cursor.description]
        # Fetch all rows
        rows = cursor.fetchall()
        # Create DataFrame
        df = pd.DataFrame.from_records(rows, columns=columns)
        cursor.close()
        return df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

def get_customer_phone(customer_id: str) -> str:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = get_customer_phone_by_id()
        cursor.execute(query, [customer_id])
        
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Error: {e}")
        return None
