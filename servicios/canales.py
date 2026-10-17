from abc import ABC, abstractmethod

from domain.excepciones import CanalNoSoportadoError


class CanalNotificacion(ABC):
    """Producto del patrón Factory Method: contrato común de todos los canales."""

    @abstractmethod
    def enviar(self, destinatario: str, mensaje: str) -> bool:
        ...

    @abstractmethod
    def obtener_nombre(self) -> str:
        ...


class CanalConsola(CanalNotificacion):
    def enviar(self, destinatario: str, mensaje: str) -> bool:
        print(f"\n[NOTIFICACIÓN -> {destinatario}]")
        print(mensaje)
        print("-" * 40)
        return True

    def obtener_nombre(self) -> str:
        return "consola"


class CanalTeamsSimulado(CanalNotificacion):
    """Simula el envío a Microsoft Teams (en producción sería un flujo de
    Power Automate Workflows). No hace llamadas de red."""

    def enviar(self, destinatario: str, mensaje: str) -> bool:
        print(f"\n[TEAMS (simulado) -> {destinatario}] {mensaje}")
        return True

    def obtener_nombre(self) -> str:
        return "teams"


class CanalMemoria(CanalNotificacion):
    """Guarda los mensajes en una lista; útil para pruebas y auditoría."""

    def __init__(self):
        self.__mensajes = []

    def enviar(self, destinatario: str, mensaje: str) -> bool:
        self.__mensajes.append((destinatario, mensaje))
        return True

    def obtener_mensajes(self):
        return list(self.__mensajes)

    def obtener_nombre(self) -> str:
        return "memoria"


class FabricaCanales:
    """Factory Method: centraliza la creación de canales según un nombre."""

    __registro = {
        "consola": CanalConsola,
        "teams": CanalTeamsSimulado,
        "memoria": CanalMemoria,
    }

    @classmethod
    def crear(cls, nombre: str) -> CanalNotificacion:
        clave = (nombre or "").strip().lower()
        if clave not in cls.__registro:
            raise CanalNoSoportadoError(
                f'El canal "{nombre}" no existe. Opciones: {", ".join(cls.__registro)}')
        return cls.__registro[clave]()

    @classmethod
    def canales_disponibles(cls):
        return list(cls.__registro)
