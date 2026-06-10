from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from services.token import TokenServices, Token
from services.recaptcha import verify_recaptcha
from services.limiter import limiter

def InitLogInRoutes(app: FastAPI):
    from fastapi.security import OAuth2PasswordRequestForm
    from typing import Annotated

    @app.post("/token")
    @limiter.limit("5/minute")
    async def login_for_access_token(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        captcha_token: str = Form(...)
    ) -> Token:
        captcha_valid = verify_recaptcha(captcha_token)
        if not captcha_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Captcha Invalido. Por favor, intente nuevamente."
            )
        return TokenServices.login_for_access_token(form_data)