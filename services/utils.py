# Es para avisar al servidor que la identificacion del usuario (token),
# se encuentra en el Bearer de la solicitud.
from fastapi.security import OAuth2PasswordBearer
from datetime import timezone, timedelta

# Para obtener un string como este ejecuten:
# openssl rand -hex 32
# Nota: De momento no lo cambien. Este vamos a usar por ahora
SECRET_KEY = "abb0e08bfdac01fcef3d5ecda2874fb54c8a7905099e901ef3f09d005cddb474"         # Llave secreta para JWT. Esto deberia ir en el .env o algun lugar seguro.
ALGORITHM = "HS256"                 # Algoritmo de JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 480    # Tiempo de expiracion de JWT (30 minutos por defecto. Podemos cambiarlo). Cambiado a 8 horas (480 minutos). Modificar para agregar un refresh token si se quiere otro comportamiento.
TIMEZONE = timezone(timedelta(hours=-3))            # Timezone global del proyecto (Buenos Aires, Argentina)

# Los enlaces con este scheme deben autenticar al usuario.
# En el caso de /docs, se puede acceder haciendo clic en el candado e ingresando los datos.
# El tokenUrl tiene de valor "token" que es el servidor {pagina.com}/token, que es el enlace donde
# el usuario registrado obtiene su token de usuario. 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")