
import csv
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_csv(name):
    with open(DATA_DIR / f"{name}.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))

errors = []
checks = 0

def check(condition, message):
    global checks
    checks += 1
    if not condition:
        errors.append(message)

# Load datasets
students = load_csv("students")
courses = load_csv("courses")
enrollments = load_csv("enrollments")
exams = load_csv("exams")
rooms = load_csv("rooms")
capacities = load_csv("room_capacities")
invigilators = load_csv("invigilators")
assignments = load_csv("schedule_assignments")
availability = load_csv("availability")
accommodations = load_csv("accommodations")

print("Starting data validation...")

# 1. Expected row counts from generation summary
with open(DATA_DIR / "generation_summary.json", encoding="utf-8") as f:
    summary = json.load(f)

expected = {
    "students": (students, summary["students"]),
    "courses": (courses, summary["courses"]),
    "enrollments": (enrollments, summary["enrollments"]),
    "exams": (exams, summary["exams"]),
    "rooms": (rooms, summary["rooms"]),
    "invigilators": (invigilators, summary["invigilators"]),
    "accommodations": (accommodations, summary["accommodations"]),
    "schedule assignments": (
        assignments,
        summary["schedule_assignments"],
    ),
}

for name, (records, count) in expected.items():
    check(
        len(records) == count,
        f"{name}: expected {count}, got {len(records)}",
    )
# 2. Primary key uniqueness
for name, records, field in [
    ("students", students, "id"),
    ("courses", courses, "id"),
    ("exams", exams, "id"),
    ("rooms", rooms, "id"),
    ("invigilators", invigilators, "id"),
    ("assignments", assignments, "id"),
]:
    values = [r[field] for r in records]
    check(len(values) == len(set(values)), f"Duplicate primary keys in {name}")

# 3. Foreign key integrity
student_ids = {r["id"] for r in students}
course_ids = {r["id"] for r in courses}
exam_ids = {r["id"] for r in exams}
room_ids = {r["id"] for r in rooms}
invigilator_ids = {r["id"] for r in invigilators}

for row in enrollments:
    check(row["student_id"] in student_ids, "Invalid enrollment student FK")
    check(row["course_id"] in course_ids, "Invalid enrollment course FK")

for row in exams:
    check(row["course_id"] in course_ids, "Invalid exam course FK")
    start = datetime.fromisoformat(row["start_time"])
    end = datetime.fromisoformat(row["end_time"])
    check(end > start, f"Invalid exam time: {row['id']}")
    check(int(row["duration_minutes"]) > 0, "Invalid exam duration")

for row in assignments:
    check(row["exam_id"] in exam_ids, "Invalid assignment exam FK")
    check(row["room_id"] in room_ids, "Invalid assignment room FK")
    check(row["invigilator_id"] in invigilator_ids,
          "Invalid assignment invigilator FK")

for row in accommodations:
    check(row["student_id"] in student_ids, "Invalid accommodation student FK")

for row in capacities:
    check(row["room_id"] in room_ids, "Invalid room capacity FK")

# 4. Room capacity validation
room_capacity = {
    row["room_id"]: int(row["capacity"])
    for row in capacities
}

for row in assignments:
    capacity = room_capacity.get(row["room_id"], 0)
    assigned = int(row["assigned_capacity"])
    check(assigned <= capacity,
          f"Room capacity exceeded: {row['id']}")

# 5. Assignment time validation
room_slots = defaultdict(list)
invigilator_slots = defaultdict(list)

for row in assignments:
    start = datetime.fromisoformat(row["start_time"])
    end = datetime.fromisoformat(row["end_time"])

    check(end > start, f"Invalid assignment time: {row['id']}")

    room_slots[row["room_id"]].append((start, end, row["id"]))
    invigilator_slots[row["invigilator_id"]].append(
        (start, end, row["id"])
    )

def check_overlaps(groups, label):
    for resource_id, slots in groups.items():
        slots.sort()
        for i in range(len(slots)):
            for j in range(i + 1, len(slots)):
                start1, end1, id1 = slots[i]
                start2, end2, id2 = slots[j]

                if start2 < end1 and start1 < end2:
                    errors.append(
                        f"{label} double booking: {resource_id}: {id1}, {id2}"
                    )

check_overlaps(room_slots, "Room")
check_overlaps(invigilator_slots, "Invigilator")

# 6. Accommodation effective dates
for row in accommodations:
    if row["effective_to"]:
        check(
            row["effective_to"] >= row["effective_from"],
            f"Invalid accommodation dates: {row['id']}"
        )

# 7. Enrollment duplicate validation
pairs = [(r["student_id"], r["course_id"]) for r in enrollments]
check(len(pairs) == len(set(pairs)), "Duplicate student-course enrollments")

# 8. Ground truth validation
import json

with open(DATA_DIR / "ground_truth.json", encoding="utf-8") as f:
    ground_truth = json.load(f)

check(len(ground_truth) == 5, "Expected five anomaly scenarios")
check(
    len({item["scenario_id"] for item in ground_truth}) == 5,
    "Duplicate anomaly scenario IDs"
)

print("\nVALIDATION SUMMARY")
print("------------------")
print(f"Checks executed: {checks}")
print(f"Errors found: {len(errors)}")

if errors:
    print("\nVALIDATION ERRORS:")
    for error in errors:
        print("-", error)
else:
    print("\nAll baseline validation checks passed!")
