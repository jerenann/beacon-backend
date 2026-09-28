from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db
from app.routers.auth import get_current_user, require_roles
from app.services.audit import create_audit_log

router = APIRouter(prefix="/interventions", tags=["Interventions"])


@router.post("/", response_model=schemas.InterventionRead, status_code=status.HTTP_201_CREATED)
def create_intervention(
    intervention_data: schemas.InterventionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_roles(
            models.UserRole.ADMIN,
            models.UserRole.FACULTY_ADVISOR,
            models.UserRole.COORDINATOR,
        )
    ),
):
    student = db.query(models.Student).filter(
        models.Student.id == intervention_data.student_db_id
    ).first()

    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    if (
        current_user.role == models.UserRole.FACULTY_ADVISOR
        and student.advisor_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="You can only record interventions for assigned students")

    intervention = models.Intervention(
        **intervention_data.model_dump(),
        created_by_user_id=current_user.id,
    )

    db.add(intervention)
    db.commit()
    db.refresh(intervention)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE_INTERVENTION",
        entity_type="Intervention",
        entity_id=str(intervention.id),
        details=f"Intervention for student database ID {student.id}",
    )

    return intervention


@router.get("/student/{student_db_id}", response_model=list[schemas.InterventionRead])
def list_student_interventions(
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
        raise HTTPException(status_code=403, detail="You can only view interventions for assigned students")

    return db.query(models.Intervention).filter(
        models.Intervention.student_db_id == student_db_id
    ).order_by(models.Intervention.intervention_date.desc()).all()