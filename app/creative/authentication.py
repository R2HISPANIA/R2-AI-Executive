

import os

import json

import hmac

import time

import base64

import secrets

import hashlib

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

    """Crea una sesión firmada con caducidad."""

    secreto = os.getenv("R2_SESSION_SECRET")

    if not secreto or len(secreto) < 32:

        raise RuntimeError(

            "R2_SESSION_SECRET debe tener al menos 32 caracteres."

        )

    ahora = int(time.time())

    datos = {

        "usuario": usuario,

        "creado": ahora,

        "expira": ahora + DURACION_SESION,

        "nonce": secrets.token_urlsafe(16),

    }

    contenido = codificar(

        json.dumps(datos, separators=(",", ":")).encode()

    )

    firma = hmac.new(

        secreto.encode(),

        contenido.encode(),

        hashlib.sha256,

    ).digest()

    return contenido + "." + codificar(firma)

def verificar_token_sesion(token: str):

    """Verifica la firma y caducidad de una sesión."""

    secreto = os.getenv("R2_SESSION_SECRET")

    usuario_configurado = os.getenv("R2_ADMIN_USERNAME")

    if not secreto or len(secreto) < 32:

        return None

    if not usuario_configurado:

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

        if int(datos.get("expira", 0)) <= int(time.time()):

            return None

        if int(datos.get("creado", 0)) > int(time.time()) + 60:

            return None

        if not datos.get("nonce"):

            return None

        return datos

    except (ValueError, TypeError, KeyError):

        return None
