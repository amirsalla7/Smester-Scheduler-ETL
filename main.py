from student_analysis import StudentAnalysis
from course_offering import CourseOffering
from scheduler_engine import SchedulerEngine
from exporter import export_schedule_to_pdf, export_summary_to_pdf
from student_summary import build_summary
import sys
import json


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
    offerings_data = offering.build_offerings()
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

    print("Building summary report...")
    summary = build_summary(
        scheduler.schedule,
        scheduler.course_demand,
        scheduler.course_demand_graduating,
        scheduler.rooms
    )

    stats = {
        "students": len(scheduler.students),
        "courses": len(scheduler.courses),
        "instructors": len(scheduler.instructors),
        "rooms": len(scheduler.rooms),
        "sections_generated": len(scheduler.schedule),
        "opened_courses": len([o for o in offerings_data if o.get("should_open", False)]),
        "conflicts": 0
    }

    print("Writing JSON files...")

    with open("schedule.json", "w", encoding="utf-8") as f:
        json.dump(scheduler.schedule, f, ensure_ascii=False, indent=2)

    with open("report.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print("Exporting schedule PDF...")
    export_schedule_to_pdf(
        scheduler.schedule,
        "semester_schedule.pdf"
    )

    print("Exporting summary PDF...")
    export_summary_to_pdf(
        summary,
        "summary_report.pdf"
    )

    print("Done successfully.")


if __name__ == "__main__":
    main()