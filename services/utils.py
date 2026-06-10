# Es para avisar al servidor que la identificacion del usuario (token),
# se encuentra en el Bearer de la solicitud.
import os
from fastapi.security import OAuth2PasswordBearer
from datetime import timezone, timedelta

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"                 # Algoritmo de JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 480    # Tiempo de expiracion de JWT (30 minutos por defecto. Podemos cambiarlo). Cambiado a 8 horas (480 minutos). Modificar para agregar un refresh token si se quiere otro comportamiento.
TIMEZONE = timezone(timedelta(hours=-3))            # Timezone global del proyecto (Buenos Aires, Argentina)

# Los enlaces con este scheme deben autenticar al usuario.
# En el caso de /docs, se puede acceder haciendo clic en el candado e ingresando los datos.
# El tokenUrl tiene de valor "token" que es el servidor {pagina.com}/token, que es el enlace donde
# el usuario registrado obtiene su token de usuario. 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")