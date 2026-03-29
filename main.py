from scheduler_engine import SchedulerEngine
from exporter import export_schedule_to_excel
def main():
    scheduler = SchedulerEngine()

    print("Loading data from database...")
    scheduler.load_data()

    print("Generating schedule...")
    scheduler.generate_schedule()

    scheduler.print_schedule()

    print("Saving schedule to database...")
    scheduler.save_schedule()

    export_schedule_to_excel(scheduler.schedule)

    print("Done successfully.")

if __name__ == "__main__":
    main()