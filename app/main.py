

import os

from datetime import datetime, timezone

from typing import Optional, Literal

from fastapi import FastAPI, HTTPException

from fastapi.responses import HTMLResponse

from pydantic import BaseModel, Field

from google import genai

from google.genai import types

app = FastAPI(

    title="R2-AI-Executive",

    description="Sistema de Dirección Ejecutiva del Grupo R2",

    version="0.2.0",

)

INSTRUCCIONES_R2 = """

Eres R2 AI Executive, el asistente de dirección ejecutiva del Grupo R2.

Tu función es ayudar a la dirección a analizar, organizar y desarrollar

proyectos empresariales, financieros, tecnológicos y comerciales.

Áreas de trabajo:

- Estrategia y dirección empresarial.

- Hispania Solar y proyectos de energía fotovoltaica.

- R2 Horlogerie y desarrollo de relojería.

- Inversiones Ropocar y proyectos mineros.

- Finanzas, presupuestos y búsqueda de capital.

- Innovación, inteligencia artificial y tecnología.

- Organización de proyectos y tareas del Grupo R2.

Responde en español, con claridad, profesionalidad y orientación práctica.

No inventes datos, cifras, contratos, permisos ni resultados.

Distingue los hechos confirmados de las hipótesis y estimaciones.

Cuando falte información importante, pregunta antes de concluir.

No realices pagos, contratos ni compromisos externos.

Solicita autorización expresa antes de cualquier acción de ese tipo.

No afirmes que has ejecutado acciones que no has realizado.

"""

class Tarea(BaseModel):

    titulo: str = Field(..., min_length=1, max_length=200)

    descripcion: Optional[str] = None

    prioridad: str = "normal"

    estado: str = "pendiente"

class Mensaje(BaseModel):

    rol: Literal["user", "model"]

    contenido: str = Field(..., min_length=1, max_length=10000)

class SolicitudChat(BaseModel):

    mensaje: str = Field(..., min_length=1, max_length=10000)

    historial: list[Mensaje] = Field(default_factory=list)

@app.get("/", response_class=HTMLResponse)

def home():

    return """

    <!DOCTYPE html>

    <html lang="es">

    <head>

      <meta charset="utf-8">

      <meta name="viewport" content="width=device-width, initial-scale=1">

      <title>R2 AI Executive</title>

      <style>

        body {

          font-family: Arial, sans-serif;

          background: #10131a;

          color: white;

          padding: 20px;

          max-width: 800px;

          margin: auto;

        }

        h1 { color: #d6b56d; }

        #chat {

          background: #1c2230;

          padding: 15px;

          border-radius: 12px;

          min-height: 250px;

          margin: 20px 0;

          white-space: pre-wrap;

        }

        input {

          box-sizing: border-box;

          width: 100%;

          padding: 14px;

          border-radius: 8px;

          border: 1px solid #555;

          background: #fff;

          font-size: 16px;

        }

        button {

          margin-top: 10px;

          padding: 13px 22px;

          border: 0;

          border-radius: 8px;

          background: #d6b56d;

          color: #10131a;

          font-weight: bold;

          font-size: 16px;

        }

        .user { color: #fff; margin: 12px 0; }

        .assistant { color: #e5c77e; margin: 12px 0; }

        a { color: #d6b56d; }

      </style>

    </head>

    <body>

      <h1>R2 AI Executive</h1>

      <h2>Sistema de Dirección Ejecutiva del Grupo R2</h2>

      <p>Centro de operaciones del Grupo R2.</p>

      <div id="chat">R2 AI Executive está preparado para recibir instrucciones.</div>

      <input id="mensaje" type="text"

        placeholder="Escribe tu instrucción para R2..." />

      <button id="enviar" onclick="enviarMensaje()">Enviar</button>

      <p><a href="/docs">Documentación técnica</a></p>

      <p><a href="/health">Estado del sistema</a></p>

      <script>

        const historial = [];

        async function enviarMensaje() {

          const input = document.getElementById("mensaje");

          const boton = document.getElementById("enviar");

          const chat = document.getElementById("chat");

          const mensaje = input.value.trim();

          if (!mensaje) return;

          chat.textContent += "\\n\\nTÚ: " + mensaje;

          input.value = "";

          boton.disabled = true;

          boton.textContent = "Procesando...";

          try {

            const respuesta = await fetch("/api/chat", {

              method: "POST",

              headers: {"Content-Type": "application/json"},

              body: JSON.stringify({

                mensaje: mensaje,

                historial: historial

              })

            });

            const datos = await respuesta.json();

            if (!respuesta.ok) {

              throw new Error(datos.detail || "Error al consultar la IA");

            }

            historial.push(

              {rol: "user", contenido: mensaje},

              {rol: "model", contenido: datos.respuesta}

            );

            chat.textContent += "\\n\\nR2 AI: " + datos.respuesta;

          } catch (error) {

            chat.textContent += "\\n\\nERROR: " + error.message;

          } finally {

            boton.disabled = false;

            boton.textContent = "Enviar";

          }

        }

        document.getElementById("mensaje").addEventListener(

          "keydown", function(event) {

            if (event.key === "Enter") enviarMensaje();

          }

        );

      </script>

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

            "aprobaciones",

            "asistente_ia"

        ],

        "estado": "operativo"

    }

@app.post("/api/tareas")

def crear_tarea(tarea: Tarea):

    return {

        "mensaje": "Tarea recibida. El almacenamiento se incorporará posteriormente.",

        "tarea": tarea.model_dump()

    }

@app.post("/api/chat")

def conversar(solicitud: SolicitudChat):

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:

        raise HTTPException(

            status_code=503,

            detail="La clave de Gemini no está configurada en Render."

        )

    contenidos = []

    for item in solicitud.historial[-20:]:

        contenidos.append(

            types.Content(

                role=item.rol,

                parts=[types.Part.from_text(text=item.contenido)]

            )

        )

    contenidos.append(

        types.Content(

            role="user",

            parts=[types.Part.from_text(text=solicitud.mensaje)]

        )

    )

    try:

        client = genai.Client(api_key=api_key)

        respuesta = client.models.generate_content(

            model="gemini-3.8-flash",

            contents=contenidos,

            config=types.GenerateContentConfig(

                system_instruction=INSTRUCCIONES_R2,

                temperature=0.4,

                max_output_tokens=1500

            )

        )

        texto = respuesta.text or "No se recibió una respuesta de Gemini."

        client.close()

        return {"estado": "ok", "respuesta": texto}

    except Exception as error:

        raise HTTPException(

            status_code=502,

            detail="No se pudo obtener respuesta de Gemini: " + str(error)

        )

