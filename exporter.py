from openpyxl import Workbook

def export_schedule_to_excel(schedule, filename="schedule.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Schedule"

    ws.append([
        "Schedule ID",
        "Course ID",
        "Course Name",
        "Instructor ID",
        "Instructor Name",
        "Room ID",
        "Room Name",
        "Time ID",
        "Day",
        "Start Time",
        "End Time",
        "Credit Hours"
    ])


    for item in schedule:
        ws.append([
            item["schedule_id"],
            item["course_id"],
            item["course_name"],
            item["instructor_id"],
            item["instructor_name"],
            item["room_id"],
            item["room_name"],
            item["time_id"],
            item["day"],
            item["start_time"],
            item["end_time"],
            item["credit_hours"]
        ])

    wb.save(filename)
    print(f"Excel file saved: {filename}")