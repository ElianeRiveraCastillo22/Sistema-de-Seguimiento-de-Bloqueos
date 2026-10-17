from domain.excepciones import CredencialInvalidaError
from domain.enums import TipoBloqueo, EstadoBloqueo
from presentation.entrada import pedir_texto, pedir_si_no, pedir_opcion_enum


def autenticar_consultor(lider_tecnico, nombre: str, id_ingresado: str):
    """HU-01: valida nombre + ID. Si no coinciden, rechaza sin crear nada."""
    for consultor in lider_tecnico.obtener_consultores():
        if consultor.obtener_nombre().strip().lower() == nombre.strip().lower():
            if consultor.validar_credencial(id_ingresado):
                return consultor
            break
    raise CredencialInvalidaError("El nombre y el ID ingresados no coinciden con ningún consultor.")


def menu_consultor(lider_tecnico, gestor, notificador):
    print("\n--- Ingreso como Consultor ---")
    nombre = pedir_texto("Tu nombre: ")
    id_ingresado = pedir_texto("Tu ID: ")

    try:
        consultor = autenticar_consultor(lider_tecnico, nombre, id_ingresado)
    except CredencialInvalidaError as e:
        print(f"\n❌ {e.obtener_mensaje()}")
        return

    proyecto = consultor.obtener_proyecto_actual()
    print(f"\nBienvenido/a {consultor.obtener_nombre()} — proyecto actual: {proyecto}")

    while True:
        print("\n--- MENÚ CONSULTOR ---")
        print("1. Registrar bloqueo")
        print("2. Ver mis bloqueos")
        print("0. Cambiar de rol")
        opcion = pedir_texto("Elige una opción: ")

        if opcion == "1":
            _registrar_bloqueo(consultor, gestor, notificador)
        elif opcion == "2":
            _ver_mis_bloqueos(consultor, gestor)
        elif opcion == "0":
            return
        else:
            print("Opción inválida.")


def _registrar_bloqueo(consultor, gestor, notificador):
    print("\n-- Registrar bloqueo --")
    tarea = pedir_texto("Tarea afectada: ")
    tipo = pedir_opcion_enum("Tipo de bloqueo:", TipoBloqueo)
    depende_de = pedir_texto("¿De quién/qué depende?: ", obligatorio=False)
    comunicado_cliente = pedir_si_no("¿Ya comunicaste esto al líder de la consultora (cliente)?")

    bloqueo = consultor.registrar_bloqueo(tarea, tipo, depende_de, comunicado_cliente)
    print(f"\n✅ Bloqueo registrado con código {bloqueo.obtener_codigo()}")
    gestor.agregar(bloqueo)  # el gestor avisa a los observadores (patrón Observer)


def _ver_mis_bloqueos(consultor, gestor):
    bloqueos = consultor.ver_bloqueos(gestor)
    if not bloqueos:
        print("\nNo tienes bloqueos registrados.")
        return

    print("\n-- Mis bloqueos --")
    for b in bloqueos:
        print(f"\n{b}")
        for c in b.obtener_comentarios():
            print(f"    {c}")

    codigo = pedir_texto("\nCódigo de bloqueo a actualizar (Enter para omitir): ", obligatorio=False)
    if not codigo:
        return

    seleccionado = next((b for b in bloqueos if b.obtener_codigo() == codigo), None)
    if seleccionado is None:
        print("  Ese código no está entre tus bloqueos.")
        return

    comentario = pedir_texto("Comentario de avance (Enter para omitir): ", obligatorio=False)
    if comentario:
        seleccionado.agregar_comentario(consultor.obtener_nombre(), comentario)

    if pedir_si_no("¿Ya se resolvió este bloqueo?"):
        gestor.cambiar_estado(seleccionado, EstadoBloqueo.CERRADO)
        print("  Bloqueo marcado como cerrado.")
