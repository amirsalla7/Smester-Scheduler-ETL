from collections import defaultdict
from datetime import datetime
from db import fetch_all, execute, execute_many
from scheduler_config import (
    LOAD_RULES,
    ADMIN_LOAD_REDUCTION,
    DEFAULT_ROOM_CAPACITY_FALLBACK,
    DEFAULT_MAX_SECTIONS_PER_COURSE,
    DEFAULT_ROOM_TYPE,
    CLEAR_OLD_SCHEDULE
)

class SchedulerEngine:
    def __init__(self):
        self.courses = []
        self.instructors = []
        self.rooms = []
        self.time_slots = []
        self.schedule = []

        # لتتبع التعارضات
        self.instructor_time_map = set()   # (instructor_id, time_id)
        self.room_time_map = set()         # (room_id, time_id)

        # لتتبع الحمل
        self.instructor_current_load = defaultdict(int)

    # تحميل البيانات من قاعدة البيانات
    def load_data(self):
        # course: course_id, course_na, credit_hours, type, major_id, plan_id, prereq_id
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

        # instructor: instructor_id, instructor_name, spec, degree_type
        self.instructors = fetch_all("""
            SELECT
                instructor_id,
                instructor_name,
                ISNULL(spec, '') AS spec,
                ISNULL(degree_type, '') AS degree_type
            FROM instructor
        """)

        # room: room_id, building, capacity, type
        self.rooms = fetch_all("""
            SELECT
                room_id,
                building,
                ISNULL(capacity, 30) AS capacity,
                ISNULL(type, 'Lecture') AS room_type
            FROM room
        """)

        # time_slot: time_id, day, s_time, e_time
        self.time_slots = fetch_all("""
            SELECT
                time_id,
                day,
                s_time,
                e_time
            FROM time_slot
            ORDER BY day, s_time
        """)

        if not self.courses:
            raise ValueError("لا يوجد مواد في جدول course")
        if not self.instructors:
            raise ValueError("لا يوجد مدرسين في جدول instructor")
        if not self.rooms:
            raise ValueError("لا يوجد قاعات في جدول room")
        if not self.time_slots:
            raise ValueError("لا يوجد أوقات في جدول time_slot")

    # حساب الحمل الأقصى للمدرس
    def get_max_load_for_instructor(self, instructor):
        _, _, _, degree_type = instructor
        max_load = LOAD_RULES.get(degree_type, 9)
        # إذا بدك لاحقًا تضيف is_department_head من جدول آخر
        return max_load

    # مطابقة المدرس مع المادة
    def instructor_matches_course(self, instructor, course):
        """
        منطق بسيط:
        إذا spec يحتوي اسم قريب من major_id أو course name نعتبره مناسب.
        لاحقًا تقدر تربطه بجدول تخصصات أدق.
        """
        _, instructor_name, spec, degree_type = instructor
        course_id, course_name, credit_hours, course_type, major_id, plan_id, prereq_id = course

        spec_lower = (spec or "").strip().lower()
        course_name_lower = (course_name or "").strip().lower()
        major_text = str(major_id).lower() if major_id is not None else ""

        if not spec_lower:
            return True

        if spec_lower in course_name_lower:
            return True

        if major_text and major_text in spec_lower:
            return True

        # مرونة بسيطة: إذا التخصص عام مثل cs أو se أو it
        keywords = ["cs", "computer", "software", "it", "information"]
        if any(k in spec_lower for k in keywords):
            return True

        return False

    # اختيار المدرس الأنسب
    def assign_instructor(self, course):
        course_id, course_name, credit_hours, course_type, major_id, plan_id, prereq_id = course

        candidates = []
        for inst in self.instructors:
            instructor_id, instructor_name, spec, degree_type = inst

            if not self.instructor_matches_course(inst, course):
                continue

            max_load = self.get_max_load_for_instructor(inst)
            current = self.instructor_current_load[instructor_id]

            if current + credit_hours <= max_load:
                remaining = max_load - current
                candidates.append((remaining, inst))

        # نختار المدرس الأقل حملًا/الأكثر توفرًا
        if not candidates:
            return None

        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    # اختيار القاعة
    def assign_room(self, course, time_id):
        course_id, course_name, credit_hours, course_type, major_id, plan_id, prereq_id = course
        needed_type = course_type if course_type else DEFAULT_ROOM_TYPE

        for room in self.rooms:
            room_id, building, capacity, room_type = room

            if room_type and needed_type:
                # مطابقة بسيطة للنوع
                if room_type.lower() != needed_type.lower():
                    continue

            if (room_id, time_id) in self.room_time_map:
                continue

            return room

        # لو ما لقينا بنفس النوع، نأخذ أي قاعة فاضية
        for room in self.rooms:
            room_id, building, capacity, room_type = room
            if (room_id, time_id) not in self.room_time_map:
                return room

        return None

    # اختيار الوقت
    def assign_time_slot(self, instructor_id):
        for slot in self.time_slots:
            time_id, day, s_time, e_time = slot
            if (instructor_id, time_id) not in self.instructor_time_map:
                return slot
        return None

    # التحقق من التعارض
    def has_conflict(self, instructor_id, room_id, time_id):
        if (instructor_id, time_id) in self.instructor_time_map:
            return True
        if (room_id, time_id) in self.room_time_map:
            return True
        return False

    # توليد جدول المواد
    def generate_schedule(self):
        self.schedule = []
        self.instructor_time_map.clear()
        self.room_time_map.clear()
        self.instructor_current_load.clear()

        schedule_id_counter = 1

        for course in self.courses:
            course_id, course_name, credit_hours, course_type, major_id, plan_id, prereq_id = course

            instructor = self.assign_instructor(course)
            if instructor is None:
                print(f"[WARNING] لم يتم العثور على مدرس مناسب للمادة: {course_name}")
                continue

            instructor_id, instructor_name, spec, degree_type = instructor

            slot = self.assign_time_slot(instructor_id)
            if slot is None:
                print(f"[WARNING] لا يوجد وقت متاح للمدرس {instructor_name} للمادة: {course_name}")
                continue

            time_id, day, s_time, e_time = slot

            room = self.assign_room(course, time_id)
            if room is None:
                print(f"[WARNING] لا توجد قاعة متاحة للمادة: {course_name}")
                continue

            room_id, building, capacity, room_type = room

            if self.has_conflict(instructor_id, room_id, time_id):
                print(f"[WARNING] تعارض تم اكتشافه للمادة: {course_name}")
                continue

            # تحديث التتبع
            self.instructor_time_map.add((instructor_id, time_id))
            self.room_time_map.add((room_id, time_id))
            self.instructor_current_load[instructor_id] += credit_hours

            self.schedule.append({
                "schedule_id": schedule_id_counter,
                "course_id": course_id,
                "course_name": course_name,
                "instructor_id": instructor_id,
                "instructor_name": instructor_name,
                "room_id": room_id,
                "room_name": building,
                "time_id": time_id,
                "day": day,
                "start_time": str(s_time),
                "end_time": str(e_time),
                "credit_hours": credit_hours
            })

            schedule_id_counter += 1

    # حفظ الجدول في قاعدة البيانات
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

        if rows:
            execute_many("""
                INSERT INTO schedule (schedule_id, room_id, time_id, course_id, instructor_id)
                VALUES (?, ?, ?, ?, ?)
            """, rows)

    # طباعة الجدول في التيرمنال
    def print_schedule(self):
        print("\n========== FINAL GENERATED SCHEDULE ==========")
        for item in self.schedule:
            print(
                f"[{item['schedule_id']}] "
                f"{item['course_name']} | "
                f"Instructor: {item['instructor_name']} | "
                f"Room: {item['room_name']} | "
                f"{item['day']} {item['start_time']} - {item['end_time']}"
            )
        print("==============================================\n")