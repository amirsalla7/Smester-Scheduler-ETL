from collections import defaultdict


def build_summary(schedule, course_demand, grad_demand, rooms):
    room_capacity_map = {
        room["room_id"]: int(room.get("capacity") or 0)
        for room in rooms
    }

    course_sections = defaultdict(list)
    for item in schedule:
        course_sections[item["course_id"]].append(item)

    summary = []

    for course_id, sections in course_sections.items():
        total_students = int(course_demand.get(course_id, 0))
        graduating_students = int(grad_demand.get(course_id, 0))
        remaining_students = total_students

        sections = sorted(sections, key=lambda x: x.get("section_no", 0))

        for item in sections:
            room_id = item["room_id"]
            capacity = room_capacity_map.get(room_id, 0)

            assigned_students = min(remaining_students, capacity)
            remaining_students -= assigned_students

            if graduating_students > 0:
                reason = "Graduating priority"
            elif total_students >= 20:
                reason = "High demand"
            elif total_students >= 5:
                reason = "Normal demand"
            else:
                reason = "Low demand"

            summary.append({
                "course_id": item["course_id"],
                "course_name": item["course_name"],
                "section": item["section_no"],
                "room": room_id,
                "room_capacity": capacity,
                "instructor": item["instructor_name"],
                "students": assigned_students,
                "graduating_students": graduating_students,
                "remaining_students": remaining_students,
                "reason": reason
            })

    return summary