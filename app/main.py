

from datetime import datetime, timezone

from typing import Optional

from fastapi import FastAPI

from fastapi.responses import HTMLResponse

from pydantic import BaseModel, Field

app = FastAPI(

    title="R2-AI-Executive",

    description="Sistema de Dirección Ejecutiva del Grupo R2",

    version="0.1.0",

)

class Tarea(BaseModel):

    titulo: str = Field(..., min_length=1, max_length=200)

    descripcion: Optional[str] = None

    prioridad: str = "normal"

    estado: str = "pendiente"

@app.get("/", response_class=HTMLResponse)

def home():

    return """

    <!DOCTYPE html>

    <html lang="es">

    <head>

      <meta charset="utf-8">

      <meta name="viewport" content="width=device-width, initial-scale=1">

      <title>R2-AI-Executive</title>

    </head>

    <body style="font-family:Arial;background:#10131a;color:white;padding:35px">

      <h1 style="color:#d6b56d">R2-AI-Executive</h1>

      <h2>Sistema de Dirección Ejecutiva del Grupo R2</h2>

      <p>Centro de operaciones del Grupo R2.</p>

      <p>Estado: Servicio operativo.</p>

      <p><a href="/docs" style="color:#d6b56d">Documentación técnica</a></p>

      <p><a href="/health" style="color:#d6b56d">Estado del sistema</a></p>

    </body>

    </html>

    """

@app.get("/health")

def salud():

    return {

        "estado": "ok",

        "servicio": "R2-AI-Executive",

        "timestamp": datetime.now(timezone.utc).isoformat()

    }

@app.get("/api/estado")

def api_estado():

    return {

        "nombre": "R2-AI-Executive",

        "descripcion": "Sistema de Dirección Ejecutiva del Grupo R2",

        "version": app.version,

        "modulos": [

            "executive_dashboard",

            "proyectos",

            "tareas",

            "aprobaciones"

        ],

        "estado": "inicial"

    }

@app.post("/api/tareas")

def crear_tarea(tarea: Tarea):

    return {

        "mensaje": "Tarea recibida. El almacenamiento se incorporará posteriormente.",

        "tarea": tarea.model_dump()

    }
