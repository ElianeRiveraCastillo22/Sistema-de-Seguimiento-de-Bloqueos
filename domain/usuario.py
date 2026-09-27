# Usuario es la clase base de Consultor y LiderTecnico (herencia). No se
# instancia directamente en ningún flujo del programa -- es "abstracta" en
# el sentido de diseño, aunque no se fuerza con el módulo abc para mantener
# el código simple en este nivel del curso.
class Usuario:
    def __init__(self, id_: str, nombre: str):
        self._id = id_
        self._nombre = nombre

    def obtener_nombre(self) -> str:
        return self._nombre

    def validar_credencial(self, id_ingresado: str) -> bool:
        return id_ingresado == self._id
