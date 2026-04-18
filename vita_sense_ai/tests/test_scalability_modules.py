import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from simulator.generator import generate_case
from ingestion.normalizer import normalize_input
from ingestion.extractor import extract_for_ai
from modules.seizure_placeholder import detect_seizure_placeholder
from modules.apnea_placeholder import detect_apnea_placeholder


scenario_name = "normal_rest"

raw = generate_case(scenario_name)
normalized = normalize_input(raw)
ai_payload = extract_for_ai(normalized)

seizure_result = detect_seizure_placeholder(ai_payload)
apnea_result = detect_apnea_placeholder(ai_payload)

print("AI PAYLOAD:")
print(ai_payload)

print("\nSEIZURE PLACEHOLDER:")
print(seizure_result)

print("\nAPNEA PLACEHOLDER:")
print(apnea_result)