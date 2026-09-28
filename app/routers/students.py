from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db
from app.routers.auth import get_current_user, require_roles
from app.services.audit import create_audit_log

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: schemas.StudentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_roles(models.UserRole.ADMIN, models.UserRole.COORDINATOR)
    ),
):
    existing_student = db.query(models.Student).filter(
        models.Student.student_id == student_data.student_id
    ).first()

    if existing_student:
        raise HTTPException(status_code=400, detail="Student ID already exists")

    if student_data.advisor_id is not None:
        advisor = db.query(models.User).filter(models.User.id == student_data.advisor_id).first()
        if advisor is None:
            raise HTTPException(status_code=404, detail="Advisor not found")

    student = models.Student(**student_data.model_dump())

    db.add(student)
    db.commit()
    db.refresh(student)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE_STUDENT",
        entity_type="Student",
        entity_id=str(student.id),
        details=f"Created student {student.student_id}",
    )

    return student


@router.get("/", response_model=list[schemas.StudentRead])
def list_students(
    department: str | None = None,
    semester: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Student).filter(models.Student.is_active.is_(True))

    if current_user.role == models.UserRole.FACULTY_ADVISOR:
        query = query.filter(models.Student.advisor_id == current_user.id)

    if department:
        query = query.filter(models.Student.department == department)

    if semester:
        query = query.filter(models.Student.semester == semester)

    return query.order_by(models.Student.student_id).all()


@router.get("/{student_db_id}", response_model=schemas.StudentRead)
def get_student(
    student_db_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    student = db.query(models.Student).filter(models.Student.id == student_db_id).first()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    if (
        current_user.role == models.UserRole.FACULTY_ADVISOR
        and student.advisor_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="You can only view assigned students")

    return student