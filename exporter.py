from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm

def export_summary_to_pdf(summary, filename="summary.pdf"):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename)
    elements = []

    elements.append(Paragraph("Course Summary Report", styles["Heading1"]))
    elements.append(Spacer(1, 10))

    table_data = [[
        "Course",
        "Section",
        "Room",
        "Capacity",
        "Type",
        "Instructor",
        "Assigned",
        "Graduating",
        "Remaining",
        "Reason"
    ]]

    for s in summary:
        table_data.append([
            s["course_name"],
            s["section"],
            s["room"],
            s["room_capacity"],
            s["room_type"],
            s["instructor"],
            s["students"],
            s["graduating_students"],
            s["remaining_students"],
            s["reason"]
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    elements.append(table)
    doc.build(elements)

    print(f"Summary PDF saved: {filename}")

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
        "Section",
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
            item.get("section_no", ""),
            item.get("instructor_name", ""),
            item.get("room_id", ""),
            item.get("day", ""),
            str(item.get("start_time", "")),
            str(item.get("end_time", "")),
            item.get("credit_hours", "")
        ])

    col_widths = [
        2.2 * cm,
        5.5 * cm,
        2.0 * cm,
        4.8 * cm,
        2.2 * cm,
        3.0 * cm,
        2.3 * cm,
        2.3 * cm,
        1.8 * cm
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