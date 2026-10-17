# En el diagrama UML esta clase base se llama "Exception". En el código la
# nombramos "ErrorSistema" para no chocar con la clase Exception propia de
# Python (si la llamáramos igual, taparíamos la de Python en este archivo).
# Conceptualmente es la misma clase del diagrama: hereda de la Exception de
# Python, guarda un mensaje y lo expone con un getter.
class ErrorSistema(Exception):
    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.__mensaje = mensaje

    def obtener_mensaje(self) -> str:
        return self.__mensaje


class CredencialInvalidaError(ErrorSistema):
    """El nombre y el ID ingresados no corresponden a ningún consultor registrado."""
    pass


class ConsultorNoEncontradoError(ErrorSistema):
    """No existe ningún consultor con el nombre buscado."""
    pass


class BloqueoNoEncontradoError(ErrorSistema):
    """No existe ningún bloqueo con el código o índice indicado."""
    pass


class CanalNoSoportadoError(ErrorSistema):
    """El canal de notificación solicitado no existe en la fábrica."""
    pass
