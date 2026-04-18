import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("No se encontró la variable MONGO_URI en el archivo .env")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    directConnection=True
)

db = client["vitasense"]
collection = db["historial_camas"]


def get_latest_bed_record() -> dict | None:
    """
    Lee el documento más reciente de MongoDB.
    Devuelve None si no hay datos.
    """
    latest = collection.find_one(sort=[("_id", -1)])

    if not latest:
        return None

    latest.pop("_id", None)
    return latest