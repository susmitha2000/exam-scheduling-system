
import csv
from pathlib import Path

import pytest

from app.services.conflict_detector import (
    detect_conflicts,
    overlaps,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"

CSV_FILES = [
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


def run_detector(folder):
    return detect_conflicts(
        exams=load_csv(folder, "exams.csv"),
        rooms=load_csv(folder, "rooms.csv"),
        room_capacities=load_csv(folder, "room_capacities.csv"),
        invigilators=load_csv(folder, "invigilators.csv"),
        enrollments=load_csv(folder, "enrollments.csv"),
        accommodations=load_csv(folder, "accommodations.csv"),
        assignments=load_csv(folder, "schedule_assignments.csv"),
        availability=load_csv(folder, "availability.csv"),
    )


def test_time_overlap_detection():
    from datetime import datetime

    first_start = datetime(2027, 1, 4, 9, 0)
    first_end = datetime(2027, 1, 4, 11, 0)
    second_start = datetime(2027, 1, 4, 10, 0)
    second_end = datetime(2027, 1, 4, 12, 0)

    assert overlaps(
        first_start, first_end, second_start, second_end
    )

    assert not overlaps(
        first_start,
        first_end,
        datetime(2027, 1, 4, 11, 0),
        datetime(2027, 1, 4, 12, 0),
    )


def test_baseline_has_no_conflicts():
    conflicts = run_detector(DATA_DIR)

    assert conflicts == []


@pytest.mark.parametrize(
    ("scenario_id", "expected_issue"),
    [
        ("ANOM-001", "student_overlapping_exams"),
        ("ANOM-002", "room_capacity_exceeded"),
        ("ANOM-003", "invigilator_double_booked"),
        ("ANOM-004", "accommodation_ignored"),
        ("ANOM-005", "exam_outside_room_availability"),
    ],
)
def test_anomaly_is_detected(scenario_id, expected_issue):
    scenario_folder = DATA_DIR / "anomalies" / scenario_id

    conflicts = run_detector(scenario_folder)

    detected_types = {
        conflict["issue_type"] for conflict in conflicts
    }

    assert expected_issue in detected_types, (
        f"{scenario_id} did not detect {expected_issue}. "
        f"Detected: {detected_types}"
    )

def test_room_double_booking_is_detected():
    exams = [
        {
            "id": "EXAM-001",
            "course_id": "CRS-001",
            "duration_minutes": 120,
        },
        {
            "id": "EXAM-002",
            "course_id": "CRS-002",
            "duration_minutes": 120,
        },
    ]

    rooms = [{"id": "ROOM-001"}]

    room_capacities = [
        {
            "room_id": "ROOM-001",
            "capacity": "100",
            "effective_from": "2026-01-01",
            "effective_to": "",
        }
    ]

    invigilators = [
        {"id": "INV-001"},
        {"id": "INV-002"},
    ]

    assignments = [
        {
            "exam_id": "EXAM-001",
            "room_id": "ROOM-001",
            "invigilator_id": "INV-001",
            "start_time": "2027-01-04T09:00:00",
            "end_time": "2027-01-04T11:00:00",
            "assigned_capacity": "50",
        },
        {
            "exam_id": "EXAM-002",
            "room_id": "ROOM-001",
            "invigilator_id": "INV-002",
            "start_time": "2027-01-04T10:00:00",
            "end_time": "2027-01-04T12:00:00",
            "assigned_capacity": "50",
        },
    ]

    conflicts = detect_conflicts(
        exams=exams,
        rooms=rooms,
        room_capacities=room_capacities,
        invigilators=invigilators,
        enrollments=[],
        accommodations=[],
        assignments=assignments,
        availability=[],
    )

    detected_types = {
        conflict["issue_type"] for conflict in conflicts
    }

    assert "room_double_booked" in detected_types