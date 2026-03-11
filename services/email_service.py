from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_user_credentials(email: str, username: str, password: str):

    message = MessageSchema(
        subject="Credenciales de acceso - Sistema DAR (Dispositivo de Accion Rapida)",
        recipients=[email],
        body=f"""
Sistema DAR
Dispositivo de Acción Rápida

Se creo su cuenta de acceso al sistema.

Este sistema fue diseñado para asistir al personal en situaciones de emergencia
y contribuir a su seguridad durante el desempeño de sus funciones.

Antes de utilizar la aplicación verifique lo siguiente:

• Contar con conexión a internet
• Tener activada la ubicación (GPS)
• No tener el teléfono en modo silencioso
• Mantener la aplicación activa (No cerrar sesion)

Credenciales de acceso:

Usuario (Legajo): {username}
Contraseña: {password}

Gracias por utilizar el Sistema DAR.
Ministerio de Seguridad de la Provincia de Jujuy
""",
        subtype="plain",
    )

    fm = FastMail(conf)
    await fm.send_message(message)