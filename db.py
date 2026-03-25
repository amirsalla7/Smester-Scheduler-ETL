import pyodbc
from scheduler_config import (
    SERVER, DATABASE, DRIVER,
    USE_TRUSTED_CONNECTION
)

def get_connection():
    if USE_TRUSTED_CONNECTION:
        conn_str = (
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"Trusted_Connection=yes;"
        )
    else:
        conn_str = (
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
           
        )
    return pyodbc.connect(conn_str)

def fetch_all(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or [])
    rows = cursor.fetchall()
    conn.close()
    return rows

def execute(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or [])
    conn.commit()
    conn.close()

def execute_many(query, data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.fast_executemany = True
    cursor.executemany(query, data)
    conn.commit()
    conn.close()