

import os

import json

import hmac

import time

import base64

import secrets

import hashlib

from app.authentication_db import (

    registrar_sesion,

    comprobar_sesion,

    revocar_sesion,

)

ITERACIONES = 600_000

DURACION_SESION = 3600 * 8

def codificar(datos: bytes) -> str:

    return base64.urlsafe_b64encode(datos).decode().rstrip("=")

def decodificar(texto: str) -> bytes:

    return base64.urlsafe_b64decode(

        texto + "=" * (-len(texto) % 4)

    )

def generar_hash_password(password: str) -> str:

    """Genera un hash seguro para la contraseña administrativa."""

    if len(password) < 12:

        raise ValueError(

            "La contraseña debe tener al menos 12 caracteres."

        )

    salt = secrets.token_bytes(16)

    resultado = hashlib.pbkdf2_hmac(

        "sha256",

        password.encode(),

        salt,

        ITERACIONES,

    )

    return (

        f"pbkdf2_sha256${ITERACIONES}"

        f"${codificar(salt)}${codificar(resultado)}"

    )

def verificar_password(password: str) -> bool:

    """Verifica las credenciales del administrador."""

    usuario_configurado = os.getenv("R2_ADMIN_USERNAME")

    hash_configurado = os.getenv("R2_ADMIN_PASSWORD_HASH")

    if not usuario_configurado or not hash_configurado:

        return False

    try:

        algoritmo, iteraciones, salt, hash_original = (

            hash_configurado.split("$")

        )

        if algoritmo != "pbkdf2_sha256":

            return False

        iteraciones = int(iteraciones)

        if iteraciones < 600_000 or iteraciones > 2_000_000:

            return False

        salt_bytes = decodificar(salt)

        hash_bytes = decodificar(hash_original)

        if len(salt_bytes) != 16 or len(hash_bytes) != 32:

            return False

        hash_calculado = hashlib.pbkdf2_hmac(

            "sha256",

            password.encode(),

            salt_bytes,

            iteraciones,

        )

        return hmac.compare_digest(

            hash_calculado,

            hash_bytes,

        )

    except (ValueError, TypeError):

        return False

def autenticar_administrador(

    usuario: str,

    password: str,

) -> bool:

    """Comprueba la identidad del administrador."""

    usuario_configurado = os.getenv("R2_ADMIN_USERNAME")

    if not usuario_configurado:

        return False

    usuario_valido = hmac.compare_digest(

        usuario.encode(),

        usuario_configurado.encode(),

    )

    password_valida = verificar_password(password)

    return usuario_valido and password_valida

def crear_token_sesion(usuario: str) -> str:

    """Crea una sesión firmada y la registra en PostgreSQL."""

    usuario_configurado = os.getenv("R2_ADMIN_USERNAME")

    secreto = os.getenv("R2_SESSION_SECRET")

    if not usuario_configurado or usuario != usuario_configurado:

        raise ValueError("Administrador no válido.")

    if not secreto or len(secreto) < 32:

        raise RuntimeError(

            "R2_SESSION_SECRET debe tener al menos 32 caracteres."

        )

    ahora = int(time.time())

    nonce = secrets.token_urlsafe(32)

    datos = {

        "usuario": usuario,

        "creado": ahora,

        "expira": ahora + DURACION_SESION,

        "nonce": nonce,

    }

    contenido = codificar(

        json.dumps(datos, separators=(",", ":")).encode()

    )

    firma = hmac.new(

        secreto.encode(),

        contenido.encode(),

        hashlib.sha256,

    ).digest()

    token = contenido + "." + codificar(firma)

    from datetime import datetime, timezone

    registrada = registrar_sesion(

        session_id=nonce,

        username=usuario,

        created_at=datetime.fromtimestamp(

            ahora, tz=timezone.utc

        ),

        expires_at=datetime.fromtimestamp(

            ahora + DURACION_SESION, tz=timezone.utc

        ),

    )

    if not registrada:

        raise RuntimeError(

            "No se pudo registrar la sesión administrativa."

        )

    return token

def verificar_token_sesion(token: str):

    """Verifica firma, caducidad y existencia de la sesión en PostgreSQL."""

    secreto = os.getenv("R2_SESSION_SECRET")

    usuario_configurado = os.getenv("R2_ADMIN_USERNAME")

    if not secreto or len(secreto) < 32:

        return None

    if not usuario_configurado or not isinstance(token, str):

        return None

    try:

        contenido, firma_recibida = token.split(".")

        firma_esperada = hmac.new(

            secreto.encode(),

            contenido.encode(),

            hashlib.sha256,

        ).digest()

        firma_bytes = decodificar(firma_recibida)

        if not hmac.compare_digest(

            firma_esperada,

            firma_bytes,

        ):

            return None

        datos = json.loads(decodificar(contenido))

        if datos.get("usuario") != usuario_configurado:

            return None

        ahora = int(time.time())

        creado = int(datos.get("creado", 0))

        expira = int(datos.get("expira", 0))

        nonce = datos.get("nonce")

        if expira <= ahora:

            return None

        if creado > ahora + 60:

            return None

        if expira <= creado or expira - creado > DURACION_SESION:

            return None

        if not isinstance(nonce, str) or not nonce:

            return None

        if not comprobar_sesion(nonce, usuario_configurado):

            return None

        return datos

    except Exception:

        return None

def cerrar_sesion(token: str) -> bool:

    """Revoca una sesión administrativa en PostgreSQL."""

    datos = verificar_token_sesion(token)

    if not datos:

        return False

    try:

        return revocar_sesion(

            session_id=datos["nonce"],

            username=datos["usuario"],

        )

    except Exception:

        return False
