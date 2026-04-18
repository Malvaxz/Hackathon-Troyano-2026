ALLOWED_ALERT_LEVELS = {"low", "medium", "high", "critical"}
ALLOWED_EVENT_TYPES = {
    "normal_movement",
    "fall_risk",
    "pressure_ulcer_risk",
    "possible_false_alarm",
    "needs_manual_review",
}
ALLOWED_ACTIONS = {
    "monitor",
    "verify_patient",
    "reposition_patient",
    "notify_staff",
}


def validate_schema(diagnosis: dict) -> dict:
    errors = []

    required_fields = [
        "alert_level",
        "event_type",
        "clinical_rationale",
        "recommended_action",
        "confidence",
    ]

    for field in required_fields:
        if field not in diagnosis:
            errors.append(f"Falta campo obligatorio: {field}")

    if errors:
        return {
            "is_valid": False,
            "errors": errors,
            "validated_diagnosis": None
        }

    if diagnosis["alert_level"] not in ALLOWED_ALERT_LEVELS:
        errors.append(f"alert_level inválido: {diagnosis['alert_level']}")

    if diagnosis["event_type"] not in ALLOWED_EVENT_TYPES:
        errors.append(f"event_type inválido: {diagnosis['event_type']}")

    if diagnosis["recommended_action"] not in ALLOWED_ACTIONS:
        errors.append(f"recommended_action inválido: {diagnosis['recommended_action']}")

    if not isinstance(diagnosis["clinical_rationale"], str) or not diagnosis["clinical_rationale"].strip():
        errors.append("clinical_rationale vacío o inválido")

    try:
        diagnosis["confidence"] = float(diagnosis["confidence"])
    except (TypeError, ValueError):
        errors.append("confidence no es numérico")

    if "confidence" in diagnosis and isinstance(diagnosis["confidence"], (int, float)):
        if diagnosis["confidence"] < 0:
            diagnosis["confidence"] = 0.0
        elif diagnosis["confidence"] > 1:
            diagnosis["confidence"] = 1.0

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "validated_diagnosis": diagnosis if len(errors) == 0 else None
    }