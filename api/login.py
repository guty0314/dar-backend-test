from fastapi import Depends, FastAPI
from services.token import TokenServices, Token

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
    ) -> Token:
        return TokenServices.login_for_access_token(form_data)