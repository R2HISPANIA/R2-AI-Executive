

from datetime import datetime, timezone

ACCIONES_LIBRES = [

    "investigar",

    "generar_ideas",

    "crear_borradores",

    "analizar",

    "planificar",

    "crear_prototipos_locales",

]

ACCIONES_REQUIEREN_AUTORIZACION = [

    "gastar_dinero",

    "contratar_servicios",

    "firmar_contratos",

    "constituir_sociedades",

    "publicar_comercialmente",

    "vender_productos",

    "ceder_derechos",

    "comprometer_recursos_externos",

]

def evaluar_autorizacion(

    accion: str,

    autorizacion_humana: bool = False,

    presupuesto: float = 0,

    presupuesto_aprobado: float = 0,

):

    """

    Evalúa si R2 Creative Studio puede realizar una acción.

    Las acciones sensibles requieren autorización humana.

    """

    accion = accion.strip().lower()

    if accion in ACCIONES_LIBRES:

        return {

            "permitido": True,

            "requiere_autorizacion": False,

            "motivo": "Acción permitida dentro de la autonomía creativa.",

        }

    if accion in ACCIONES_REQUIEREN_AUTORIZACION:

        if not autorizacion_humana:

            return {

                "permitido": False,

                "requiere_autorizacion": True,

                "motivo": "Se necesita autorización humana.",

            }

        if presupuesto > presupuesto_aprobado:

            return {

                "permitido": False,

                "requiere_autorizacion": True,

                "motivo": "El presupuesto supera el importe autorizado.",

            }

        return {

            "permitido": True,

            "requiere_autorizacion": False,

            "motivo": "Autorización humana indicada y presupuesto dentro del límite.",

        }

    return {

        "permitido": False,

        "requiere_autorizacion": True,

        "motivo": "Acción no reconocida. Requiere revisión humana.",

    }

def registrar_solicitud(

    accion: str,

    descripcion: str,

    presupuesto: float = 0,

):

    """Prepara una solicitud pendiente de autorización humana."""

    return {

        "id": datetime.now(timezone.utc).isoformat(),

        "accion": accion,

        "descripcion": descripcion,

        "presupuesto_solicitado": presupuesto,

        "estado": "pendiente_de_autorizacion",

        "autorizado_por": None,

    }
