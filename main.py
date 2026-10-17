from datetime import date

from domain.lider_tecnico import LiderTecnico
from domain.proyecto import Proyecto
from servicios.gestor_bloqueo import GestorBloqueo
from servicios.canales import FabricaCanales
from servicios.observadores import NotificadorLider, RegistroAuditoria
from presentation.menu_consultor import menu_consultor
from presentation.menu_lider import menu_lider
from presentation.entrada import pedir_texto


def datos_de_arranque(lider_tecnico: LiderTecnico) -> None:
    """Crea un par de consultores de ejemplo para poder probar el sistema
    de inmediato, sin tener que registrar todo a mano en cada ejecución."""
    proyecto_bbva = Proyecto("PRY-001", "BBVA", date(2026, 1, 1), date(2026, 12, 31), 100.0)
    proyecto_interbank = Proyecto("PRY-002", "Interbank", date(2026, 3, 1), date(2026, 9, 30), 80.0)

    c1 = lider_tecnico.registrar_consultor("1111", "Eliane", proyecto_bbva, ["LitElement", "CELLS"])
    c2 = lider_tecnico.registrar_consultor("2222", "Jesus", proyecto_interbank, ["Python", "SQL"])

    print("=== Datos de arranque creados (solo para pruebas) ===")
    print(f"  {c1.obtener_nombre()} -> ID: 1111")
    print(f"  {c2.obtener_nombre()} -> ID: 2222")
    print("=" * 55)


def main():
    lider_tecnico = LiderTecnico("admin", "Jazmín")
    gestor = GestorBloqueo()
    # Observer + Factory: el gestor avisa a sus observadores; el canal lo crea la fábrica
    notificador = NotificadorLider(FabricaCanales.crear("consola"))
    gestor.suscribir(notificador)
    gestor.suscribir(RegistroAuditoria())

    datos_de_arranque(lider_tecnico)

    while True:
        print("\n========== SISTEMA DE SEGUIMIENTO DE BLOQUEOS ==========")
        print("1. Ingresar como Consultor")
        print("2. Ingresar como Líder Técnico")
        print("0. Salir")
        opcion = pedir_texto("Elige una opción: ")

        if opcion == "1":
            menu_consultor(lider_tecnico, gestor, notificador)
        elif opcion == "2":
            menu_lider(lider_tecnico, gestor, notificador)
        elif opcion == "0":
            print("Hasta luego.")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
