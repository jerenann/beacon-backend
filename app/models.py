import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    FACULTY_ADVISOR = "FACULTY_ADVISOR"
    COORDINATOR = "COORDINATOR"
    ML_ADMIN = "ML_ADMIN"


class RiskCategory(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class FactorDirection(str, enum.Enum):
    RISK_INCREASING = "RISK_INCREASING"
    PROTECTIVE = "PROTECTIVE"


class AlertStatus(str, enum.Enum):
    UNREAD = "UNREAD"
    READ = "READ"
    RESOLVED = "RESOLVED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    assigned_students = relationship(
        "Student",
        back_populates="advisor",
        foreign_keys="Student.advisor_id",
    )
    created_interventions = relationship(
        "Intervention",
        back_populates="created_by",
        foreign_keys="Intervention.created_by_user_id",
    )
    audit_logs = relationship("AuditLog", back_populates="user")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    program: Mapped[str | None] = mapped_column(String(100), nullable=True)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    admission_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    advisor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    advisor = relationship(
        "User",
        back_populates="assigned_students",
        foreign_keys=[advisor_id],
    )
    academic_records = relationship(
        "AcademicRecord",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    attendance_records = relationship(
        "AttendanceRecord",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    predictions = relationship(
        "RiskPrediction",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    alerts = relationship(
        "Alert",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    interventions = relationship(
        "Intervention",
        back_populates="student",
        cascade="all, delete-orphan",
    )


class UploadBatch(Base):
    __tablename__ = "upload_batches"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AcademicRecord(Base):
    __tablename__ = "academic_records"
    __table_args__ = (
        CheckConstraint("cgpa IS NULL OR (cgpa >= 0 AND cgpa <= 10)", name="valid_cgpa"),
        CheckConstraint("sgpa IS NULL OR (sgpa >= 0 AND sgpa <= 10)", name="valid_sgpa"),
        CheckConstraint("backlog_count >= 0", name="valid_backlog_count"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_db_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    upload_batch_id: Mapped[int | None] = mapped_column(ForeignKey("upload_batches.id"), nullable=True)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    cgpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    sgpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    internal_marks: Mapped[float | None] = mapped_column(Float, nullable=True)
    backlog_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="academic_records")


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        CheckConstraint(
            "attendance_percentage >= 0 AND attendance_percentage <= 100",
            name="valid_attendance_percentage",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_db_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    upload_batch_id: Mapped[int | None] = mapped_column(ForeignKey("upload_batches.id"), nullable=True)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    attendance_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="attendance_records")


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"
    __table_args__ = (
        CheckConstraint("probability >= 0 AND probability <= 1", name="valid_probability"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    student_db_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    risk_category: Mapped[RiskCategory] = mapped_column(Enum(RiskCategory), nullable=False)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="predictions")
    explanations = relationship(
        "Explanation",
        back_populates="prediction",
        cascade="all, delete-orphan",
    )


class Explanation(Base):
    __tablename__ = "explanations"

    id: Mapped[int] = mapped_column(primary_key=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("risk_predictions.id"), nullable=False)
    feature_name: Mapped[str] = mapped_column(String(120), nullable=False)
    feature_value: Mapped[str | None] = mapped_column(String(150), nullable=True)
    shap_value: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[FactorDirection] = mapped_column(Enum(FactorDirection), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)

    prediction = relationship("RiskPrediction", back_populates="explanations")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_db_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    advisor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    prediction_id: Mapped[int | None] = mapped_column(ForeignKey("risk_predictions.id"), nullable=True)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus),
        default=AlertStatus.UNREAD,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="alerts")


class Intervention(Base):
    __tablename__ = "interventions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_db_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    intervention_type: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    intervention_date: Mapped[Date] = mapped_column(Date, nullable=False)
    follow_up_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="interventions")
    created_by = relationship(
        "User",
        back_populates="created_interventions",
        foreign_keys=[created_by_user_id],
    )


class RiskThreshold(Base):
    __tablename__ = "risk_thresholds"
    __table_args__ = (
        CheckConstraint(
            "medium_threshold >= 0 AND high_threshold <= 1 AND medium_threshold < high_threshold",
            name="valid_thresholds",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    medium_threshold: Mapped[float] = mapped_column(Float, default=0.30, nullable=False)
    high_threshold: Mapped[float] = mapped_column(Float, default=0.60, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(150), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")