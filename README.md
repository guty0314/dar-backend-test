# Como instalar
Ejecutar el bat ```crear_venv.bat``` y dejar instalar las librerias. Los que sepan de entornos virtuales en Python pueden instalar desde ```requirements.txt```, sino usar este bat.
Uso la version de Python 3.13. 

# Ejecutar
Ejecutar el bat ```ejecutar_servidor.bat``` para correr el servidor. Se ejecuta en http://127.0.0.1:8000 (entrar por el navegador)

# Que es cada carpeta
## api
Guarda los endpoints exclusivamente.
## models
Guarda las definiciones de las tablas de la BD.
## repositories
Guarda las clases que acceden a la DB para recuperar filas, crearlas y eliminarlas (si se da el caso).
## services
Guarda la logica de negocio.

# Jugar con la API
Entrar a http://127.0.0.1:8000/docs para acceder a la documentacion autogenerada por FastAPI. Esta se genera siguiendo las reglas que puse en ```main.py```

# Dedicado a Frontend
Los usuarios al menos aqui se manejan usando JWT (JSON web tokens), que es en resumen un cifrado de un texto (normalmente el username), al que se le adjunta un tiempo de duracion.
Como resultado se entrega una cadena de texto larga y venosa (?) que sirve para que el servidor reconozca al usuario en cuestion.
No es necesario que entiendan como funciona esto internamente, pero si externamente. En el frontend deben, ademas de almacenar el nombre del usuario y su informacion, este token.
Cuando hagan solicitudes a la API en enlaces donde pide autenticacion, deben adjuntar en el BEARER este token (solo el token, no el nombre de usuario).
Las transacciones con la API son SIEMPRE en formato JSON. Su trabajo es procesar el JSON recibido para mostrarlo en la app, ademas de preparar los JSON a enviar al servidor
si es necesario.

Ya saben, el JSON se ve asi:
```
{
  "msg" : "Nerf this!",
  "code" : 64
}
```
Si tienen dudas con el funcionamiento de JSON, consulten en internet.

# En caso de agregar mas liberias...
Agregar la liberia a instalar en ```requirements.txt``` para instalarlo cuando haya que actualizar.

# Reglitas para programar xd
* Las variables y nombres de funciones en ingles. Me paso que mezcle ingles y español y es bastante feo como queda despues el codigo, peor si hay que documentar.
* Las funciones deben tener la estructura ```esto_es_esparta```.
* De momento con las variables no vamos a usar nomenclaturas, pero procuren hacer que su nombre sea descriptivo de lo que almacena.


**CREDENCIALES FIREBASE**: cómo configurar `GOOGLE_APPLICATION_CREDENTIALS`

- **Descripción**: El proyecto usa Firebase Admin para enviar notificaciones push. El SDK necesita la ruta al JSON de la cuenta de servicio en la variable de entorno `GOOGLE_APPLICATION_CREDENTIALS`.

- **Archivo en este repo**: `push-notificaciones-758a9-firebase-adminsdk-fbsvc-388aaffc2e.json`

- **Opciones para configurar**:
  - **Sesión actual (PowerShell, temporal)**: válida hasta cerrar la ventana de terminal:
    ```powershell
    $env:GOOGLE_APPLICATION_CREDENTIALS = 'C:\Users\Gustavo\Desktop\DAR-Servidor-main\push-notificaciones-758a9-firebase-adminsdk-fbsvc-388aaffc2e.json'
    ```
  - **Persistente para el usuario (nuevas terminales)**:
    ```powershell
    setx GOOGLE_APPLICATION_CREDENTIALS "C:\Users\Gustavo\Desktop\DAR-Servidor-main\push-notificaciones-758a9-firebase-adminsdk-fbsvc-388aaffc2e.json"
    ```
    (abrir nueva terminal para ver el efecto)
  - **Persistente para todo el sistema (requiere Administrador)**:
    ```powershell
    setx GOOGLE_APPLICATION_CREDENTIALS "C:\Users\Gustavo\Desktop\DAR-Servidor-main\push-notificaciones-758a9-firebase-adminsdk-fbsvc-388aaffc2e.json" /M
    ```

- **Nota sobre `ejecutar_servidor.bat`**: `ejecutar_servidor.bat` ahora define la variable localmente al inicio, de modo que si arrancas el servidor con ese script la variable estará disponible para el proceso (no modifica variables del sistema ni del usuario fuera de ese proceso).
