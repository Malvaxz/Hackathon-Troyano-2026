def extract_for_ai(normalized_data: dict) -> dict:
    return {
        "bed_id": normalized_data["bed_id"],
        "timestamp": normalized_data["timestamp"],
        "heart_rate": normalized_data["vitals"]["heart_rate"],
        "resp_rate": normalized_data["vitals"]["resp_rate"],
        "spo2": normalized_data["vitals"]["spo2"],
        "movement_level": normalized_data["movement"]["movement_level"],
        "movement_state": normalized_data["movement"]["movement_state"],
        "pressure_risk_score": normalized_data["pressure"]["pressure_risk_score"],
        "prolonged_static_pressure": normalized_data["pressure"]["prolonged_static_pressure"],
        "edge_risk": normalized_data["risk_flags"]["edge_risk"]
    }