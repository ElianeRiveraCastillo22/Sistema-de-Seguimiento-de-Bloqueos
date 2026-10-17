from typing import List, Optional

from domain.bloqueo import Bloqueo
from domain.enums import EstadoBloqueo
from domain.excepciones import BloqueoNoEncontradoError
from servicios.observadores import ObservadorBloqueo, EVENTO_REGISTRADO, EVENTO_ESTADO


class GestorBloqueo:
    """Sujeto (Subject) del patrón Observer: avisa a sus observadores cuando
    se registra un bloqueo o cambia su estado."""

    def __init__(self):
        self.__bloqueos: List[Bloqueo] = []
        self.__observadores: List[ObservadorBloqueo] = []

    # --- Observer ---
    def suscribir(self, observador: ObservadorBloqueo) -> None:
        if observador not in self.__observadores:
            self.__observadores.append(observador)

    def desuscribir(self, observador: ObservadorBloqueo) -> None:
        if observador in self.__observadores:
            self.__observadores.remove(observador)

    def __notificar(self, evento: str, bloqueo: Bloqueo) -> None:
        for o in list(self.__observadores):
            o.actualizar(evento, bloqueo)

    # --- operaciones ---
    def agregar(self, bloqueo: Bloqueo) -> None:
        self.__bloqueos.append(bloqueo)
        self.__notificar(EVENTO_REGISTRADO, bloqueo)

    def cambiar_estado(self, bloqueo: Bloqueo, nuevo_estado: EstadoBloqueo) -> None:
        bloqueo.cambiar_estado(nuevo_estado)
        self.__notificar(EVENTO_ESTADO, bloqueo)

    def buscar_por_nombre_consultor(self, nombre: str) -> List[Bloqueo]:
        return [
            b for b in self.__bloqueos
            if b.obtener_consultor().obtener_nombre().strip().lower() == nombre.strip().lower()
        ]

    def buscar_por_codigo(self, codigo: str) -> Bloqueo:
        for b in self.__bloqueos:
            if b.obtener_codigo() == codigo:
                return b
        raise BloqueoNoEncontradoError(f'No existe ningún bloqueo con código "{codigo}"')

    def listar(self, consultor=None, estado: Optional[EstadoBloqueo] = None) -> List[Bloqueo]:
        resultado = list(self.__bloqueos)
        if consultor is not None:
            resultado = [b for b in resultado if b.obtener_consultor() is consultor]
        if estado is not None:
            resultado = [b for b in resultado if b.obtener_estado() == estado]
        return resultado
