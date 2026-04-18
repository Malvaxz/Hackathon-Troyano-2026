def build_placeholder_response(
    module_name: str,
    future_inputs: list,
    notes: str = "Pendiente de implementación futura"
) -> dict:
    return {
        "module": module_name,
        "status": "placeholder",
        "supported": False,
        "future_inputs": future_inputs,
        "notes": notes
    }