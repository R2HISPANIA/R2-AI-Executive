

from datetime import datetime, timezone

from uuid import uuid4

ACCIONES_LIBRES = [

    "investigar",

    "generar_ideas",

    "crear_borradores",

    "analizar",

    "planificar",

    "crear_prototipos_locales",

]

ACCIONES_REQUIEREN_AUTORIZACION = [

    "generar_imagen",

    "gastar_dinero",

    "contratar_servicios",

    "firmar_contratos",

    "constituir_sociedades",

    "publicar_comercialmente",

    "vender_productos",

    "ceder_derechos",

    "comprometer_recursos_externos",

]

def registrar_solicitud(

    accion: str,

    descripcion: str,

    presupuesto: float = 0,

):

    """

    Registra una solicitud pendiente de aprobación humana.

    Esta función no autoriza ni ejecuta acciones.

    """

    accion = accion.strip().lower()

    if accion not in ACCIONES_REQUIEREN_AUTORIZACION:

        raise ValueError("La acción no requiere este tipo de solicitud.")

    if not descripcion or not descripcion.strip():

        raise ValueError("La descripción es obligatoria.")

    if presupuesto < 0:

        raise ValueError("El presupuesto no puede ser negativo.")

    return {

        "id": str(uuid4()),

        "accion": accion,

        "descripcion": descripcion.strip(),

        "presupuesto_solicitado": presupuesto,

        "estado": "pendiente_de_autorizacion",

        "fecha_solicitud": datetime.now(timezone.utc).isoformat(),

        "autorizado_por": None,

        "fecha_autorizacion": None,

    }

def evaluar_autorizacion(accion: str):

    """

    Evalúa si una acción está permitida.

    Las acciones sensibles requieren aprobación humana verificable.

    """

    accion = accion.strip().lower()

    if accion in ACCIONES_LIBRES:

        return {

            "permitido": True,

            "requiere_autorizacion": False,

            "motivo": "Acción permitida dentro de la autonomía creativa.",

        }

    if accion in ACCIONES_REQUIEREN_AUTORIZACION:

        return {

            "permitido": False,

            "requiere_autorizacion": True,

            "motivo": (

                "Acción bloqueada. Requiere aprobación humana "

                "mediante el sistema de autorización verificable."

            ),

        }

    return {

        "permitido": False,

        "requiere_autorizacion": True,

        "motivo": "Acción no reconocida. Requiere revisión humana.",

    }
