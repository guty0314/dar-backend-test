from sqlmodel import Session, select

from db.session import engine
from models.user import User

class UserRepository:
    """
    Clase que accede a la base de datos para trabajar informacion respecto a los usuarios
    """
    @staticmethod
    def get_user_by_id(id_user: int) -> User | None:
        with Session(engine) as session:
            return session.get(User, id_user)

    @staticmethod 
    def get_user_by_username(username: str) -> User | None:
        with Session(engine) as session:
            return session.exec(select(User).where(User.username==username)).first()

    @staticmethod
    def get_all_users() -> list[User]:
        with Session(engine) as session:
            return session.exec(select(User)).all()
        
    @staticmethod
    def create_user(user: User) -> User:
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        
    @staticmethod
    def update_user(user: User) -> User:
        """
        Actualiza la informacion del usuario en la base de datos.

        :param user: Usuario a actualizar.
        :type user: User
        :return: Usuario actualizado.
        :rtype: User
        """
        with Session(engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    @staticmethod
    def update_user_role(username: str, new_role: str):
        """
        Cambia el rol de un usuario (admin / agent)
        """
        if new_role not in ["admin", "agent"]:
            return {"error": "Invalid role"}

        with Session(engine) as session:
            user = session.exec(
                select(User).where(User.username == username)
            ).first()

            if not user:
                return {"error": "User not found"}

            user.role = new_role
            session.add(user)
            session.commit()
            session.refresh(user)

            return {"msg": f"Role updated to {new_role}"}
        
    @staticmethod
    def disable_user(username: str):
        """
        Desactiva un usuario
        """
        with Session(engine) as session:
            user = session.exec(
                select(User).where(User.username == username)
            ).first()

            if not user:
                return {"error": "User not found"}

            user.disabled = True
            session.add(user)
            session.commit()
            session.refresh(user)

            return {"msg": "User disabled successfully"}

    @staticmethod
    def enable_user(username: str):
        with Session(engine) as session:
            user = session.exec(
                select(User).where(User.username == username)
            ).first()

            if not user:
                return {"error": "User not found"}

            user.disabled = False
            session.add(user)
            session.commit()
            session.refresh(user)

            return {"msg": "User enabled successfully"}

    @staticmethod
    def update_user_data(username: str, data):
        """
        Modifica datos generales de un usuario (admin only)
        """
        with Session(engine) as session:
            user = session.exec(
                select(User).where(User.username == username)
            ).first()

            if not user:
                return {"error": "User not found"}

            # Actualizar campos si vienen informados
            if data.full_name is not None:
                user.full_name = data.full_name

            if data.email is not None:
                user.email = data.email

            if data.number_phone is not None:
                user.number_phone = data.number_phone

            if data.role is not None:
                if data.role not in ["admin", "agent"]:
                    return {"error": "Invalid role"}
                user.role = data.role

            if data.disabled is not None:
                user.disabled = data.disabled

            session.add(user)
            session.commit()
            session.refresh(user)

            return {"msg": "User updated successfully"}