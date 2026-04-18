SCENARIOS = {
    "normal_rest": {
        "pressure_matrix": [0.2, 0.3, 0.2, 0.3],
        "bcg_vibration": 18.0,
        "is_edge_active": False,
        "heart_rate": 74,
        "resp_rate": 16,
        "spo2": 98
    },
    "high_movement": {
        "pressure_matrix": [0.4, 0.6, 0.5, 0.7],
        "bcg_vibration": 82.0,
        "is_edge_active": False,
        "heart_rate": 116,
        "resp_rate": 22,
        "spo2": 97
    },
    "fall_risk": {
        "pressure_matrix": [0.1, 0.2, 0.9, 1.0],
        "bcg_vibration": 67.0,
        "is_edge_active": True,
        "heart_rate": 108,
        "resp_rate": 20,
        "spo2": 97
    },
    "pressure_ulcer_risk": {
        "pressure_matrix": [0.9, 0.9, 0.8, 0.9],
        "bcg_vibration": 8.0,
        "is_edge_active": False,
        "heart_rate": 76,
        "resp_rate": 15,
        "spo2": 98
    },
    "possible_false_alarm": {
        "pressure_matrix": [0.3, 0.5, 0.4, 0.5],
        "bcg_vibration": 88.0,
        "is_edge_active": False,
        "heart_rate": 124,
        "resp_rate": 24,
        "spo2": 98
    }
}