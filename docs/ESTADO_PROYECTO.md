# Estado verificado — INE FARO

Actualizado 24/11/2026 (Guatemala). Estado local; no implica publicación ni merge.

| Tarea | Estado | Evidencia / dependencia |
|---|---|---|
| I-01 | Entrega remota parcial | dd73e11: datos e inventario; faltan detalles de procedencia en inventario original |
| I-02 | Sin exploración publicada | 313796c añade plan y gitignore vacío; se conserva su rama |
| I-03 | Pendiente | pesos/universo/precisión y validación del 70.3% antes de usar informalidad |
| I-04 | Validada localmente | CSV, script, metadatos y evidencia; lista para M-03 cuando M-01 esté validada |
| I-05 | Auditada localmente | transversal separada viable; crecimiento/altas/formalización excluidos |
| I-06 | Opcional, sin implementación verificada | variables adicionales dentro de ENCOVI |
| M-01 a M-06 | Pendientes | no se generaron indicadores ENCOVI, matriz, radar ni UI |
| F-01 a F-05 | Pendientes | integración, pruebas de app, entrega y presentación |

Decisiones del usuario: sector informal según definición oficial ENCOVI como
indicador principal; main como integración futura. ENEIC y ENIGH fuera del MVP.
DINESE no bloquea el núcleo. No se toma el aumento de registros por crecimiento.

Antes de publicar estadísticas ENCOVI: validar FORMAL_INFORMAL, universo de
ocupados, edad, denominador, FACTOR y diseño; intentar reproducir 70.3% nacional;
investigar cualquier discrepancia y evaluar precisión departamental. Esta sesión
no utiliza esa tasa como resultado calculado del proyecto.

Comandos y salidas: README, metadata_pib.md, viabilidad_dinese.md y evidencia/.
Los documentos del ZIP no reemplazan por sí solos el estado de implementación.
