ni from datetime import datetime, timezone

from typing import Optional

from fastapi import FastAPI

from fastapi.responses import HTMLResponse

from pydantic import BaseModel, Field

app = FastAPI(

    title="R2-AI-Executive",

    description="Sistema de Dirección Ejecutiva del Grupo R2",

    version="0.1.0",

)

class Task(BaseModel):

    title: str = Field(..., min_length=1, max_length=200)

    description: Optional[str] = None

    priority: str = "normal"

    status: str = "pending"

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

def health():

    return {

        "status": "ok",

        "service": "R2-AI-Executive",

        "timestamp": datetime.now(timezone.utc).isoformat()

    }

@app.get("/api/status")

def api_status():

    return {

        "name": "R2-AI-Executive",

        "description": "Sistema de Dirección Ejecutiva del Grupo R2",

        "version": app.version,

        "modules": [

            "executive_dashboard",

            "projects",

            "tasks",

            "approvals"

        ],

        "status": "initial"

    }

@app.post("/api/tasks")

def create_task(task: Task):

    return {

        "message": "Tarea recibida. El almacenamiento se incorporará posteriormente.",

        "task": task.model_dump()

    }
