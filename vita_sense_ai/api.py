from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data_sources.mongo_reader import get_latest_bed_record
from simulator.generator import generate_case
from ingestion.normalizer import normalize_input
from ingestion.extractor import extract_for_ai
from diagnosis.diagnosis_service import run_gemini_diagnosis, fallback_diagnosis
from validation.schema_validator import validate_schema
from validation.logic_validator import validate_logic
from validation.fatigue_reducer import reduce_alarm_fatigue


app = FastAPI(title="VITA-Sense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def format_central_time(iso_timestamp: str) -> str:
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    central_dt = dt.astimezone(ZoneInfo("America/Mexico_City"))
    return central_dt.strftime("%H:%M:%S")


def format_central_datetime(iso_timestamp: str) -> str:
    dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    central_dt = dt.astimezone(ZoneInfo("America/Mexico_City"))
    return central_dt.strftime("%d/%m/%Y %H:%M:%S")


def reshape_pressure_matrix(matrix: list[float], cols: int = 4) -> list[list[float]]:
    """
    Convierte una lista plana en una matriz por filas.
    Si vienen 16 valores, devuelve 4 filas de 4 columnas.
    """
    if not matrix:
        return [[0.0 for _ in range(cols)] for _ in range(cols)]

    rows = [matrix[i:i + cols] for i in range(0, len(matrix), cols)]

    # Si alguna fila queda incompleta, la rellenamos
    normalized_rows = []
    for row in rows:
        if len(row) < cols:
            row = row + [0.0] * (cols - len(row))
        normalized_rows.append(row)

    return normalized_rows


def run_common_pipeline(raw: dict):
    previous_alerts = []

    normalized = normalize_input(raw)
    ai_payload = extract_for_ai(normalized)

    movement_level = ai_payload["movement_level"]
    edge_risk = ai_payload["edge_risk"]
    prolonged_static_pressure = ai_payload["prolonged_static_pressure"]

    should_use_ai = (
        movement_level >= 0.5 or
        edge_risk or
        prolonged_static_pressure
    )
    analysis_source = "gemini" if should_use_ai else "rules"

    if should_use_ai:
        diagnosis = run_gemini_diagnosis(ai_payload)
    else:
        diagnosis = fallback_diagnosis(ai_payload)

    schema_result = validate_schema(diagnosis)
    if not schema_result["is_valid"]:
        return {
            "raw": raw,
            "normalized": normalized,
            "ai_payload": ai_payload,
            "diagnosis": diagnosis,
            "schema_result": schema_result,
            "logic_result": None,
            "fatigue_result": None,
            "analysis_source": analysis_source,
        }

    validated_diagnosis = schema_result["validated_diagnosis"]
    logic_result = validate_logic(ai_payload, validated_diagnosis)
    corrected_diagnosis = logic_result["corrected_diagnosis"]

    fatigue_result = reduce_alarm_fatigue(corrected_diagnosis, previous_alerts)

    if fatigue_result["emit_alert"]:
        previous_alerts.append(fatigue_result["final_alert"])

    return {
        "raw": raw,
        "normalized": normalized,
        "ai_payload": ai_payload,
        "diagnosis": diagnosis,
        "schema_result": schema_result,
        "logic_result": logic_result,
        "fatigue_result": fatigue_result,
        "analysis_source": analysis_source,
    }


def run_pipeline(scenario_name: str):
    raw = generate_case(scenario_name)
    result = run_common_pipeline(raw)
    result["scenario"] = scenario_name
    return result


def run_pipeline_from_raw(raw: dict):
    return run_common_pipeline(raw)


def build_dashboard_payload(result: dict):
    raw = result["raw"]
    normalized = result["normalized"]
    final_alert = result["fatigue_result"]["final_alert"] if result["fatigue_result"] else result["diagnosis"]

    movement_map = {
        "low": "Bajo",
        "moderate": "Moderado",
        "high": "Alto",
    }

    event_map = {
        "normal_movement": "Movimiento normal",
        "fall_risk": "Riesgo de caída",
        "pressure_ulcer_risk": "Riesgo de escaras",
        "possible_false_alarm": "Posible falsa alarma",
        "needs_manual_review": "Revisión manual necesaria",
    }

    action_map = {
        "monitor": "Monitorear",
        "verify_patient": "Verificar paciente",
        "reposition_patient": "Reposicionar paciente",
        "notify_staff": "Notificar al personal",
    }

    pressure_matrix = raw.get("sensors", {}).get("pressure_matrix", [])
    heatmap_matrix = reshape_pressure_matrix(pressure_matrix, cols=4)

    payload = {
        "bedId": raw["bed_id"],
        "patientName": "Paciente demo",
        "timestamp": format_central_datetime(raw["timestamp"]),
        "vitals": {
            "heartRate": raw["clinical_monitor"]["heart_rate"],
            "respRate": raw["clinical_monitor"]["resp_rate"],
            "spo2": raw["clinical_monitor"]["spo2"],
            "movement": movement_map.get(
                normalized["movement"]["movement_state"],
                normalized["movement"]["movement_state"]
            ),
        },
        "normalized": {
            "movementLevel": normalized["movement"]["movement_level"],
            "pressureRiskScore": normalized["pressure"]["pressure_risk_score"],
            "edgeRisk": normalized["risk_flags"]["edge_risk"],
            "prolongedStaticPressure": normalized["pressure"]["prolonged_static_pressure"],
        },
        "diagnosis": {
            "alertLevel": final_alert["alert_level"],
            "eventType": event_map.get(final_alert["event_type"], final_alert["event_type"]),
            "rationale": final_alert["clinical_rationale"],
            "action": action_map.get(final_alert["recommended_action"], final_alert["recommended_action"]),
            "confidence": final_alert["confidence"],
            "emitAlert": result["fatigue_result"]["emit_alert"] if result["fatigue_result"] else True,
            "suppressed": result["fatigue_result"]["suppressed"] if result["fatigue_result"] else False,
        },
        "history": [
            {
                "time": format_central_time(raw["timestamp"]),
                "event": event_map.get(final_alert["event_type"], final_alert["event_type"]),
                "status": final_alert["alert_level"],
            }
        ],
        "heatmap": heatmap_matrix,
        "analysisSource": result.get("analysis_source", "rules"),
    }

    return payload


@app.get("/")
def root():
    return {"message": "VITA-Sense API running"}


@app.get("/status")
def get_status(scenario: str = "normal_rest", source: str = "simulator"):
    if source == "mongo":
        raw = get_latest_bed_record()

        if not raw:
            return {"error": "No hay datos en MongoDB"}

        print("\n===== ULTIMO DATO LEIDO DE MONGO =====")
        print(raw)

        result = run_pipeline_from_raw(raw)
        payload = build_dashboard_payload(result)

        print("===== PAYLOAD ENVIADO AL DASHBOARD =====")
        print(payload)

        return payload

    result = run_pipeline(scenario)
    return build_dashboard_payload(result)