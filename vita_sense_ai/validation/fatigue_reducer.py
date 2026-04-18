def reduce_alarm_fatigue(current_diagnosis: dict, previous_alerts: list) -> dict:
    """
    previous_alerts: lista de dicts con alertas previas del mismo bed_id
    """
    suppressed = False
    suppression_reason = None
    final_alert = current_diagnosis.copy()

    current_event = current_diagnosis["event_type"]
    current_level = current_diagnosis["alert_level"]

    # Regla 1: suprimir repetición exacta inmediata
    if previous_alerts:
        last_alert = previous_alerts[-1]

        if (
            last_alert["event_type"] == current_event and
            last_alert["alert_level"] == current_level
        ):
            suppressed = True
            suppression_reason = "Alerta repetida consecutiva"

    # Regla 2: falsa alarma con low se mantiene en monitor
    if current_event == "possible_false_alarm" and current_level == "low":
        final_alert["recommended_action"] = "monitor"

    # Regla 3: needs_manual_review nunca se suprime si viene con high/critical
    if current_event == "needs_manual_review" and current_level in {"high", "critical"}:
        suppressed = False
        suppression_reason = None

    return {
        "emit_alert": not suppressed,
        "suppressed": suppressed,
        "suppression_reason": suppression_reason,
        "final_alert": final_alert
    }