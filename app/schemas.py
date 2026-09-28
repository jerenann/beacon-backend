from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import AlertStatus, RiskCategory, UserRole


class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserRead"


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    role: UserRole


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime


class StudentCreate(BaseModel):
    student_id: str = Field(min_length=1, max_length=30)
    full_name: str = Field(min_length=2, max_length=150)
    department: str = Field(min_length=2, max_length=100)
    program: str | None = None
    semester: int = Field(ge=1, le=12)
    admission_year: int | None = Field(default=None, ge=2000, le=2100)
    advisor_id: int | None = None


class StudentRead(StudentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class InterventionCreate(BaseModel):
    student_db_id: int
    intervention_type: str = Field(min_length=2, max_length=100)
    notes: str | None = None
    intervention_date: date
    follow_up_date: date | None = None


class InterventionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_db_id: int
    created_by_user_id: int
    intervention_type: str
    notes: str | None
    intervention_date: date
    follow_up_date: date | None
    created_at: datetime


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_db_id: int
    advisor_id: int | None
    prediction_id: int | None
    message: str
    status: AlertStatus
    created_at: datetime


class ThresholdUpdate(BaseModel):
    medium_threshold: float = Field(ge=0, le=1)
    high_threshold: float = Field(ge=0, le=1)


class ThresholdRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medium_threshold: float
    high_threshold: float
    is_active: bool
    updated_at: datetime


class PredictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_db_id: int
    probability: float
    risk_category: RiskCategory
    model_version: str
    predicted_at: datetime