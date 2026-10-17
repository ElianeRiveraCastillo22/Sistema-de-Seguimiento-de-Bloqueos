from datetime import datetime


class Comentario:
    def __init__(self, autor: str, texto: str):
        self.__fecha = datetime.now()
        self.__autor = autor
        self.__texto = texto

    def obtener_fecha(self) -> datetime:
        return self.__fecha

    def obtener_autor(self) -> str:
        return self.__autor

    def obtener_texto(self) -> str:
        return self.__texto

    def __str__(self) -> str:
        return f"[{self.__fecha.strftime('%d/%m %H:%M')}] {self.__autor}: {self.__texto}"
