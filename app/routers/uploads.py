import io

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import models
from app.dependencies import get_db
from app.routers.auth import require_roles
from app.services.audit import create_audit_log
from app.services.validation import REQUIRED_UPLOAD_COLUMNS, validate_upload_row

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/students")
async def upload_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(models.UserRole.ADMIN)),
):
    filename = file.filename or ""

    if not (filename.endswith(".csv") or filename.endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Upload only CSV or XLSX files")

    content = await file.read()

    try:
        if filename.endswith(".csv"):
            dataframe = pd.read_csv(io.BytesIO(content))
        else:
            dataframe = pd.read_excel(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to read the uploaded file")

    dataframe.columns = [str(column).strip().lower() for column in dataframe.columns]

    missing_columns = REQUIRED_UPLOAD_COLUMNS - set(dataframe.columns)
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(sorted(missing_columns))}",
        )

    batch = models.UploadBatch(
        original_filename=filename,
        uploaded_by_user_id=current_user.id,
        total_rows=len(dataframe),
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    errors = []
    valid_count = 0

    for index, row in dataframe.iterrows():
        row_number = int(index) + 2
        row_dict = row.where(pd.notnull(row), None).to_dict()

        row_errors = validate_upload_row(row_dict, row_number)
        if row_errors:
            errors.extend(row_errors)
            continue

        student = db.query(models.Student).filter(
            models.Student.student_id == str(row_dict["student_id"])
        ).first()

        if student is None:
            student = models.Student(
                student_id=str(row_dict["student_id"]),
                full_name=str(row_dict["full_name"]),
                department=str(row_dict["department"]),
                program=str(row_dict["program"]) if row_dict.get("program") else None,
                semester=int(row_dict["semester"]),
                admission_year=int(row_dict["admission_year"])
                if row_dict.get("admission_year") is not None
                else None,
            )
            db.add(student)
            db.flush()

        academic_record = models.AcademicRecord(
            student_db_id=student.id,
            upload_batch_id=batch.id,
            semester=int(row_dict["semester"]),
            cgpa=float(row_dict["cgpa"]) if row_dict.get("cgpa") is not None else None,
            sgpa=float(row_dict["sgpa"]) if row_dict.get("sgpa") is not None else None,
            internal_marks=float(row_dict["internal_marks"])
            if row_dict.get("internal_marks") is not None
            else None,
            backlog_count=int(row_dict["backlog_count"]),
        )

        attendance_record = models.AttendanceRecord(
            student_db_id=student.id,
            upload_batch_id=batch.id,
            semester=int(row_dict["semester"]),
            attendance_percentage=float(row_dict["attendance_percentage"]),
        )

        db.add(academic_record)
        db.add(attendance_record)
        valid_count += 1

    batch.valid_rows = valid_count
    batch.invalid_rows = len(dataframe) - valid_count
    db.commit()

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPLOAD_STUDENT_DATA",
        entity_type="UploadBatch",
        entity_id=str(batch.id),
        details=f"Uploaded {filename}: {valid_count} valid rows, {len(errors)} errors",
    )

    return {
        "message": "Upload processed",
        "batch_id": batch.id,
        "total_rows": len(dataframe),
        "valid_rows": valid_count,
        "invalid_rows": len(dataframe) - valid_count,
        "errors": errors,
    }