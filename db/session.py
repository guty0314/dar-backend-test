from sqlmodel import create_engine, Session
from dotenv import load_dotenv
import os

load_dotenv()

# Primer intentamos obtener la base de datos de prueba
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # BASE DE DATOS SERVIDOR DE PRUEBA (Render)
    print("🌍 Usando base de datos de PRODUCCIÓN (Render)")
    engine = create_engine(DATABASE_URL, echo=True)

else:
    # BASE DE DATOS CON SERVIDOR (AMAZON)
    print("💻 Usando base de datos SERVIDOR (Postgre)")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASS", "")
    DB_NAME = os.getenv("DB_NAME", "dar_db")
    DB_ENGINE = os.getenv("DB_ENGINE", "mysql+pymysql")

    DATABASE_URL = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session