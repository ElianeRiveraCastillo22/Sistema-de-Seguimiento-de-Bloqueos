# Sistema de Seguimiento de Bloqueos

Trabajo final IS275 — Fundamentos de Programación 2 (UPC).
## Ejecutar

```
python3 main.py
```

No requiere dependencias externas (solo librería estándar de Python).

Al arrancar, el programa crea dos consultores de prueba para que puedas entrar de
inmediato sin registrar nada a mano:

| Nombre | ID |
|---|---|
| Eliane | 1111 |
| Jesus  | 2222 |

## Estructura (arquitectura en capas)

```
domain/         Entidades: Usuario, Consultor, LiderTecnico, Proyecto, Bloqueo,
                Comentario, enums (TipoBloqueo, EstadoBloqueo) y excepciones propias
servicios/      GestorBloqueo (Subject del Observer), canales.py (Factory),
                observadores.py (Observer), estrategias.py (Strategy)
tests/          Pruebas unitarias de los métodos de negocio (unittest)
presentation/   El CLI: selección de rol, menú de Consultor y menú de Líder Técnico
main.py         Arranca todo y crea los datos de prueba
```

## Patrones de diseño (TB2)

| Patrón | Dónde | Para qué |
|---|---|---|
| Observer | `servicios/observadores.py` + `GestorBloqueo.suscribir()` | Avisar al líder técnico cuando se registra o se cierra un bloqueo, sin que el menú sepa quién escucha |
| Strategy | `servicios/estrategias.py` | Cambiar el orden de la revisión (antigüedad, estado, sin comunicar al cliente) |
| Factory Method | `servicios/canales.py` (`FabricaCanales`) | Crear el canal de notificación (consola, Teams simulado, memoria) por nombre |

Las interfaces son clases abstractas (`abc.ABC`): `ObservadorBloqueo`, `EstrategiaOrden`
y `CanalNotificacion`.

## Pruebas

```
python3 -m unittest discover -s tests -t . -v
```

## Historias de usuario cubiertas

- **Consultor**: HU-01 (registrar bloqueo), HU-02 (ver mis bloqueos, con días
  bloqueado calculados automáticamente y comentarios)
- **Líder técnico**: HU-03 (registrar consultor) a HU-08 (marcar seguimiento hoy)
- **Transversal**: HU-09 (selección de rol al iniciar), HU-10 (notificar al líder
  automáticamente), HU-11 (ordenar la revisión), HU-12 (configurar canal)

## Excepciones controladas

`CredencialInvalidaError`, `ConsultorNoEncontradoError`, `BloqueoNoEncontradoError`,
`CanalNoSoportadoError` —
todas heredan de `ErrorSistema` (que a su vez hereda de `Exception`), tal como se
modeló en el diagrama de clases.
