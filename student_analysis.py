from collections import defaultdict
from db import fetch_all


class StudentAnalysis:
    def __init__(self, graduating_hours_threshold=18):
        self.graduating_hours_threshold = graduating_hours_threshold

        self.students = []
        self.courses = []
        self.student_courses = []

        self.courses_by_major = defaultdict(list)
        self.course_by_id = {}

        self.student_passed_courses = defaultdict(set)
        self.student_attempted_courses = defaultdict(set)
        self.student_completed_hours = defaultdict(int)
        self.student_remaining_hours = defaultdict(int)
        self.graduating_students = set()

        self.analysis_result = []

    # -------------------------------------------------
    # LOAD DATA
    # -------------------------------------------------
    def load_data(self):
        self.students = fetch_all("""
            SELECT
                s.std_id,
                s.std_na,
                s.major_id,
                ISNULL(m.credit_hours, 0) AS major_total_hours
            FROM std s
            LEFT JOIN major m ON s.major_id = m.major_id
        """)

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

        self.course_by_id = {c["course_id"]: c for c in self.courses}

        self.courses_by_major.clear()
        for course in self.courses:
            self.courses_by_major[course.get("major_id")].append(course)

    # -------------------------------------------------
    # HELPERS
    # -------------------------------------------------
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

    # -------------------------------------------------
    # CORE ANALYSIS
    # -------------------------------------------------
    def analyze_students(self):
        self.student_passed_courses.clear()
        self.student_attempted_courses.clear()
        self.student_completed_hours.clear()
        self.student_remaining_hours.clear()
        self.graduating_students.clear()
        self.analysis_result = []

        # تحليل السجل الأكاديمي
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

        # تحليل حالة كل طالب
        for student in self.students:
            std_id = student["std_id"]
            std_name = student["std_na"]
            major_id = student.get("major_id")
            total_required = int(student.get("major_total_hours") or 0)

            passed_courses = self.student_passed_courses.get(std_id, set())
            completed_hours = self.student_completed_hours.get(std_id, 0)
            remaining_hours = max(total_required - completed_hours, 0)

            self.student_remaining_hours[std_id] = remaining_hours

            is_graduating = remaining_hours <= self.graduating_hours_threshold
            if is_graduating:
                self.graduating_students.add(std_id)

            eligible_courses = []
            pending_courses = []

            for course in self.courses_by_major.get(major_id, []):
                course_id = course["course_id"]
                prereq_id = course.get("prereq_id")

                # إذا الطالب نجح بالمادة لا نعيدها
                if course_id in passed_courses:
                    continue

                # pending = كل مادة لم ينجح بها
                pending_courses.append(course_id)

                # eligible = لم ينجح بها، ومتطلبها السابق منجز أو لا يوجد متطلب
                if not prereq_id or prereq_id in passed_courses:
                    eligible_courses.append(course_id)

            self.analysis_result.append({
                "std_id": std_id,
                "std_name": std_name,
                "major_id": major_id,
                "completed_hours": completed_hours,
                "remaining_hours": remaining_hours,
                "is_graduating": is_graduating,
                "passed_courses": sorted(list(passed_courses)),
                "eligible_courses": sorted(list(eligible_courses)),
                "pending_courses": sorted(list(set(pending_courses))),
            })

        return self.analysis_result

    # -------------------------------------------------
    # GETTERS
    # -------------------------------------------------
    def get_analysis_result(self):
        return self.analysis_result

    def get_graduating_students(self):
        return self.graduating_students

    def get_student_remaining_hours(self):
        return self.student_remaining_hours

    def get_student_passed_courses(self):
        return self.student_passed_courses

    # -------------------------------------------------
    # PRINT
    # -------------------------------------------------
    def print_summary(self):
        print("\n========== STUDENT ANALYSIS ==========")
        for row in self.analysis_result:
            print(
                f"Student: {row['std_name']} | "
                f"Completed: {row['completed_hours']} | "
                f"Remaining: {row['remaining_hours']} | "
                f"Graduating: {row['is_graduating']} | "
                f"Eligible: {len(row['eligible_courses'])}"
            )
        print("======================================\n")