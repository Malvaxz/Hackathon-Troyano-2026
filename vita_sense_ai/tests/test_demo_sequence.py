import sys
from pathlib import Path
from time import sleep

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from simulator.generator import generate_case
from ingestion.normalizer import normalize_input
from ingestion.extractor import extract_for_ai
from diagnosis.diagnosis_service import run_gemini_diagnosis
from validation.schema_validator import validate_schema
from validation.logic_validator import validate_logic
from validation.fatigue_reducer import reduce_alarm_fatigue


SCENARIO_SEQUENCE = [
    "normal_rest",
    "high_movement",
    "possible_false_alarm",
    "fall_risk",
    "pressure_ulcer_risk",
]


def process_scenario(scenario_name: str, previous_alerts: list) -> dict:
    raw = generate_case(scenario_name)
    normalized = normalize_input(raw)
    ai_payload = extract_for_ai(normalized)
    diagnosis = run_gemini_diagnosis(ai_payload)

    schema_result = validate_schema(diagnosis)
    if not schema_result["is_valid"]:
        return {
            "scenario": scenario_name,
            "raw": raw,
            "normalized": normalized,
            "ai_payload": ai_payload,
            "diagnosis": diagnosis,
            "schema_result": schema_result,
            "logic_result": None,
            "fatigue_result": None,
        }

    validated_diagnosis = schema_result["validated_diagnosis"]
    logic_result = validate_logic(ai_payload, validated_diagnosis)
    corrected_diagnosis = logic_result["corrected_diagnosis"]

    fatigue_result = reduce_alarm_fatigue(corrected_diagnosis, previous_alerts)

    if fatigue_result["emit_alert"]:
        previous_alerts.append(fatigue_result["final_alert"])

    return {
        "scenario": scenario_name,
        "raw": raw,
        "normalized": normalized,
        "ai_payload": ai_payload,
        "diagnosis": diagnosis,
        "schema_result": schema_result,
        "logic_result": logic_result,
        "fatigue_result": fatigue_result,
    }


def print_result(result: dict):
    print("=" * 80)
    print(f"SCENARIO: {result['scenario']}")

    print("\nRAW:")
    print(result["raw"])

    print("\nNORMALIZED:")
    print(result["normalized"])

    print("\nAI PAYLOAD:")
    print(result["ai_payload"])

    print("\nGEMINI DIAGNOSIS:")
    print(result["diagnosis"])

    print("\nSCHEMA RESULT:")
    print(result["schema_result"])

    if result["logic_result"] is not None:
        print("\nLOGIC RESULT:")
        print(result["logic_result"])

    if result["fatigue_result"] is not None:
        print("\nFATIGUE RESULT:")
        print(result["fatigue_result"])

    print("=" * 80)
    print()


def main():
    previous_alerts = []

    for scenario in SCENARIO_SEQUENCE:
        result = process_scenario(scenario, previous_alerts)
        print_result(result)

        # pausa pequeña opcional para que se vea como secuencia
        sleep(1)


if __name__ == "__main__":
    main()