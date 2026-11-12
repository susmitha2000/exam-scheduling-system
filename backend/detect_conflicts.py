import csv
import json
from collections import Counter
from pathlib import Path

from app.services.conflict_detector import detect_conflicts


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(filename):
    file_path = DATA_DIR / filename

    with file_path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def main():
    print("Loading scheduling data...")

    exams = load_csv("exams.csv")
    rooms = load_csv("rooms.csv")
    room_capacities = load_csv("room_capacities.csv")
    invigilators = load_csv("invigilators.csv")
    enrollments = load_csv("enrollments.csv")
    accommodations = load_csv("accommodations.csv")
    assignments = load_csv("schedule_assignments.csv")
    availability = load_csv("availability.csv")

    print("Running conflict detection...")

    conflicts = detect_conflicts(
        exams=exams,
        rooms=rooms,
        room_capacities=room_capacities,
        invigilators=invigilators,
        enrollments=enrollments,
        accommodations=accommodations,
        assignments=assignments,
        availability=availability,
    )

    report_path = DATA_DIR / "conflict_report.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(conflicts, file, indent=4)

    counts = Counter(
        conflict["issue_type"] for conflict in conflicts
    )

    print("\nCONFLICT DETECTION SUMMARY")
    print("--------------------------")
    print(f"Assignments checked: {len(assignments)}")
    print(f"Total conflicts found: {len(conflicts)}")

    if counts:
        for issue_type, count in sorted(counts.items()):
            print(f"{issue_type}: {count}")
    else:
        print("No scheduling conflicts found.")

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()