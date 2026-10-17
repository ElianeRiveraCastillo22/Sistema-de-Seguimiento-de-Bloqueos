from datetime import datetime
from typing import List, Optional

from domain.enums import TipoBloqueo, EstadoBloqueo
from domain.comentario import Comentario


class Bloqueo:
    __contador = 0  # usado solo para generar códigos autoincrementales

    def __init__(self, tarea: str, tipo_bloqueo: TipoBloqueo, consultor, depende_de: str,
                 comunicado_cliente: bool, registrado_por: str,
                 motivo_registro_tardio: Optional[str] = None,
                 estado: EstadoBloqueo = EstadoBloqueo.SIGUE_BLOQUEADO):
        Bloqueo.__contador += 1
        self.__codigo = f"B-{Bloqueo.__contador:04d}"
        self.__tarea = tarea
        self.__tipo_bloqueo = tipo_bloqueo
        self.__depende_de = depende_de
        self.__comunicado_cliente = comunicado_cliente
        self.__fecha_comunicado_cliente = datetime.now() if comunicado_cliente else None
        self.__estado = estado
        self.__consultor = consultor
        self.__registrado_por = registrado_por
        self.__motivo_registro_tardio = motivo_registro_tardio
        self.__fecha_creacion = datetime.now()
        self.__seguimiento_hoy = False
        self.__comentarios: List[Comentario] = []

    # --- métodos de negocio ---

    def calcular_dias_bloqueado(self) -> int:
        return (datetime.now() - self.__fecha_creacion).days

    def agregar_comentario(self, autor: str, texto: str) -> None:
        self.__comentarios.append(Comentario(autor, texto))

    def cambiar_estado(self, nuevo_estado: EstadoBloqueo) -> None:
        self.__estado = nuevo_estado

    def marcar_seguimiento_hoy(self) -> None:
        self.__seguimiento_hoy = True

    # --- getters (atributos privados, acceso controlado) ---

    def obtener_codigo(self) -> str:
        return self.__codigo

    def obtener_tarea(self) -> str:
        return self.__tarea

    def obtener_tipo_bloqueo(self) -> TipoBloqueo:
        return self.__tipo_bloqueo

    def obtener_estado(self) -> EstadoBloqueo:
        return self.__estado

    def obtener_consultor(self):
        return self.__consultor

    def obtener_comentarios(self) -> List[Comentario]:
        return list(self.__comentarios)

    def obtener_dependencia(self) -> str:
        return self.__depende_de

    def fue_comunicado_al_cliente(self) -> bool:
        return self.__comunicado_cliente

    def obtener_registrado_por(self) -> str:
        return self.__registrado_por

    def obtener_motivo_registro_tardio(self) -> Optional[str]:
        return self.__motivo_registro_tardio

    def fue_seguido_hoy(self) -> bool:
        return self.__seguimiento_hoy

    def __str__(self) -> str:
        return (f"{self.__codigo} | {self.__tarea} | {self.__tipo_bloqueo.value} | "
                f"{self.__estado.value} | {self.calcular_dias_bloqueado()} día(s)")
