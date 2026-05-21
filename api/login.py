from fastapi import Depends, FastAPI, Form, HTTPException, status
from services.token import TokenServices, Token
from services.recaptcha import verify_recaptcha

def InitLogInRoutes(app: FastAPI):
    # Es para recolectar la informacion de "username" y "password".
    from fastapi.security import OAuth2PasswordRequestForm
    # Se usa para que FastAPI pueda mostrar en /docs los parametros que pide un enlace
    # (para ser mas claros y facilitar pruebas y uso de la API por parte de los de frontend)
    from typing import Annotated

    # Devuelve un JSON con la estructura de Token, solo si el usuario ingreado es correcto.
    @app.post("/token")
    async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        captcha_token: str = Form(...)
    ) -> Token:
        # Verificar el token de reCAPTCHA
        captcha_valid = verify_recaptcha(captcha_token)
        if not captcha_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Captcha Invalido. Por favor, intente nuevamente."
            )
        #Continuar con el proceso de login si el captcha es válido
        return TokenServices.login_for_access_token(form_data)