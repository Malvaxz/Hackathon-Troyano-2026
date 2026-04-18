from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL


def get_gemini_client():
    if not GEMINI_API_KEY:
        raise ValueError("No se encontró GEMINI_API_KEY.")
    return genai.Client(api_key=GEMINI_API_KEY)


def run_gemini_raw(system_instruction: str, user_prompt: str) -> str:
    client = get_gemini_client()

    full_prompt = f"{system_instruction}\n\n{user_prompt}"

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=full_prompt
    )

    return response.text