# Sistema de Seguimiento de Bloqueos

Trabajo final IS275 — Fundamentos de Programación 2 (UPC). Ver `PROPUESTA.md` para el
planteamiento del problema, `HISTORIAS_USUARIO.md` para el backlog (9 historias, con
criterios de aceptación) y `diagrama_clases.modelio` para el modelo UML.

## Ejecutar

```
python main.py
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
servicios/      GestorBloqueo (centraliza la colección) y Notificador (simulado)
presentation/   El CLI: selección de rol, menú de Consultor y menú de Líder Técnico
main.py         Arranca todo y crea los datos de prueba
```

No se usan interfaces ni patrones de diseño en este código — esa parte queda para el
TB2. La separación en capas ya deja el terreno listo para agregarlos después sin
reescribir el dominio.

## Historias de usuario cubiertas

- **Consultor**: HU-01 (registrar bloqueo), HU-02 (ver mis bloqueos, con días
  bloqueado calculados automáticamente y comentarios)
- **Líder técnico**: HU-03 (registrar consultor) a HU-08 (marcar seguimiento hoy)
- **Transversal**: HU-09 (selección de rol al iniciar)

## Excepciones controladas

`CredencialInvalidaError`, `ConsultorNoEncontradoError`, `BloqueoNoEncontradoError` —
todas heredan de `ErrorSistema` (que a su vez hereda de `Exception`), tal como se
modeló en el diagrama de clases.
