"""
web_app.py

Eel bridge for the Semester Scheduling Generator UI.
"""

import eel
import json
import sys
import hashlib

from student_analysis import StudentAnalysis
from course_offering import CourseOffering
from scheduler_engine import SchedulerEngine
from exporter import export_schedule_to_pdf, export_summary_to_pdf
from student_summary import build_summary

eel.init("web")

# ── Credentials ────────────────────────────────────────────────────────────────
USERS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
}

# ── Auth ───────────────────────────────────────────────────────────────────────
@eel.expose
def check_login(username: str, password: str) -> dict:
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return {"ok": False, "message": "Please enter username and password."}

    expected = USERS.get(username)
    if expected is None or hashlib.sha256(password.encode()).hexdigest() != expected:
        return {"ok": False, "message": "Invalid username or password."}

    return {"ok": True}


# ── Main Pipeline ──────────────────────────────────────────────────────────────
@eel.expose
def run_pipeline():
    try:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

        analysis = StudentAnalysis(graduating_hours_threshold=18)
        analysis.load_data()
        analysis.analyze_students()

        offering = CourseOffering(analysis)
        offering.load_data()
        offerings_data = offering.build_offerings()

        scheduler = SchedulerEngine()
        scheduler.load_data()
        scheduler.generate_schedule()

        if not scheduler.schedule:
            return {"status": "error", "message": "No schedule rows were generated."}

        scheduler.save_schedule()

        summary = build_summary(
            scheduler.schedule,
            scheduler.course_demand,
            scheduler.course_demand_graduating,
            scheduler.rooms,
        )

        conflicts = validate_schedule(scheduler.schedule)

        stats = {
            "students": len(getattr(scheduler, "students", [])),
            "courses": len(getattr(scheduler, "courses", [])),
            "instructors": len(getattr(scheduler, "instructors", [])),
            "rooms": len(getattr(scheduler, "rooms", [])),
            "sections_generated": len(scheduler.schedule),
            "opened_courses": len([o for o in offerings_data if o.get("should_open", False)]),
            "conflicts": len(conflicts),
        }

        with open("web/schedule.json", "w", encoding="utf-8") as f:
            json.dump(scheduler.schedule, f, ensure_ascii=False, indent=2)

        with open("web/report.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        with open("web/stats.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        export_schedule_to_pdf(scheduler.schedule, "web/semester_schedule.pdf")
        export_summary_to_pdf(summary, "web/summary_report.pdf")

        return {
            "status": "success",
            "sections_generated": len(scheduler.schedule),
            "conflicts": len(conflicts),
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Resources for Edit Dropdowns ───────────────────────────────────────────────
@eel.expose
def get_available_resources() -> dict:
    """
    Returns instructors and rooms for schedule edit dropdowns.
    """
    from db import fetch_all

    instructors = fetch_all("""
        SELECT
            instructor_id,
            instructor_name,
            ISNULL(degree_type, 'Master') AS degree_type
        FROM instructor
        ORDER BY instructor_name
    """)

    rooms = fetch_all("""
        SELECT
            room_id,
            building AS room_name,
            ISNULL(capacity, 40) AS capacity,
            ISNULL(type, 'Lecture') AS room_type
        FROM room
        ORDER BY building
    """)

    return {
        "instructors": instructors,
        "rooms": rooms
    }


# ── Save Edited Schedule ───────────────────────────────────────────────────────
@eel.expose
def save_schedule_edits(edited_schedule: list) -> dict:
    """
    Validate and persist a schedule edited in the frontend.

    Steps:
      1. Validate schedule
      2. Save web/schedule.json
      3. Rebuild web/report.json
      4. Update web/stats.json
      5. Re-export PDFs only if no conflicts
    """
    try:
        from db import fetch_all
    
        # 1) Validate schedule
        conflicts = validate_schedule(edited_schedule)

        # 2) Save schedule.json
        with open("web/schedule.json", "w", encoding="utf-8") as f:
            json.dump(edited_schedule, f, ensure_ascii=False, indent=2)

        # 3) Rebuild demand dicts from edited schedule
        course_demand = {}
        course_demand_graduating = {}

        for row in edited_schedule:
            cid = row["course_id"]
            if cid not in course_demand:
                course_demand[cid] = row.get("total_demand", 0)
                course_demand_graduating[cid] = row.get("graduating_demand", 0)

        # Load rooms for summary
        rooms = fetch_all("""
            SELECT
                room_id,
                building AS room_name,
                ISNULL(capacity, 40) AS capacity,
                ISNULL(type, 'Lecture') AS room_type
            FROM room
        """)

        # Build summary
        summary = build_summary(
            edited_schedule,
            course_demand,
            course_demand_graduating,
            rooms,
        )

        with open("web/report.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # 4) Update stats.json
        # Keep same structure used by dashboard
        stats = {
            "students": 1000,
            "courses": 38,
            "instructors": 12,
            "rooms": 32,
            "sections_generated": len(edited_schedule),
            "opened_courses": len(set(row["course_id"] for row in edited_schedule)),
            "conflicts": len(conflicts),
        }

        with open("web/stats.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        print("CONFLICTS FOUND =", len(conflicts))

        # If conflicts exist, do not regenerate final PDFs
        if conflicts:
            return {
                "status": "error",
                "message": f"{len(conflicts)} conflict(s) found. Fix before saving.",
                "conflicts": conflicts
            }

        # 5) Re-export PDFs
        export_schedule_to_pdf(edited_schedule, "web/semester_schedule.pdf")
        export_summary_to_pdf(summary, "web/summary_report.pdf")

        return {
            "status": "success",
            "message": "Schedule saved and PDFs regenerated.",
            "conflicts": []
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "conflicts": []
        }


# ── Conflict Validator ─────────────────────────────────────────────────────────
def validate_schedule(schedule: list) -> list:
    """
    Check for:
    - room conflicts
    - instructor conflicts
    - bad times
    - bad day patterns

    Returns a list of human-readable conflict strings.
    """
    conflicts = []
    VALID_DAYS = {"Sun/Tue", "Mon/Wed"}

    def overlaps(s1, e1, s2, e2):
        return s1 < e2 and s2 < e1

    room_slots = {}
    instr_slots = {}

    for row in schedule:
        course = row.get("course_name", "?")
        section = row.get("section_no", "?")
        day = row.get("day", "")
        start = row.get("start_time", "")
        end = row.get("end_time", "")
        room_id = row.get("room_id")
        instr_id = row.get("instructor_id")
        label = f"{course} §{section}"

        # Day pattern validation
        if day not in VALID_DAYS:
            conflicts.append(
                f"{label}: invalid day pattern '{day}'. Must be Sun/Tue or Mon/Wed."
            )

        # Time validation
        if start and end:
            if start >= end:
                conflicts.append(
                    f"{label}: start ({_fmt(start)}) must be before end ({_fmt(end)})."
                )
            if start < "08:00:00":
                conflicts.append(f"{label}: start time {_fmt(start)} is before 08:00.")
            if end > "16:00:00":
                conflicts.append(f"{label}: end time {_fmt(end)} is after 16:00.")
        else:
            conflicts.append(f"{label}: missing start or end time.")

        # Room conflict
        if room_id and day and start and end:
            for (d, rid, rs, re), other_label in list(room_slots.items()):
                if d == day and rid == room_id and overlaps(start, end, rs, re):
                    rname = row.get("room_name", room_id)
                    conflicts.append(
                        f"Room conflict: {label} and {other_label} share room "
                        f"{rname} on {day} ({_fmt(start)}–{_fmt(end)})."
                    )
            room_slots[(day, room_id, start, end)] = label

        # Instructor conflict
        if instr_id and day and start and end:
            for (d, iid, is_, ie), other_label in list(instr_slots.items()):
                if d == day and iid == instr_id and overlaps(start, end, is_, ie):
                    iname = row.get("instructor_name", instr_id)
                    conflicts.append(
                        f"Instructor conflict: {label} and {other_label} have "
                        f"{iname} on {day} ({_fmt(start)}–{_fmt(end)})."
                    )
            instr_slots[(day, instr_id, start, end)] = label

    return conflicts


def _fmt(t: str) -> str:
    """08:00:00 -> 08:00"""
    return str(t)[:5]


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    eel.start("index.html", size=(1440, 900))