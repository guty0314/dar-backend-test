import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def _validate_env():
    faltantes = []

    if not os.getenv("SECRET_KEY"):
        faltantes.append("SECRET_KEY")

    if not os.getenv("DATABASE_URL"):
        faltantes.append("DATABASE_URL")

    skip_captcha = os.getenv("SKIP_CAPTCHA", "false").lower() == "true"
    if not skip_captcha:
        provider = os.getenv("CAPTCHA_PROVIDER", "recaptcha")
        if provider == "turnstile" and not os.getenv("TURNSTILE_SECRET_KEY"):
            faltantes.append("TURNSTILE_SECRET_KEY")
        elif provider == "recaptcha" and not os.getenv("RECAPTCHA_SECRET_KEY"):
            faltantes.append("RECAPTCHA_SECRET_KEY")

    if faltantes:
        logger.critical(f"Faltan variables de entorno requeridas: {', '.join(faltantes)}")
        raise RuntimeError(f"Variables de entorno faltantes: {', '.join(faltantes)}")

    for opcional in ["MAIL_USERNAME", "AWS_ACCESS_KEY_ID", "GOOGLE_APPLICATION_CREDENTIALS"]:
        if not os.getenv(opcional):
            logger.warning(f"Variable opcional no configurada: {opcional}")


_validate_env()


from api.user import InitUserRoutes
from api.login import InitLogInRoutes
from api.emergency import InitEmergencyRoutes
from api.emergency_extra import InitEmergencyExtraRoutes
from api.chat import InitChatRoutes
from api.account_request import InitAccountRequestRoutes
from api.app_config import InitAppConfigRoutes
from fastapi.middleware.cors import CORSMiddleware
from services.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_frontend_url = os.getenv("FRONTEND_URL")
_allowed_origins = ["http://localhost:5173", "http://localhost:3000"]
if _frontend_url:
    _allowed_origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>404</title></head>
        <body style="font-family: Arial; text-align:center; margin-top:50px;">
            <h1>Error 404</h1>
            <p>Página inexistente</p>
        </body>
    </html>       
    """


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return HTMLResponse(
        """
        <html>
            <head><title>404</title></head>
            <body style="font-family: Arial; text-align:center; margin-top:80px;">
                <h1>Error 404</h1>
                <p>Página inexistente</p>
            </body>
        </html>
        """,
        status_code=exc.status_code
    )


def init_db():
    from sqlmodel import SQLModel, Session
    from db.session import engine

    from models.user import User
    from models.emergency import Emergency
    from models.emergency_type import EmergencyType
    from models.emergency_category import EmergencyCategory
    from models.emergency_response import EmergencyResponse
    from models.activity_log import ActivityLog
    from models.chat_message import ChatMessage
    from models.account_request import AccountRequest
    from models.app_config import AppConfig

    logger.info("Creando tablas en la base de datos...")
    SQLModel.metadata.create_all(engine)
    logger.info("Tablas creadas exitosamente")

    logger.info("Verificando usuarios iniciales...")
    with Session(engine) as session:
        existing_users = session.query(User).count()

        if existing_users == 0:
            logger.info("Insertando usuarios iniciales...")
            usuarios_iniciales = [
                User(id_user=1, username="villarrubia", full_name="Villarrubia Gustavo", disabled=False,
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090, longitude=-58.3720, cuil="12345678"),
                User(id_user=2, username="valle", full_name="Valle Diego", disabled=False,
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090, longitude=-58.3720, cuil="12345678"),
                User(id_user=3, username="lamas", full_name="Lamas Maximiliano", disabled=False,
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090, longitude=-58.3720, cuil="12345678"),
                User(id_user=4, username="manzano", full_name="Manzano Cesar", disabled=False,
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090, longitude=-58.3720, cuil="12345678"),
            ]
            session.add_all(usuarios_iniciales)
            session.commit()
            logger.info(f"{len(usuarios_iniciales)} usuarios insertados exitosamente")
        else:
            logger.info(f"Base de datos ya contiene {existing_users} usuarios. Saltando inserción.")


# === Enlaces ===
InitLogInRoutes(app)
InitUserRoutes(app)
InitEmergencyExtraRoutes(app)
InitEmergencyRoutes(app)
InitChatRoutes(app)
InitAccountRequestRoutes(app)
InitAppConfigRoutes(app)