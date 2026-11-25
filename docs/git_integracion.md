# Preparación local de integración

Base confirmada para revisión: dd73e113904a890313e0bb6b3c76440017ac9526.
Es ancestro común de las dos ramas publicadas al inspeccionarlas el 24/11/2026:

- feature/I-01-inventario: dd73e113904a890313e0bb6b3c76440017ac9526.
- feature/I-02-exploracion-encovi: 313796ce178fa7a2694945d9010acad5e04cb6e8.

I-02 conserva el commit anterior y añade el plan Markdown y gitignore vacío.
No hay scripts de exploración en ese snapshot. El clon de inspección y las
referencias remotas locales preservan los commits originales.

Se preparó main local en dd73e11, sin publicar ni mover ramas remotas, sin cambiar
la rama predeterminada y sin fusionar I-02. La predeterminada remota observada
sigue siendo feature/I-01-inventario. Las tareas se conservan en ramas de trabajo.

No se borran archivos raw ya rastreados ni se reescribe historia. El gitignore
previene nuevas descargas accidentales; no elimina los binarios ya versionados.
Publicar main, cambiar la predeterminada, crear PR o integrar requieren la
autorización del usuario. No ejecutar esas operaciones como parte de reproducir.
