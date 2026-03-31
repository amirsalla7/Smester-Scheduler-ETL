from collections import defaultdict
from math import ceil

from db import fetch_all
from scheduler_config import (
    DEFAULT_ROOM_CAPACITY_FALLBACK,
    DEFAULT_MAX_SECTIONS_PER_COURSE
)

try:
    from scheduler_config import MIN_STUDENTS_TO_OPEN_COURSE
except ImportError:
    MIN_STUDENTS_TO_OPEN_COURSE = 5

try:
    from scheduler_config import MIN_GRADUATING_TO_FORCE_OPEN
except ImportError:
    MIN_GRADUATING_TO_FORCE_OPEN = 3


class CourseOffering:
    def __init__(self, student_analysis):
        self.student_analysis = student_analysis

        self.courses = []
        self.rooms = []

        self.course_by_id = {}
        self.course_demand = defaultdict(int)
        self.course_demand_graduating = defaultdict(int)
        self.course_demand_normal = defaultdict(int)

        self.offerings = []

    # -------------------------------------------------
    # LOAD DATA
    # -------------------------------------------------
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

        self.rooms = fetch_all("""
            SELECT
                room_id,
                building,
                ISNULL(capacity, 30) AS capacity,
                ISNULL(type, 'Lecture') AS room_type
            FROM room
        """)

        self.course_by_id = {c["course_id"]: c for c in self.courses}

    # -------------------------------------------------
    # HELPERS
    # -------------------------------------------------
    def get_max_capacity_for_type(self, course_type):
        course_type_text = str(course_type or "Lecture").strip().lower()

        matching_rooms = [
            room for room in self.rooms
            if str(room.get("room_type") or "Lecture").strip().lower() == course_type_text
        ]

        if matching_rooms:
            return max(
                int(room.get("capacity") or DEFAULT_ROOM_CAPACITY_FALLBACK)
                for room in matching_rooms
            )

        if self.rooms:
            return max(
                int(room.get("capacity") or DEFAULT_ROOM_CAPACITY_FALLBACK)
                for room in self.rooms
            )

        return DEFAULT_ROOM_CAPACITY_FALLBACK

    # -------------------------------------------------
    # DEMAND
    # -------------------------------------------------
    def calculate_demand(self):
        self.course_demand.clear()
        self.course_demand_graduating.clear()
        self.course_demand_normal.clear()

        analysis_result = self.student_analysis.get_analysis_result()
        graduating_students = self.student_analysis.get_graduating_students()

        for student in analysis_result:
            std_id = student["std_id"]
            eligible_courses = student["eligible_courses"]

            for course_id in eligible_courses:
                self.course_demand[course_id] += 1

                if std_id in graduating_students:
                    self.course_demand_graduating[course_id] += 1
                else:
                    self.course_demand_normal[course_id] += 1

    # -------------------------------------------------
    # OFFERING DECISION
    # -------------------------------------------------
    def build_offerings(self):
        self.offerings = []
        self.calculate_demand()

        for course in self.courses:
            course_id = course["course_id"]
            course_name = course["course_na"]
            course_type = course.get("course_type") or "Lecture"

            total_demand = self.course_demand.get(course_id, 0)
            graduating_demand = self.course_demand_graduating.get(course_id, 0)
            normal_demand = self.course_demand_normal.get(course_id, 0)

            # المادة تفتح إذا:
            # 1) العدد الكلي وصل الحد الأدنى
            # أو
            # 2) عدد الخريجين وحده وصل الحد المطلوب
            should_open = (
                total_demand >= MIN_STUDENTS_TO_OPEN_COURSE
                or graduating_demand >= MIN_GRADUATING_TO_FORCE_OPEN
            )

            if not should_open:
                self.offerings.append({
                    "course_id": course_id,
                    "course_name": course_name,
                    "course_type": course_type,
                    "total_demand": total_demand,
                    "graduating_demand": graduating_demand,
                    "normal_demand": normal_demand,
                    "should_open": False,
                    "open_reason": "demand too low",
                    "sections_needed": 0,
                    "estimated_section_capacity": 0
                })
                continue

            section_capacity = self.get_max_capacity_for_type(course_type)
            sections_needed = max(1, ceil(total_demand / max(section_capacity, 1)))

            if DEFAULT_MAX_SECTIONS_PER_COURSE and DEFAULT_MAX_SECTIONS_PER_COURSE > 0:
                sections_needed = min(sections_needed, DEFAULT_MAX_SECTIONS_PER_COURSE)

            if graduating_demand >= MIN_GRADUATING_TO_FORCE_OPEN and total_demand < MIN_STUDENTS_TO_OPEN_COURSE:
                open_reason = "graduating priority"
            else:
                open_reason = "normal demand"

            self.offerings.append({
                "course_id": course_id,
                "course_name": course_name,
                "course_type": course_type,
                "total_demand": total_demand,
                "graduating_demand": graduating_demand,
                "normal_demand": normal_demand,
                "should_open": True,
                "open_reason": open_reason,
                "sections_needed": sections_needed,
                "estimated_section_capacity": section_capacity
            })

        # ترتيب:
        # 1) المواد المفتوحة أولًا
        # 2) المواد التي يحتاجها الخريجون أولًا
        # 3) ثم الأعلى طلبًا
        self.offerings.sort(
            key=lambda x: (
                x["should_open"],
                x["graduating_demand"],
                x["total_demand"]
            ),
            reverse=True
        )

        return self.offerings

    # -------------------------------------------------
    # GETTERS
    # -------------------------------------------------
    def get_open_courses(self):
        return [row for row in self.offerings if row["should_open"]]

    def get_all_offerings(self):
        return self.offerings

    # -------------------------------------------------
    # PRINT
    # -------------------------------------------------
    def print_offerings(self):
        print("\n========== COURSE OFFERING DECISION ==========")
        for row in self.offerings:
            status = "OPEN" if row["should_open"] else "CLOSED"
            print(
                f"{row['course_name']} | "
                f"Demand={row['total_demand']} | "
                f"Graduating={row['graduating_demand']} | "
                f"Normal={row['normal_demand']} | "
                f"Sections={row['sections_needed']} | "
                f"Reason={row['open_reason']} | "
                f"Status={status}"
            )
        print("==============================================\n")