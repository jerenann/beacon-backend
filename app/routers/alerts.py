from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=list[schemas.AlertRead])
def list_alerts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Alert)

    if current_user.role == models.UserRole.FACULTY_ADVISOR:
        query = query.filter(models.Alert.advisor_id == current_user.id)

    return query.order_by(models.Alert.created_at.desc()).all()


@router.patch("/{alert_id}/read", response_model=schemas.AlertRead)
def mark_alert_as_read(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    if (
        current_user.role == models.UserRole.FACULTY_ADVISOR
        and alert.advisor_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="You cannot update this alert")

    alert.status = models.AlertStatus.READ
    db.commit()
    db.refresh(alert)

    return alert