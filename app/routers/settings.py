from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db
from app.routers.auth import get_current_user, require_roles
from app.services.audit import create_audit_log

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/thresholds", response_model=schemas.ThresholdRead)
def get_thresholds(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    threshold = db.query(models.RiskThreshold).filter(
        models.RiskThreshold.is_active.is_(True)
    ).first()

    if threshold is None:
        threshold = models.RiskThreshold(
            medium_threshold=0.30,
            high_threshold=0.60,
            is_active=True,
        )
        db.add(threshold)
        db.commit()
        db.refresh(threshold)

    return threshold


@router.put("/thresholds", response_model=schemas.ThresholdRead)
def update_thresholds(
    data: schemas.ThresholdUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(models.UserRole.ADMIN)),
):
    if data.medium_threshold >= data.high_threshold:
        raise HTTPException(
            status_code=400,
            detail="Medium threshold must be lower than high threshold",
        )

    current_threshold = db.query(models.RiskThreshold).filter(
        models.RiskThreshold.is_active.is_(True)
    ).first()

    if current_threshold is not None:
        current_threshold.is_active = False

    new_threshold = models.RiskThreshold(
        medium_threshold=data.medium_threshold,
        high_threshold=data.high_threshold,
        is_active=True,
        updated_by_user_id=current_user.id,
    )

    db.add(new_threshold)
    db.commit()
    db.refresh(new_threshold)

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE_THRESHOLDS",
        entity_type="RiskThreshold",
        entity_id=str(new_threshold.id),
        details=f"Medium={data.medium_threshold}, High={data.high_threshold}",
    )

    return new_threshold