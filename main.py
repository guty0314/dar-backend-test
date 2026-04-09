from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from api.user import InitUserRoutes
from api.login import InitLogInRoutes
from api.emergency import InitEmergencyRoutes
from api.emergency_extra import InitEmergencyExtraRoutes

# Esto se ejecuta cuando el servidor inicia.
# Solo carga los datos de los usuarios al sistema
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

# Servidor
"""app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
    )"""
app = FastAPI(lifespan=lifespan)

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

# --- Inicialización ---
def init_db():
    """Inicializa la base de datos."""
    from sqlmodel import SQLModel, Session
    from db.session import engine

    # IMPORTAR TODOS LOS MODELOS
    from models.user import User
    from models.emergency import Emergency
    from models.emergency_type import EmergencyType
    from models.emergency_category import EmergencyCategory
    from models.emergency_response import EmergencyResponse
    
    print("📊 Creando tablas en MariaDB...")
    SQLModel.metadata.create_all(engine)
    print("✅ Tablas creadas exitosamente")
    
    print("👥 Verificando usuarios iniciales...")
    with Session(engine) as session:
        existing_users = session.query(User).count()
        
        if existing_users == 0:
            print("📝 Insertando usuarios iniciales...")
            usuarios_iniciales = [

                User(
                    id_user=1, 
                    username="villarrubia", 
                    full_name="Villarrubia Gustavo", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True,
                    cuil="12345678"
                    ),
                User(
                    id_user=2, 
                    username="valle", 
                    full_name="Valle Diego", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True,
                    cuil="12345678"
                    ),
                User(
                    id_user=3, 
                    username="lamas", 
                    full_name="Lamas Maximiliano", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True,
                    cuil="12345678"
                    ),
                User(
                    id_user=4, 
                    username="manzano", 
                    full_name="Manzano Cesar", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True,
                    cuil="12345678"
                    ),

            ]
            session.add_all(usuarios_iniciales)
            session.commit()
            print(f"✅ {len(usuarios_iniciales)} usuarios insertados exitosamente")
        else:
            print(f"⚠️  Base de datos ya contiene {existing_users} usuarios. Saltando inserción.")

# === Enlaces ===
# Para estar mas comodos, propongo poner todos los enlaces en
# estas funciones generales para poder separarlas mejor.
InitLogInRoutes(app)
InitUserRoutes(app)
InitEmergencyExtraRoutes(app)
InitEmergencyRoutes(app)
