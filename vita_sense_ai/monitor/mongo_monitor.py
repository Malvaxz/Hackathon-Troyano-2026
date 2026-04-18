import os
import time
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    print("❌ Error: No se encontró MONGO_URI en el archivo .env")
    sys.exit(1)

try:
    cliente = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        directConnection=True
    )
    cliente.admin.command("ping")

    db = cliente["vitasense"]
    collection = db["historial_camas"]
except Exception as e:
    print(f"❌ Error conectando a MongoDB: {e}")
    sys.exit(1)

print("📡 Iniciando Monitor Clínico VITA-Sense...")
print("Esperando datos nuevos (Ctrl+C para salir)...")
print("-" * 90)

ultimo_id_visto = None

try:
    while True:
        latest = collection.find_one(sort=[("_id", -1)])

        if latest:
            current_id = latest["_id"]

            if current_id != ultimo_id_visto:
                timestamp = latest.get("timestamp", "N/A")
                sensors = latest.get("sensors", {})
                vitals = latest.get("clinical_monitor", {})

                vibration = sensors.get("bcg_vibration", 0)
                is_edge = sensors.get("is_edge_active", False)
                pressure_matrix = sensors.get("pressure_matrix", [])

                hr = vitals.get("heart_rate", 0)
                rr = vitals.get("resp_rate", 0)
                spo2 = vitals.get("spo2", 0)

                pressure_avg = 0
                if pressure_matrix:
                    pressure_avg = round(sum(pressure_matrix) / len(pressure_matrix), 3)

                if is_edge:
                    status = "⚠️ RIESGO DE CAÍDA"
                elif hr == 0 and rr == 0 and spo2 == 0:
                    status = "⚫ CAMA VACÍA"
                elif pressure_avg > 0.8:
                    status = "🟠 RIESGO DE ESCARAS"
                elif hr > 100:
                    status = "🔴 ACTIVIDAD / AGITACIÓN"
                else:
                    status = "🟢 PACIENTE ESTABLE"

                print(
                    f"[{timestamp}] "
                    f"{status:<22} | "
                    f"Vib: {vibration:+.4f} | "
                    f"HR: {hr:>3} bpm | "
                    f"RR: {rr:>2} rpm | "
                    f"SpO2: {spo2:>2}% | "
                    f"PressureAvg: {pressure_avg}"
                )

                ultimo_id_visto = current_id

        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Monitor detenido por el usuario.")