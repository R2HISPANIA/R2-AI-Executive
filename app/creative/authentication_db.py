

from datetime import datetime

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

                    revoked_at TIMESTAMPTZ,

                    CHECK (expires_at > created_at)

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

    if not isinstance(session_id, str) or not session_id.strip():

        raise ValueError("Identificador de sesión no válido.")

    if not isinstance(username, str) or not username.strip():

        raise ValueError("Usuario no válido.")

    if not isinstance(created_at, datetime):

        raise ValueError("Fecha de creación no válida.")

    if not isinstance(expires_at, datetime):

        raise ValueError("Fecha de caducidad no válida.")

    if created_at.tzinfo is None or created_at.utcoffset() is None:

        raise ValueError("La fecha de creación debe incluir zona horaria.")

    if expires_at.tzinfo is None or expires_at.utcoffset() is None:

        raise ValueError("La fecha de caducidad debe incluir zona horaria.")

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

                session_id.strip(),

                username.strip(),

                created_at,

                expires_at,

            ))

            registrada = cursor.rowcount == 1

        conexion.commit()

        return registrada

    finally:

        conexion.close()

def comprobar_sesion(session_id: str, username: str):

    """Comprueba que una sesión esté vigente y no revocada."""

    if not isinstance(session_id, str) or not session_id.strip():

        return False

    if not isinstance(username, str) or not username.strip():

        return False

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute("""

                SELECT 1

                FROM admin_sessions

                WHERE session_id = %s

                  AND username = %s

                  AND revoked_at IS NULL

                  AND expires_at > NOW()

                LIMIT 1;

            """, (session_id.strip(), username.strip()))

            return cursor.fetchone() is not None

    finally:

        conexion.close()

def revocar_sesion(session_id: str, username: str):

    """Revoca una sesión administrativa."""

    if not isinstance(session_id, str) or not session_id.strip():

        return False

    if not isinstance(username, str) or not username.strip():

        return False

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute("""

                UPDATE admin_sessions

                SET revoked_at = NOW()

                WHERE session_id = %s

                  AND username = %s

                  AND revoked_at IS NULL

                  AND expires_at > NOW()

                RETURNING session_id;

            """, (session_id.strip(), username.strip()))

            revocada = cursor.fetchone() is not None

        conexion.commit()

        return revocada

    finally:

        conexion.close()

def listar_sesiones(username: str, limite: int = 50):

    """Consulta un número limitado de sesiones de un administrador."""

    if not isinstance(username, str) or not username.strip():

        raise ValueError("Usuario no válido.")

    if not isinstance(limite, int) or isinstance(limite, bool):

        raise ValueError("El límite debe ser un número entero.")

    limite = max(1, min(limite, 200))

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

                ORDER BY created_at DESC

                LIMIT %s;

            """, (username.strip(), limite))

            return cursor.fetchall()

    finally:

        conexion.close()
