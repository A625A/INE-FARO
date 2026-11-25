# Validación y code-review de I-04 / I-05

Base de revisión confirmada por el usuario: dd73e11. Especificación:
`docs/specs/I-04-I-05.md`. Dos revisores independientes, ejes Standards y Spec.

## Standards

Se encontró un P2: el proceso normal aceptaba un archivo de hash distinto y sólo
registraba la discordancia. Infringía procedencia acreditada/insumos fijados.
Corregido: ambos comandos exigen coincidencia de SHA-256 antes de procesar, con o
sin descarga. El revisor repitió pruebas dirigidas: 16 pasaron, 3 deseleccionadas.
No encontró incumplimientos nuevos ni smells que justificaran refactorización.
**Resultado: 1 hallazgo corregido; 0 pendientes.**

## Spec

Se reprodujo el mismo P2 cambiando sólo Guatemala 2023 per cápita a 1. El comando
antes lo publicaba; ahora rechaza el snapshot y no crea salidas. El revisor repitió
el experimento y seis pruebas pertinentes. Las unidades, VAB/PIB, Extrarregional,
volúmenes y exclusión del crecimiento DINESE cumplen la especificación.
**Resultado: 1 hallazgo corregido; 0 pendientes.**

## Pruebas y reproducción

- Rojo inicial de cada CLI por inexistencia; verde después de implementación.
- Rojo/verde para rechazo de sección desconocida y protección de descarga.
- Rojo/verde de la regresión per cápita manipulado sin descarga.
- Suite inicial: 17 passed en 54.44 s.
- Suite posterior a corrección: **19 passed en 55.27 s** (`python -m pytest -q`).
- `python -m compileall -q scripts tests` y `git diff --check`: sin errores.
- Rama I-04 corregida, en worktree separado: 9 pruebas PIB pasaron.
- Descarga limpia Banguat mediante el CLI: hashes acreditados y tres CSV
  idénticos byte por byte a los entregados.
- Auditoría completa de 1070895 registros DINESE: controles nacionales y Guatemala
  de ambos años conciliados; sin descartes ni códigos duplicados dentro de año.
- Cinco descargas oficiales independientes coinciden con los hashes del equipo.

No hay verificador estático de tipos configurado. No se afirma validación de una
app ni cálculo de indicadores ENCOVI, que no pertenecen a esta entrega.

## Revisión crítica Grill Me

Se revisaron definición de informalidad, correspondencia territorial/sectorial,
unidades, no aditividad, comparabilidad administrativa, inferencias causales y
estado de Git. Q1/Q2 están resueltas. El límite temporal de DINESE se maneja con
la exclusión ya autorizada. No surgieron decisiones científicas esenciales nuevas.
Los cambios concurrentes del equipo se inspeccionaron sin integrarlos; las
precauciones para ENCOVI están en `docs/revision_integracion_encovi.md`.

Publicación, PR, merges y cambio de predeterminada continúan sin autorización y
no se ejecutaron. Los resultados son locales y están preparados para revisión.
