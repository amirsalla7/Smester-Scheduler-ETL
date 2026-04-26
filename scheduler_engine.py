from collections import defaultdict
from datetime import datetime, time
from math import ceil

from db import fetch_all, execute, execute_many
from scheduler_config import (
    LOAD_RULES,
    ADMIN_LOAD_REDUCTION,
    DEFAULT_ROOM_CAPACITY_FALLBACK,
    DEFAULT_MAX_SECTIONS_PER_COURSE,
    DEFAULT_ROOM_TYPE,
    CLEAR_OLD_SCHEDULE,
    ALLOWED_START,
    ALLOWED_END,
    GRADUATING_HOURS_THRESHOLD,
)

try:
    from scheduler_config import MIN_STUDENTS_TO_OPEN_COURSE
except ImportError:
    MIN_STUDENTS_TO_OPEN_COURSE = 5

try:
    from scheduler_config import MIN_GRADUATING_TO_FORCE_OPEN
except ImportError:
    MIN_GRADUATING_TO_FORCE_OPEN = 1

try:
    from scheduler_config import GRADUATING_PRIORITY_ENABLED
except ImportError:
    GRADUATING_PRIORITY_ENABLED = True


class SchedulerEngine:
    def __init__(self):
        self.courses = []
        self.instructors = []
        self.rooms = []
        self.time_slots = []
        self.students = []
        self.student_courses = []
        self.schedule = []

        self.course_by_id = {}
        self.rooms_by_type = defaultdict(list)

        self.course_demand = defaultdict(int)
        self.course_demand_graduating = defaultdict(int)
        self.course_demand_normal = defaultdict(int)

        self.student_passed_courses = defaultdict(set)
        self.student_attempted_courses = defaultdict(set)
        self.student_completed_hours = defaultdict(int)
        self.student_remaining_hours = defaultdict(int)
        self.graduating_students = set()

        self.course_primary_instructor = {}        # course_id -> instructor_id
        self.course_day_patterns = defaultdict(set)  # course_id -> {"Sun/Tue", "Mon/Wed"}  
        
        # conflict maps
        self.instructor_time_map = set()   # (instructor_id, time_id)
        self.room_time_map = set()         # (room_id, time_id)

        self.instructor_current_load = defaultdict(int)

        # new rules
        self.instructor_course_sections = defaultdict(int)  # (instructor_id, course_id) -> count

    # =====================================================
    # HELPERS
    # =====================================================
    def parse_time_value(self, value):
        if value is None:
            return None

        if isinstance(value, time):
            return value

        if isinstance(value, datetime):
            return value.time()

        value = str(value).strip()

        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                continue

        return None

    def is_passed_status(self, status, grade=None):
        status_text = str(status or "").strip().lower()
        grade_text = str(grade or "").strip().lower()

        passed_statuses = {
            "passed", "pass", "success", "successful", "p",
            "ناجح", "نجاح"
        }

        failed_statuses = {
            "failed", "fail", "f", "راسب", "رسوب"
        }

        if status_text in passed_statuses:
            return True

        if status_text in failed_statuses:
            return False

        try:
            grade_num = float(grade)
            return grade_num >= 50
        except Exception:
            pass

        if grade_text in {"a", "a-", "b", "b+", "b-", "c", "c+", "c-", "d", "d+", "d-"}:
            return True

        return False

    def get_room_capacity_for_course_type(self, course_type):
        matching_rooms = [
            room for room in self.rooms
            if str(room.get("room_type") or DEFAULT_ROOM_TYPE).lower()
            == str(course_type or DEFAULT_ROOM_TYPE).lower()
        ]

        if matching_rooms:
            return max(int(room.get("capacity") or DEFAULT_ROOM_CAPACITY_FALLBACK) for room in matching_rooms)

        if self.rooms:
            return max(int(room.get("capacity") or DEFAULT_ROOM_CAPACITY_FALLBACK) for room in self.rooms)

        return DEFAULT_ROOM_CAPACITY_FALLBACK

    def get_sections_needed(self, course):
        course_id = course["course_id"]
        demand = self.course_demand.get(course_id, 0)
        grad_demand = self.course_demand_graduating.get(course_id, 0)
        course_type = course.get("course_type") or DEFAULT_ROOM_TYPE

        if demand < MIN_STUDENTS_TO_OPEN_COURSE:
            if grad_demand >= MIN_GRADUATING_TO_FORCE_OPEN:
                return 1
            return 0

        section_capacity = self.get_room_capacity_for_course_type(course_type)
        estimated_sections = max(1, ceil(demand / max(section_capacity, 1)))

        if DEFAULT_MAX_SECTIONS_PER_COURSE and DEFAULT_MAX_SECTIONS_PER_COURSE > 0:
            estimated_sections = min(estimated_sections, DEFAULT_MAX_SECTIONS_PER_COURSE)

        return estimated_sections

    def get_paired_day(self, day):
        pairs = {
            "Sunday": "Tuesday",
            "Tuesday": "Sunday",
            "Monday": "Wednesday",
            "Wednesday": "Monday",
        }
        return pairs.get(day)

    def get_day_label(self, day):
        labels = {
            "Sunday": "Sun/Tue",
            "Tuesday": "Sun/Tue",
            "Monday": "Mon/Wed",
            "Wednesday": "Mon/Wed",
            "Thursday": "Thu"
        }
        return labels.get(day, day)

    def build_time_slot_pairs(self):
        slot_map = {}

        for slot in self.time_slots:
            day = slot.get("day")
            start_time = str(slot.get("s_time"))
            end_time = str(slot.get("e_time"))
            slot_map[(day, start_time, end_time)] = slot

        pairs = []
        used = set()

        for slot in self.time_slots:
            day = slot.get("day")
            start_time = str(slot.get("s_time"))
            end_time = str(slot.get("e_time"))

            if slot["time_id"] in used:
                continue

            paired_day = self.get_paired_day(day)

            if paired_day:
                pair_slot = slot_map.get((paired_day, start_time, end_time))
                if pair_slot and pair_slot["time_id"] not in used:
                    pairs.append({
                        "day_label": self.get_day_label(day),
                        "slot1": slot,
                        "slot2": pair_slot,
                        "start_time": start_time,
                        "end_time": end_time
                    })
                    used.add(slot["time_id"])
                    used.add(pair_slot["time_id"])
                    continue

            pairs.append({
                "day_label": self.get_day_label(day),
                "slot1": slot,
                "slot2": None,
                "start_time": start_time,
                "end_time": end_time
            })
            used.add(slot["time_id"])

        return pairs

   
    # =====================================================
    # LOAD DATA
    # =====================================================
    def load_data(self):
        self.courses = fetch_all("""
            SELECT 
                course_id,
                course_na,
                ISNULL(credit_hours, 0) AS credit_hours,
                ISNULL(type, 'Lecture') AS course_type,
                major_id,
                plan_id,
                prereq_id
            FROM course
        """)

        self.instructors = fetch_all("""
            SELECT
                instructor_id,
                instructor_name,
                ISNULL(spec, '') AS spec,
                ISNULL(degree_type, '') AS degree_type
            FROM instructor
        """)

        self.rooms = fetch_all("""
            SELECT
                room_id,
                building,
                ISNULL(capacity, 30) AS capacity,
                ISNULL(type, 'Lecture') AS room_type
            FROM room
        """)

        self.time_slots = fetch_all("""
            SELECT
                time_id,
                day,
                s_time,
                e_time
            FROM time_slot
            WHERE day IN ('Sunday', 'Tuesday', 'Monday', 'Wednesday')
            ORDER BY
                CASE
                    WHEN day = 'Sunday' THEN 1
                    WHEN day = 'Tuesday' THEN 2
                    WHEN day = 'Monday' THEN 3
                    WHEN day = 'Wednesday' THEN 4
                    ELSE 5
                END,
                s_time
        """)

        self.students = fetch_all("""
            SELECT
                s.std_id,
                s.std_na,
                s.major_id,
                ISNULL(p.total_hours, 0) AS major_total_hours
            FROM std s
            LEFT JOIN [plan] p ON s.major_id = p.major_id
        """)

        self.student_courses = fetch_all("""
            SELECT
                sc.history_id,
                sc.std_id,
                sc.course_id,
                sc.semester_id,
                sc.garde,
                sc.status,
                sc.section,
                ISNULL(c.credit_hours, 0) AS course_credit_hours
            FROM std_course sc
            LEFT JOIN course c ON sc.course_id = c.course_id
        """)

        if not self.courses:
            raise ValueError("No courses found in table course")

        if not self.instructors:
            raise ValueError("No instructors found in table instructor")

        if not self.rooms:
            raise ValueError("No rooms found in table room")

        if not self.time_slots:
            raise ValueError("No time slots found in table time_slot")

        self.course_by_id = {c["course_id"]: c for c in self.courses}

        self.rooms_by_type.clear()
        for room in self.rooms:
            room_type = str(room.get("room_type") or DEFAULT_ROOM_TYPE)
            self.rooms_by_type[room_type.lower()].append(room)

    # =====================================================
    # STUDENT ANALYSIS
    # =====================================================
    def analyze_students(self):
        self.student_passed_courses.clear()
        self.student_attempted_courses.clear()
        self.student_completed_hours.clear()
        self.student_remaining_hours.clear()
        self.graduating_students.clear()

        for row in self.student_courses:
            std_id = row["std_id"]
            course_id = row["course_id"]
            grade = row.get("garde")
            status = row.get("status")
            hours = int(row.get("course_credit_hours") or 0)

            self.student_attempted_courses[std_id].add(course_id)

            if self.is_passed_status(status, grade):
                self.student_passed_courses[std_id].add(course_id)
                self.student_completed_hours[std_id] += hours

        for student in self.students:
            std_id = student["std_id"]
            total_required = int(student.get("major_total_hours") or 0)
            completed = self.student_completed_hours.get(std_id, 0)
            remaining = max(total_required - completed, 0)
            self.student_remaining_hours[std_id] = remaining

            if GRADUATING_PRIORITY_ENABLED and remaining <= GRADUATING_HOURS_THRESHOLD:
                self.graduating_students.add(std_id)

    def calculate_course_demand(self):
        self.course_demand.clear()
        self.course_demand_graduating.clear()
        self.course_demand_normal.clear()

        self.analyze_students()

        courses_by_major = defaultdict(list)
        for course in self.courses:
            courses_by_major[course.get("major_id")].append(course)

        for student in self.students:
            std_id = student["std_id"]
            major_id = student.get("major_id")
            passed_courses = self.student_passed_courses.get(std_id, set())

            for course in courses_by_major.get(major_id, []):
                course_id = course["course_id"]
                prereq_id = course.get("prereq_id")

                if course_id in passed_courses:
                    continue

                if prereq_id and prereq_id not in passed_courses:
                    continue

                self.course_demand[course_id] += 1

                if std_id in self.graduating_students:
                    self.course_demand_graduating[course_id] += 1
                else:
                    self.course_demand_normal[course_id] += 1

    # =====================================================
    # INSTRUCTOR LOGIC
    # =====================================================
    def get_max_load_for_instructor(self, instructor):
        degree_type = str(instructor.get("degree_type") or "").strip()
        max_load = LOAD_RULES.get(degree_type, 9)

        if instructor.get("is_admin"):
            max_load = max(0, max_load - ADMIN_LOAD_REDUCTION)

        return max_load

    def instructor_matches_course(self, instructor, course):
        spec = str(instructor.get("spec") or "").strip().lower()
        course_name = str(course.get("course_na") or "").strip().lower()
        major_id = str(course.get("major_id") or "").strip().lower()

        if not spec:
            return True

        if spec in course_name:
            return True

        if major_id and major_id in spec:
            return True

        keywords = ["cs", "computer", "software", "it", "information", "ai", "network", "security", "cy", "se"]
        if any(k in spec for k in keywords):
            return True

        return False

    def assign_instructor(self, course, section_no, time_ids=None):

        credit_hours = int(course.get("credit_hours") or 0)

        course_id = course["course_id"]

        primary_instructor_id = self.course_primary_instructor.get(course_id)

        candidates = []

        for inst in self.instructors:

            instructor_id = inst["instructor_id"]

            if not self.instructor_matches_course(inst, course):
                continue

            max_load = self.get_max_load_for_instructor(inst)

            current_load = self.instructor_current_load[instructor_id]

            if current_load + credit_hours > max_load:
                continue

            # الدكتور لا يدرّس أكثر من شعبتين لنفس المادة
            if self.instructor_course_sections[(instructor_id, course_id)] >= 2:
                continue

            # الشعبة الثانية تفضّل نفس دكتور الشعبة الأولى لكن لا تُجبر عليه

            # تحقق من تعارض الوقت
            if time_ids:

                conflict = False

                for t in time_ids:

                    if (instructor_id, t) in self.instructor_time_map:

                        conflict = True
                        break

                if conflict:
                    continue

            remaining_load = max_load - (current_load + credit_hours)

            candidates.append(
                (remaining_load, current_load, inst)
            )

        if not candidates:
            return None

        candidates.sort(
            key=lambda x: (
                0 if (section_no == 2 and primary_instructor_id is not None
                      and x[2]["instructor_id"] == primary_instructor_id) else 1,
                x[1],
                x[0],
            )
        )

        return candidates[0][2]
    # =====================================================
    # ROOM / TIME LOGIC
    # =====================================================
    def assign_room(self, course, time_ids):
        needed_type = str(course.get("course_type") or DEFAULT_ROOM_TYPE).lower()

        for room in self.rooms_by_type.get(needed_type, []):
            room_id = room["room_id"]
            busy = False

            for time_id in time_ids:
                if (room_id, time_id) in self.room_time_map:
                    busy = True
                    break

            if not busy:
                return room

        for room in self.rooms:
            room_id = room["room_id"]
            busy = False

            for time_id in time_ids:
                if (room_id, time_id) in self.room_time_map:
                    busy = True
                    break

            if not busy:
                return room

        return None

    def has_conflict(self, instructor_id, room_id, time_ids):
        for time_id in time_ids:
            if (instructor_id, time_id) in self.instructor_time_map:
                return True

            if (room_id, time_id) in self.room_time_map:
                return True

        return False
    

    def can_use_day_pattern_for_course(self, course_id, section_no, day_label):
        used_patterns = self.course_day_patterns[course_id]

        if section_no <= 2:
            if day_label in used_patterns:
                return False

        return True
    # =====================================================
    # SCHEDULING
    # =====================================================
    def generate_schedule(self):
        self.schedule = []
        self.instructor_time_map.clear()
        self.room_time_map.clear()
        self.instructor_current_load.clear()
        self.instructor_course_sections.clear()
        self.calculate_course_demand()
        self.course_primary_instructor.clear()
        self.course_day_patterns.clear()

        schedule_id_counter = 1

        sorted_courses = sorted(
            self.courses,
            key=lambda c: (
                self.course_demand_graduating.get(c["course_id"], 0),
                self.course_demand.get(c["course_id"], 0),
                int(c.get("credit_hours") or 0)
            ),
            reverse=True
        )

        slot_pairs = self.build_time_slot_pairs()

        for course in sorted_courses:
            course_id = course["course_id"]
            course_name = course["course_na"]
            total_demand = self.course_demand.get(course_id, 0)
            grad_demand = self.course_demand_graduating.get(course_id, 0)
            sections_needed = self.get_sections_needed(course)

            if total_demand < MIN_STUDENTS_TO_OPEN_COURSE and grad_demand < MIN_GRADUATING_TO_FORCE_OPEN:
                print(f"[SKIP] Course {course_name} will not open because demand = {total_demand}")
                continue

            if sections_needed <= 0:
                print(f"[SKIP] Course {course_name} does not need any sections")
                continue

            for section_no in range(1, sections_needed + 1):
                assigned = False

                for pair in slot_pairs:
                    slot1 = pair["slot1"]
                    slot2 = pair["slot2"]

                    time_ids = [slot1["time_id"]]
                    if slot2:
                        time_ids.append(slot2["time_id"])

                    start_t = self.parse_time_value(pair["start_time"])
                    end_t = self.parse_time_value(pair["end_time"])
                    allowed_start = self.parse_time_value(ALLOWED_START)
                    allowed_end = self.parse_time_value(ALLOWED_END)

                    if start_t is None or end_t is None:
                        continue

                    if allowed_start and start_t < allowed_start:
                        continue

                    if allowed_end and end_t > allowed_end:
                        continue

                    day_label = pair["day_label"]
                    base_day = slot1.get("day", "")
                        
                 # إذا المادة لها أكثر من شعبة، لازم الشعب تكون في pattern مختلف
                    if not self.can_use_day_pattern_for_course(course_id, section_no,day_label):
                        continue

                    instructor = self.assign_instructor(course,section_no=section_no,  time_ids=time_ids)
                    if instructor is None:
                        continue

                    room = self.assign_room(course, time_ids)
                    if room is None:
                        continue

                    instructor_id = instructor["instructor_id"]
                    instructor_name = instructor["instructor_name"]
                    room_id = room["room_id"]
                    room_name = room.get("building", "")

                    if self.has_conflict(instructor_id, room_id, time_ids):
                        continue

                    for time_id in time_ids:
                        self.instructor_time_map.add((instructor_id, time_id))
                        self.room_time_map.add((room_id, time_id))

                    self.instructor_current_load[instructor_id] += int(course.get("credit_hours") or 0)
                    self.instructor_course_sections[(instructor_id, course_id)] += 1
                    self.course_day_patterns[course_id].add(day_label)

                    if section_no == 1:
                        self.course_primary_instructor[course_id] = instructor_id
                    self.schedule.append({
                        "schedule_id": schedule_id_counter,
                        "course_id": course_id,
                        "course_name": course_name,
                        "section_no": section_no,
                        "total_demand": total_demand,
                        "graduating_demand": grad_demand,
                        "instructor_id": instructor_id,
                        "instructor_name": instructor_name,
                        "room_id": room_id,
                        "room_name": room_name,
                        "time_id": slot1["time_id"],
                        "day": day_label,
                        "start_time": pair["start_time"],
                        "end_time": pair["end_time"],
                        "credit_hours": int(course.get("credit_hours") or 0),
                    })

                    schedule_id_counter += 1
                    assigned = True
                    break

                if not assigned:
                    print(f"[WARNING] Could not schedule section {section_no} for course: {course_name}")

    # =====================================================
    # DB SAVE
    # =====================================================
    def ensure_schedule_table(self):
        execute("""
        IF NOT EXISTS (
            SELECT * FROM sysobjects WHERE name='schedule' AND xtype='U'
        )
        CREATE TABLE schedule (
            schedule_id INT PRIMARY KEY,
            room_id INT,
            time_id INT,
            course_id INT,
            instructor_id INT
        )
        """)

    def save_schedule(self):
        self.ensure_schedule_table()

        if not self.schedule:
            raise ValueError("Schedule is empty. Nothing to save.")

        if CLEAR_OLD_SCHEDULE:
            execute("DELETE FROM schedule")

        rows = []
        for item in self.schedule:
            rows.append((
                item["schedule_id"],
                item["room_id"],
                item["time_id"],
                item["course_id"],
                item["instructor_id"]
            ))

        execute_many("""
            INSERT INTO schedule (schedule_id, room_id, time_id, course_id, instructor_id)
            VALUES (?, ?, ?, ?, ?)
        """, rows)

    # =====================================================
    # OUTPUT
    # =====================================================
    def print_course_demand(self):
        print("\n========== COURSE DEMAND ==========")
        for course in sorted(self.courses, key=lambda c: self.course_demand.get(c["course_id"], 0), reverse=True):
            cid = course["course_id"]
            print(
                f"{course['course_na']} | "
                f"Total={self.course_demand.get(cid, 0)} | "
                f"Graduating={self.course_demand_graduating.get(cid, 0)} | "
                f"Normal={self.course_demand_normal.get(cid, 0)}"
            )
        print("===================================\n")

    def print_schedule(self):
        print("\n" + "=" * 120)
        print("FINAL GENERATED SCHEDULE")
        print("=" * 120)
        print(f"{'Course ID':<10} {'Course Name':<25} {'Sec':<5} {'Instructor':<20} {'Room ID':<10} {'Day':<12} {'Start':<8} {'End':<8} {'Hours':<6}")
        print("-" * 120)

        for item in self.schedule:
            print(
                f"{item['course_id']:<10} "
                f"{item['course_name']:<25} "
                f"{item['section_no']:<5} "
                f"{item['instructor_name']:<20} "
                f"{item['room_id']:<10} "
                f"{item['day']:<12} "
                f"{item['start_time']:<8} "
                f"{item['end_time']:<8} "
                f"{item['credit_hours']:<6}"
            )

        print("=" * 120 + "\n")