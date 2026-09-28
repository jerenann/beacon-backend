from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.dependencies import get_db
from app.routers.auth import get_current_user, require_roles
from app.services.audit import create_audit_log
from app.services.ml_client import predict_student

router = APIRouter(prefix="/predictions", tags=["Predictions"])


def get_active_thresholds(db: Session) -> models.RiskThreshold:
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


def get_risk_category(
    probability: float,
    medium_threshold: float,
    high_threshold: float,
) -> models.RiskCategory:
    if probability >= high_threshold:
        return models.RiskCategory.HIGH
    if probability >= medium_threshold:
        return models.RiskCategory.MEDIUM
    return models.RiskCategory.LOW


@router.post("/run", response_model=list[schemas.PredictionRead])
def run_predictions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(
        require_roles(models.UserRole.ADMIN, models.UserRole.ML_ADMIN)
    ),
):
    thresholds = get_active_thresholds(db)
    students = db.query(models.Student).filter(models.Student.is_active.is_(True)).all()
    created_predictions = []

    for student in students:
        latest_academic = db.query(models.AcademicRecord).filter(
            models.AcademicRecord.student_db_id == student.id
        ).order_by(models.AcademicRecord.recorded_at.desc()).first()

        latest_attendance = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.student_db_id == student.id
        ).order_by(models.AttendanceRecord.recorded_at.desc()).first()

        if latest_academic is None or latest_attendance is None:
            continue

        previous_prediction = db.query(models.RiskPrediction).filter(
            models.RiskPrediction.student_db_id == student.id
        ).order_by(models.RiskPrediction.predicted_at.desc()).first()

        result = predict_student({
            "cgpa": latest_academic.cgpa,
            "backlog_count": latest_academic.backlog_count,
            "attendance_percentage": latest_attendance.attendance_percentage,
        })

        risk_category = get_risk_category(
            result["probability"],
            thresholds.medium_threshold,
            thresholds.high_threshold,
        )

        prediction = models.RiskPrediction(
            student_db_id=student.id,
            probability=result["probability"],
            risk_category=risk_category,
            model_version=result["model_version"],
        )

        db.add(prediction)
        db.flush()

        increasing_rank = 1
        protective_rank = 1

        for factor in result["explanations"]:
            direction = models.FactorDirection(factor["direction"])

            if direction == models.FactorDirection.RISK_INCREASING:
                rank = increasing_rank
                increasing_rank += 1
            else:
                rank = protective_rank
                protective_rank += 1

            explanation = models.Explanation(
                prediction_id=prediction.id,
                feature_name=factor["feature_name"],
                feature_value=factor.get("feature_value"),
                shap_value=factor["shap_value"],
                direction=direction,
                rank=rank,
            )
            db.add(explanation)

        if (
            risk_category == models.RiskCategory.HIGH
            and (previous_prediction is None or previous_prediction.risk_category != models.RiskCategory.HIGH)
        ):
            alert = models.Alert(
                student_db_id=student.id,
                advisor_id=student.advisor_id,
                prediction_id=prediction.id,
                message=f"{student.full_name} has newly entered the HIGH risk category.",
            )
            db.add(alert)

        created_predictions.append(prediction)

    db.commit()

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="RUN_BATCH_PREDICTIONS",
        entity_type="RiskPrediction",
        details=f"Created {len(created_predictions)} predictions",
    )

    return created_predictions


@router.get("/", response_model=list[schemas.PredictionRead])
def list_predictions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.RiskPrediction)

    if current_user.role == models.UserRole.FACULTY_ADVISOR:
        query = query.join(models.Student).filter(
            models.Student.advisor_id == current_user.id
        )

    return query.order_by(models.RiskPrediction.predicted_at.desc()).all()