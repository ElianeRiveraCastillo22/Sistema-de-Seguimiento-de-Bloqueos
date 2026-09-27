from enum import Enum


class TipoBloqueo(Enum):
    ACCESO = "Falta de accesos"
    DEPENDENCIA_EQUIPO = "Dependencia de otro equipo"
    INFO_CLIENTE = "Falta de información del cliente"
    OTRO = "Otro"


class EstadoBloqueo(Enum):
    AVANZADO = "Avanzado"
    SIGUE_BLOQUEADO = "Sigue bloqueado"
    CERRADO = "Cerrado"
