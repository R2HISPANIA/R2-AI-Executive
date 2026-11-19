

from datetime import datetime, timezone

from app.creative.memory import obtener_conexion

def inicializar_sesiones():

    """Crea la tabla de sesiones administrativas."""

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS admin_sessions (

                    session_id VARCHAR(100) PRIMARY KEY,

                    username VARCHAR(150) NOT NULL,

                    created_at TIMESTAMPTZ NOT NULL,

                    expires_at TIMESTAMPTZ NOT NULL,

                    revoked_at TIMESTAMPTZ

                );

            """)

            cursor.execute("""

                CREATE INDEX IF NOT EXISTS

                idx_admin_sessions_username

                ON admin_sessions (username);

            """)

        conexion.commit()

    finally:

        conexion.close()

def registrar_sesion(

    session_id: str,

    username: str,

    created_at: datetime,

    expires_at: datetime,

):

    """Registra una nueva sesión administrativa."""

    if not session_id or not username:

        raise ValueError("Identificador y usuario son obligatorios.")

    if created_at.tzinfo is None or expires_at.tzinfo is None:

        raise ValueError("Las fechas deben incluir zona horaria.")

    if expires_at <= created_at:

        raise ValueError("La caducidad debe ser posterior a la creación.")

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute("""

                INSERT INTO admin_sessions (

                    session_id,

                    username,

                    created_at,

                    expires_at

                )

                VALUES (%s, %s, %s, %s)

                ON CONFLICT (session_id) DO NOTHING;

            """, (

                session_id,

                username,

                created_at,

                expires_at,

            ))

            registrada = cursor.rowcount == 1

        conexion.commit()

        return registrada

    finally:

        conexion.close()

def comprobar_sesion(

    session_id: str,

    username: str,

):

    """Comprueba que una sesión esté vigente y no revocada."""

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute("""

                SELECT session_id

                FROM admin_sessions

                WHERE session_id = %s

                  AND username = %s

                  AND revoked_at IS NULL

                  AND expires_at > NOW()

                LIMIT 1;

            """, (session_id, username))

            return cursor.fetchone() is not None

    finally:

        conexion.close()

def revocar_sesion(session_id: str, username: str):

    """Revoca una sesión administrativa."""

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute("""

                UPDATE admin_sessions

                SET revoked_at = NOW()

                WHERE session_id = %s

                  AND username = %s

                  AND revoked_at IS NULL

                RETURNING session_id;

            """, (session_id, username))

            revocada = cursor.fetchone() is not None

        conexion.commit()

        return revocada

    finally:

        conexion.close()

def listar_sesiones(username: str):

    """Consulta las sesiones de un administrador."""

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute("""

                SELECT

                    session_id,

                    username,

                    created_at,

                    expires_at,

                    revoked_at

                FROM admin_sessions

                WHERE username = %s

                ORDER BY created_at DESC;

            """, (username,))

            return cursor.fetchall()

    finally:

        conexion.close()
