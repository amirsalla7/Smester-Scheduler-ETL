from scheduler_engine import SchedulerEngine
from exporter import export_schedule_to_pdf


def main():
    scheduler = SchedulerEngine()

    print("Loading data from database...")
    scheduler.load_data()

    print("Generating schedule...")
    scheduler.generate_schedule()

    scheduler.print_schedule()

    print("Saving schedule to database...")
    scheduler.save_schedule()

    print("Exporting schedule to PDF...")
    export_schedule_to_pdf(scheduler.schedule, "semester_schedule.pdf")

    print("Done successfully.")


if __name__ == "__main__":
    main()