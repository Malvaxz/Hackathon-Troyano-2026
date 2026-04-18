import os
from dotenv import load_dotenv
from google import genai

# 🔹 Cargar variables del .env
load_dotenv()

# 🔹 Verificar si la variable existe
print("API KEY:", os.getenv("GEMINI_API_KEY"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Responde solo: API funcionando"
)

print(response.text)


#pip install google-genai
#pip install python-dotenv