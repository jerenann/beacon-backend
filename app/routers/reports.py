import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import models
from app.dependencies import get_db
from app.routers.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/risk-summary.csv")
def export_risk_summary(
    department: str | None = None,
    semester: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Student)

    if current_user.role == models.UserRole.FACULTY_ADVISOR:
        query = query.filter(models.Student.advisor_id == current_user.id)

    if department:
        query = query.filter(models.Student.department == department)

    if semester:
        query = query.filter(models.Student.semester == semester)

    students = query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Student ID",
        "Name",
        "Department",
        "Semester",
        "Latest Risk",
        "Probability",
        "Model Version",
        "Prediction Date",
    ])

    for student in students:
        prediction = db.query(models.RiskPrediction).filter(
            models.RiskPrediction.student_db_id == student.id
        ).order_by(models.RiskPrediction.predicted_at.desc()).first()

        writer.writerow([
            student.student_id,
            student.full_name,
            student.department,
            student.semester,
            prediction.risk_category.value if prediction else "NOT PREDICTED",
            prediction.probability if prediction else "",
            prediction.model_version if prediction else "",
            prediction.predicted_at.isoformat() if prediction else "",
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=beacon_risk_report.csv"},
    )