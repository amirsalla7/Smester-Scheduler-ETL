import os
import tempfile
import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
    PageBreak
)
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from datetime import datetime


def generate_demand_chart(offerings, output_path):
    filtered = [o for o in offerings if o.get("total_demand", 0) > 0]
    filtered.sort(key=lambda x: x.get("total_demand", 0), reverse=True)
    filtered = filtered[:10]

    if not filtered:
        return None

    course_names = [o["course_name"] for o in filtered]
    demand_values = [o["total_demand"] for o in filtered]

    plt.figure(figsize=(12, 6))
    plt.bar(course_names, demand_values)
    plt.title("Number of Students Eligible to Register per Course")
    plt.xlabel("Course")
    plt.ylabel("Eligible Students Count")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    return output_path


def export_schedule_to_pdf(schedule, offerings, filename="semester_schedule.pdf"):
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

    # =========================
    # MAIN SCHEDULE TABLE
    # =========================
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
        2.2 * cm,  # Course ID
        5.5 * cm,  # Course Name
        2.0 * cm,  # Section
        4.8 * cm,  # Instructor Name
        2.2 * cm,  # Room ID
        3.0 * cm,  # Day
        2.3 * cm,  # Start
        2.3 * cm,  # End
        1.8 * cm   # Hours
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
    elements.append(PageBreak())

    # =========================
    # DEMAND CHART
    # =========================
    chart_title = Paragraph("Course Demand Chart", styles["Title"])
    elements.append(chart_title)
    elements.append(Spacer(1, 0.5 * cm))

    temp_chart = os.path.join(tempfile.gettempdir(), "course_demand_chart.png")
    chart_path = generate_demand_chart(offerings, temp_chart)

    if chart_path and os.path.exists(chart_path):
        chart_img = Image(chart_path, width=24 * cm, height=12 * cm)
        elements.append(chart_img)
        elements.append(Spacer(1, 0.6 * cm))

    # =========================
    # DEMAND SUMMARY TABLE
    # =========================
    summary_title = Paragraph("Eligible Students per Course", styles["Heading2"])
    elements.append(summary_title)
    elements.append(Spacer(1, 0.3 * cm))

    demand_table_data = [[
        "Course ID",
        "Course Name",
        "Eligible Students",
        "Graduating Students",
        "Open Status"
    ]]

    for item in sorted(offerings, key=lambda x: x.get("total_demand", 0), reverse=True):
        demand_table_data.append([
            item.get("course_id", ""),
            item.get("course_name", ""),
            item.get("total_demand", 0),
            item.get("graduating_demand", 0),
            "OPEN" if item.get("should_open", False) else "CLOSED"
        ])

    demand_table = Table(
        demand_table_data,
        colWidths=[2.5 * cm, 7 * cm, 3.5 * cm, 3.5 * cm, 3 * cm],
        repeatRows=1
    )

    demand_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))

    elements.append(demand_table)

    doc.build(elements)

    print(f"PDF file saved: {filename}")