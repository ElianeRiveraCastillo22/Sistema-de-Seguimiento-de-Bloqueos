import uuid

from domain.excepciones import ConsultorNoEncontradoError, BloqueoNoEncontradoError
from domain.proyecto import Proyecto
from domain.enums import TipoBloqueo, EstadoBloqueo
from domain.excepciones import CanalNoSoportadoError
from servicios.canales import FabricaCanales
from servicios.estrategias import ESTRATEGIAS_DISPONIBLES
from presentation.entrada import (
    pedir_texto, pedir_float_rango, pedir_fecha, pedir_si_no, pedir_opcion_enum,
)


def menu_lider(lider_tecnico, gestor, notificador):
    # notificador: observador NotificadorLider (permite cambiar de canal)
    print(f"\n--- Ingreso como Líder Técnico ({lider_tecnico.obtener_nombre()}) ---")

    while True:
        print("\n--- MENÚ LÍDER TÉCNICO ---")
        print("1. Registrar consultor")
        print("2. Registrar bloqueo en nombre de un consultor")
        print("3. Buscar bloqueos por nombre de consultor")
        print("4. Listar bloqueos (por consultor o estado)")
        print("5. Revisar bloqueos abiertos")
        print("6. Marcar seguimiento realizado hoy")
        print("7. Configurar canal de notificación")
        print("0. Cambiar de rol")
        opcion = pedir_texto("Elige una opción: ")

        if opcion == "1":
            _registrar_consultor(lider_tecnico)
        elif opcion == "2":
            _registrar_bloqueo_por_lider(lider_tecnico, gestor)
        elif opcion == "3":
            _buscar_por_nombre(lider_tecnico, gestor)
        elif opcion == "4":
            _listar_bloqueos(lider_tecnico, gestor)
        elif opcion == "5":
            _revisar_abiertos(lider_tecnico, gestor)
        elif opcion == "6":
            _marcar_seguimiento(lider_tecnico, gestor)
        elif opcion == "7":
            _configurar_canal(notificador)
        elif opcion == "0":
            return
        else:
            print("Opción inválida.")


def _registrar_consultor(lider_tecnico):
    print("\n-- Registrar consultor --")
    nombre = pedir_texto("Nombre del consultor: ")
    codigo_proy = pedir_texto("Código de proyecto: ")
    cliente = pedir_texto("Cliente: ")
    fecha_inicio = pedir_fecha("Fecha de inicio")
    fecha_fin = pedir_fecha("Fecha de fin estimada")
    porcentaje = pedir_float_rango("Porcentaje de asignación (0-100): ", 0, 100)
    tecnologias_raw = pedir_texto("Tecnologías (separadas por coma): ", obligatorio=False)
    tecnologias = [t.strip() for t in tecnologias_raw.split(",") if t.strip()]

    proyecto = Proyecto(codigo_proy, cliente, fecha_inicio, fecha_fin, porcentaje)
    id_generado = uuid.uuid4().hex[:8]
    lider_tecnico.registrar_consultor(id_generado, nombre, proyecto, tecnologias)

    print(f"\n✅ Consultor '{nombre}' registrado.")
    print(f"   ID secreto (solo debe conocerlo {nombre}): {id_generado}")


def _registrar_bloqueo_por_lider(lider_tecnico, gestor):
    print("\n-- Registrar bloqueo en nombre de un consultor --")
    nombre = pedir_texto("Nombre del consultor: ")
    try:
        consultor = lider_tecnico.buscar_consultor_por_nombre(nombre)
    except ConsultorNoEncontradoError as e:
        print(f"\n❌ {e.obtener_mensaje()}")
        return

    tarea = pedir_texto("Tarea afectada: ")
    tipo = pedir_opcion_enum("Tipo de bloqueo:", TipoBloqueo)
    estado = pedir_opcion_enum("Estado actual:", EstadoBloqueo)
    motivo = pedir_texto("Motivo por el que se registra recién ahora: ")

    bloqueo = lider_tecnico.registrar_bloqueo(consultor, tarea, tipo, estado, motivo)
    gestor.agregar(bloqueo)
    print(f"\n✅ Bloqueo registrado con código {bloqueo.obtener_codigo()} (registrado por líder técnico)")


def _buscar_por_nombre(lider_tecnico, gestor):
    nombre = pedir_texto("\nNombre del consultor a buscar: ")
    resultados = lider_tecnico.buscar_bloqueos_por_nombre(gestor, nombre)
    if not resultados:
        print("  No se encontraron bloqueos para ese nombre.")
        return
    for b in resultados:
        print(f"  {b}")


def _listar_bloqueos(lider_tecnico, gestor):
    print("\n-- Listar bloqueos --")
    consultor = None
    if pedir_si_no("¿Filtrar por consultor?"):
        nombre = pedir_texto("Nombre del consultor: ")
        try:
            consultor = lider_tecnico.buscar_consultor_por_nombre(nombre)
        except ConsultorNoEncontradoError as e:
            print(f"❌ {e.obtener_mensaje()}")
            return

    estado = None
    if pedir_si_no("¿Filtrar por estado?"):
        estado = pedir_opcion_enum("Estado:", EstadoBloqueo)

    resultados = lider_tecnico.listar_bloqueos(gestor, consultor, estado)
    if not resultados:
        print("  No hay bloqueos que coincidan con el filtro.")
        return
    for b in resultados:
        print(f"  {b} — consultor: {b.obtener_consultor().obtener_nombre()}")


def _elegir_estrategia():
    print("\nOrden de revisión:")
    for i, clase in enumerate(ESTRATEGIAS_DISPONIBLES, start=1):
        print(f"  {i}. {clase().obtener_nombre()}")
    while True:
        eleccion = pedir_texto("Elige el orden: ")
        if eleccion.isdigit() and 1 <= int(eleccion) <= len(ESTRATEGIAS_DISPONIBLES):
            return ESTRATEGIAS_DISPONIBLES[int(eleccion) - 1]()
        print("  Opción inválida.")


def _configurar_canal(notificador):
    print(f"\nCanal actual: {notificador.obtener_canal().obtener_nombre()}")
    print("Canales disponibles: " + ", ".join(FabricaCanales.canales_disponibles()))
    nombre = pedir_texto("Nuevo canal: ")
    try:
        notificador.cambiar_canal(FabricaCanales.crear(nombre))
    except CanalNoSoportadoError as e:
        print(f"\n❌ {e.obtener_mensaje()}")
        return
    print(f"✅ Canal cambiado a {nombre.strip().lower()}")


def _revisar_abiertos(lider_tecnico, gestor):
    estrategia = _elegir_estrategia()
    abiertos = lider_tecnico.revisar_bloqueos_abiertos(gestor, estrategia)
    if not abiertos:
        print("\nNo hay bloqueos abiertos por revisar.")
        return

    print(f"\n-- Sesión de revisión de bloqueos abiertos ({estrategia.obtener_nombre()}) --")
    for b in abiertos:
        print(f"\n{b} — consultor: {b.obtener_consultor().obtener_nombre()}")
        comentario = pedir_texto("Comentario de avance (Enter para omitir): ", obligatorio=False)
        if comentario:
            b.agregar_comentario(lider_tecnico.obtener_nombre(), comentario)
        if pedir_si_no("¿Cambiar el estado de este bloqueo?"):
            nuevo_estado = pedir_opcion_enum("Nuevo estado:", EstadoBloqueo)
            gestor.cambiar_estado(b, nuevo_estado)


def _marcar_seguimiento(lider_tecnico, gestor):
    codigo = pedir_texto("\nCódigo del bloqueo: ")
    try:
        bloqueo = gestor.buscar_por_codigo(codigo)
    except BloqueoNoEncontradoError as e:
        print(f"❌ {e.obtener_mensaje()}")
        return
    lider_tecnico.marcar_seguimiento_hoy(bloqueo)
    print(f"✅ Seguimiento de hoy registrado para {codigo}")
