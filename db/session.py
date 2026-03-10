from sqlmodel import create_engine, Session

# Base de datos MariaDB persistente
# Asegúrate de que MariaDB esté instalado y corriendo
# Usuario: root, Contraseña: ABC123, Base de datos: dar_db
from dotenv import load_dotenv
import os
load_dotenv()  # Cargar variables de entorno desde .env si existe
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "dar_db")
DB_ENGINE = os.getenv("DB_ENGINE", "mysql+pymysql")

# AVISO: Crear un archivo .env en el directorio raíz del proyecto para definir las variables de entorno.
# Ahi poner las credenciales reales y no subirlas a un repositorio público.
DATABASE_URL = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

