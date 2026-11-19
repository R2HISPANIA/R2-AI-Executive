

import os

import uuid

import psycopg2

from psycopg2.extras import RealDictCursor

def obtener_conexion():

    """Conecta con la base de datos PostgreSQL de R2."""

    database_url = os.getenv("DATABASE_URL")

    if not database_url:

        raise RuntimeError("DATABASE_URL no está configurada.")

    return psycopg2.connect(database_url)

def inicializar_memoria_creativa():

    """Crea la tabla propia de memoria de R2 Creative Studio."""

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute("""

                CREATE TABLE IF NOT EXISTS creative_memories (

                    id UUID PRIMARY KEY,

                    categoria VARCHAR(100) NOT NULL,

                    contenido TEXT NOT NULL,

                    proyecto_id VARCHAR(100),

                    fuente VARCHAR(150),

                    fecha_creacion TIMESTAMPTZ DEFAULT NOW()

                );

            """)

        conexion.commit()

    finally:

        conexion.close()

def guardar_memoria(

    categoria: str,

    contenido: str,

    proyecto_id: str = None,

    fuente: str = "R2 Creative Studio",

):

    """Guarda un recuerdo permanente del estudio."""

    if not categoria or not categoria.strip():

        raise ValueError("La categoría es obligatoria.")

    if not contenido or not contenido.strip():

        raise ValueError("El contenido es obligatorio.")

    memoria_id = str(uuid.uuid4())

    conexion = obtener_conexion()

    try:

        with conexion.cursor() as cursor:

            cursor.execute("""

                INSERT INTO creative_memories (

                    id,

                    categoria,

                    contenido,

                    proyecto_id,

                    fuente

                )

                VALUES (%s, %s, %s, %s, %s);

            """, (

                memoria_id,

                categoria.strip(),

                contenido.strip(),

                proyecto_id,

                fuente,

            ))

        conexion.commit()

        return {

            "id": memoria_id,

            "categoria": categoria,

            "estado": "guardada",

        }

    finally:

        conexion.close()

def recuperar_memorias(

    categoria: str = None,

    limite: int = 50,

):

    """Recupera recuerdos de la memoria histórica."""

    limite = max(1, min(limite, 200))

    conexion = obtener_conexion()

    try:

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:

            if categoria:

                cursor.execute("""

                    SELECT *

                    FROM creative_memories

                    WHERE categoria = %s

                    ORDER BY fecha_creacion DESC

                    LIMIT %s;

                """, (categoria, limite))

            else:

                cursor.execute("""

                    SELECT *

                    FROM creative_memories

                    ORDER BY fecha_creacion DESC

                    LIMIT %s;

                """, (limite,))

            return cursor.fetchall()

    finally:

        conexion.close()
