import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from simulator.generator import generate_case
from ingestion.normalizer import normalize_input
from ingestion.extractor import extract_for_ai
from diagnosis.diagnosis_service import run_gemini_diagnosis


scenario_name = "possible_false_alarm"

raw = generate_case(scenario_name)
normalized = normalize_input(raw)
ai_payload = extract_for_ai(normalized)
diagnosis = run_gemini_diagnosis(ai_payload)

print("RAW:")
print(raw)

print("\nNORMALIZED:")
print(normalized)

print("\nAI PAYLOAD:")
print(ai_payload)

print("\nGEMINI DIAGNOSIS:")
print(diagnosis)