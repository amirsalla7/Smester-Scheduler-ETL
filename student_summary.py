"""
student_summary.py
Builds the summary report from the generated schedule.

Change from original:
- Added "room_name" field to each summary row so the frontend can
  display the human-readable room name (e.g. "A101") instead of the
  integer room_id.
"""

from collections import defaultdict


def build_summary(schedule, course_demand, grad_demand, rooms):
    """
    Build a per-section summary list.

    Args:
        schedule:       list of schedule dicts (output of SchedulerEngine)
        course_demand:  dict {course_id: total_demand_count}
        grad_demand:    dict {course_id: graduating_demand_count}
        rooms:          list of room dicts with keys room_id, capacity

    Returns:
        list of dicts, one entry per schedule row, with keys:
            course_id, course_name, section, room, room_name,
            room_capacity, instructor, students, graduating_students,
            remaining_students, reason
    """

    # Build room_id → capacity lookup
    room_capacity_map = {
        room["room_id"]: int(room.get("capacity") or 0)
        for room in rooms
    }

    # Group schedule rows by course_id (preserves section ordering)
    course_sections = defaultdict(list)
    for item in schedule:
        course_sections[item["course_id"]].append(item)

    summary = []

    for course_id, sections in course_sections.items():
        total_students     = int(course_demand.get(course_id, 0))
        graduating_students = int(grad_demand.get(course_id, 0))
        remaining_students = total_students

        # Sort sections by section_no so they appear in order
        sections = sorted(sections, key=lambda x: x.get("section_no", 0))

        for item in sections:
            room_id  = item["room_id"]
            capacity = room_capacity_map.get(room_id, 0)

            assigned_students   = min(remaining_students, capacity)
            remaining_students -= assigned_students

            # Reason logic — exact strings used by the frontend badge mapper
            if graduating_students > 0:
                reason = "Graduating priority"
            elif total_students >= 20:
                reason = "High demand"
            elif total_students >= 5:
                reason = "Normal demand"
            else:
                reason = "Low demand"

            summary.append({
                "course_id":           item["course_id"],
                "course_name":         item["course_name"],
                "section":             item["section_no"],
                # room_id kept for backward compatibility
                "room":                room_id,
                # room_name is the human-readable name (e.g. "A101")
                "room_name":           item.get("room_name", str(room_id)),
                "room_capacity":       capacity,
                "instructor":          item["instructor_name"],
                "students":            assigned_students,
                "graduating_students": graduating_students,
                "remaining_students":  remaining_students,
                "reason":              reason,
            })

    return summary
