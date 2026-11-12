
# Exam Scheduling and Room Allocation System

## Project Overview

An examination scheduling management system designed to schedule university examinations while respecting student enrollment, room capacity, room availability, equipment requirements, student accommodations, and invigilator availability.

## Project Objectives

- Generate and manage synthetic university data.
- Manage students, courses, enrollments, and examinations.
- Manage examination rooms and invigilators.
- Detect student, room, and invigilator scheduling conflicts.
- Automatically allocate examination rooms and time slots.
- Apply student accommodation requirements.
- Identify unscheduled examinations with reason codes.
- Maintain scheduling history and audit records.
- Generate analytics and validation reports.

## Technology Stack

- Frontend: React + TypeScript
- Backend: Python + FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- Data Generation: Python
- Data Validation: Pydantic

## Project Structure

```text
exam-scheduling-system/
├── backend/
├── frontend/
├── data/
├── docs/
├── scripts/
├── prompt-history/
└── README.md
```

## Project Status

Currently in development.

## Synthetic Data

The project will use reproducible synthetic data with a fixed random seed: 20261022.

Target baseline:
- 5,000 students
- 300 examinations
- 100 rooms
- 200 invigilators

## Documentation

Additional documentation will be maintained in the docs/ directory.

## AI Usage Disclosure

AI tools are used for development assistance. All prompts will be documented in prompt-history/. Implementation decisions, code, and validation will be reviewed and understood by the candidate.

## License

To be determined.
```

### 5.3 Save the file

Press:

`Ctrl + S`

<badge color="success">Checkpoint 5.1</badge>

You should now see `README.md` under your project folder.

**Send me a screenshot of your VS Code Explorer showing README.md.**

Next, we'll create `.gitignore` to protect environment files, passwords and other sensitive information before uploading anything publicly.

We'll keep going step by step!