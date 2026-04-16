"""
scheduler_engine_room_patch.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOW TO USE
──────────
This file is NOT meant to run standalone. It shows exactly what
to change inside your existing scheduler_engine.py to implement
Feature 2: "largest suitable room → highest student demand".

STEP 1  Copy the helper functions below into SchedulerEngine
        (anywhere before generate_schedule).

STEP 2  Inside generate_schedule(), find the place where you
        assign a room_id to a section. Replace that section
        with the call pattern shown at the bottom of this file.

STEP 3  Make sure each schedule row now includes room_type.
        See the row-building section at the bottom.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


# ── STEP 1: Add these two methods to SchedulerEngine ──────────────────────────

def _sort_rooms_by_capacity(self, rooms, descending=True):
    """
    Return rooms sorted by capacity.
    descending=True → largest first (use for demand-matching).
    """
    return sorted(
        rooms,
        key=lambda r: int(r.get("capacity") or 0),
        reverse=descending,
    )


def _pick_room_for_demand(self, demand, available_rooms):
    """
    Given a student demand count and a list of available rooms,
    return the best-fit room:

      1. Find all rooms with capacity >= demand (suitable rooms).
      2. From those, return the SMALLEST one that still fits
         (avoids wasting a 200-seat auditorium on 30 students).
      3. If no room fits the demand, return the LARGEST available
         as a fallback (better than no assignment).

    Args:
        demand          : int  — total_demand for the course section
        available_rooms : list — room dicts with at least room_id, capacity

    Returns:
        room dict, or None if available_rooms is empty
    """
    if not available_rooms:
        return None

    suitable = [
        r for r in available_rooms
        if int(r.get("capacity") or 0) >= demand
    ]

    if suitable:
        # Best fit = smallest room that still covers the demand
        return min(suitable, key=lambda r: int(r.get("capacity") or 0))
    else:
        # No room is large enough — use the biggest available
        return max(available_rooms, key=lambda r: int(r.get("capacity") or 0))


# ── STEP 2: Replace room-assignment block in generate_schedule() ───────────────
#
# BEFORE (typical pattern):
#
#   room = available_rooms[0]   # or random.choice(available_rooms)
#   room_id = room["room_id"]
#
# AFTER (demand-aware):
#
#   room = self._pick_room_for_demand(section_demand, available_rooms)
#   if room is None:
#       continue   # skip this section — no room available
#   room_id = room["room_id"]
#
# NOTE: 'section_demand' is the total_demand value for this specific section.
#       It should already be in scope wherever you build each schedule row.
# ────────────────────────────────────────────────────────────────────────────────


# ── STEP 3: Add room_type to each schedule row ────────────────────────────────
#
# When building the schedule row dict in generate_schedule(), add room_type:
#
#   row = {
#       "schedule_id":       ...,
#       "course_id":         ...,
#       "course_name":       ...,
#       "section_no":        ...,
#       "total_demand":      ...,
#       "graduating_demand": ...,
#       "instructor_id":     ...,
#       "instructor_name":   ...,
#       "room_id":           room["room_id"],
#       "room_name":         room.get("building") or room.get("room_name", ""),
#       "room_type":         room.get("type") or room.get("room_type", "Lecture"),  # ← ADD THIS
#       "time_id":           ...,
#       "day":               ...,
#       "start_time":        ...,
#       "end_time":          ...,
#       "credit_hours":      ...,
#   }
#
# The room dict loaded from the DB (via load_data) will have the "type" column
# because the room table has: room_id, building, capacity, type
# ────────────────────────────────────────────────────────────────────────────────


# ── STEP 4: Ensure load_data() fetches room_type ─────────────────────────────
#
# In SchedulerEngine.load_data(), the rooms query should include the type column.
# Typical current query:
#
#   SELECT room_id, building, ISNULL(capacity, 40) AS capacity FROM room
#
# Updated query:
#
#   SELECT
#       room_id,
#       building,
#       ISNULL(capacity,  40)       AS capacity,
#       ISNULL(type, 'Lecture')     AS room_type
#   FROM room
#
# Alternatively, if your query already selects all columns, just make sure
# the "type" key is accessible as room.get("type") or room.get("room_type").
# ────────────────────────────────────────────────────────────────────────────────


# ── COMPLETE EXAMPLE of the demand-sorted assignment loop ─────────────────────
#
# If your current generate_schedule() iterates over courses sorted by demand
# and assigns rooms, here is a complete example of the updated loop pattern:
#
#   # Sort courses by demand, highest first (already the case in most engines)
#   sorted_courses = sorted(
#       self.course_offerings,
#       key=lambda c: c.get("total_demand", 0),
#       reverse=True
#   )
#
#   used_rooms_this_slot = set()   # reset per time slot
#
#   for course in sorted_courses:
#       demand     = course.get("total_demand", 0)
#       free_rooms = [
#           r for r in self.rooms
#           if r["room_id"] not in used_rooms_this_slot
#       ]
#
#       room = self._pick_room_for_demand(demand, free_rooms)
#       if room is None:
#           continue
#
#       used_rooms_this_slot.add(room["room_id"])
#       # build row with room_type included …
#
# ────────────────────────────────────────────────────────────────────────────────
