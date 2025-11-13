from pymongo import MongoClient
from bson import ObjectId
import os
import requests

from fastapi import HTTPException

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://admin:1234@cluster0.ts8dp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["Sorora"]
collection = db["alertas"]

NOTIFICACIONES_URL = os.getenv("NOTIFICACIONES_URL", "http://api-web-ii.vercel.app/notificaciones/enviar")

def crear_alerta(alerta, background_tasks):
    nueva_alerta = {
        "tipo": alerta.tipo,
        "descripcion": alerta.descripcion,
        "nivel": alerta.nivel,
        "latitude": alerta.latitude,
        "longitude": alerta.longitude
    }
    resultado = collection.insert_one(nueva_alerta)
    alerta_id = str(resultado.inserted_id)

    payload = {
        "asunto": f"Nueva alerta: {alerta.tipo}",
        "mensaje": f"Se ha registrado una alerta de nivel {alerta.nivel}\n\nDescripción: {alerta.descripcion}\nUbicación: ({alerta.latitude}, {alerta.longitude})"
    }

    background_tasks.add_task(enviar_notificacion, payload)
    return {"mensaje": "Alerta creada con éxito", "id": alerta_id}


def enviar_notificacion(payload):
    import requests
    try:
        requests.post("http://api-web-ii.vercel.app/notificaciones/enviar", json=payload, timeout=5)
    except Exception as e:
        print(f"Error al enviar notificación: {e}")
