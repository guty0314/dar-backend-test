"""Envío de NOTIFICAIONES push usando Firebase Cloud Messaging (FCM).

- Se debe configurar variable de entorno `GOOGLE_APPLICATION_CREDENTIALS` apuntando
  al JSON de la cuenta de servicio de Firebase o inicializar firebase_admin
  manualmente antes de usar.

  

- Si `firebase_admin` no está configurado/available, el módulo hace log en consola
  en lugar de enviar notificaciones (fallback útil para desarrollo).
"""

from typing import Iterable, Dict, Any, List
import os
import logging

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    _HAS_FIREBASE = True
except Exception:
    firebase_admin = None
    messaging = None
    credentials = None
    _HAS_FIREBASE = False

_logger = logging.getLogger(__name__)


def _init_firebase():
    if not _HAS_FIREBASE:
        return False
    if firebase_admin._apps:
        return True
    
    # Cambiado a uso de .env para mayor flexibilidad (sin depender de cambio de SO)
    from dotenv import load_dotenv
    load_dotenv()  # Cargar variables de entorno desde .env si existe
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        _logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set; FCM not initialized")
        return False
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        return True
    except Exception as e:
        _logger.exception("Failed to initialize firebase_admin: %s", e)
        return False


def send_push_notification(
    token: str, title: str, body: str, data: Dict[str, Any] | None = None
) -> bool:
    """Envía una notificación push a un único token.

    Devuelve True si el envío se realizó sin excepción.
    """
    if not token:
        return False
    payload_data = data or {}
    # Intentar enviar vía FCM si está disponible
    if _init_firebase():
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data={k: str(v) for k, v in payload_data.items()},
                token=token,
            )
            resp = messaging.send(message)
            _logger.info("FCM sent: %s", resp)
            return True
        except Exception as e:
            _logger.exception("FCM send failed: %s", e)
            return False

    # Fallback: log the notification (útil para desarrollo sin credenciales)
    _logger.info("[PUSH LOG] To=%s Title=%s Body=%s Data=%s", token, title, body, payload_data)
    return True


def send_push_notifications(tokens: Iterable[str], title: str, body: str, data: Dict[str, Any] | None = None) -> Dict[str, int]:
    """Envía notificaciones a varios tokens. Retorna conteo de éxitos y fallos."""
    ok = 0
    fail = 0
    for t in tokens:
        try:
            if send_push_notification(t, title, body, data):
                ok += 1
            else:
                fail += 1
        except Exception:
            fail += 1
    return {"ok": ok, "fail": fail}
