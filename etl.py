import requests
import pyodbc
from mapping_engine import get_field, normalize_value


SERVER = 'localhost'
DATABASE = 'UniversityDB'

conn_str = f'''
DRIVER={{ODBC Driver 17 for SQL Server}};
SERVER={SERVER};
DATABASE={DATABASE};
Trusted_Connection=yes;
'''

def fetch_api(endpoint):
    url = f"https://api.example.com/{endpoint}"  # غيره حسب API

    try:
        res = requests.get(url)
        res.raise_for_status()
        print(f"{endpoint} fetched")
        return res.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return []


def insert_data(query, data):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    for row in data:
        try:
            cursor.execute(query, row)
        except Exception as e:
            print("Insert error:", e)

    conn.commit()
    conn.close()


def transform_students(data):
    result = []

    for row in data:
        student_id = get_field(row, "student", "id")
        name = get_field(row, "student", "name")
        major = get_field(row, "student", "major_id")

        major = normalize_value("major", major)

        if not student_id or not name:
            continue

        result.append((student_id, name, major))

    return result


def transform_courses(data):
    result = []

    for row in data:
        cid = get_field(row, "course", "id")
        name = get_field(row, "course", "name")
        hours = get_field(row, "course", "hours")
        major = get_field(row, "course", "major_id")

        if not cid:
            continue

        result.append((cid, name, hours, major))

    return result


def load_students():
    raw = fetch_api("students")
    data = transform_students(raw)

    insert_data("""
    MERGE std AS target
    USING (SELECT ? AS id, ? AS name, ? AS major_id) AS source
    ON target.std_id = source.id
    WHEN MATCHED THEN
        UPDATE SET std_na = source.name,
                   major_id = source.major_id
    WHEN NOT MATCHED THEN
        INSERT (std_id, std_na, major_id)
        VALUES (source.id, source.name, source.major_id);
    """, data)


def load_courses():
    raw = fetch_api("courses")
    data = transform_courses(raw)

    insert_data("""
    MERGE course AS target
    USING (SELECT ? AS id, ? AS name, ? AS hours, ? AS major_id) AS source
    ON target.course_id = source.id
    WHEN MATCHED THEN
        UPDATE SET course_na = source.name,
                   credit_hours = source.hours,
                   major_id = source.major_id
    WHEN NOT MATCHED THEN
        INSERT (course_id, course_na, credit_hours, major_id)
        VALUES (source.id, source.name, source.hours, source.major_id);
    """, data)


def run_etl():
    print("Starting ETL 🔥")

    load_students()
    load_courses()

    print("ETL DONE ✅")


if __name__ == "__main__":
    run_etl()