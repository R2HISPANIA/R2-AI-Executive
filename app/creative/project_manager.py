

from datetime import datetime, timezone

from uuid import uuid4

ESTADOS_PROYECTO = [

    "propuesto",

    "planificacion",

    "en_desarrollo",

    "en_revision",

    "finalizado",

    "suspendido",

]

def crear_proyecto(

    nombre: str,

    descripcion: str,

    categoria: str = "general",

    responsable: str = "Creative Director",

):

    """Crea un nuevo proyecto de R2 Creative Studio."""

    if not nombre or not nombre.strip():

        raise ValueError("El proyecto debe tener un nombre.")

    if not descripcion or not descripcion.strip():

        raise ValueError("El proyecto debe tener una descripción.")

    return {

        "id": str(uuid4()),

        "nombre": nombre.strip(),

        "descripcion": descripcion.strip(),

        "categoria": categoria.strip().lower(),

        "responsable": responsable.strip(),

        "estado": "propuesto",

        "tareas": [],

        "fecha_creacion": datetime.now(timezone.utc).isoformat(),

    }

def cambiar_estado_proyecto(proyecto: dict, nuevo_estado: str):

    """Actualiza el estado de un proyecto."""

    if nuevo_estado not in ESTADOS_PROYECTO:

        raise ValueError("Estado de proyecto no válido.")

    proyecto["estado"] = nuevo_estado

    proyecto["fecha_actualizacion"] = datetime.now(

        timezone.utc

    ).isoformat()

    return proyecto

def agregar_tarea(

    proyecto: dict,

    titulo: str,

    descripcion: str = "",

    responsable: str = "Creative Director",

):

    """Añade una tarea al proyecto."""

    if not titulo or not titulo.strip():

        raise ValueError("La tarea debe tener un título.")

    tarea = {

        "id": str(uuid4()),

        "titulo": titulo.strip(),

        "descripcion": descripcion.strip(),

        "responsable": responsable.strip(),

        "estado": "pendiente",

        "fecha_creacion": datetime.now(timezone.utc).isoformat(),

    }

    proyecto.setdefault("tareas", []).append(tarea)

    return tarea
