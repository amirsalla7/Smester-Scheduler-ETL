import eel
import json
import sys

from student_analysis import StudentAnalysis
from course_offering import CourseOffering
from scheduler_engine import SchedulerEngine
from exporter import export_schedule_to_pdf, export_summary_to_pdf
from student_summary import build_summary

eel.init("web")   # اسم مجلد الواجهة


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
            return {
                "status": "error",
                "message": "No schedule rows were generated."
            }

        scheduler.save_schedule()

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

        with open("web/schedule.json", "w", encoding="utf-8") as f:
            json.dump(scheduler.schedule, f, ensure_ascii=False, indent=2)

        with open("web/report.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        with open("web/stats.json", "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        export_schedule_to_pdf(
            scheduler.schedule,
            "web/semester_schedule.pdf"
        )

        export_summary_to_pdf(
            summary,
            "web/summary_report.pdf"
        )

        return {
            "status": "success",
            "sections_generated": len(scheduler.schedule),
            "conflicts": 0
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    eel.start("index.html", size=(1440, 900))