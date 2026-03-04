# Configuración de MariaDB para DAR Servidor

## Requisitos previos

1. **Instalar MariaDB** (si no lo tienes)
   - Descargar desde: https://mariadb.org/download/
   - Versión recomendada: 10.5 o superior

2. **Instalar dependencias Python**
   ```powershell
   pip install -r requirements.txt
   ```

## Pasos de configuración

### 1. Instalar y ejecutar MariaDB

**En Windows:**
```powershell
# Si usas MariaDB Portable
mariadb.exe -uroot -proot

# O si está instalado como servicio
net start MariaDB
```

### 2. Crear la base de datos

**Opción A: Usando MariaDB CLI**
```sql
CREATE DATABASE IF NOT EXISTS dar_db;
USE dar_db;
```

**Opción B: Automaticamente** (el servidor lo hace en el inicio)

### 3. Inicializar la base de datos con usuarios

```powershell
python scripts/init_mariadb.py
```

Este script:
-  Crea las tablas `User` y `Emergency`
-  Inserta 3 usuarios de prueba (nieto, villarrubia, valle)
-  Verifica que no haya duplicados

### 4. Iniciar el servidor

```powershell
python main.py
```

## Credenciales por defecto

- **Usuario MariaDB:** root
- **Contraseña:** root
- **Base de datos:** dar_db
- **Host:** localhost:3306

## Cambiar credenciales

Si usas diferentes credenciales en MariaDB, edita `db/session.py`:

```python
DATABASE_URL = "mysql+pymysql://usuario:contraseña@localhost:3306/nombre_db"
```

## Verificar la conexión

```powershell
python -c "from db.session import engine; engine.connect(); print('✅ Conexión exitosa')"
```

## Tablas creadas

### User
- id_user (PK)
- username
- full_name
- disabled
- hashed_password
- latitude
- longitude
- device_token
- online

### Emergency
- id_emergency (PK)
- latitude
- longitude
- type_emergency (rojo, amarillo, verde)
- active
- date_created
- id_first_responder

## Troubleshooting

**Error: "Access denied for user 'root'@'localhost'"**
- Verifica que MariaDB esté corriendo
- Verifica las credenciales en `db/session.py`

**Error: "Unknown database 'dar_db'"**
- Ejecuta el comando SQL: `CREATE DATABASE dar_db;`
- O deja que el servidor lo cree automáticamente

**Error: "No module named 'pymysql'"**
- Instala las dependencias: `pip install -r requirements.txt`
