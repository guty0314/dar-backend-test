#!/usr/bin/env python3
"""Prueba de integración vía API (requiere servidor corriendo).

Flujo:
1. Autentica con /token usando usuario `nieto` / `ABC123`.
2. Registra el `DEVICE_TOKEN_REAL` para el usuario autenticado (PUT /users/me/device_token/).
3. Crea una emergencia real (POST /emergencies/).
4. Opcional: intenta enviar localmente (desde el script) una notificación idéntica vía Firebase
   para garantizar que el dispositivo reciba el mensaje (útil si la tarea en background del servidor
   no llega por alguna razón inmediata).

Requisitos: tener el servidor FastAPI corriendo en `http://127.0.0.1:8000` y la variable
de entorno `GOOGLE_APPLICATION_CREDENTIALS` configurada si desea que la parte de Firebase funcione.
"""

from __future__ import annotations

import os
import sys
import time
import logging
from pathlib import Path

try:
    import requests
except Exception:
    raise SystemExit("Instala la dependencia 'requests' (pip install requests) para usar este script")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_logger = logging.getLogger("test_api_emergency")

# Configuración
BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")
TEST_USERNAME = "nieto"
TEST_PASSWORD = "ABC123"

# Token del dispositivo real proporcionado por el usuario
DEVICE_TOKEN_REAL = (
    "frO7eBL6Q-WKlfjKlmM8CH:APA91bGXJi4A4WhjPVc8PtZmkwxWMD7WbAnUnM1_yOeD_nsgsdTd7Z8dlbyPZ29zEI-9pJPIb_fsWCL8DFQhHkgYYBwl0DWk2B9qlzz4Y3q2AWfPZAyFN68"
)


def authenticate(username: str, password: str) -> str:
    url = f"{BASE_URL}/token"
    _logger.info("Autenticando en %s...", url)
    resp = requests.post(url, data={"username": username, "password": password})
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError("No se obtuvo access_token")
    _logger.info("Autenticación OK (token recibido)")
    return token


def register_device_token(token: str, device_token: str) -> None:
    url = f"{BASE_URL}/users/me/device_token/"
    headers = {"Authorization": f"Bearer {token}"}
    _logger.info("Registrando device_token en %s...", url)
    # El endpoint acepta el parámetro como query/form, enviamos como params
    resp = requests.put(url, params={"device_token": device_token}, headers=headers)
    resp.raise_for_status()
    _logger.info("Device token registrado en el servidor para el usuario autenticado")


def create_emergency(token: str, latitude: float, longitude: float, color: str) -> dict:
    url = f"{BASE_URL}/emergencies/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"latitude": latitude, "longitude": longitude, "emergency_color": color}
    _logger.info("Creando emergencia en %s ...", url)
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    _logger.info("Emergencia creada (respuesta recibida)")
    return resp.json()


def send_direct_firebase_notification(title: str, body: str, data: dict[str, str], to_token: str) -> bool:
    """Intenta enviar la misma notificación directamente usando Firebase Admin (opcional).
    Devuelve True si el envío fue aceptado por FCM.
    """
    try:
        import firebase_admin
        from firebase_admin import credentials, messaging
    except Exception as e:
        _logger.warning("No se pudo importar firebase_admin: %s. Saltando envío directo.", e)
        return False

    # Inicializar si es necesario
    try:
        if not firebase_admin._apps:
            from dotenv import load_dotenv, find_dotenv
            load_dotenv(find_dotenv())  # Cargar .env si existe
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not cred_path:
                _logger.warning("GOOGLE_APPLICATION_CREDENTIALS no definida; no se puede inicializar firebase_admin")
                return False
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
    except Exception as e:
        _logger.exception("Error inicializando firebase_admin: %s", e)
        return False

    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in data.items()},
            token=to_token,
        )
        resp = messaging.send(message)
        _logger.info("Envío directo FCM aceptado: %s", resp)
        return True
    except Exception as e:
        _logger.exception("Envío directo FCM falló: %s", e)
        return False


def main() -> int:
    # 1) Autenticación
    try:
        access_token = authenticate(TEST_USERNAME, TEST_PASSWORD)
    except Exception as e:
        _logger.error("Fallo en autenticación: %s", e)
        return 1

    # 2) Registrar device token para el usuario autenticado
    try:
        register_device_token(access_token, DEVICE_TOKEN_REAL)
    except Exception as e:
        _logger.error("Fallo al registrar device token: %s", e)
        return 2

    # 3) Crear emergencia cerca del usuario (usamos las coordenadas del usuario 'nieto' por defecto)
    # Estas coordenadas están definidas en `main.init_db` y en tests locales.
    latitude = -34.6038
    longitude = -58.3816
    color = "rojo"

    try:
        resp = create_emergency(access_token, latitude, longitude, color)
        _logger.info("Respuesta del endpoint /emergencies/: %s", resp)
    except Exception as e:
        _logger.error("Fallo al crear emergencia via API: %s", e)
        return 3

    # Esperar un poco para que las tareas en background del servidor procesen notificaciones
    _logger.info("Esperando 2s para que el servidor procese notificaciones en background...")
    time.sleep(2)

    # 4) Envío directo (opcional) de la notificación al dispositivo real con payload de primera zona
    title = f"Emergencia: {color}"
    body = f"{TEST_USERNAME} reportó una emergencia. Estás en zona CRÍTICA (Primer Anillo)"
    data = {
        "emergency_id": str(resp.get("emergency_id", "-1")),
        "ring_zone": "1",
        "reporter_username": TEST_USERNAME,
        "reporter_full_name": TEST_USERNAME,
        "reporter_latitude": str(latitude),
        "reporter_longitude": str(longitude),
        "emergency_color": color,
    }

    sent = send_direct_firebase_notification(title, body, data, DEVICE_TOKEN_REAL)
    if sent:
        _logger.info("Envío directo de prueba completado (FCM)")
    else:
        _logger.info("No se realizó envío directo (FCM no disponible o falló). Confiando en envío desde el servidor.")

    _logger.info("Prueba finalizada. Verifica el dispositivo para confirmar recepción.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
