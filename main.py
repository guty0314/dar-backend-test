from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from api.user import InitUserRoutes
from api.login import InitLogInRoutes
from api.emergency import InitEmergencyRoutes

# Esto se ejecuta cuando el servidor inicia.
# Solo carga los datos de los usuarios al sistema
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

# Servidor
app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
    )

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Pagina Inexistente</title>
        </head>
        <body style="font-family: Arial; text-align:center; margin-top:50px;">
            <h1>API DAR</h1>
            <p>Pagina Inexistente</p>
        </body>
    </html>       
    """

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request,exc: StarletteHTTPException):
    if exc.status_code == 404:
        return HTMLResponse(
            """
            <html>
                <head>
                    <title>Página no encontrada</title>
                </head>
                <body style="font-family: Arial; text-align:center; margin-top:80px;">
                    <h1>Error 404</h1>
                    <h2>Página no encontrada</h2>
                    <p>El recurso solicitado no existe.</p>
                    <p>Pagina Inexistente</p>
                </body>
            </html>
            """,
            status_code=404
        )
    return HTMLResponse(f"<h1>Error {exc.status_code}</h1>", status_code=exc.status_code)
# --- Inicialización ---
def init_db():
    """Inicializa la base de datos MariaDB."""
    from sqlmodel import SQLModel, Session
    from db.session import engine
    from models.user import User
    
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
                    username="nieto", 
                    full_name="Nieto Leandro", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6038,
                    longitude=-58.3816,
                    online=True
                    ),
                User(
                    id_user=2, 
                    username="villarrubia", 
                    full_name="Villarrubia Gustavo", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True
                    ),
                User(
                    id_user=3, 
                    username="valle", 
                    full_name="Valle Diego", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True
                    ),
                User(
                    id_user=4, 
                    username="lamas", 
                    full_name="Lamas Maximiliano", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True
                    ),
                User(
                    id_user=5, 
                    username="manzano", 
                    full_name="Manzano Cesar", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True
                    ),
                User(
                    id_user=6, 
                    username="chocala", 
                    full_name="Chocala Cristian", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True
                    ),
                User(
                    id_user=7, 
                    username="marcos", 
                    full_name="Marcos Andres", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True
                    ),
                User(
                    id_user=8, 
                    username="dummy", 
                    full_name="Usuario online", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    online=True
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
InitEmergencyRoutes(app)