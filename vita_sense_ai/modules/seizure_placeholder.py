from modules.base_module import build_placeholder_response


def detect_seizure_placeholder(ai_payload: dict) -> dict:
    return build_placeholder_response(
        module_name="seizure",
        future_inputs=[
            "repetitive_movement_pattern",
            "movement_intensity_curve",
            "episode_duration_seconds",
            "bcg_anomaly_pattern"
        ],
        notes=(
            "Módulo reservado para detección futura de convulsiones. "
            "Requerirá análisis temporal de movimiento repetitivo, duración del episodio "
            "y posibles anomalías vibracionales."
        )
    )