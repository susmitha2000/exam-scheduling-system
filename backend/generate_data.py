

import argparse
import csv
import json
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

from app.database import Base, engine, SessionLocal
from app.models.entities import (
    Student,
    Course,
    Enrollment,
    Exam,
    ExamRequirement,
    Room,
    RoomCapacity,
    Invigilator,
    Availability,
    Accommodation,
    ScheduleAssignment,
)

# Configurable dataset generation.
parser = argparse.ArgumentParser(
    description="Generate reproducible synthetic exam scheduling data."
)

parser.add_argument("--students", type=int, default=5000)
parser.add_argument("--courses", type=int, default=100)
parser.add_argument("--exams", type=int, default=300)
parser.add_argument("--rooms", type=int, default=100)
parser.add_argument("--invigilators", type=int, default=200)
parser.add_argument("--seed", type=int, default=20261022)

args = parser.parse_args()

STUDENT_COUNT = args.students
COURSE_COUNT = args.courses
EXAM_COUNT = args.exams
ROOM_COUNT = args.rooms
INVIGILATOR_COUNT = args.invigilators
SEED = args.seed

if STUDENT_COUNT < 1:
    parser.error("Students must be at least 1.")

if COURSE_COUNT < 1:
    parser.error("Courses must be at least 1.")

if STUDENT_COUNT < COURSE_COUNT:
    parser.error("Students must be at least the number of courses.")

if EXAM_COUNT < 2:
    parser.error("At least 2 exams are required for anomaly testing.")

if COURSE_COUNT > EXAM_COUNT:
    parser.error("Courses cannot exceed exams.")

if ROOM_COUNT < 5:
    parser.error("At least 5 rooms are required.")

if INVIGILATOR_COUNT < 5:
    parser.error("At least 5 invigilators are required.")

random.seed(SEED)

BASE_DATE = date(2027, 1, 4)
GENERATED_AT = datetime(2026, 1, 1, 0, 0, 0)
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# Start with a fresh, reproducible database.
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

students = []
courses = []
enrollments = []
exams = []
rooms = []
capacities = []
invigilators = []
availability = []
accommodations = []
assignments = []

student_course = {}

# 1. Students: distribute students evenly across courses.
for i in range(1, STUDENT_COUNT + 1):
    course_number = ((i - 1) % COURSE_COUNT) + 1
    student_id = f"STU-{i:06d}"
    course_id = f"CRS-{course_number:06d}"

    student = Student(
        id=student_id,
        full_name=f"Student {i:05d}",
        email=f"student{i:05d}@example.edu",
        department=f"Department {(course_number - 1) % 10 + 1}",
        created_at=GENERATED_AT,
    )
    students.append(student)
    student_course[student_id] = course_id

    enrollments.append(
        Enrollment(
            student_id=student_id,
            course_id=course_id,
            enrolled_on=BASE_DATE - timedelta(days=60),
            status="active",
        )
    )

# 2. Courses: 100 courses.
for i in range(1, COURSE_COUNT + 1):
    courses.append(
        Course(
            id=f"CRS-{i:06d}",
            code=f"COURSE-{i:03d}",
            name=f"Academic Course {i:03d}",
            department=f"Department {(i - 1) % 10 + 1}",
        )
    )

# 3. Rooms and capacities: 100 rooms.
for i in range(1, ROOM_COUNT + 1):
    room_id = f"ROOM-{i:06d}"
    rooms.append(
        Room(
            id=room_id,
            name=f"Room {i:03d}",
            building=f"Building {(i - 1) // 20 + 1}",
            room_type="standard",
            has_projector=(i % 3 == 0),
            has_computers=(i % 5 == 0),
            is_accessible=(i % 4 == 0),
        )
    )

    capacities.append(
        RoomCapacity(
            room_id=room_id,
            capacity=random.randint(65, 100),
            effective_from=BASE_DATE - timedelta(days=365),
            effective_to=None,
        )
    )

# 4. Invigilators: 200 invigilators.
for i in range(1, INVIGILATOR_COUNT + 1):
    invigilators.append(
        Invigilator(
            id=f"INV-{i:06d}",
            full_name=f"Invigilator {i:03d}",
            email=f"invigilator{i:03d}@example.edu",
            department=f"Department {(i - 1) % 10 + 1}",
            is_active=True,
        )
    )

# 5. Student accommodations: one student in every 20 gets 30 extra minutes.
accommodation_students = set()

for i in range(1, STUDENT_COUNT + 1, 20):
    student_id = f"STU-{i:06d}"
    accommodation_students.add(student_id)

    accommodations.append(
        Accommodation(
            student_id=student_id,
            accommodation_type="extra_time",
            extra_minutes=30,
            details="Synthetic extended-time accommodation",
            effective_from=BASE_DATE - timedelta(days=30),
            effective_to=None,
        )
    )

# 6. Exams and valid baseline assignments.
for i in range(EXAM_COUNT):
    course_number = (i % COURSE_COUNT) + 1
    course_id = f"CRS-{course_number:06d}"
    exam_id = f"EXAM-2027-{i + 1:06d}"

    exam_day = BASE_DATE + timedelta(days=i // 10)
    slot = i % 10

    start = datetime.combine(
        exam_day,
        time(9, 0) if slot < 5 else time(14, 0),
    )

    duration = 180
    end = start + timedelta(minutes=duration)

    room_id = f"ROOM-{(i % ROOM_COUNT) + 1:06d}"
    invigilator_id = f"INV-{(i % INVIGILATOR_COUNT) + 1:06d}"

    course_students = [
        sid for sid, cid in student_course.items()
        if cid == course_id
    ]

    extra_time_needed = any(
        sid in accommodation_students for sid in course_students
    )

    assigned_end = end + timedelta(
        minutes=30 if extra_time_needed else 0
    )

    exams.append(
        Exam(
            id=exam_id,
            course_id=course_id,
            title=f"Examination {i + 1:03d}",
            exam_date=exam_day,
            start_time=start,
            end_time=end,
            duration_minutes=duration,
            status="scheduled",
        )
    )

    assignments.append(
        ScheduleAssignment(
            id=f"ASN-{exam_id}-{room_id}",
            exam_id=exam_id,
            room_id=room_id,
            invigilator_id=invigilator_id,
            start_time=start,
            end_time=assigned_end,
            assigned_capacity=len(course_students),
            status="scheduled",
            created_at=GENERATED_AT,
        )
    )

    # Mark the assigned room and invigilator available.
    availability.append(
        Availability(
            invigilator_id=invigilator_id,
            room_id=None,
            start_time=start,
            end_time=assigned_end,
            is_available=True,
            reason="Baseline assignment availability",
        )
    )

    availability.append(
        Availability(
            invigilator_id=None,
            room_id=room_id,
            start_time=start,
            end_time=assigned_end,
            is_available=True,
            reason="Baseline room availability",
        )
    )

# 6.1 Exam equipment and accessibility requirements.
exam_requirements = []

for index, exam in enumerate(exams):
    if index % 3 == 0:
        exam_requirements.append(
            ExamRequirement(
                exam_id=exam.id,
                requirement_type="projector",
                required_quantity=1,
                details="Projector required for this examination",
            )
        )

    if index % 5 == 0:
        exam_requirements.append(
            ExamRequirement(
                exam_id=exam.id,
                requirement_type="computers",
                required_quantity=1,
                details="Computer room required for this examination",
            )
        )

    if index % 7 == 0:
        exam_requirements.append(
            ExamRequirement(
                exam_id=exam.id,
                requirement_type="accessible_seating",
                required_quantity=1,
                details="Accessible seating required",
            )
        )
# 6.2 General room availability for all exam sessions.
exam_days = sorted({exam.exam_date for exam in exams})

for room in rooms:
    for exam_day in exam_days:
        for session_start, session_end in [
            (time(9, 0), time(12, 30)),
            (time(14, 0), time(17, 30)),
        ]:
            availability.append(
                Availability(
                    invigilator_id=None,
                    room_id=room.id,
                    start_time=datetime.combine(
                        exam_day, session_start
                    ),
                    end_time=datetime.combine(
                        exam_day, session_end
                    ),
                    is_available=True,
                    reason="General room availability",
                )
            )

# 7. Save all baseline data to SQLite.
with SessionLocal() as db:
    db.add_all(students)
    db.add_all(courses)
    db.add_all(enrollments)
    db.add_all(rooms)
    db.add_all(capacities)
    db.add_all(invigilators)
    db.add_all(accommodations)
    db.add_all(exams)
    db.add_all(exam_requirements)
    db.add_all(assignments)
    db.add_all(availability)


    db.commit()

    # Export database tables as CSV.
    export_models = {
        "students": Student,
        "courses": Course,
        "enrollments": Enrollment,
        "exams": Exam,
        "exam_requirements": ExamRequirement,
        "rooms": Room,
        "room_capacities": RoomCapacity,
        "invigilators": Invigilator,
        "availability": Availability,
        "accommodations": Accommodation,
        "schedule_assignments": ScheduleAssignment,
    }

    for filename, model in export_models.items():
        records = db.query(model).all()
        columns = [column.name for column in model.__table__.columns]

        with open(
            OUTPUT_DIR / f"{filename}.csv",
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()

            for record in records:
                writer.writerow({
                    column: (
                        getattr(record, column).isoformat()
                        if hasattr(getattr(record, column), "isoformat")
                        else getattr(record, column)
                    )
                    for column in columns
                })

# 8. Labelled anomalies, separate from baseline records.
first_exam = exams[0]
second_exam = exams[1]
first_room = rooms[0]
first_capacity = capacities[0]
first_student = "STU-000001"

ground_truth = [
    {
        "scenario_id": "ANOM-001",
        "issue_type": "student_overlapping_exams",
        "ground_truth": True,
        "source_record_ids": [
            first_student, first_exam.id, second_exam.id
        ],
        "description": (
            "Simulate enrollment of the same student in two exams "
            "scheduled at the same time."
        ),
    },
    {
        "scenario_id": "ANOM-002",
        "issue_type": "room_capacity_exceeded",
        "ground_truth": True,
        "source_record_ids": [first_exam.id, first_room.id],
        "proposed_student_count": first_capacity.capacity + 1,
        "room_capacity": first_capacity.capacity,
    },
    {
        "scenario_id": "ANOM-003",
        "issue_type": "invigilator_double_booked",
        "ground_truth": True,
        "source_record_ids": [first_exam.id, second_exam.id, "INV-000001"],
        "description": "Assign the same invigilator to both overlapping exams.",
    },
    {
        "scenario_id": "ANOM-004",
        "issue_type": "accommodation_ignored",
        "ground_truth": True,
        "source_record_ids": [first_student, first_exam.id],
        "required_extra_minutes": 30,
        "proposed_extra_minutes": 0,
    },
    {
        "scenario_id": "ANOM-005",
        "issue_type": "exam_outside_room_availability",
        "ground_truth": True,
        "source_record_ids": [first_exam.id, assignments[0].room_id],
        "description": "Simulate assigning the exam to a closed room.",
    },
]

with open(
    OUTPUT_DIR / "ground_truth.json",
    "w",
    encoding="utf-8",
) as file:
    json.dump(ground_truth, file, indent=4)


summary = {
    "seed": SEED,
    "students": len(students),
    "courses": len(courses),
    "enrollments": len(enrollments),
    "exams": len(exams),
    "exam_requirements": len(exam_requirements),
    "rooms": len(rooms),
    "room_capacities": len(capacities),
    "invigilators": len(invigilators),
    "availability": len(availability),
    "accommodations": len(accommodations),
    "schedule_assignments": len(assignments),
    "labelled_anomalies": len(ground_truth),
}


with open(
    OUTPUT_DIR / "generation_summary.json",
    "w",
    encoding="utf-8",
) as file:
    json.dump(summary, file, indent=4)

print("Synthetic data generation completed!")
print(json.dumps(summary, indent=4))
print(f"CSV and JSON files saved to: {OUTPUT_DIR}")
