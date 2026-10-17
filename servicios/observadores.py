from abc import ABC, abstractmethod
from typing import List

from domain.bloqueo import Bloqueo
from domain.enums import EstadoBloqueo
from servicios.canales import CanalNotificacion

EVENTO_REGISTRADO = "BLOQUEO_REGISTRADO"
EVENTO_ESTADO = "ESTADO_CAMBIADO"


class ObservadorBloqueo(ABC):
    """Observer: quien quiera enterarse de cambios en los bloqueos implementa esto."""

    @abstractmethod
    def actualizar(self, evento: str, bloqueo: Bloqueo) -> None:
        ...


class NotificadorLider(ObservadorBloqueo):
    """Avisa al líder técnico por el canal elegido (HU de notificación)."""

    def __init__(self, canal: CanalNotificacion, destinatario: str = "Líder Técnico"):
        self.__canal = canal
        self.__destinatario = destinatario

    def cambiar_canal(self, canal: CanalNotificacion) -> None:
        self.__canal = canal

    def obtener_canal(self) -> CanalNotificacion:
        return self.__canal

    def actualizar(self, evento: str, bloqueo: Bloqueo) -> None:
        consultor = bloqueo.obtener_consultor().obtener_nombre()
        if evento == EVENTO_REGISTRADO:
            self.__canal.enviar(
                self.__destinatario,
                f"Nuevo bloqueo de {consultor}: {bloqueo.obtener_tarea()} "
                f"({bloqueo.obtener_tipo_bloqueo().value})")
        elif evento == EVENTO_ESTADO and bloqueo.obtener_estado() == EstadoBloqueo.CERRADO:
            self.__canal.enviar(
                self.__destinatario,
                f"El bloqueo {bloqueo.obtener_codigo()} de {consultor} fue cerrado.")


class RegistroAuditoria(ObservadorBloqueo):
    """Guarda una línea por cada evento (trazabilidad)."""

    def __init__(self):
        self.__lineas: List[str] = []

    def actualizar(self, evento: str, bloqueo: Bloqueo) -> None:
        self.__lineas.append(
            f"{evento} | {bloqueo.obtener_codigo()} | {bloqueo.obtener_estado().value}")

    def obtener_lineas(self) -> List[str]:
        return list(self.__lineas)
