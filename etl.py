import requests
from typing import Any, Dict, List, Tuple, Optional

from db import execute, get_connection
from scheduler_config import API_BASE_URL, API_TIMEOUT
from mapping_engine import (
    get_field,
    normalize_major,
    normalize_degree,
    normalize_course_type,
    normalize_room_type,
    normalize_day,
)

# =========================================================
# GENERAL HELPERS
# =========================================================
def to_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except Exception:
        return default


def to_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


_etl_errors: List[str] = []


def fetch_api(endpoint: str) -> List[Dict[str, Any]]:
    url = f"{API_BASE_URL}/{endpoint}"

    try:
        response = requests.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            print(f"[FETCHED] {endpoint}: {len(data)}")
            return data

        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
            print(f"[FETCHED] {endpoint}: {len(data['data'])}")
            return data["data"]

        print(f"[WARN] Unexpected JSON format in {endpoint}")
        return []

    except Exception as e:
        msg = f"Failed to fetch {endpoint}: {e}"
        print(f"[ERROR] {msg}")
        _etl_errors.append(msg)
        return []


def execute_many_merge(query: str, rows: List[Tuple], label: str):
    if not rows:
        print(f"[SKIP] No rows for {label}")
        return

    processed = 0
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        for row in rows:
            try:
                cursor.execute(query, row)
                processed += 1
            except Exception as e:
                print(f"[INSERT ERROR] {label} | row={row} | error={e}")

        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"[CONNECT ERROR] {label}: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    print(f"[OK] {label}: {processed}/{len(rows)} rows processed")


# =========================================================
# TRANSFORM FUNCTIONS
# =========================================================
def transform_students(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        std_id = to_int(get_field(row, "student", "id"))
        std_name = to_str(get_field(row, "student", "name"))
        major_id = normalize_major(get_field(row, "student", "major_id"))

        if not std_id or not std_name:
            continue

        rows.append((std_id, std_name, major_id))

    return rows


def transform_courses(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        course_id = to_int(get_field(row, "course", "id"))
        course_name = to_str(get_field(row, "course", "name"))
        credit_hours = to_int(get_field(row, "course", "hours"), 0)
        course_type = to_str(normalize_course_type(get_field(row, "course", "type")), "Lecture")
        major_id = normalize_major(get_field(row, "course", "major_id"))
        plan_id = to_int(get_field(row, "course", "plan_id"))
        prereq_id = to_int(get_field(row, "course", "prereq_id"))

        if not course_id or not course_name:
            continue

        rows.append((
            course_id,
            course_name,
            credit_hours,
            course_type,
            major_id,
            plan_id,
            prereq_id
        ))

    return rows


def transform_instructors(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        instructor_id = to_int(get_field(row, "instructor", "id"))
        instructor_name = to_str(get_field(row, "instructor", "name"))
        specialization = to_str(get_field(row, "instructor", "specialization"))
        degree = to_str(normalize_degree(get_field(row, "instructor", "degree")))

        if not instructor_id or not instructor_name:
            continue

        rows.append((
            instructor_id,
            instructor_name,
            specialization,
            degree
        ))

    return rows


def transform_rooms(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        room_id = to_int(get_field(row, "room", "id"))
        building = to_str(get_field(row, "room", "building"))
        capacity = to_int(get_field(row, "room", "capacity"), 30)
        room_type = to_str(normalize_room_type(get_field(row, "room", "type")), "Lecture")

        if not room_id:
            continue

        rows.append((room_id, building, capacity, room_type))

    return rows


def transform_time_slots(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        time_id = to_int(get_field(row, "time_slot", "id"))
        day = to_str(normalize_day(get_field(row, "time_slot", "day")))
        s_time = to_str(get_field(row, "time_slot", "start_time"))
        e_time = to_str(get_field(row, "time_slot", "end_time"))

        if not time_id or not day or not s_time or not e_time:
            continue

        rows.append((time_id, day, s_time, e_time))

    return rows


def transform_departments(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        department_id = to_int(get_field(row, "department", "id"))
        department_na = to_str(get_field(row, "department", "name"))
        collage_id = to_int(get_field(row, "department", "college_id"))

        if not department_id or not department_na:
            continue

        rows.append((department_id, department_na, collage_id))

    return rows


def transform_colleges(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        collage_id = to_int(get_field(row, "college", "id"))
        collage_na = to_str(get_field(row, "college", "name"))

        if not collage_id or not collage_na:
            continue

        rows.append((collage_id, collage_na))

    return rows


def transform_majors(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        major_id = to_int(get_field(row, "major", "id"))
        major_na = to_str(normalize_major(get_field(row, "major", "name")))
        credit_hours = to_int(get_field(row, "major", "credit_hours"), 0)
        department_id = to_int(get_field(row, "major", "department_id"))

        if not major_id or not major_na:
            continue

        rows.append((major_id, major_na, credit_hours, department_id))

    return rows


def transform_semesters(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        semester_id = to_int(get_field(row, "semester", "id"))
        name = to_str(get_field(row, "semester", "name"))
        s_date = to_str(get_field(row, "semester", "start_date"))
        e_date = to_str(get_field(row, "semester", "end_date"))
        status = to_str(get_field(row, "semester", "status"))

        if not semester_id or not name:
            continue

        rows.append((semester_id, name, s_date, e_date, status))

    return rows


def transform_plans(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        plan_id    = to_int(get_field(row, "plan", "id"))
        plan_name  = to_str(get_field(row, "plan", "name"))
        major_id   = to_int(get_field(row, "plan", "major_id"))
        total_hours = to_int(get_field(row, "plan", "total_hours"), 0)

        if not plan_id:
            continue

        rows.append((plan_id, plan_name, major_id, total_hours))

    return rows


def transform_std_courses(data: List[Dict[str, Any]]) -> List[Tuple]:
    rows = []

    for row in data:
        history_id  = to_int(get_field(row, "std_course", "id"))
        std_id      = to_int(get_field(row, "std_course", "student_id"))
        course_id   = to_int(get_field(row, "std_course", "course_id"))
        semester_id = to_int(get_field(row, "std_course", "semester_id"))
        grade       = to_str(get_field(row, "std_course", "grade"))
        status      = to_str(get_field(row, "std_course", "status"))
        section     = to_str(get_field(row, "std_course", "section"))

        if not history_id or not std_id or not course_id:
            continue

        rows.append((history_id, std_id, course_id, semester_id, grade, status, section))

    return rows


# =========================================================
# LOADERS
# =========================================================
def load_colleges():
    data = transform_colleges(fetch_api("colleges"))

    execute_many_merge("""
    MERGE collage AS target
    USING (
        SELECT ? AS collage_id, ? AS collage_na
    ) AS source
    ON target.collage_id = source.collage_id
    WHEN MATCHED THEN
        UPDATE SET collage_na = source.collage_na
    WHEN NOT MATCHED THEN
        INSERT (collage_id, collage_na)
        VALUES (source.collage_id, source.collage_na);
    """, data, "colleges")


def load_departments():
    data = transform_departments(fetch_api("departments"))

    execute_many_merge("""
    MERGE department AS target
    USING (
        SELECT ? AS department_id, ? AS department_na, ? AS collage_id
    ) AS source
    ON target.department_id = source.department_id
    WHEN MATCHED THEN
        UPDATE SET department_na = source.department_na,
                   collage_id = source.collage_id
    WHEN NOT MATCHED THEN
        INSERT (department_id, department_na, collage_id)
        VALUES (source.department_id, source.department_na, source.collage_id);
    """, data, "departments")


def load_majors():
    data = transform_majors(fetch_api("majors"))

    execute_many_merge("""
    MERGE major AS target
    USING (
        SELECT ? AS major_id, ? AS major_na, ? AS credit_hours, ? AS department_id
    ) AS source
    ON target.major_id = source.major_id
    WHEN MATCHED THEN
        UPDATE SET major_na = source.major_na,
                   credit_hours = source.credit_hours,
                   department_id = source.department_id
    WHEN NOT MATCHED THEN
        INSERT (major_id, major_na, credit_hours, department_id)
        VALUES (source.major_id, source.major_na, source.credit_hours, source.department_id);
    """, data, "majors")


def load_plans():
    data = transform_plans(fetch_api("plans"))

    execute_many_merge("""
    MERGE [plan] AS target
    USING (
        SELECT ? AS plan_id, ? AS plan_name, ? AS major_id, ? AS total_hours
    ) AS source
    ON target.plan_id = source.plan_id
    WHEN MATCHED THEN
        UPDATE SET plan_name   = source.plan_name,
                   major_id    = source.major_id,
                   total_hours = source.total_hours
    WHEN NOT MATCHED THEN
        INSERT (plan_id, plan_name, major_id, total_hours)
        VALUES (source.plan_id, source.plan_name, source.major_id, source.total_hours);
    """, data, "plans")


def load_students():
    data = transform_students(fetch_api("students"))

    execute_many_merge("""
    MERGE std AS target
    USING (
        SELECT ? AS std_id, ? AS std_na, ? AS major_id
    ) AS source
    ON target.std_id = source.std_id
    WHEN MATCHED THEN
        UPDATE SET std_na = source.std_na,
                   major_id = source.major_id
    WHEN NOT MATCHED THEN
        INSERT (std_id, std_na, major_id)
        VALUES (source.std_id, source.std_na, source.major_id);
    """, data, "students")


def load_courses():
    data = transform_courses(fetch_api("courses"))

    execute_many_merge("""
    MERGE course AS target
    USING (
        SELECT
            ? AS course_id,
            ? AS course_na,
            ? AS credit_hours,
            ? AS type,
            ? AS major_id,
            ? AS plan_id,
            ? AS prereq_id
    ) AS source
    ON target.course_id = source.course_id
    WHEN MATCHED THEN
        UPDATE SET
            course_na = source.course_na,
            credit_hours = source.credit_hours,
            type = source.type,
            major_id = source.major_id,
            plan_id = source.plan_id,
            prereq_id = source.prereq_id
    WHEN NOT MATCHED THEN
        INSERT (course_id, course_na, credit_hours, type, major_id, plan_id, prereq_id)
        VALUES (source.course_id, source.course_na, source.credit_hours, source.type, source.major_id, source.plan_id, source.prereq_id);
    """, data, "courses")


def load_instructors():
    data = transform_instructors(fetch_api("instructors"))

    execute_many_merge("""
    MERGE instructor AS target
    USING (
        SELECT
            ? AS instructor_id,
            ? AS instructor_name,
            ? AS spec,
            ? AS degree_type
    ) AS source
    ON target.instructor_id = source.instructor_id
    WHEN MATCHED THEN
        UPDATE SET instructor_name = source.instructor_name,
                   spec = source.spec,
                   degree_type = source.degree_type
    WHEN NOT MATCHED THEN
        INSERT (instructor_id, instructor_name, spec, degree_type)
        VALUES (source.instructor_id, source.instructor_name, source.spec, source.degree_type);
    """, data, "instructors")


def load_rooms():
    data = transform_rooms(fetch_api("rooms"))

    execute_many_merge("""
    MERGE room AS target
    USING (
        SELECT ? AS room_id, ? AS building, ? AS capacity, ? AS type
    ) AS source
    ON target.room_id = source.room_id
    WHEN MATCHED THEN
        UPDATE SET building = source.building,
                   capacity = source.capacity,
                   type = source.type
    WHEN NOT MATCHED THEN
        INSERT (room_id, building, capacity, type)
        VALUES (source.room_id, source.building, source.capacity, source.type);
    """, data, "rooms")


def load_time_slots():
    data = transform_time_slots(fetch_api("time-slots"))

    execute_many_merge("""
    MERGE time_slot AS target
    USING (
        SELECT ? AS time_id, ? AS day, ? AS s_time, ? AS e_time
    ) AS source
    ON target.time_id = source.time_id
    WHEN MATCHED THEN
        UPDATE SET day = source.day,
                   s_time = source.s_time,
                   e_time = source.e_time
    WHEN NOT MATCHED THEN
        INSERT (time_id, day, s_time, e_time)
        VALUES (source.time_id, source.day, source.s_time, source.e_time);
    """, data, "time_slots")


def load_semesters():
    data = transform_semesters(fetch_api("semesters"))

    execute_many_merge("""
    MERGE semester AS target
    USING (
        SELECT ? AS semester_id, ? AS name, ? AS s_date, ? AS e_date, ? AS status
    ) AS source
    ON target.semester_id = source.semester_id
    WHEN MATCHED THEN
        UPDATE SET name = source.name,
                   s_date = source.s_date,
                   e_date = source.e_date,
                   status = source.status
    WHEN NOT MATCHED THEN
        INSERT (semester_id, name, s_date, e_date, status)
        VALUES (source.semester_id, source.name, source.s_date, source.e_date, source.status);
    """, data, "semesters")


def load_std_courses():
    data = transform_std_courses(fetch_api("std-courses"))

    execute_many_merge("""
    MERGE std_course AS target
    USING (
        SELECT
            ? AS history_id,
            ? AS std_id,
            ? AS course_id,
            ? AS semester_id,
            ? AS garde,
            ? AS status,
            ? AS section
    ) AS source
    ON target.history_id = source.history_id
    WHEN MATCHED THEN
        UPDATE SET
            std_id = source.std_id,
            course_id = source.course_id,
            semester_id = source.semester_id,
            garde = source.garde,
            status = source.status,
            section = source.section
    WHEN NOT MATCHED THEN
        INSERT (history_id, std_id, course_id, semester_id, garde, status, section)
        VALUES (source.history_id, source.std_id, source.course_id, source.semester_id, source.garde, source.status, source.section);
    """, data, "std_courses")


# =========================================================
# MAIN
# =========================================================
def run_etl() -> int:
    """Run the full ETL and return the number of fetch errors (0 = all good)."""
    global _etl_errors
    _etl_errors = []

    print("========== START ETL ==========")

    load_colleges()
    load_departments()
    load_majors()
    load_plans()

    load_students()
    load_courses()
    load_instructors()
    load_rooms()
    load_time_slots()
    load_semesters()
    load_std_courses()

    print("========== ETL DONE ==========")
    return len(_etl_errors)


if __name__ == "__main__":
    run_etl()