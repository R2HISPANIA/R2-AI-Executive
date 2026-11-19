

from datetime import datetime, timezone

from uuid import uuid4

from psycopg2.extras import RealDictCursor

from app.creative.memory import obtener_conexion

def inicializar_autorizaciones():

    """Crea la tabla permanente de solicitudes."""

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS creative_authorizations (

                    id UUID PRIMARY KEY,

                    accion VARCHAR(100) NOT NULL,

                    descripcion TEXT NOT NULL,

                    presupuesto_solicitado NUMERIC(14, 2) NOT NULL DEFAULT 0,

                    estado VARCHAR(40) NOT NULL DEFAULT 'pendiente',

                    solicitante VARCHAR(150) NOT NULL,

                    autorizado_por VARCHAR(150),

                    fecha_solicitud TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                    fecha_autorizacion TIMESTAMPTZ,

                    fecha_caducidad TIMESTAMPTZ,

                    presupuesto_aprobado NUMERIC(14, 2)

                );

            """)

        conexion.commit()

    finally:

        conexion.close()

def crear_solicitud(

    accion: str,

    descripcion: str,

    solicitante: str,

    presupuesto: float = 0,

):

    """Registra una solicitud pendiente de autorización."""

    if not accion or not accion.strip():

        raise ValueError("La acción es obligatoria.")

    if not descripcion or not descripcion.strip():

        raise ValueError("La descripción es obligatoria.")

    if not solicitante or not solicitante.strip():

        raise ValueError("El solicitante es obligatorio.")

    if presupuesto < 0:

        raise ValueError("El presupuesto no puede ser negativo.")

    solicitud_id = str(uuid4())

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("""

                INSERT INTO creative_authorizations (

                    id,

                    accion,

                    descripcion,

                    presupuesto_solicitado,

                    solicitante

                )

                VALUES (%s, %s, %s, %s, %s)

                RETURNING *;

            """, (

                solicitud_id,

                accion.strip().lower(),

                descripcion.strip(),

                presupuesto,

                solicitante.strip(),

            ))

            solicitud = cursor.fetchone()

        conexion.commit()

        return dict(solicitud)

    finally:

        conexion.close()

def consultar_solicitud(solicitud_id: str):

    """Consulta una solicitud por su identificador."""

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("""

                SELECT *

                FROM creative_authorizations

                WHERE id = %s;

            """, (solicitud_id,))

            solicitud = cursor.fetchone()

            return dict(solicitud) if solicitud else None

    finally:

        conexion.close()

def listar_solicitudes(limite: int = 50):

    """Lista las solicitudes más recientes."""

    limite = max(1, min(limite, 200))

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute("""

                SELECT *

                FROM creative_authorizations

                ORDER BY fecha_solicitud DESC

                LIMIT %s;

            """, (limite,))

            return [dict(item) for item in cursor.fetchall()]

    finally:

        conexion.close()
