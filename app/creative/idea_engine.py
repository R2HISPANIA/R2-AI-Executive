

from datetime import datetime, timezone

from uuid import uuid4

def crear_idea(titulo: str, descripcion: str, categoria: str = "general"):

    """

    Registra una nueva idea para R2 Creative Studio.

    """

    if not titulo or not titulo.strip():

        raise ValueError("La idea debe tener un título.")

    if not descripcion or not descripcion.strip():

        raise ValueError("La idea debe tener una descripción.")

    return {

        "id": str(uuid4()),

        "titulo": titulo.strip(),

        "descripcion": descripcion.strip(),

        "categoria": categoria.strip().lower(),

        "estado": "exploracion",

        "fecha_creacion": datetime.now(timezone.utc).isoformat(),

    }

def evaluar_idea(idea: dict, evaluacion: str, observaciones: str = ""):

    """

    Añade una evaluación inicial a una idea.

    """

    estados_validos = [

        "exploracion",

        "en_evaluacion",

        "aprobada",

        "descartada",

        "en_desarrollo",

    ]

    if evaluacion not in estados_validos:

        raise ValueError("Estado de evaluación no válido.")

    idea["estado"] = evaluacion

    idea["evaluacion"] = observaciones

    idea["fecha_evaluacion"] = datetime.now(timezone.utc).isoformat()

    return idea
