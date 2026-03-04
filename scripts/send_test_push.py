#!/usr/bin/env python3
"""Script de prueba para enviar una notificación push usando
`services.notifications.send_push_notification`.

Este script usa el token que proporcionaste y hace un envío.
Si `firebase_admin` no está configurado o faltan credenciales, el módulo
hará un fallback y registrará la notificación en el log (útil en desarrollo).
"""

from __future__ import annotations

import logging
import sys
from typing import Dict, Any
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services import notifications

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Token proporcionado por el usuario
TOKEN = (
    "frO7eBL6Q-WKlfjKlmM8CH:APA91bGXJi4A4WhjPVc8PtZmkwxWMD7WbAnUnM1_yOeD_nsgsdTd7Z8dlbyPZ29zEI-9pJPIb_fsWCL8DFQhHkgYYBwl0DWk2B9qlzz4Y3q2AWfPZAyFN68"
)


def main() -> int:
    title = "Prueba FCM"
    body = "Mensaje de prueba desde send_test_push.py"
    data: Dict[str, Any] = {"env": "test"}

    logging.info("Enviando notificación de prueba al token proporcionado...")
    ok = notifications.send_push_notification(TOKEN, title, body, data)
    if ok:
        logging.info("Resultado: Envío OK (o log fallback realizado).")
        print("ENVIADO")
        return 0
    else:
        logging.error("Resultado: Envío FALLIDO.")
        print("FALLÓ")
        return 2


if __name__ == "__main__":
    sys.exit(main())
