from typing import List, Optional

from domain.usuario import Usuario
from domain.proyecto import Proyecto
from domain.bloqueo import Bloqueo
from domain.enums import TipoBloqueo


class Consultor(Usuario):
    def __init__(self, id_: str, nombre: str, proyecto_actual: Proyecto,
                 tecnologias: Optional[List[str]] = None,
                 historial_proyectos: Optional[List[Proyecto]] = None):
        super().__init__(id_, nombre)
        self.__proyecto_actual = proyecto_actual
        self.__historial_proyectos: List[Proyecto] = historial_proyectos or []
        self.__tecnologias: List[str] = tecnologias or []

    def obtener_proyecto_actual(self) -> Proyecto:
        return self.__proyecto_actual

    def obtener_historial_proyectos(self) -> List[Proyecto]:
        return list(self.__historial_proyectos)

    def obtener_tecnologias(self) -> List[str]:
        return list(self.__tecnologias)

    # Polimorfismo: este método se comporta distinto al de LiderTecnico
    # (aquí siempre se registra sobre uno mismo, sin motivo de registro tardío)
    def registrar_bloqueo(self, tarea: str, tipo: TipoBloqueo, depende_de: str,
                           comunicado_cliente: bool) -> Bloqueo:
        return Bloqueo(
            tarea=tarea,
            tipo_bloqueo=tipo,
            consultor=self,
            depende_de=depende_de,
            comunicado_cliente=comunicado_cliente,
            registrado_por=self.obtener_nombre(),
        )

    def ver_bloqueos(self, gestor) -> List[Bloqueo]:
        return gestor.listar(consultor=self)