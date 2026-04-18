import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from simulator.generator import generate_case
from ingestion.normalizer import normalize_input
from ingestion.extractor import extract_for_ai
from diagnosis.diagnosis_service import run_gemini_diagnosis
from validation.schema_validator import validate_schema
from validation.logic_validator import validate_logic
from validation.fatigue_reducer import reduce_alarm_fatigue


scenario_name = "possible_false_alarm"

raw = generate_case(scenario_name)
normalized = normalize_input(raw)
ai_payload = extract_for_ai(normalized)
diagnosis = run_gemini_diagnosis(ai_payload)

schema_result = validate_schema(diagnosis)

if not schema_result["is_valid"]:
    print("SCHEMA ERRORS:")
    print(schema_result["errors"])
else:
    validated_diagnosis = schema_result["validated_diagnosis"]

    logic_result = validate_logic(ai_payload, validated_diagnosis)
    corrected_diagnosis = logic_result["corrected_diagnosis"]

    previous_alerts = [
        {
            "event_type": "possible_false_alarm",
            "alert_level": "low",
            "recommended_action": "monitor"
        }
    ]

    fatigue_result = reduce_alarm_fatigue(corrected_diagnosis, previous_alerts)

    print("RAW:")
    print(raw)

    print("\nAI PAYLOAD:")
    print(ai_payload)

    print("\nGEMINI DIAGNOSIS:")
    print(diagnosis)

    print("\nSCHEMA RESULT:")
    print(schema_result)

    print("\nLOGIC RESULT:")
    print(logic_result)

    print("\nFATIGUE RESULT:")
    print(fatigue_result)