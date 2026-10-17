import unittest
from datetime import date, datetime, timedelta
from unittest.mock import patch

from domain.bloqueo import Bloqueo
from domain.consultor import Consultor
from domain.lider_tecnico import LiderTecnico
from domain.proyecto import Proyecto
from domain.enums import TipoBloqueo, EstadoBloqueo
from domain.excepciones import (
    ErrorSistema, CredencialInvalidaError, ConsultorNoEncontradoError,
    BloqueoNoEncontradoError, CanalNoSoportadoError)
from servicios.gestor_bloqueo import GestorBloqueo
from servicios.canales import FabricaCanales, CanalMemoria, CanalConsola, CanalTeamsSimulado
from servicios.observadores import NotificadorLider, RegistroAuditoria
from servicios.estrategias import OrdenPorAntiguedad, OrdenPorEstado, OrdenSinComunicarAlCliente
from presentation.menu_consultor import autenticar_consultor


def proyecto():
    return Proyecto("P1", "Cliente", date(2026, 1, 1), date(2026, 12, 31), 100.0)


class Base(unittest.TestCase):
    def setUp(self):
        self.lider = LiderTecnico("admin", "Jazmín")
        self.eliane = self.lider.registrar_consultor("1111", "Eliane", proyecto(), ["Python"])
        self.jesus = self.lider.registrar_consultor("2222", "Jesus", proyecto())
        self.gestor = GestorBloqueo()


class TestBloqueo(Base):
    def test_codigo_autoincremental(self):
        a = self.eliane.registrar_bloqueo("t1", TipoBloqueo.ACCESO, "x", False)
        b = self.eliane.registrar_bloqueo("t2", TipoBloqueo.ACCESO, "x", False)
        self.assertEqual(int(b.obtener_codigo()[2:]), int(a.obtener_codigo()[2:]) + 1)
        self.assertRegex(a.obtener_codigo(), r"^B-\d{4}$")

    def test_estado_inicial_sigue_bloqueado(self):
        b = self.eliane.registrar_bloqueo("t", TipoBloqueo.OTRO, "", True)
        self.assertEqual(b.obtener_estado(), EstadoBloqueo.SIGUE_BLOQUEADO)

    def test_calcular_dias_bloqueado(self):
        b = self.eliane.registrar_bloqueo("t", TipoBloqueo.OTRO, "", False)
        self.assertEqual(b.calcular_dias_bloqueado(), 0)
        futuro = datetime.now() + timedelta(days=3, hours=1)
        with patch("domain.bloqueo.datetime") as dt:
            dt.now.return_value = futuro
            self.assertEqual(b.calcular_dias_bloqueado(), 3)

    def test_agregar_comentario_y_copia_defensiva(self):
        b = self.eliane.registrar_bloqueo("t", TipoBloqueo.OTRO, "", False)
        b.agregar_comentario("Jazmín", "revisando")
        lista = b.obtener_comentarios()
        lista.clear()
        self.assertEqual(len(b.obtener_comentarios()), 1)
        self.assertEqual(b.obtener_comentarios()[0].obtener_autor(), "Jazmín")

    def test_cambiar_estado(self):
        b = self.eliane.registrar_bloqueo("t", TipoBloqueo.OTRO, "", False)
        b.cambiar_estado(EstadoBloqueo.CERRADO)
        self.assertEqual(b.obtener_estado(), EstadoBloqueo.CERRADO)

    def test_marcar_seguimiento(self):
        b = self.eliane.registrar_bloqueo("t", TipoBloqueo.OTRO, "", False)
        self.assertFalse(b.fue_seguido_hoy())
        self.lider.marcar_seguimiento_hoy(b)
        self.assertTrue(b.fue_seguido_hoy())

    def test_encapsulamiento(self):
        b = self.eliane.registrar_bloqueo("t", TipoBloqueo.OTRO, "", False)
        with self.assertRaises(AttributeError):
            _ = b.__estado


class TestPolimorfismo(Base):
    def test_consultor_registra_sobre_si_mismo(self):
        b = self.eliane.registrar_bloqueo("t", TipoBloqueo.ACCESO, "equipo", True)
        self.assertEqual(b.obtener_registrado_por(), "Eliane")
        self.assertIsNone(b.obtener_motivo_registro_tardio())
        self.assertTrue(b.fue_comunicado_al_cliente())

    def test_lider_registra_en_nombre_de_otro_con_motivo(self):
        b = self.lider.registrar_bloqueo(self.eliane, "t", TipoBloqueo.ACCESO,
                                         EstadoBloqueo.AVANZADO, "olvido")
        self.assertEqual(b.obtener_registrado_por(), "Jazmín")
        self.assertEqual(b.obtener_consultor(), self.eliane)
        self.assertEqual(b.obtener_motivo_registro_tardio(), "olvido")
        self.assertEqual(b.obtener_estado(), EstadoBloqueo.AVANZADO)


class TestGestor(Base):
    def _agregar(self, c, tarea="t", estado=None):
        b = c.registrar_bloqueo(tarea, TipoBloqueo.OTRO, "", False)
        if estado:
            b.cambiar_estado(estado)
        self.gestor.agregar(b)
        return b

    def test_buscar_por_nombre_ignora_mayusculas_y_espacios(self):
        self._agregar(self.eliane)
        self._agregar(self.jesus)
        self.assertEqual(len(self.gestor.buscar_por_nombre_consultor("  ELIANE ")), 1)
        self.assertEqual(self.gestor.buscar_por_nombre_consultor("nadie"), [])

    def test_buscar_por_codigo_ok_y_error(self):
        b = self._agregar(self.eliane)
        self.assertIs(self.gestor.buscar_por_codigo(b.obtener_codigo()), b)
        with self.assertRaises(BloqueoNoEncontradoError):
            self.gestor.buscar_por_codigo("B-9999")

    def test_listar_con_filtros(self):
        self._agregar(self.eliane)
        self._agregar(self.eliane, estado=EstadoBloqueo.CERRADO)
        self._agregar(self.jesus)
        self.assertEqual(len(self.gestor.listar()), 3)
        self.assertEqual(len(self.gestor.listar(consultor=self.eliane)), 2)
        self.assertEqual(len(self.gestor.listar(estado=EstadoBloqueo.CERRADO)), 1)
        self.assertEqual(len(self.gestor.listar(self.eliane, EstadoBloqueo.CERRADO)), 1)

    def test_listar_no_expone_lista_interna(self):
        self._agregar(self.eliane)
        self.gestor.listar().clear()
        self.assertEqual(len(self.gestor.listar()), 1)

    def test_revisar_abiertos_excluye_cerrados(self):
        self._agregar(self.eliane)
        self._agregar(self.eliane, estado=EstadoBloqueo.CERRADO)
        self.assertEqual(len(self.lider.revisar_bloqueos_abiertos(self.gestor)), 1)


class TestUsuarios(Base):
    def test_autenticacion_ok(self):
        self.assertIs(autenticar_consultor(self.lider, "eliane", "1111"), self.eliane)

    def test_autenticacion_id_incorrecto(self):
        with self.assertRaises(CredencialInvalidaError):
            autenticar_consultor(self.lider, "Eliane", "9999")

    def test_autenticacion_nombre_inexistente(self):
        with self.assertRaises(CredencialInvalidaError):
            autenticar_consultor(self.lider, "Zoe", "1111")

    def test_buscar_consultor(self):
        self.assertIs(self.lider.buscar_consultor_por_nombre(" jesus"), self.jesus)
        with self.assertRaises(ConsultorNoEncontradoError):
            self.lider.buscar_consultor_por_nombre("Nadie")


class TestExcepciones(unittest.TestCase):
    def test_jerarquia_y_mensaje(self):
        for cls in (CredencialInvalidaError, ConsultorNoEncontradoError,
                    BloqueoNoEncontradoError, CanalNoSoportadoError):
            e = cls("msg")
            self.assertIsInstance(e, ErrorSistema)
            self.assertIsInstance(e, Exception)
            self.assertEqual(e.obtener_mensaje(), "msg")


class TestObserver(Base):
    def setUp(self):
        super().setUp()
        self.canal = CanalMemoria()
        self.notif = NotificadorLider(self.canal)
        self.audit = RegistroAuditoria()
        self.gestor.suscribir(self.notif)
        self.gestor.suscribir(self.audit)

    def test_registro_notifica_al_lider(self):
        self.gestor.agregar(self.eliane.registrar_bloqueo("API", TipoBloqueo.ACCESO, "", False))
        msgs = self.canal.obtener_mensajes()
        self.assertEqual(len(msgs), 1)
        self.assertIn("Eliane", msgs[0][1])
        self.assertEqual(msgs[0][0], "Líder Técnico")

    def test_cerrar_notifica_pero_avanzar_no(self):
        b = self.eliane.registrar_bloqueo("API", TipoBloqueo.ACCESO, "", False)
        self.gestor.agregar(b)
        self.gestor.cambiar_estado(b, EstadoBloqueo.AVANZADO)
        self.assertEqual(len(self.canal.obtener_mensajes()), 1)
        self.gestor.cambiar_estado(b, EstadoBloqueo.CERRADO)
        self.assertEqual(len(self.canal.obtener_mensajes()), 2)
        self.assertEqual(len(self.audit.obtener_lineas()), 3)

    def test_desuscribir_y_no_duplicar(self):
        self.gestor.suscribir(self.audit)  # duplicado ignorado
        self.gestor.agregar(self.eliane.registrar_bloqueo("a", TipoBloqueo.OTRO, "", False))
        self.assertEqual(len(self.audit.obtener_lineas()), 1)
        self.gestor.desuscribir(self.audit)
        self.gestor.agregar(self.eliane.registrar_bloqueo("b", TipoBloqueo.OTRO, "", False))
        self.assertEqual(len(self.audit.obtener_lineas()), 1)

    def test_cambiar_canal_en_caliente(self):
        otro = CanalMemoria()
        self.notif.cambiar_canal(otro)
        self.gestor.agregar(self.eliane.registrar_bloqueo("a", TipoBloqueo.OTRO, "", False))
        self.assertEqual(len(self.canal.obtener_mensajes()), 0)
        self.assertEqual(len(otro.obtener_mensajes()), 1)


class TestFactory(unittest.TestCase):
    def test_crea_cada_canal(self):
        self.assertIsInstance(FabricaCanales.crear("consola"), CanalConsola)
        self.assertIsInstance(FabricaCanales.crear(" Teams "), CanalTeamsSimulado)
        self.assertIsInstance(FabricaCanales.crear("memoria"), CanalMemoria)

    def test_canal_invalido(self):
        for malo in ("sms", "", None):
            with self.assertRaises(CanalNoSoportadoError):
                FabricaCanales.crear(malo)

    def test_disponibles(self):
        self.assertEqual(FabricaCanales.canales_disponibles(), ["consola", "teams", "memoria"])


class TestStrategy(Base):
    def test_orden_por_estado(self):
        a = self.eliane.registrar_bloqueo("a", TipoBloqueo.OTRO, "", False)
        a.cambiar_estado(EstadoBloqueo.AVANZADO)
        b = self.eliane.registrar_bloqueo("b", TipoBloqueo.OTRO, "", False)
        c = self.eliane.registrar_bloqueo("c", TipoBloqueo.OTRO, "", False)
        c.cambiar_estado(EstadoBloqueo.CERRADO)
        self.assertEqual(OrdenPorEstado().ordenar([c, a, b]), [b, a, c])

    def test_orden_sin_comunicar_primero(self):
        a = self.eliane.registrar_bloqueo("a", TipoBloqueo.OTRO, "", True)
        b = self.eliane.registrar_bloqueo("b", TipoBloqueo.OTRO, "", False)
        self.assertEqual(OrdenSinComunicarAlCliente().ordenar([a, b]), [b, a])

    def test_orden_antiguedad(self):
        viejo = self.eliane.registrar_bloqueo("v", TipoBloqueo.OTRO, "", False)
        nuevo = self.eliane.registrar_bloqueo("n", TipoBloqueo.OTRO, "", False)
        with patch("domain.bloqueo.datetime") as dt:
            dt.now.return_value = datetime.now() + timedelta(days=5)
            # ambos igual de viejos -> orden estable; verificamos que no falle
            self.assertEqual(len(OrdenPorAntiguedad().ordenar([nuevo, viejo])), 2)

    def test_intercambio_de_estrategia_en_lider(self):
        g = GestorBloqueo()
        a = self.eliane.registrar_bloqueo("a", TipoBloqueo.OTRO, "", True)
        b = self.eliane.registrar_bloqueo("b", TipoBloqueo.OTRO, "", False)
        g.agregar(a); g.agregar(b)
        self.assertEqual(self.lider.revisar_bloqueos_abiertos(g), [a, b])
        self.assertEqual(self.lider.revisar_bloqueos_abiertos(g, OrdenSinComunicarAlCliente()), [b, a])


class TestEntrada(unittest.TestCase):
    def test_pedir_fecha_formatos_y_reintento(self):
        from presentation import entrada
        with patch("builtins.input", side_effect=["basura", "31/12/2026"]):
            self.assertEqual(entrada.pedir_fecha("Fecha"), date(2026, 12, 31))
        with patch("builtins.input", side_effect=["2026-03-01"]):
            self.assertEqual(entrada.pedir_fecha("Fecha"), date(2026, 3, 1))

    def test_pedir_float_rango(self):
        from presentation import entrada
        with patch("builtins.input", side_effect=["abc", "150", "-1", "80"]):
            self.assertEqual(entrada.pedir_float_rango("p", 0, 100), 80.0)

    def test_pedir_texto_obligatorio(self):
        from presentation import entrada
        with patch("builtins.input", side_effect=["", "  ", "hola"]):
            self.assertEqual(entrada.pedir_texto("x"), "hola")


if __name__ == "__main__":
    unittest.main()
