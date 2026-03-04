# Conexion SSH
El servidor que nos dio el gobierno tiene un acceso curioso a este. Se accede mediante SSH.
No basta solo con los datos de la base de datos de siempre. Primero para hacer esto hay que reflejar el servidor del
sistema en el EC2 (o si quieren probar, en sus PCs tambien) en un puerto del mismo.
Para eso hacemos los siguiente:

## Pasos
1. Instalar OpenSSH
Normalmente viene instalado por defecto en Windows 11 pero si no, instalar.
2. Crear la conexion al EC2
La base de datos solo se puede acceder mediante el EC2. Para eso requiere la clave .pem (el que la quiera me la pide. Va a estar en el servidor del sistema para que pueda conectarse). Usar el comando en el cmd a continuacion:
`ssh -i {DIRECCION DEL ARCHIVO .pem} -L 5433:ls-12d7b609c2b3f5bc72b708b72e5db7a4547c7783.cjft96j28czt.us-east-1.rds.amazonaws.com:5432 ubuntu@34.229.78.137`
3. Entrar a la base de datos
Usar distintos clientes que tengan a disposicion. Pueden usar pgadmin4 por ejemplo. En el caso del servidor de DAR, recordar que los valores a cambiar SIEMPRE deben ser en su archivo .env generado. Los datos que deben ir ahi son los siguientes:
```DB_HOST=localhost
DB_USER=app_dar
DB_PASS=app_dar_2026_M1NS36
DB_PORT=5433
DB_NAME=app_dar
DB_ENGINE=postgresql+psycopg2

GOOGLE_APPLICATION_CREDENTIALS=push-notificaciones-758a9-firebase-adminsdk-fbsvc-388aaffc2e.json
```
Recordar que esto puede cambiar dependiendo de que base de datos usen ustedes. Estos son los datos del servidor DAR original.

Esta conexion funcionara mientras el cmd de la conexion este abierto. Al cerrarse la conexion se pierde.
