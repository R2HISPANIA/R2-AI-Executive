

import os

from google import genai

from google.genai import types

MODELO_IMAGEN = "gemini-3.1-flash-image"

def generar_imagen(prompt: str, relacion_aspecto: str = "1:1"):

    """

    Genera una imagen con Gemini y devuelve sus datos.

    """

    if not isinstance(prompt, str) or not prompt.strip():

        raise ValueError("Debes proporcionar una descripción.")

    formatos = ("1:1", "16:9", "9:16", "4:3", "3:4")

    if relacion_aspecto not in formatos:

        raise ValueError("Relación de aspecto no admitida.")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:

        raise RuntimeError("GEMINI_API_KEY no está configurada.")

    cliente = genai.Client(api_key=api_key)

    respuesta = cliente.models.generate_content(

        model=MODELO_IMAGEN,

        contents=prompt.strip(),

        config=types.GenerateContentConfig(

            response_modalities=["IMAGE"],

            image_config=types.ImageConfig(

                aspect_ratio=relacion_aspecto

            ),

        ),

    )

    for parte in respuesta.parts:

        if parte.inline_data and parte.inline_data.data:

            return {

                "imagen": parte.inline_data.data,

                "formato": parte.inline_data.mime_type,

                "modelo": MODELO_IMAGEN,

                "estado": "generada",

            }

    raise RuntimeError("Gemini no devolvió ninguna imagen.")
