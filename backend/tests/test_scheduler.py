
import pytest

from app.services.scheduler import room_meets_requirements
from app.services.scheduler import build_assignment_events


@pytest.mark.parametrize(
    ("requirement_type", "room", "expected"),
    [
        (
            "projector",
            {"has_projector": "False"},
            False,
        ),
        (
            "projector",
            {"has_projector": "True"},
            True,
        ),
        (
            "computers",
            {"has_computers": "False"},
            False,
        ),
        (
            "computers",
            {"has_computers": "True"},
            True,
        ),
        (
            "accessible_seating",
            {"is_accessible": "False"},
            False,
        ),
        (
            "accessible_seating",
            {"is_accessible": "True"},
            True,
        ),
    ],
)
def test_room_equipment_and_accessibility_requirements(
    requirement_type, room, expected
):
    exam = {"id": "EXAM-001"}

    requirements_by_exam = {
        "EXAM-001": [
            {
                "requirement_type": requirement_type,
                "required_quantity": "1",
            }
        ]
    }

    result = room_meets_requirements(
        room, exam, requirements_by_exam
    )

    assert result is expected


def test_room_without_requirements_is_accepted():
    room = {
        "has_projector": "False",
        "has_computers": "False",
        "is_accessible": "False",
    }

    exam = {"id": "EXAM-001"}

    result = room_meets_requirements(
        room, exam, {}
    )

    assert result is True

def test_build_assignment_events():
    assignments = [
        {
            "id": "ASN-EXAM-001-ROOM-001",
            "status": "scheduled",
            "created_at": "2026-01-01T00:00:00",
        }
    ]

    events = build_assignment_events(assignments)

    assert len(events) == 1
    assert events[0]["assignment_id"] == "ASN-EXAM-001-ROOM-001"
    assert events[0]["event_type"] == "assignment_created"
    assert events[0]["new_status"] == "scheduled"
    assert events[0]["changed_by"] == "scheduler"
