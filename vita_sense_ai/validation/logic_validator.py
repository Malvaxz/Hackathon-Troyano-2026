def validate_logic(ai_payload: dict, diagnosis: dict) -> dict:
    warnings = []
    corrected = diagnosis.copy()

    edge_risk = ai_payload["edge_risk"]
    prolonged_static_pressure = ai_payload["prolonged_static_pressure"]
    movement_level = ai_payload["movement_level"]
    spo2 = ai_payload["spo2"]
    heart_rate = ai_payload["heart_rate"]

    event_type = diagnosis["event_type"]
    alert_level = diagnosis["alert_level"]
    confidence = diagnosis["confidence"]

    # Regla 1: si hay edge_risk, no debería ser normal_movement
    if edge_risk and event_type == "normal_movement":
        warnings.append("edge_risk presente pero event_type fue normal_movement")
        corrected["event_type"] = "fall_risk"
        corrected["recommended_action"] = "verify_patient"
        if corrected["alert_level"] == "low":
            corrected["alert_level"] = "medium"

    # Regla 2: si hay presión prolongada, no debería ignorarse riesgo de escaras
    if prolonged_static_pressure and event_type == "normal_movement":
        warnings.append("prolonged_static_pressure presente pero event_type fue normal_movement")
        corrected["event_type"] = "pressure_ulcer_risk"
        corrected["recommended_action"] = "reposition_patient"
        if corrected["alert_level"] == "low":
            corrected["alert_level"] = "medium"

    # Regla 3: FC alta + movimiento alto + SpO2 normal sí puede ser falsa alarma
    if heart_rate >= 110 and movement_level >= 0.7 and spo2 >= 95:
        if event_type not in {"possible_false_alarm", "needs_manual_review"}:
            warnings.append("patrón compatible con falsa alarma, pero Gemini devolvió otro evento")

    # Regla 4: critical con confianza baja es inconsistente
    if alert_level == "critical" and confidence < 0.5:
        warnings.append("alerta critical con confidence baja")
        corrected["event_type"] = "needs_manual_review"
        corrected["recommended_action"] = "verify_patient"

    return {
        "is_logically_valid": len(warnings) == 0,
        "warnings": warnings,
        "corrected_diagnosis": corrected
    }