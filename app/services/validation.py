REQUIRED_UPLOAD_COLUMNS = {
    "student_id",
    "full_name",
    "department",
    "semester",
    "attendance_percentage",
    "backlog_count",
}


def validate_upload_row(row: dict, row_number: int) -> list[str]:
    errors = []

    for column in REQUIRED_UPLOAD_COLUMNS:
        value = row.get(column)
        if value is None or str(value).strip() == "":
            errors.append(f"Row {row_number}: Missing required field '{column}'")

    try:
        attendance = float(row.get("attendance_percentage", 0))
        if attendance < 0 or attendance > 100:
            errors.append(f"Row {row_number}: attendance_percentage must be between 0 and 100")
    except (TypeError, ValueError):
        errors.append(f"Row {row_number}: attendance_percentage must be a number")

    try:
        backlog_count = int(row.get("backlog_count", 0))
        if backlog_count < 0:
            errors.append(f"Row {row_number}: backlog_count cannot be negative")
    except (TypeError, ValueError):
        errors.append(f"Row {row_number}: backlog_count must be an integer")

    if row.get("cgpa") not in (None, ""):
        try:
            cgpa = float(row["cgpa"])
            if cgpa < 0 or cgpa > 10:
                errors.append(f"Row {row_number}: cgpa must be between 0 and 10")
        except (TypeError, ValueError):
            errors.append(f"Row {row_number}: cgpa must be a number")

    return errors