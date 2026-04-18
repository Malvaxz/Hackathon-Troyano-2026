import json
import re

from diagnosis.prompt_builder import build_system_instruction, build_user_prompt
from diagnosis.gemini_client import run_gemini_raw


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


def clean_json_response(raw_response: str) -> str:
    cleaned = raw_response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def extract_json_object(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No se encontró un objeto JSON en la respuesta.")
    return match.group(0)


def validate_diagnosis_structure(data: dict) -> dict:
    required_fields = {
        "alert_level",
        "event_type",
        "clinical_rationale",
        "recommended_action",
        "confidence",
    }

    missing = required_fields - data.keys()
    if missing:
        raise ValueError(f"Faltan campos obligatorios: {missing}")

    if data["alert_level"] not in ALLOWED_ALERT_LEVELS:
        raise ValueError(f"alert_level inválido: {data['alert_level']}")

    if data["event_type"] not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"event_type inválido: {data['event_type']}")

    if data["recommended_action"] not in ALLOWED_ACTIONS:
        raise ValueError(f"recommended_action inválido: {data['recommended_action']}")

    if not isinstance(data["clinical_rationale"], str) or not data["clinical_rationale"].strip():
        raise ValueError("clinical_rationale vacío o inválido.")

    try:
        data["confidence"] = float(data["confidence"])
    except (TypeError, ValueError):
        raise ValueError("confidence no es numérico.")

    if data["confidence"] < 0:
        data["confidence"] = 0.0
    elif data["confidence"] > 1:
        data["confidence"] = 1.0

    return data


def build_fallback_diagnosis(raw_response: str, reason: str) -> dict:
    return {
        "alert_level": "medium",
        "event_type": "needs_manual_review",
        "clinical_rationale": f"{reason}. Respuesta original: {raw_response}",
        "recommended_action": "verify_patient",
        "confidence": 0.3,
    }


def parse_gemini_response(raw_response: str) -> dict:
    cleaned = clean_json_response(raw_response)

    try:
        parsed = json.loads(cleaned)
        return validate_diagnosis_structure(parsed)
    except Exception:
        pass

    try:
        extracted = extract_json_object(cleaned)
        parsed = json.loads(extracted)
        return validate_diagnosis_structure(parsed)
    except Exception as e:
        raise ValueError(f"No se pudo parsear/validar la respuesta: {e}")


def fallback_diagnosis(ai_payload: dict) -> dict:
    hr = ai_payload["heart_rate"]
    movement = ai_payload["movement_level"]
    edge = ai_payload["edge_risk"]
    pressure = ai_payload["pressure_risk_score"]

    if edge:
        return {
            "alert_level": "high",
            "event_type": "fall_risk",
            "clinical_rationale": "Paciente en el borde de la cama",
            "recommended_action": "verify_patient",
            "confidence": 0.9
        }

    if pressure > 0.8:
        return {
            "alert_level": "high",
            "event_type": "pressure_ulcer_risk",
            "clinical_rationale": "Presión prolongada detectada",
            "recommended_action": "reposition_patient",
            "confidence": 0.9
        }

    if hr > 110 and movement > 0.7:
        return {
            "alert_level": "low",
            "event_type": "possible_false_alarm",
            "clinical_rationale": "Movimiento alto con frecuencia cardiaca elevada",
            "recommended_action": "monitor",
            "confidence": 0.8
        }

    return {
        "alert_level": "low",
        "event_type": "normal_movement",
        "clinical_rationale": "Condiciones normales",
        "recommended_action": "monitor",
        "confidence": 0.9
    }


def run_gemini_diagnosis(ai_payload: dict) -> dict:
    system_instruction = build_system_instruction()
    user_prompt = build_user_prompt(ai_payload)

    try:
        raw_response = run_gemini_raw(system_instruction, user_prompt)
    except Exception as e:
        print("⚠️ Gemini falló, usando fallback:", str(e))
        return fallback_diagnosis(ai_payload)

    try:
        return parse_gemini_response(raw_response)
    except Exception as e:
        print("⚠️ No se pudo parsear la respuesta de Gemini, usando fallback:", str(e))
        return fallback_diagnosis(ai_payload)