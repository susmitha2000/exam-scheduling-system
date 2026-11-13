
import csv
import json
import shutil
from pathlib import Path

from app.services.conflict_detector import detect_conflicts


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ANOMALY_DIR = DATA_DIR / "anomalies"

FILES = [
    "exams.csv",
    "rooms.csv",
    "room_capacities.csv",
    "invigilators.csv",
    "enrollments.csv",
    "accommodations.csv",
    "schedule_assignments.csv",
    "availability.csv",
]


def load_csv(folder, filename):
    with (folder / filename).open(
        "r", newline="", encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def save_csv(folder, filename, rows):
    if not rows:
        return

    with (folder / filename).open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def create_scenario(scenario_id):
    folder = ANOMALY_DIR / scenario_id

    if folder.exists():
        shutil.rmtree(folder)

    folder.mkdir(parents=True)

    for filename in FILES:
        shutil.copy2(DATA_DIR / filename, folder / filename)

    return folder


def detect_scenario(folder):
    conflicts = detect_conflicts(
        exams=load_csv(folder, "exams.csv"),
        rooms=load_csv(folder, "rooms.csv"),
        room_capacities=load_csv(folder, "room_capacities.csv"),
        invigilators=load_csv(folder, "invigilators.csv"),
        enrollments=load_csv(folder, "enrollments.csv"),
        accommodations=load_csv(folder, "accommodations.csv"),
        assignments=load_csv(folder, "schedule_assignments.csv"),
        availability=load_csv(folder, "availability.csv"),
    )

    report = folder / "conflict_report.json"

    with report.open("w", encoding="utf-8") as file:
        json.dump(conflicts, file, indent=4)

    return conflicts



def scenario_1_student_overlap():
    folder = create_scenario("ANOM-001")

    exams = load_csv(folder, "exams.csv")
    enrollments = load_csv(folder, "enrollments.csv")
    accommodations = load_csv(folder, "accommodations.csv")

    first = next(
        e for e in exams if e["id"] == "EXAM-2027-000001"
    )
    second = next(
        e for e in exams if e["id"] == "EXAM-2027-000002"
    )

    accommodated_students = {
        item["student_id"] for item in accommodations
    }

    first_course_students = {
        e["student_id"]
        for e in enrollments
        if e["course_id"] == first["course_id"]
    }

    student_id = next(
        e["student_id"]
        for e in enrollments
        if e["course_id"] == second["course_id"]
        and e["student_id"] not in accommodated_students
        and e["student_id"] not in first_course_students
    )

    enrollments.append({
        **enrollments[0],
        "id": "ANOM-ENR-001",
        "student_id": student_id,
        "course_id": first["course_id"],
    })

    save_csv(folder, "enrollments.csv", enrollments)

    return folder



def scenario_2_room_capacity():
    folder = create_scenario("ANOM-002")

    assignments = load_csv(folder, "schedule_assignments.csv")
    capacities = load_csv(folder, "room_capacities.csv")

    assignment = assignments[0]

    capacity = next(
        int(item["capacity"])
        for item in capacities
        if item["room_id"] == assignment["room_id"]
    )

    assignment["assigned_capacity"] = str(capacity + 1)

    save_csv(folder, "schedule_assignments.csv", assignments)

    return folder


def scenario_3_invigilator_double_booking():
    folder = create_scenario("ANOM-003")

    assignments = load_csv(folder, "schedule_assignments.csv")

    first = assignments[0]
    second = assignments[1]

    second["invigilator_id"] = first["invigilator_id"]
    second["start_time"] = first["start_time"]
    second["end_time"] = first["end_time"]

    save_csv(folder, "schedule_assignments.csv", assignments)

    return folder



def scenario_4_accommodation_ignored():
    folder = create_scenario("ANOM-004")

    exams = load_csv(folder, "exams.csv")
    enrollments = load_csv(folder, "enrollments.csv")
    accommodations = load_csv(folder, "accommodations.csv")
    assignments = load_csv(folder, "schedule_assignments.csv")

    # Select one student who has extra exam time.
    accommodation = next(
        item for item in accommodations
        if int(item.get("extra_minutes", 0)) > 0
    )

    student_id = accommodation["student_id"]

    enrollment = next(
        item for item in enrollments
        if item["student_id"] == student_id
        and item.get("status", "active") == "active"
    )

    course_id = enrollment["course_id"]

    exam = next(
        item for item in exams
        if item["course_id"] == course_id
    )

    assignment = next(
        item for item in assignments
        if item["exam_id"] == exam["id"]
    )

    # Keep only this student's accommodation for this course.
    course_student_ids = {
        item["student_id"]
        for item in enrollments
        if item["course_id"] == course_id
        and item.get("status", "active") == "active"
    }

    accommodations = [
        item for item in accommodations
        if item["student_id"] not in course_student_ids
        or item["student_id"] == student_id
    ]

    save_csv(folder, "accommodations.csv", accommodations)

    # Shorten the assignment to the standard exam duration.
    from datetime import datetime, timedelta

    start = datetime.fromisoformat(
        assignment["start_time"].replace("Z", "+00:00")
    )

    standard_end = start + timedelta(
        minutes=int(exam["duration_minutes"])
    )

    assignment["end_time"] = standard_end.isoformat()

    save_csv(folder, "schedule_assignments.csv", assignments)

    return folder


def scenario_5_room_closure():
    folder = create_scenario("ANOM-005")

    assignments = load_csv(folder, "schedule_assignments.csv")
    availability = load_csv(folder, "availability.csv")

    assignment = assignments[0]

    closure = {key: "" for key in availability[0].keys()}
    closure.update({
        "id": "ANOM-AV-005",
        "invigilator_id": "",
        "room_id": assignment["room_id"],
        "start_time": assignment["start_time"],
        "end_time": assignment["end_time"],
        "is_available": "False",
        "reason": "Injected room closure anomaly",
    })

    availability.append(closure)

    save_csv(folder, "availability.csv", availability)

    return folder


def main():
    ANOMALY_DIR.mkdir(parents=True, exist_ok=True)

    scenarios = [
        ("ANOM-001", scenario_1_student_overlap),
        ("ANOM-002", scenario_2_room_capacity),
        ("ANOM-003", scenario_3_invigilator_double_booking),
        ("ANOM-004", scenario_4_accommodation_ignored),
        ("ANOM-005", scenario_5_room_closure),
    ]

    summary = []

    for scenario_id, create_function in scenarios:
        folder = create_function()
        conflicts = detect_scenario(folder)

        summary.append({
            "scenario_id": scenario_id,
            "conflicts_detected": len(conflicts),
            "detected_issue_types": sorted({
                item["issue_type"] for item in conflicts
            }),
        })

    summary_path = ANOMALY_DIR / "anomaly_test_summary.json"

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    print("\nANOMALY DETECTION SUMMARY")
    print("-------------------------")

    for item in summary:
        print(
            f'{item["scenario_id"]}: '
            f'{item["conflicts_detected"]} conflict(s) detected'
        )
        print(f'  Types: {item["detected_issue_types"]}')

    print(f"\nSummary saved to: {summary_path}")


if __name__ == "__main__":
    main()
