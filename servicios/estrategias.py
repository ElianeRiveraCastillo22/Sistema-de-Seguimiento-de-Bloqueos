from abc import ABC, abstractmethod
from typing import List

from domain.bloqueo import Bloqueo
from domain.enums import EstadoBloqueo


class EstrategiaOrden(ABC):
    """Strategy: algoritmo intercambiable para ordenar bloqueos en la revisión."""

    @abstractmethod
    def ordenar(self, bloqueos: List[Bloqueo]) -> List[Bloqueo]:
        ...

    @abstractmethod
    def obtener_nombre(self) -> str:
        ...


class OrdenPorAntiguedad(EstrategiaOrden):
    """Los más antiguos (más días bloqueados) primero."""

    def ordenar(self, bloqueos):
        return sorted(bloqueos, key=lambda b: b.calcular_dias_bloqueado(), reverse=True)

    def obtener_nombre(self):
        return "Más antiguos primero"


class OrdenPorEstado(EstrategiaOrden):
    """Primero los que siguen bloqueados, luego avanzados, luego cerrados."""

    __prioridad = {EstadoBloqueo.SIGUE_BLOQUEADO: 0, EstadoBloqueo.AVANZADO: 1,
                   EstadoBloqueo.CERRADO: 2}

    def ordenar(self, bloqueos):
        return sorted(bloqueos, key=lambda b: self.__prioridad[b.obtener_estado()])

    def obtener_nombre(self):
        return "Sigue bloqueado primero"


class OrdenSinComunicarAlCliente(EstrategiaOrden):
    """Primero los que el consultor aún no comunicó al cliente (riesgo)."""

    def ordenar(self, bloqueos):
        return sorted(bloqueos, key=lambda b: b.fue_comunicado_al_cliente())

    def obtener_nombre(self):
        return "Sin comunicar al cliente primero"


ESTRATEGIAS_DISPONIBLES = [OrdenPorAntiguedad, OrdenPorEstado, OrdenSinComunicarAlCliente]
