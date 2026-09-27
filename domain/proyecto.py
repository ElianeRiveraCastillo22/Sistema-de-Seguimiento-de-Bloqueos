from datetime import date

class Proyecto:
    def __init__(self, codigo: str, cliente: str, fecha_inicio: date, fecha_fin: date,
                 porcentaje_asignacion: float):
        self.__codigo = codigo
        self.__cliente = cliente
        self.__fecha_inicio = fecha_inicio
        self.__fecha_fin = fecha_fin
        self.__porcentaje_asignacion = porcentaje_asignacion

    def obtener_codigo(self) -> str:
        return self.__codigo

    def obtener_cliente(self) -> str:
        return self.__cliente

    def obtener_fecha_inicio(self) -> date:
        return self.__fecha_inicio

    def obtener_fecha_fin(self) -> date:
        return self.__fecha_fin

    def obtener_porcentaje_asignacion(self) -> float:
        return self.__porcentaje_asignacion

    def __str__(self) -> str:
        return f"{self.__codigo} - {self.__cliente} ({self.__fecha_inicio} a {self.__fecha_fin})"