from datetime import datetime, date, timedelta


def parse_datetime(value):
    """Convert an ISO date/time string into a datetime."""
    if isinstance(value, datetime):
        return value

    if not value:
        return None

    value = str(value).strip()

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.combine(date.fromisoformat(value), datetime.min.time())
        except ValueError:
            return None


def parse_bool(value):
    """Safely convert CSV boolean values."""
    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in ("true", "1", "yes")


def overlaps(start1, end1, start2, end2):
    """Return True when two time intervals overlap."""
    return start1 < end2 and start2 < end1


def get_room_capacity(room_id, assignment_start, room_capacities):
    """Find the room capacity effective on the assignment date."""
    assignment_date = assignment_start.date()

    for capacity_record in room_capacities:
        if str(capacity_record.get("room_id")) != str(room_id):
            continue

        effective_from = capacity_record.get("effective_from")
        effective_to = capacity_record.get("effective_to")

        try:
            start_date = date.fromisoformat(str(effective_from)[:10])
            end_date = (
                date.fromisoformat(str(effective_to)[:10])
                if effective_to
                else None
            )
        except (TypeError, ValueError):
            continue

        if start_date <= assignment_date and (
            end_date is None or assignment_date <= end_date
        ):
            return int(capacity_record["capacity"])

    return None


def detect_conflicts(
    exams,
    rooms,
    room_capacities,
    invigilators,
    enrollments,
    accommodations,
    assignments,
    availability,
):
    """
    Detect scheduling conflicts.

    All arguments should be lists of dictionaries, normally loaded from CSV.
    Returns a list of conflict dictionaries.
    """
    conflicts = []

    exam_map = {str(item["id"]): item for item in exams}
    room_map = {str(item["id"]): item for item in rooms}
    invigilator_map = {
        str(item["id"]): item for item in invigilators
    }


    # Map each course to its enrolled students.
    course_students = {}

    for enrollment in enrollments:
        if enrollment.get("status", "active") != "active":
            continue

        course_id = str(enrollment["course_id"])
        student_id = str(enrollment["student_id"])

        course_students.setdefault(course_id, set()).add(student_id)

    # Map students to their accommodations.
    student_accommodations = {}

    for accommodation in accommodations:
        student_id = str(accommodation["student_id"])
        student_accommodations.setdefault(student_id, []).append(
            accommodation
        )

    valid_assignments = []

    # ---------------------------------------------------------
    # 1. Validate each assignment and check room capacity
    # ---------------------------------------------------------
    for assignment in assignments:
        exam_id = str(assignment["exam_id"])
        room_id = str(assignment["room_id"])
        invigilator_id = str(assignment["invigilator_id"])

        exam = exam_map.get(exam_id)
        room = room_map.get(room_id)
        invigilator = invigilator_map.get(invigilator_id)

        if exam is None or room is None or invigilator is None:
            conflicts.append({
                "issue_type": "invalid_reference",
                "exam_id": exam_id,
                "room_id": room_id,
                "description": "Assignment references an unknown exam, room, or invigilator.",
            })
            continue
        if not parse_bool(invigilator.get("is_active", True)):
            conflicts.append({
                "issue_type": "inactive_invigilator_assigned",
                "exam_id": exam_id,
                "invigilator_id": invigilator_id,
                "description": "An inactive invigilator is assigned to an exam.",
            })

        start = parse_datetime(assignment.get("start_time"))
        end = parse_datetime(assignment.get("end_time"))

        if start is None or end is None or start >= end:
            conflicts.append({
                "issue_type": "invalid_assignment_time",
                "exam_id": exam_id,
                "description": "Assignment has missing or invalid start/end times.",
            })
            continue

        valid_assignments.append(assignment)

        capacity = get_room_capacity(
            room_id,
            start,
            room_capacities,
        )

        assigned_capacity = int(assignment.get("assigned_capacity", 0))

        if capacity is None:
            conflicts.append({
                "issue_type": "missing_room_capacity",
                "exam_id": exam_id,
                "room_id": room_id,
                "description": "No effective room capacity was found.",
            })
        elif assigned_capacity > capacity:
            conflicts.append({
                "issue_type": "room_capacity_exceeded",
                "exam_id": exam_id,
                "room_id": room_id,
                "assigned_capacity": assigned_capacity,
                "room_capacity": capacity,
                "description": "Assigned students exceed room capacity.",
            })

        # -----------------------------------------------------
        # 2. Check room availability and closures
        # -----------------------------------------------------
        for slot in availability:
            if str(slot.get("room_id")) != room_id:
                continue

            if parse_bool(slot.get("is_available")):
                continue

            blocked_start = parse_datetime(slot.get("start_time"))
            blocked_end = parse_datetime(slot.get("end_time"))

            if (
                blocked_start
                and blocked_end
                and overlaps(start, end, blocked_start, blocked_end)
            ):
                conflicts.append({
                    "issue_type": "exam_outside_room_availability",
                    "exam_id": exam_id,
                    "room_id": room_id,
                    "description": "Exam is scheduled during a room closure or unavailable period.",
                })

        # -----------------------------------------------------
        # 3. Check invigilator availability
        # -----------------------------------------------------
        for slot in availability:
            if str(slot.get("invigilator_id")) != invigilator_id:
                continue

            if parse_bool(slot.get("is_available")):
                continue

            blocked_start = parse_datetime(slot.get("start_time"))
            blocked_end = parse_datetime(slot.get("end_time"))

            if (
                blocked_start
                and blocked_end
                and overlaps(start, end, blocked_start, blocked_end)
            ):
                conflicts.append({
                    "issue_type": "invigilator_unavailable",
                    "exam_id": exam_id,
                    "invigilator_id": invigilator_id,
                    "description": "Invigilator is assigned during an unavailable period.",
                })

        # -----------------------------------------------------
        # 4. Verify full room and invigilator availability
        # -----------------------------------------------------
        room_covered = any(
            str(slot.get("room_id")) == room_id
            and parse_bool(slot.get("is_available"))
            and (slot_start := parse_datetime(slot.get("start_time"))) is not None
            and (slot_end := parse_datetime(slot.get("end_time"))) is not None
            and slot_start <= start
            and slot_end >= end
            for slot in availability
        )

        if not room_covered:
            conflicts.append({
                "issue_type": "room_availability_not_confirmed",
                "exam_id": exam_id,
                "room_id": room_id,
                "description": "No available room slot covers the entire exam duration.",
            })

        invigilator_covered = any(
            str(slot.get("invigilator_id")) == invigilator_id
            and parse_bool(slot.get("is_available"))
            and (slot_start := parse_datetime(slot.get("start_time"))) is not None
            and (slot_end := parse_datetime(slot.get("end_time"))) is not None
            and slot_start <= start
            and slot_end >= end
            for slot in availability
        )

        if not invigilator_covered:
            conflicts.append({
                "issue_type": "invigilator_availability_not_confirmed",
                "exam_id": exam_id,
                "invigilator_id": invigilator_id,
                "description": "No available invigilator slot covers the entire exam duration.",
            })

        # ---------------------------------------------------------
    # 4. Check room double-booking
    # ---------------------------------------------------------
    for index, first in enumerate(valid_assignments):
        for second in valid_assignments[index + 1:]:
            if str(first["room_id"]) != str(second["room_id"]):
                continue

            first_start = parse_datetime(first["start_time"])
            first_end = parse_datetime(first["end_time"])
            second_start = parse_datetime(second["start_time"])
            second_end = parse_datetime(second["end_time"])

            if overlaps(first_start, first_end, second_start, second_end):
                conflicts.append({
                    "issue_type": "room_double_booked",
                    "exam_id": str(second["exam_id"]),
                    "other_exam_id": str(first["exam_id"]),
                    "room_id": str(first["room_id"]),
                    "description": "The same room is assigned to overlapping exams.",
                })



    # ---------------------------------------------------------
    # 4. Check invigilator double-booking
    # ---------------------------------------------------------
    for index, first in enumerate(valid_assignments):
        for second in valid_assignments[index + 1:]:
            if str(first["invigilator_id"]) != str(second["invigilator_id"]):
                continue

            first_start = parse_datetime(first["start_time"])
            first_end = parse_datetime(first["end_time"])
            second_start = parse_datetime(second["start_time"])
            second_end = parse_datetime(second["end_time"])

            if overlaps(first_start, first_end, second_start, second_end):
                conflicts.append({
                    "issue_type": "invigilator_double_booked",
                    "exam_id": str(second["exam_id"]),
                    "other_exam_id": str(first["exam_id"]),
                    "invigilator_id": str(first["invigilator_id"]),
                    "description": "The same invigilator is assigned to overlapping exams.",
                })

    # ---------------------------------------------------------
    # 5. Check student overlapping exams and accommodations
    # ---------------------------------------------------------
    student_exam_slots = {}

    for assignment in valid_assignments:
        exam = exam_map.get(str(assignment["exam_id"]))

        if exam is None:
            continue

        course_id = str(exam["course_id"])
        exam_id = str(exam["id"])
        start = parse_datetime(assignment["start_time"])

        duration = int(exam.get("duration_minutes", 0))
        standard_end = start + timedelta(minutes=duration)

        enrolled_students = course_students.get(course_id, set())

        for student_id in enrolled_students:
            extra_minutes = 0

            for accommodation in student_accommodations.get(student_id, []):
                accommodation_type = str(
                    accommodation.get("accommodation_type", "")
                ).lower()

                if accommodation_type not in (
                    "extra_time",
                    "extended_time",
                    "extra_minutes",
                ):
                    continue

                effective_from = accommodation.get("effective_from")
                effective_to = accommodation.get("effective_to")

                try:
                    from_date = date.fromisoformat(str(effective_from)[:10])
                    to_date = (
                        date.fromisoformat(str(effective_to)[:10])
                        if effective_to
                        else None
                    )
                except (TypeError, ValueError):
                    continue

                if from_date <= start.date() and (
                    to_date is None or start.date() <= to_date
                ):
                    extra_minutes = max(
                        extra_minutes,
                        int(accommodation.get("extra_minutes", 0)),
                    )

            student_end = standard_end + timedelta(minutes=extra_minutes)

            if extra_minutes > 0:
                assigned_end = parse_datetime(assignment["end_time"])

                if assigned_end < student_end:
                    conflicts.append({
                        "issue_type": "accommodation_ignored",
                        "exam_id": exam_id,
                        "student_id": student_id,
                        "required_extra_minutes": extra_minutes,
                        "description": "Assignment ends before the student's accommodated exam duration.",
                    })

            student_exam_slots.setdefault(student_id, []).append({
                "exam_id": exam_id,
                "start": start,
                "end": student_end,
            })

    for student_id, slots in student_exam_slots.items():
        for index, first in enumerate(slots):
            for second in slots[index + 1:]:
                if overlaps(
                    first["start"],
                    first["end"],
                    second["start"],
                    second["end"],
                ):
                    conflicts.append({
                        "issue_type": "student_overlapping_exams",
                        "student_id": student_id,
                        "exam_id": second["exam_id"],
                        "other_exam_id": first["exam_id"],
                        "description": "Student has two exams scheduled at overlapping times.",
                    })

    return conflicts
