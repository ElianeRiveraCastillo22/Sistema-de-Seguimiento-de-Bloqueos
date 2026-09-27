from typing import List, Optional

from domain.usuario import Usuario
from domain.consultor import Consultor
from domain.proyecto import Proyecto
from domain.bloqueo import Bloqueo
from domain.enums import TipoBloqueo, EstadoBloqueo
from domain.excepciones import ConsultorNoEncontradoError


class LiderTecnico(Usuario):
    def __init__(self, id_: str, nombre: str):
        super().__init__(id_, nombre)
        self.__consultores: List[Consultor] = []

    def obtener_consultores(self) -> List[Consultor]:
        return list(self.__consultores)

    def registrar_consultor(self, id_: str, nombre: str, proyecto: Proyecto,
                             tecnologias: Optional[List[str]] = None) -> Consultor:
        nuevo = Consultor(id_, nombre, proyecto, tecnologias)
        self.__consultores.append(nuevo)
        return nuevo

    def buscar_consultor_por_nombre(self, nombre: str) -> Consultor:
        for c in self.__consultores:
            if c.obtener_nombre().strip().lower() == nombre.strip().lower():
                return c
        raise ConsultorNoEncontradoError(f'No existe ningún consultor llamado "{nombre}"')

    # Polimorfismo: mismo nombre de método que Consultor.registrar_bloqueo,
    # pero con comportamiento distinto (registra en nombre de otro, con motivo)
    def registrar_bloqueo(self, consultor: Consultor, tarea: str, tipo: TipoBloqueo,
                           estado: EstadoBloqueo, motivo_tardio: str) -> Bloqueo:
        return Bloqueo(
            tarea=tarea,
            tipo_bloqueo=tipo,
            consultor=consultor,
            depende_de="",
            comunicado_cliente=False,
            registrado_por=self.obtener_nombre(),
            motivo_registro_tardio=motivo_tardio,
            estado=estado,
        )

    def buscar_bloqueos_por_nombre(self, gestor, nombre: str) -> List[Bloqueo]:
        return gestor.buscar_por_nombre_consultor(nombre)

    def listar_bloqueos(self, gestor, consultor: Optional[Consultor] = None,
                         estado: Optional[EstadoBloqueo] = None) -> List[Bloqueo]:
        return gestor.listar(consultor=consultor, estado=estado)

    def revisar_bloqueos_abiertos(self, gestor) -> List[Bloqueo]:
        return [b for b in gestor.listar() if b.obtener_estado() != EstadoBloqueo.CERRADO]

    def marcar_seguimiento_hoy(self, bloqueo: Bloqueo) -> None:
        bloqueo.marcar_seguimiento_hoy()