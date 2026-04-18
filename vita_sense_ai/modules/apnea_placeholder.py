from modules.base_module import build_placeholder_response


def detect_apnea_placeholder(ai_payload: dict) -> dict:
    return build_placeholder_response(
        module_name="apnea",
        future_inputs=[
            "respiratory_pause_seconds",
            "bcg_respiration_pattern",
            "spo2_trend",
            "resp_rate_trend"
        ],
        notes=(
            "Módulo reservado para detección futura de apnea. "
            "Requerirá análisis de pausas respiratorias, patrón respiratorio derivado del BCG "
            "y tendencia de saturación de oxígeno."
        )
    )