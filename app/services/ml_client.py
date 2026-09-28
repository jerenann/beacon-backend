def predict_student(student_features: dict) -> dict:
    """
    Temporary demo prediction.
    Member 1 will replace this with the real model-loading
    and SHAP-explanation code.
    """

    attendance = float(student_features.get("attendance_percentage", 75))
    backlogs = int(student_features.get("backlog_count", 0))
    cgpa = student_features.get("cgpa")

    probability = 0.15

    if attendance < 75:
        probability += 0.25

    if attendance < 60:
        probability += 0.15

    if backlogs >= 1:
        probability += min(backlogs * 0.08, 0.25)

    if cgpa is not None and float(cgpa) < 6:
        probability += 0.15

    probability = min(round(probability, 2), 0.99)

    explanations = []

    if attendance < 75:
        explanations.append({
            "feature_name": "Attendance Percentage",
            "feature_value": str(attendance),
            "shap_value": 0.25,
            "direction": "RISK_INCREASING",
        })

    if backlogs > 0:
        explanations.append({
            "feature_name": "Backlog Count",
            "feature_value": str(backlogs),
            "shap_value": min(backlogs * 0.08, 0.25),
            "direction": "RISK_INCREASING",
        })

    if cgpa is not None and float(cgpa) < 6:
        explanations.append({
            "feature_name": "CGPA",
            "feature_value": str(cgpa),
            "shap_value": 0.15,
            "direction": "RISK_INCREASING",
        })

    if not explanations:
        explanations.append({
            "feature_name": "Academic Status",
            "feature_value": "Stable",
            "shap_value": -0.10,
            "direction": "PROTECTIVE",
        })

    return {
        "probability": probability,
        "explanations": explanations,
        "model_version": "demo-rule-model-v1",
    }