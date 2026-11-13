
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Date,
    ForeignKey,
    Boolean,
    Text,
    UniqueConstraint,
    CheckConstraint,
)
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True)  # STU-000001
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    department = Column(String(100))
    created_at = Column(DateTime, nullable=False)


class Course(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True)
    code = Column(String(30), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    department = Column(String(100))


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    enrolled_on = Column(Date, nullable=False)
    status = Column(String(30), nullable=False, default="active")

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )


class Exam(Base):
    __tablename__ = "exams"

    id = Column(String, primary_key=True)  # EXAM-2026-000001
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    exam_date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False, default="draft")

    __table_args__ = (
        CheckConstraint("duration_minutes > 0"),
        CheckConstraint("end_time > start_time"),
    )


class ExamRequirement(Base):
    __tablename__ = "exam_requirements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(String, ForeignKey("exams.id"), nullable=False)
    requirement_type = Column(String(50), nullable=False)
    required_quantity = Column(Integer, nullable=False, default=1)
    details = Column(Text)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(String, primary_key=True)  # ROOM-000001
    name = Column(String(100), nullable=False)
    building = Column(String(100))
    room_type = Column(String(50), default="standard")
    has_projector = Column(Boolean, default=False)
    has_computers = Column(Boolean, default=False)
    is_accessible = Column(Boolean, default=False)


class RoomCapacity(Base):
    __tablename__ = "room_capacities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False)
    capacity = Column(Integer, nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)

    __table_args__ = (
        CheckConstraint("capacity > 0"),
        CheckConstraint("effective_to IS NULL OR effective_to >= effective_from"),
    )


class Invigilator(Base):
    __tablename__ = "invigilators"

    id = Column(String, primary_key=True)  # INV-000001
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    department = Column(String(100))
    is_active = Column(Boolean, default=True)


class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invigilator_id = Column(String, ForeignKey("invigilators.id"))
    room_id = Column(String, ForeignKey("rooms.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    reason = Column(String(255))

    __table_args__ = (
        CheckConstraint("end_time > start_time"),
        CheckConstraint(
            "(invigilator_id IS NOT NULL AND room_id IS NULL) OR "
            "(invigilator_id IS NULL AND room_id IS NOT NULL)"
        ),
    )


class Accommodation(Base):
    __tablename__ = "accommodations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    accommodation_type = Column(String(60), nullable=False)
    extra_minutes = Column(Integer, nullable=False, default=0)
    details = Column(Text)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)

    __table_args__ = (
        CheckConstraint("extra_minutes >= 0"),
        CheckConstraint("effective_to IS NULL OR effective_to >= effective_from"),
    )


class ScheduleAssignment(Base):
    __tablename__ = "schedule_assignments"

    id = Column(String, primary_key=True)  # ASN-<exam-id>-<room-id>
    exam_id = Column(String, ForeignKey("exams.id"), nullable=False)
    room_id = Column(String, ForeignKey("rooms.id"), nullable=False)
    invigilator_id = Column(String, ForeignKey("invigilators.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    assigned_capacity = Column(Integer, nullable=False)
    status = Column(String(30), nullable=False, default="scheduled")
    created_at = Column(DateTime, nullable=False)

    __table_args__ = (
        CheckConstraint("end_time > start_time"),
        CheckConstraint("assigned_capacity > 0"),
        UniqueConstraint("exam_id", "room_id", name="uq_exam_room"),
    )

class ScheduleAssignmentHistory(Base):
    __tablename__ = "schedule_assignment_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assignment_id = Column(
        String,
        ForeignKey("schedule_assignments.id"),
        nullable=False,
    )
    event_type = Column(String(50), nullable=False)
    previous_status = Column(String(30))
    new_status = Column(String(30))
    changed_at = Column(DateTime, nullable=False)
    changed_by = Column(String(100))
    notes = Column(Text)
