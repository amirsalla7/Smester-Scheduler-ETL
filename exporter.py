from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime


def export_schedule_to_pdf(schedule, filename="semester_schedule.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("Semester Schedule", styles["Title"])
    subtitle = Paragraph(
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        styles["Normal"]
    )

    elements.append(title)
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(subtitle)
    elements.append(Spacer(1, 0.5 * cm))

    table_data = [[
        "Course ID",
        "Course Name",
        "Instructor Name",
        "Room ID",
        "Day",
        "Start",
        "End",
        "Hours"
    ]]

    for item in schedule:
        table_data.append([
            item.get("course_id", ""),
            item.get("course_name", ""),
            item.get("instructor_name", ""),
            item.get("room_id", ""),
            item.get("day", ""),
            str(item.get("start_time", "")),
            str(item.get("end_time", "")),
            item.get("credit_hours", "")
        ])

    col_widths = [
        2.5 * cm,  # Course ID
        6.0 * cm,  # Course Name
        5.0 * cm,  # Instructor Name
        2.5 * cm,  # Room ID
        3.0 * cm,  # Day
        2.5 * cm,  # Start
        2.5 * cm,  # End
        2.0 * cm   # Hours
    ]

    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
    ]))

    elements.append(table)
    doc.build(elements)

    print(f"PDF file saved: {filename}")