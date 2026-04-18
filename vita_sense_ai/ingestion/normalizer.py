def normalize_input(raw: dict) -> dict:
    bed_id = raw.get("bed_id", "UNKNOWN")
    timestamp = raw.get("timestamp")

    sensors = raw.get("sensors", {})
    monitor = raw.get("clinical_monitor", {})

    pressure_matrix = sensors.get("pressure_matrix", [])
    bcg_vibration = float(sensors.get("bcg_vibration", 0.0))
    is_edge_active = bool(sensors.get("is_edge_active", False))

    heart_rate = int(monitor.get("heart_rate", 0))
    resp_rate = int(monitor.get("resp_rate", 0))
    spo2 = int(monitor.get("spo2", 0))

    # Riesgo por presión
    pressure_risk_score = 0.0
    if pressure_matrix:
        pressure_risk_score = sum(pressure_matrix) / len(pressure_matrix)

    # Movimiento basado en vibración
    movement_level = abs(bcg_vibration)

    if movement_level >= 0.50:
        movement_state = "high"
    elif movement_level >= 0.30:
        movement_state = "moderate"
    else:
        movement_state = "low"

    prolonged_static_pressure = pressure_risk_score >= 0.80 and movement_level < 0.10

    return {
        "bed_id": bed_id,
        "timestamp": timestamp,
        "vitals": {
            "heart_rate": heart_rate,
            "resp_rate": resp_rate,
            "spo2": spo2,
        },
        "movement": {
            "movement_level": round(movement_level, 4),
            "movement_state": movement_state,
        },
        "pressure": {
            "pressure_risk_score": round(pressure_risk_score, 4),
            "prolonged_static_pressure": prolonged_static_pressure,
        },
        "risk_flags": {
            "edge_risk": is_edge_active,
        },
    }