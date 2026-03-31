from student_analysis import StudentAnalysis
from course_offering import CourseOffering
from scheduler_engine import SchedulerEngine
from exporter import export_schedule_to_pdf
from db import execute
import sys


def cleanup_database_except_schedule():
    print("Cleaning database except schedule table...")

    # امسح البيانات بترتيب يحترم العلاقات
    execute("DELETE FROM std_course")
    execute("DELETE FROM semester")
    execute("DELETE FROM time_slot")
    execute("DELETE FROM room")
    execute("DELETE FROM instructor")
    execute("DELETE FROM std")
    execute("DELETE FROM course")
    execute("DELETE FROM [plan]")
    execute("DELETE FROM major")
    execute("DELETE FROM department")
    execute("DELETE FROM collage")
    execute("DELETE FROM schedule ")
    print("Database cleaned successfully.")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("Starting system...")

    analysis = StudentAnalysis(graduating_hours_threshold=18)

    print("Loading student analysis data...")
    analysis.load_data()

    print("Analyzing students...")
    analysis.analyze_students()
    analysis.print_summary()

    offering = CourseOffering(analysis)

    print("Loading course offering data...")
    offering.load_data()

    print("Building course offerings...")
    offering.build_offerings()
    offering.print_offerings()

    scheduler = SchedulerEngine()

    print("Loading scheduling data from database...")
    scheduler.load_data()

    print("Generating schedule...")
    scheduler.generate_schedule()

    print("Generated rows:", len(scheduler.schedule))

    if not scheduler.schedule:
        raise ValueError("No schedule rows were generated.")

    scheduler.print_schedule()

    print("Saving schedule to database...")
    scheduler.save_schedule()

    print("Exporting schedule to PDF...")
    export_schedule_to_pdf(scheduler.schedule, "semester_schedule.pdf")

    print("Cleaning all database tables except schedule...")
    cleanup_database_except_schedule()

    print("Done successfully.")


if __name__ == "__main__":
    main()