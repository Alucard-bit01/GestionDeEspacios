# Sistema de Gestión de Espacios y Comunicación

Una aplicación web completa desarrollada en Flask para la gestión de reservas de espacios, facilitando también la comunicación en tiempo real entre los usuarios.

## Características Principales

- **Gestión de Reservas**: Visualiza la disponibilidad de aulas en tiempo real, realiza nuevas reservas y cancela las existentes fácilmente.
- **Chat en Tiempo Real**: Comunicación instantánea entre usuarios mediante WebSockets (SocketIO). Incluye historial de mensajes y notificaciones de mensajes no leídos.
- **Videollamadas**: Intefaz para realizar videollamadas entre usuarios.
- **Autenticación de Usuarios**: Sistema seguro de registro e inicio de sesión.
- **Panel de Control Personalizado**: Dashboard de usuario y configuración de perfil (cambio de avatar, contraseña y nombre de usuario).

## Tecnologías Utilizadas

- **Backend**: Python, Flask
- **Base de Datos**: SQL Server (MSSQL) via SQLAlchemy
- **Tiempo Real**: Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap implícito en estructura común, o estilos personalizados)

## Requisitos Previos

- Python 3.8 o superior
- SQL Server (y controlador ODBC 17)

## Instalación

1.  **Clonar el repositorio**

    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd proyecto_Int
    ```

2.  **Crear y activar un entorno virtual**

    ```bash
    python -m venv venv
    # En Windows:
    .\venv\Scripts\activate
    # En macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instalar dependencias**

    ```bash
    pip install -r requirements.txt
    ```

    _Nota: Asegúrate de tener también instalados `flask-socketio` y `pyodbc` si no están en el archivo requirements._

    ```bash
    pip install flask-socketio pyodbc
    ```

4.  **Configuración de la Base de Datos**

    El proyecto está configurado para conectar a una base de datos SQL Server local. Verifica la cadena de conexión en `app.py`:

    ```python
    app.config['SQLALCHEMY_DATABASE_URI'] = r'mssql+pyodbc://@ALEXIS\SQLEXPRESS/Integradora?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    ```

    Asegúrate de que tu instancia de SQL Server esté corriendo y que la base de datos `Integradora` exista (o deja que SQLAlchemy cree las tablas).

5.  **Ejecutar la aplicación**

    ```bash
    python app.py
    ```

    La aplicación estará disponible en `http://127.0.0.1:5000`.

## Uso

1.  Regístrate con un nuevo usuario.
2.  Inicia sesión para acceder al Dashboard.
3.  Navega a **Reservas** para ver y gestionar espacios.
4.  Usa la sección de **Chat** para enviar mensajes a otros usuarios registrados.

## Estructura del Proyecto

- `app.py`: Punto de entrada de la aplicación y configuración.
- `model/`: Definición de modelos de base de datos (User, Classroom, Reservation, Message).
- `templates/`: Plantillas HTML para las vistas.
- `static/`: Archivos estáticos (CSS, JS, imágenes de perfil).
