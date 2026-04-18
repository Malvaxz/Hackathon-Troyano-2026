from datetime import datetime, timezone
from simulator.scenarios import SCENARIOS


def generate_case(scenario_name: str, bed_id: str = "BED_01") -> dict:
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Escenario no válido: {scenario_name}")

    scenario = SCENARIOS[scenario_name]

    return {
        "bed_id": bed_id,
        "sensors": {
            "pressure_matrix": scenario["pressure_matrix"],
            "bcg_vibration": scenario["bcg_vibration"],
            "is_edge_active": scenario["is_edge_active"]
        },
        "clinical_monitor": {
            "heart_rate": scenario["heart_rate"],
            "resp_rate": scenario["resp_rate"],
            "spo2": scenario["spo2"]
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }