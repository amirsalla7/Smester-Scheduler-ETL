"""
student_summary.py  —  updated
Changes from original:
  • rooms list now expected to carry 'room_type' and 'room_name' keys
    (supplied by the updated web_app.py / save_schedule_edits query)
  • Each summary row now includes:
      - room_name  : human-readable room label  (e.g. "A101")
      - room_type  : room category              (e.g. "Lecture", "Lab")
  • 'room' key kept for backward compatibility (still holds room_id integer)
"""
from collections import defaultdict


def build_summary(schedule, course_demand, grad_demand, rooms):
    """
    Build a per-section summary list.

    Args:
        schedule      : list of schedule dicts (SchedulerEngine or edited output)
        course_demand : dict { course_id → total demand count }
        grad_demand   : dict { course_id → graduating demand count }
        rooms         : list of room dicts with keys:
                          room_id, room_name (=building), capacity, room_type (=type)

    Returns:
        list of dicts with keys:
          course_id, course_name, section,
          room, room_name, room_type, room_capacity,
          instructor, students, graduating_students,
          remaining_students, reason
    """
    # room_id → capacity
    room_capacity_map = {
        room["room_id"]: int(room.get("capacity") or 0)
        for room in rooms
    }

    # room_id → room_name  (building column)
    room_name_map = {
        room["room_id"]: str(room.get("room_name") or room.get("building") or room["room_id"])
        for room in rooms
    }

    # room_id → room_type  (type column, normalised)
    room_type_map = {
        room["room_id"]: str(room.get("room_type") or room.get("type") or "Lecture")
        for room in rooms
    }

    # Group schedule rows by course_id, preserving section order
    course_sections = defaultdict(list)
    for item in schedule:
        course_sections[item["course_id"]].append(item)

    summary = []

    for course_id, sections in course_sections.items():
        total_students      = int(course_demand.get(course_id, 0))
        graduating_students = int(grad_demand.get(course_id, 0))
        remaining_students  = total_students

        sections = sorted(sections, key=lambda x: x.get("section_no", 0))

        for item in sections:
            room_id  = item["room_id"]
            capacity = room_capacity_map.get(room_id, 0)

            assigned_students   = min(remaining_students, capacity)
            remaining_students -= assigned_students

            # Reason strings — must match REASON constants in config.js exactly
            if graduating_students > 0:
                reason = "Graduating priority"
            elif total_students >= 20:
                reason = "High demand"
            elif total_students >= 5:
                reason = "Normal demand"
            else:
                reason = "Low demand"

            summary.append({
                # identifiers
                "course_id":            item["course_id"],
                "course_name":          item["course_name"],
                "section":              item["section_no"],
                # room info — room_name from schedule row takes priority,
                # fall back to the lookup map built from the rooms list
                "room":                 room_id,
                "room_name":            item.get("room_name") or room_name_map.get(room_id, str(room_id)),
                "room_type":            item.get("room_type") or room_type_map.get(room_id, "Lecture"),
                "room_capacity":        capacity,
                # instructor
                "instructor":           item["instructor_name"],
                # students
                "students":             assigned_students,
                "graduating_students":  graduating_students,
                "remaining_students":   remaining_students,
                # reason
                "reason":               reason,
            })

    return summary
