"""
Script para inicializar la base de datos MariaDB.
Crea las tablas necesarias e inserta los usuarios iniciales.
"""

import sys
sys.path.insert(0, '.')

from sqlmodel import SQLModel, Session
from db.session import engine
from models.user import User
from models.emergency import Emergency

def init_mariadb():
    """Crea todas las tablas e inserta datos iniciales."""
    
    print("📊 Creando tablas en MariaDB...")
    SQLModel.metadata.create_all(engine)
    print("✅ Tablas creadas exitosamente")
    
    print("\n👥 Insertando usuarios iniciales...")
    with Session(engine) as session:
        # Verificar si los usuarios ya existen
        existing_users = session.query(User).count()
        
        if existing_users == 0:
            usuarios_iniciales = [
                User(
                    id_user=1, 
                    username="nieto", 
                    full_name="Nieto Leandro", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6038,
                    longitude=-58.3816,
                    is_admin=True,
                ),
                User(
                    id_user=2, 
                    username="villarrubia", 
                    full_name="Villarrubia Gustavo", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6090,
                    longitude=-58.3720,
                    is_admin=True,
                ),
                User(
                    id_user=3, 
                    username="valle", 
                    full_name="Valle Diego", 
                    disabled=False, 
                    hashed_password="$argon2id$v=19$m=65536,t=3,p=4$Lu6pKMPN9Yw4y4BhxIJMZA$HG0f97fVWgSukmZyn93eVsmgLBzGr5hrXa9S283oEJs",
                    latitude=-34.6010,
                    longitude=-58.3780,
                    is_admin=True,
                ),
            ]
            
            for user in usuarios_iniciales:
                session.add(user)
            
            session.commit()
            print(f"✅ {len(usuarios_iniciales)} usuarios insertados exitosamente")
        else:
            print(f"⚠️  La base de datos ya contiene {existing_users} usuarios. Saltando inserción.")
    
    print("\n✨ Inicialización completada")

if __name__ == "__main__":
    init_mariadb()
