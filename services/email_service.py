from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
import os

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True
)

async def send_user_credentials(email: str, username: str, password: str):

    message = MessageSchema(
        subject="Credenciales de acceso - Sistema DAR (Dispositivo de Accion Rapida)",
        recipients=[email],
        body=f"""
        <!DOCTYPE html>
        <html>
        <body style="margin: 0; padding: 0; background-color: #f0f0f0; font-family: Arial, sans-serif;">

            <div style="max-width: 500px; margin: 30px auto; background-color: #1a1a2e; border-radius: 8px; overflow: hidden;">

                <!-- Header -->
                <div style="background-color: #16213e; padding: 24px 32px; text-align: center; border-bottom: 2px solid #e94560;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 22px; letter-spacing: 2px;">SISTEMA DAR</h1>
                    <p style="color: #a0a0b0; margin: 6px 0 0 0; font-size: 13px; letter-spacing: 1px;">DISPOSITIVO DE ACCIÓN RÁPIDA</p>
                </div>

                <!-- Body -->
                <div style="padding: 32px;">
                    <p style="color: #c0c0d0; font-size: 14px; line-height: 1.7; margin-top: 0;">
                        Se creó su cuenta de acceso al sistema. Este sistema fue diseñado para asistir 
                        al personal en situaciones de emergencia y contribuir a su seguridad durante 
                        el desempeño de sus funciones.
                    </p>

                    <p style="color: #a0a0b0; font-size: 13px; margin-bottom: 8px;">Antes de utilizar la aplicación verifique lo siguiente:</p>
                    <ul style="color: #c0c0d0; font-size: 13px; line-height: 2; padding-left: 20px;">
                        <li>Contar con conexión a internet</li>
                        <li>Tener activada la ubicación (GPS)</li>
                        <li>No tener el teléfono en modo silencioso</li>
                        <li>Mantener la aplicación activa (No cerrar sesión)</li>
                    </ul>

                    <!-- Credenciales -->
                    <div style="background-color: #0f3460; border-left: 4px solid #e94560; border-radius: 4px; padding: 20px; margin-top: 24px;">
                        <p style="color: #e94560; font-size: 13px; font-weight: bold; margin: 0 0 16px 0; letter-spacing: 1px;">CREDENCIALES DE ACCESO</p>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="color: #a0a0b0; font-size: 13px; padding: 8px 0; width: 140px;">Usuario (Legajo)</td>
                                <td style="color: #ffffff; font-size: 15px; font-weight: bold; padding: 8px 0;">{username}</td>
                            </tr>
                            <tr style="border-top: 1px solid #1a3a6e;">
                                <td style="color: #a0a0b0; font-size: 13px; padding: 8px 0;">Contraseña</td>
                                <td style="color: #ffffff; font-size: 15px; font-weight: bold; padding: 8px 0;">{password}</td>
                            </tr>
                        </table>
                    </div>
                </div>

                <!-- Footer -->
                <div style="background-color: #16213e; padding: 16px 32px; text-align: center; border-top: 1px solid #2a2a4a;">
                    <p style="color: #606070; font-size: 12px; margin: 0;">Ministerio de Seguridad de la Provincia de Jujuy</p>
                </div>

            </div>

        </body>
        </html>
        """,
        subtype=MessageType.html,
    )  

    fm = FastMail(conf)
    await fm.send_message(message)