import pyodbc
from scheduler_config import (
    SERVER,
    DATABASE,
    DRIVER,
    USE_TRUSTED_CONNECTION
)


# =====================================================
# CONNECTION
# =====================================================
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


# =====================================================
# SELECT
# =====================================================
def fetch_all(query, params=None):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query, params or [])

        columns = [col[0] for col in cursor.description]

        rows = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        return rows

    except Exception as e:

        print("DB fetch_all error:", e)
        return []

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


def fetch_one(query, params=None):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query, params or [])

        row = cursor.fetchone()

        if not row:
            return None

        columns = [col[0] for col in cursor.description]

        return dict(zip(columns, row))

    except Exception as e:

        print("DB fetch_one error:", e)
        return None

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =====================================================
# INSERT / UPDATE / DELETE
# =====================================================
def execute(query, params=None):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query, params or [])

        conn.commit()

    except Exception as e:

        print("DB execute error:", e)

        if conn:
            conn.rollback()

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


def execute_many(query, data):

    if not data:
        return

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.fast_executemany = True

        cursor.executemany(query, data)

        conn.commit()

    except Exception as e:

        print("DB execute_many error:", e)

        if conn:
            conn.rollback()

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()