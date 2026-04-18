import os
import time
import random
import sys
from collections import deque
from dotenv import load_dotenv
import requests
from pymongo import MongoClient

# ==========================================
# CONFIG
# ==========================================
load_dotenv()

BED_ID = os.getenv("BED_ID", "BED_01")
PHYPHOX_IP = os.getenv("PHYPHOX_IP", "10.37.90.111")
PHYPHOX_PORT = os.getenv("PHYPHOX_PORT", "8080")
PHYPHOX_URL = f"http://{PHYPHOX_IP}:{PHYPHOX_PORT}/get?accZ"

MONGO_URI = os.getenv("MONGO_URI")

# 👇 Escenario fijo (puedes cambiarlo manualmente)
current_scenario = "NORMAL"
# Opciones: NORMAL | BORDE | VACIO

# ==========================================
# FILTRO DSP
# ==========================================
class MovingAverageFilter:
    def __init__(self, window_size=5):
        self.buffer = deque(maxlen=window_size)
        self._sum = 0.0

    def process(self, value):
        if len(self.buffer) == self.buffer.maxlen:
            self._sum -= self.buffer[0]
        self.buffer.append(value)
        self._sum += value
        return self._sum / len(self.buffer)

# ==========================================
# CONEXIÓN A MONGO
# ==========================================
try:
    print("📡 Conectando a Mongo...")
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        directConnection=True
    )
    client.admin.command('ping')

    db = client["vitasense"]
    collection = db["historial_camas"]

    print("✅ Conectado a MongoDB")
except Exception as e:
    print(f"❌ Error Mongo: {e}")
    sys.exit(1)

# ==========================================
# SIMULACIÓN DE SIGNOS VITALES
# ==========================================
def simulate_vitals(vibration):
    if current_scenario == "VACIO":
        return {"heart_rate": 0, "resp_rate": 0, "spo2": 0}

    abs_vibe = abs(vibration)

    if abs_vibe > 0.30:
        return {"heart_rate": random.randint(100, 125), "resp_rate": random.randint(20, 26), "spo2": random.randint(92, 95)}
    elif abs_vibe > 0.15:
        return {"heart_rate": random.randint(80, 95), "resp_rate": random.randint(16, 20), "spo2": random.randint(96, 98)}
    else:
        return {"heart_rate": random.randint(70, 78), "resp_rate": random.randint(14, 18), "spo2": random.randint(97, 99)}

# ==========================================
# LOOP PRINCIPAL
# ==========================================
def run_sensor():
    print(f"🚀 VITA-Sense Sensor activo ({current_scenario})")
    print("-" * 60)

    filter = MovingAverageFilter()
    session = requests.Session()

    while True:
        try:
            # Leer Phyphox
            res = session.get(PHYPHOX_URL, timeout=0.5)
            data = res.json()

            buffer_data = data.get('buffer', {}).get('accZ', {}).get('buffer', [])
            raw_vibe = float(buffer_data[-1]) if buffer_data else 0.0

            # Filtrar
            clean_vibe = filter.process(raw_vibe)

            # Signos vitales
            vitals = simulate_vitals(clean_vibe)

            # Presión
            if current_scenario == "BORDE":
                matrix = [1.0, 0.0, 0.0, 0.0] * 4
                is_edge = True
            elif current_scenario == "VACIO":
                matrix = [0.0] * 16
                is_edge = False
            else:
                matrix = [0.0]*4 + [0.0, 0.8, 0.8, 0.0]*2 + [0.0]*4
                is_edge = False

            payload = {
                "bed_id": BED_ID,
                "sensors": {
                    "pressure_matrix": matrix,
                    "bcg_vibration": round(clean_vibe, 4),
                    "is_edge_active": is_edge
                },
                "clinical_monitor": vitals,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }

            collection.insert_one(payload)

            print(f"\r📊 Vib: {clean_vibe:+.4f} | HR: {vitals['heart_rate']} | SpO2: {vitals['spo2']}% | DB ✔", end="")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            time.sleep(2)

        time.sleep(0.5)

if __name__ == "__main__":
    run_sensor()