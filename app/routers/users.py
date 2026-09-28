from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db
from app.routers.auth import get_current_user, hash_password, require_roles
from app.services.audit import create_audit_log

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(models.UserRole.ADMIN)),
):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE_USER",
        entity_type="User",
        entity_id=str(new_user.id),
        details=f"Created user {new_user.email} with role {new_user.role.value}",
    )

    return new_user


@router.get("/", response_model=list[schemas.UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(models.UserRole.ADMIN)),
):
    return db.query(models.User).order_by(models.User.id.desc()).all()