# Exam Scheduling and Room Allocation System

## 1. Project Overview

An examination scheduling system that allocates examinations to rooms and invigilators while considering student enrollment, room capacity, availability, equipment requirements, accommodations, and scheduling conflicts.

The project uses reproducible synthetic academic data.

## 2. Implemented Features

- Generate synthetic students, courses, enrollments, examinations, rooms, and invigilators.
- Generate room capacity, availability, exam requirements, and accommodation records.
- Validate primary keys, foreign keys, data constraints, and record consistency.
- Detect student, room, and invigilator scheduling conflicts.
- Generate five labelled anomaly scenarios for testing.
- Allocate examinations using a greedy constraint-based scheduling algorithm.
- Consider room capacity, equipment, accessibility, availability, student conflicts, and invigilator availability.
- Generate scheduling and validation reports.
- Verify reproducibility using SHA-256 checksums.

## 3. Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- CSV and JSON (Python standard library)
- Pytest

## 4. Project Structure

```text
exam-scheduling-system/
â”œâ”€â”€ backend/
â”‚   â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ tests/
â”‚   â”œâ”€â”€ generate_data.py
â”‚   â”œâ”€â”€ validate_data.py
â”‚   â”œâ”€â”€ inject_anomalies.py
â”‚   â”œâ”€â”€ run_scheduler.py
â”‚   â”œâ”€â”€ validate_generated_schedule.py
â”‚   â””â”€â”€ verify_reproducibility.py
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ anomalies/
â”‚   â””â”€â”€ scheduler_output/
â”œâ”€â”€ docs/
â”‚   â””â”€â”€ schema-and-data-dictionary.md
â”œâ”€â”€ prompt-history/
â””â”€â”€ README.md
```

## 5. Synthetic Dataset

The baseline dataset is generated using seed `20261022`.

| Entity | Records |
|---|---:|
| Students | 5,000 |
| Courses | 100 |
| Enrollments | 5,000 |
| Exams | 300 |
| Exam Requirements | 203 |
| Rooms | 100 |
| Room Capacities | 100 |
| Invigilators | 200 |
| Availability | 6,600 |
| Accommodations | 250 |
| Schedule Assignments | 300 |

All generated records are synthetic.

## 6. Setup Instructions

### Prerequisites

- Python 3.11 or later
- Git

### Create and activate a virtual environment

From the repository root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 7. Run the Project

Run these commands from the `backend` directory with the virtual environment activated.

### Generate synthetic data

```powershell
python generate_data.py
```

Custom dataset sizes can be supplied through command-line arguments:

```powershell
python generate_data.py --students 5000 --courses 100 --exams 300 --rooms 100 --invigilators 200 --seed 20261022
```

### Validate baseline data

```powershell
python validate_data.py
```

### Generate labelled anomaly scenarios

```powershell
python inject_anomalies.py
```

### Run the scheduling algorithm

```powershell
python run_scheduler.py
```

### Independently validate the generated schedule

```powershell
python validate_generated_schedule.py
```

### Verify reproducibility

```powershell
python verify_reproducibility.py
```

### Run automated tests

```powershell
python -m pytest tests/ -v
```

### Start the FastAPI application

```powershell
python -m uvicorn app.main:app --reload
```

The API documentation is available at:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 8. Expected Verification Results

The current baseline verification results include:

- 15 automated tests passing.
- 12,767 baseline validation checks with zero errors.
- Five labelled anomaly scenarios detected.
- 300 examinations scheduled out of 300.
- Zero conflicts in the independently validated generated schedule.
- Reproducibility verification using SHA-256 checksums.

Run the verification commands to reproduce these results.

## 9. Documentation

See `docs/schema-and-data-dictionary.md` for entity definitions, relationships, data fields, integrity rules, and implementation limitations.

## 10. AI Usage Disclosure

AI tools were used as development assistance for project planning, code guidance, debugging, test development, and documentation.

The candidate reviewed, executed, and tested the implementation and is responsible for understanding its design, decisions, limitations, and results.

A record of AI-assisted work is maintained in `prompt-history/`. The prompt history should be treated as a summary where verbatim exports are unavailable.

## 11. Current Limitations

- A dedicated audit/event history table is not implemented.
- Complete lifecycle state-transition validation is not implemented.
- Equipment quantities are not yet validated; current room matching uses Boolean equipment attributes.
- Very large datasets may require further performance optimization and resource testing.
- Portable SQL seed export is not yet implemented.
