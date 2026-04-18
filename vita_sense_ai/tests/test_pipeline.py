import sys
from pathlib import Path

# Agrega la raíz del proyecto al path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ingestion.normalizer import normalize_input

raw = {
    "bed_id": "BED_01",
    "sensors": {
        "pressure_matrix": [0.1, 0.8, 0.0, 1.0],
        "bcg_vibration": 45.2,
        "is_edge_active": False
    },
    "clinical_monitor": {
        "heart_rate": 75,
        "resp_rate": 16,
        "spo2": 98
    },
    "timestamp": "2026-04-17T20:40:00Z"
}

normalized = normalize_input(raw)

print("OUTPUT NORMALIZADO:")
print(normalized)