from typing import List, Optional

from domain.bloqueo import Bloqueo
from domain.enums import EstadoBloqueo
from domain.excepciones import BloqueoNoEncontradoError


class GestorBloqueo:
    def __init__(self):
        self.__bloqueos: List[Bloqueo] = []

    def agregar(self, bloqueo: Bloqueo) -> None:
        self.__bloqueos.append(bloqueo)

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
        resultado = self.__bloqueos
        if consultor is not None:
            resultado = [b for b in resultado if b.obtener_consultor() is consultor]
        if estado is not None:
            resultado = [b for b in resultado if b.obtener_estado() == estado]
        return resultado