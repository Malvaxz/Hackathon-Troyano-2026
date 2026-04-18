import json


def build_system_instruction() -> str:
    return """
Eres el módulo de interpretación clínica de VITA-Sense.

Tu función es analizar señales derivadas de una cama hospitalaria inteligente y emitir
un veredicto estructurado para priorización de alertas.

Restricciones:
- No diagnosticas enfermedades.
- No sustituyes al personal médico.
- Solo clasificas eventos dentro del MVP actual.
- Si hay ambigüedad, usa "needs_manual_review".
- Sé conservador con alertas críticas.
- Devuelve únicamente JSON puro.
- No agregues explicaciones fuera del JSON.
- No uses bloques markdown.
- No uses ```json ni ```.
- Escribe el campo "clinical_rationale" en español claro y breve.
- Mantén los valores técnicos de "alert_level", "event_type" y "recommended_action" exactamente como fueron definidos.
""".strip()


def build_user_prompt(ai_payload: dict) -> str:
    return f"""
Analiza el siguiente evento de VITA-Sense y clasifícalo.

Reglas del MVP:
- Si edge_risk = true, considera riesgo de caída.
- Si prolonged_static_pressure = true, considera riesgo de escaras.
- Si heart_rate está alto, movement_level está alto y spo2 está normal, considera possible_false_alarm.
- Si los datos no son concluyentes, usa needs_manual_review.

Importante:
- El campo "clinical_rationale" debe escribirse en español.
- Los valores de "alert_level", "event_type" y "recommended_action" deben mantenerse exactamente como se especifican.

Datos de entrada:
{json.dumps(ai_payload, indent=2)}

Devuelve un JSON con estos campos:
- alert_level: low | medium | high | critical
- event_type: normal_movement | fall_risk | pressure_ulcer_risk | possible_false_alarm | needs_manual_review
- clinical_rationale: string breve
- recommended_action: monitor | verify_patient | reposition_patient | notify_staff
- confidence: número entre 0 y 1
""".strip()