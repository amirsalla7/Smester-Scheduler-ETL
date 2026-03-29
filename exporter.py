from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def export_schedule_to_pdf(schedule, filename="schedule.pdf"):

    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4)
    )

    styles = getSampleStyleSheet()

    title = Paragraph(
        "Semester Schedule",
        styles["Title"]
    )

    table_data = [[
        "Schedule ID",
        "Course ID",
        "Course Name",
        "Instructor ID",
        "Instructor Name",
        "Room ID",
        "Room",
        "Time ID",
        "Day",
        "Start",
        "End",
        "Hours"
    ]]

    for item in schedule:

        table_data.append([
            item["schedule_id"],
            item["course_id"],
            item["course_name"],
            item["instructor_id"],
            item["instructor_name"],
            item["room_id"],
            item["room_name"],
            item["time_id"],
            item["day"],
            str(item["start_time"]),
            str(item["end_time"]),
            item["credit_hours"]
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([

        ("FONT", (0, 0), (-1, -1), "Helvetica", 8),

        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),

        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.whitesmoke,
            colors.transparent
        ])

    ]))

    elements = [
        title,
        table
    ]

    doc.build(elements)

    print(f"PDF file saved: {filename}")