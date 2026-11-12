
import csv
import json
from collections import Counter
from pathlib import Path

from app.services.conflict_detector import detect_conflicts


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(filename):
    path = DATA_DIR / filename

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def main():
    print("Loading baseline data and generated schedule...")

    exams = load_csv("exams.csv")
    rooms = load_csv("rooms.csv")
    capacities = load_csv("room_capacities.csv")
    invigilators = load_csv("invigilators.csv")
    enrollments = load_csv("enrollments.csv")
    accommodations = load_csv("accommodations.csv")
    availability = load_csv("availability.csv")

    assignments = load_csv(
        "scheduler_output/generated_schedule.csv"
    )

    print("Running independent conflict detection...")

    conflicts = detect_conflicts(
        exams=exams,
        rooms=rooms,
        room_capacities=capacities,
        invigilators=invigilators,
        enrollments=enrollments,
        accommodations=accommodations,
        assignments=assignments,
        availability=availability,
    )

    report_path = (
        DATA_DIR / "scheduler_output" / "validation_report.json"
    )

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(conflicts, file, indent=4)

    counts = Counter(
        conflict["issue_type"] for conflict in conflicts
    )

    print("\nGENERATED SCHEDULE VALIDATION")
    print("-----------------------------")
    print(f"Exams in source data: {len(exams)}")
    print(f"Generated assignments: {len(assignments)}")
    print(f"Total conflicts: {len(conflicts)}")

    for issue_type, count in sorted(counts.items()):
        print(f"{issue_type}: {count}")

    if not conflicts:
        print("\nSUCCESS: No detected scheduling conflicts.")
    else:
        print("\nWARNING: Scheduling conflicts were detected.")

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
