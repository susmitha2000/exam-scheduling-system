
# Exam Scheduling System - Schema and Data Dictionary

## 1. Overview

The database stores academic scheduling information, including students, courses, enrollments, exams, rooms, invigilators, availability, accommodations, and schedule assignments.

All generated records are synthetic.

## 2. Entity Relationships

- One Course can have many Enrollments.
- One Student can have many Enrollments.
- One Course can have many Exams.
- One Exam can have many Exam Requirements.
- One Room can have multiple Room Capacity records over time.
- One Invigilator can have multiple Availability records.
- One Room can have multiple Availability records.
- One Student can have multiple Accommodation records.
- One Exam can have multiple Schedule Assignments.
- One Room can be used by multiple Schedule Assignments over time.
- One Invigilator can have multiple Schedule Assignments over time.

Enrollment resolves the many-to-many relationship between Students and Courses.

## 3. Data Dictionary

### Student

| Field | Description |
|---|---|
| id | Unique student identifier |
| full_name | Student's synthetic name |
| email | Unique email address |
| department | Academic department |
| created_at | Record creation timestamp |

### Course

| Field | Description |
|---|---|
| id | Unique course identifier |
| code | Unique course code |
| name | Course name |
| department | Academic department |

### Enrollment

| Field | Description |
|---|---|
| id | Enrollment identifier |
| student_id | Reference to Student |
| course_id | Reference to Course |
| enrolled_on | Enrollment date |
| status | Enrollment status |

### Exam

| Field | Description |
|---|---|
| id | Unique exam identifier |
| course_id | Reference to Course |
| title | Exam title |
| exam_date | Scheduled exam date |
| start_time | Exam start time |
| end_time | Exam end time |
| duration_minutes | Exam duration |
| status | Exam lifecycle status |

### ExamRequirement

| Field | Description |
|---|---|
| id | Requirement identifier |
| exam_id | Reference to Exam |
| requirement_type | Type of requirement |
| required_quantity | Required quantity |
| details | Additional requirement details |

### Room

| Field | Description |
|---|---|
| id | Unique room identifier |
| name | Room name |
| building | Building name |
| room_type | Room category |
| has_projector | Projector availability |
| has_computers | Computer availability |
| is_accessible | Accessibility indicator |

### RoomCapacity

| Field | Description |
|---|---|
| id | Capacity record identifier |
| room_id | Reference to Room |
| capacity | Maximum room capacity |
| effective_from | Capacity start date |
| effective_to | Capacity end date |

### Invigilator

| Field | Description |
|---|---|
| id | Unique invigilator identifier |
| full_name | Invigilator name |
| email | Unique email address |
| department | Department |
| is_active | Active status |

### Availability

| Field | Description |
|---|---|
| id | Availability record identifier |
| invigilator_id | Optional Invigilator reference |
| room_id | Optional Room reference |
| start_time | Availability start |
| end_time | Availability end |
| is_available | Availability indicator |
| reason | Availability explanation |

Exactly one of `invigilator_id` or `room_id` must be populated.

### Accommodation

| Field | Description |
|---|---|
| id | Accommodation identifier |
| student_id | Reference to Student |
| accommodation_type | Accommodation category |
| extra_minutes | Additional exam time |
| details | Accommodation details |
| effective_from | Effective start date |
| effective_to | Effective end date |

### ScheduleAssignment

| Field | Description |
|---|---|
| id | Assignment identifier |
| exam_id | Reference to Exam |
| room_id | Reference to Room |
| invigilator_id | Reference to Invigilator |
| start_time | Assignment start |
| end_time | Assignment end |
| assigned_capacity | Number of assigned students |
| status | Assignment status |
| created_at | Creation timestamp |

## 4. Data Integrity Rules

- Primary keys must be unique.
- Foreign keys must reference existing records.
- Student-course enrollment pairs must be unique.
- Exam duration must be positive.
- Exam end time must be later than start time.
- Room capacity must be positive.
- Availability end time must be later than start time.
- Accommodation extra minutes cannot be negative.
- Assignment end time must be later than start time.
- Assignment capacity must be positive.
- A room and invigilator cannot be assigned to overlapping exams when unavailable.
- Students cannot attend overlapping exams.
- Accommodations must be respected when calculating exam duration.

## 5. Synthetic Dataset

| Entity | Baseline Records |
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

Generation seed: `20261022`

## 6. Anomaly Scenarios

Five isolated negative test scenarios are generated:

1. Student overlapping exams.
2. Room capacity exceeded.
3. Invigilator double-booked.
4. Accommodation ignored.
5. Exam outside room availability.

Each scenario has a labelled anomaly identifier and a conflict report.

## 7. Data Provenance

All records are programmatically generated synthetic data.

No real student or staff personal information is used.

## 8. Implementation Limitations and Future Improvements

The current implementation focuses on synthetic data generation, baseline validation, anomaly detection, and conflict-free exam scheduling.

The following improvements remain:

1. **Event history:** A dedicated audit/event history table is not yet implemented. Future work should record important changes to exams, assignments, and other scheduling records, including timestamps and the responsible user.

2. **Lifecycle transitions:** Entities contain status fields, but a complete state-transition workflow with validation of permitted transitions is not yet implemented.

3. **Equipment quantities:** Exam requirements include a `required_quantity` field. Current room matching checks equipment and accessibility using Boolean room attributes rather than validating equipment quantities.

4. **Generator scalability:** The generator supports configurable student, course, exam, room, and invigilator counts through command-line arguments. Larger datasets may require performance optimization and additional resource testing.

5. **SQL export:** CSV and JSON exports are provided. A portable SQL seed export is a future improvement.

These limitations are documented so that the current implementation and its future development scope are clear.
