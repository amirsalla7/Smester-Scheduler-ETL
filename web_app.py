"""
web_app.py

Eel bridge for the Semester Scheduling Generator UI.
"""

import eel
import json
import os
import sys
import hashlib
import threading
import tempfile
import shutil

from student_analysis import StudentAnalysis
from course_offering import CourseOffering
from scheduler_engine import SchedulerEngine
from exporter import export_schedule_to_pdf, export_summary_to_pdf
from student_summary import build_summary
from etl import run_etl

eel.init("web")

# ── Pipeline guard (prevents double-run deadlocks) ─────────────────────────────
_pipeline_lock   = threading.Lock()
_pipeline_active = False

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


# ── Safe PDF writer (handles Windows file-lock issues) ────────────────────────
def _write_pdf_safe(export_fn, filepath):
    """
    Write a PDF safely on Windows.
    Writes to a temp file first then renames, so a browser-locked
    old file never blocks the new write.
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    # Try to remove the old file first (releases browser lock on most systems)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except OSError:
        pass  # file might still be locked — temp-rename approach will handle it

    # Write to a temp file in the same folder, then move into place
    dir_name = os.path.dirname(filepath) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp.pdf")
    os.close(fd)
    try:
        export_fn(tmp_path)
        try:
            shutil.move(tmp_path, filepath)
        except OSError:
            # Old file still locked — keep the temp file under a timestamped name
            import time as _time
            safe_path = filepath.replace(".pdf", f"_{int(_time.time())}.pdf")
            shutil.move(tmp_path, safe_path)
            print(f"[WARN] Could not replace {filepath} (file locked). Saved as {safe_path}")
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


# ── Main Pipeline ──────────────────────────────────────────────────────────────
@eel.expose
def run_pipeline():
    global _pipeline_active

    # ── Guard against concurrent runs ─────────────────────────────────────────
    with _pipeline_lock:
        if _pipeline_active:
            return {
                "status": "error",
                "message": "Pipeline is already running. Please wait for it to finish.",
            }
        _pipeline_active = True

    try:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

        # Ensure output folder exists
        os.makedirs("web", exist_ok=True)

        # ── Step 0: Sync latest data from API into local DB ────────────────────
        print("[ETL] Syncing data from API...")
        run_etl()
        print("[ETL] Sync complete.")

        analysis = StudentAnalysis(graduating_hours_threshold=21)
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

        # PDFs are written safely — a locked/deleted file won't crash the pipeline
        pdf_warning = None
        try:
            _write_pdf_safe(
                lambda p: export_schedule_to_pdf(scheduler.schedule, p),
                "web/semester_schedule.pdf"
            )
            _write_pdf_safe(
                lambda p: export_summary_to_pdf(summary, p),
                "web/summary_report.pdf"
            )
        except Exception as pdf_err:
            pdf_warning = str(pdf_err)
            print(f"[WARN] PDF export failed: {pdf_err}")

        return {
            "status": "success",
            "sections_generated": len(scheduler.schedule),
            "conflicts": len(conflicts),
            "pdf_warning": pdf_warning,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        # Always release the lock so next run isn't blocked
        with _pipeline_lock:
            _pipeline_active = False


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

        # 5) Re-export PDFs (safe write handles Windows file locks)
        _write_pdf_safe(
            lambda p: export_schedule_to_pdf(edited_schedule, p),
            "web/semester_schedule.pdf"
        )
        _write_pdf_safe(
            lambda p: export_summary_to_pdf(summary, p),
            "web/summary_report.pdf"
        )

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
    Checks:
    - room conflicts
    - instructor conflicts
    - invalid times
    - invalid day patterns

    Returns a list of human-readable conflict messages.
    """

    conflicts = []

    VALID_DAYS = {"Sun", "Mon", "Tue", "Wed", "Thu"}
    VALID_PATTERNS = {"Sun/Tue", "Mon/Wed", "Sun/Tue/Thu"}

    def normalize_time(t: str) -> str:
        """
        Converts:
        8:00 -> 08:00:00
        08:00 -> 08:00:00
        08:00:00 -> 08:00:00
        """
        if not t:
            return ""

        t = str(t).strip()

        if len(t) == 4:   # 8:00
            t = "0" + t

        if len(t) == 5:   # 08:00
            t = t + ":00"

        return t

    def time_to_minutes(t: str) -> int:
        t = normalize_time(t)
        if not t:
            return -1
        hh, mm, _ = t.split(":")
        return int(hh) * 60 + int(mm)

    def overlaps(s1, e1, s2, e2):
        s1m = time_to_minutes(s1)
        e1m = time_to_minutes(e1)
        s2m = time_to_minutes(s2)
        e2m = time_to_minutes(e2)

        return s1m < e2m and s2m < e1m

    def expand_days(day_pattern: str) -> set:
        """
        Sun/Tue -> {'Sun', 'Tue'}
        Mon/Wed -> {'Mon', 'Wed'}
        Sun/Tue/Thu -> {'Sun', 'Tue', 'Thu'}
        """
        if not day_pattern:
            return set()

        parts = [p.strip() for p in str(day_pattern).split("/") if p.strip()]
        return {p for p in parts if p in VALID_DAYS}

    room_slots = []
    instr_slots = []

    for row in schedule:
        course = row.get("course_name", "?")
        section = row.get("section_no", "?")
        day = str(row.get("day", "")).strip()

        start = normalize_time(row.get("start_time", ""))
        end = normalize_time(row.get("end_time", ""))

        room_id = row.get("room_id")
        room_name = row.get("room_name", room_id)

        # استخدم id إذا موجود، وإلا name
        instr_key = row.get("instructor_id") or row.get("instructor_name")
        instructor_name = row.get("instructor_name", instr_key)

        label = f"{course} §{section}"

        # ── Day validation ─────────────────────────────────────────────────────
        if day not in VALID_PATTERNS:
            conflicts.append(
                f"{label}: invalid day pattern '{day}'. Must be Sun/Tue, Mon/Wed, or Sun/Tue/Thu."
            )

        row_days = expand_days(day)
        if not row_days:
            conflicts.append(f"{label}: no valid teaching days found.")

        # ── Time validation ────────────────────────────────────────────────────
        if start and end:
            if time_to_minutes(start) >= time_to_minutes(end):
                conflicts.append(
                    f"{label}: start ({start[:5]}) must be before end ({end[:5]})."
                )

            if time_to_minutes(start) < time_to_minutes("08:00:00"):
                conflicts.append(f"{label}: start time {start[:5]} is before 08:00.")

            if time_to_minutes(end) > time_to_minutes("16:00:00"):
                conflicts.append(f"{label}: end time {end[:5]} is after 16:00.")
        else:
            conflicts.append(f"{label}: missing start or end time.")

        # ── Room conflict ──────────────────────────────────────────────────────
        if room_id and row_days and start and end:
            for existing in room_slots:
                common_days = row_days.intersection(existing["days"])
                if existing["room_id"] == room_id and common_days:
                    if overlaps(start, end, existing["start"], existing["end"]):
                        conflicts.append(
                            f"Room conflict: {label} and {existing['label']} share room "
                            f"{room_name} on {', '.join(sorted(common_days))} "
                            f"({start[:5]}–{end[:5]})."
                        )

            room_slots.append({
                "room_id": room_id,
                "days": row_days,
                "start": start,
                "end": end,
                "label": label
            })

        # ── Instructor conflict ───────────────────────────────────────────────
            instr_key = (
            str(row.get("instructor_id") or row.get("instructor_name") or "")
            .strip()
            .lower()
        )

        if instr_key and row_days and start and end:
            for existing in instr_slots:
                if existing["instr_key"] != instr_key:
                    continue

                common_days = row_days & existing["days"]
                if not common_days:
                    continue

                if overlaps(start, end, existing["start"], existing["end"]):
                    conflicts.append(
                        f"Instructor conflict: {label} and {existing['label']} have "
                        f"{instructor_name} on {', '.join(sorted(common_days))} "
                        f"({start[:5]}–{end[:5]})."
                    )

            instr_slots.append({
                "instr_key": instr_key,
                "days": set(row_days),
                "start": start,
                "end": end,
                "label": label
            })

    return conflicts


def _fmt(t: str) -> str:
    """08:00:00 -> 08:00"""
    return str(t)[:5]


# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    eel.start("index.html", size=(1440, 900))