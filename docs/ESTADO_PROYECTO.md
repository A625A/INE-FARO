# Estado verificado — INE FARO

El estado de la integración final y la demostración están en [M-05](M05_IMPLEMENTACION.md).

Actualizado 25/11/2026 (Guatemala). Estado local; no implica publicación ni merge
de los cambios posteriores al último push.

| Tarea | Estado | Evidencia / dependencia |
|---|---|---|
| I-01 | Corregido localmente | F2 en `docs/fuentes.csv` apunta a `data/raw/encovi_2023/Guia-para-el-uso-de-bases-de-datos_v_final.pdf` |
| I-02 | Validado localmente | Notebook ejecutado, diccionario reconciliado, `PPA03`, `FORMAL_INFORMAL`, `POBREZA`, `NO_HOGAR`, `FACTOR`, `Factor2` y `Factor3` verificados; 70.305% reproducido; CV/CI declarados |
| I-03 | Documentado y pusheado, con actualización local pendiente | Commit `585f674` en `origin/main`; `docs/metodologia.md` e `docs/indicadores_objetivo.csv` actualizados después con resultados I-02 |
| I-04 | Validada localmente | CSV, script, metadatos y evidencia; lista para M-03 cuando M-01 esté integrada |
| I-05 | Auditada localmente | transversal separada viable; crecimiento/altas/formalización excluidos |
| I-06 | Opcional, sin implementación verificada | Gini e ingresos derivados siguen sin acreditar en I-02 |
| M-01 a M-06 | Pendientes | faltan archivos de indicadores, matriz, radar y UI Streamlit |
| F-01 a F-05 | Pendientes | integración, pruebas de app, entrega y presentación |

Decisiones del usuario: sector informal según definición oficial ENCOVI como
indicador principal territorial. La especificación v1.1 incorpora ENEIC IV-2025 para empleo e ingresos. ENIGH queda fuera del MVP.
DINESE no bloquea el núcleo. No se toma el aumento de registros por crecimiento.

Resultados I-02 ya utilizables: informalidad nacional 70.305% con `FACTOR`
(`n=17,523`, CV 0.97%), urbana 61.3329%, rural 83.0248%; pobreza total 56.0413%
y extrema 16.2366% con `Factor3` (`n=10,930`, CV 1.45% y 4.22%). De 66
estimaciones departamentales con aproximación `DEPTO`/`UPM`, 61 son
`publicable_con_reserva` y cinco de pobreza extrema son `no_publicable`.
La diferencia máxima frente a la tabla oficial de pobreza departamental es 0.05
puntos porcentuales.

Pendientes científicos menores: descargar los PDF de F8 al repositorio, recuperar
una tasa de respuesta documental y guardar localmente la nota conceptual de la
OIT. Ninguno modifica los valores calculados. El 49.4% del perfil nacional se
explica como departamento `01 Guatemala` (49.42%), no como total nacional.

Dependencias: `requirements.txt` ampliado con numpy, pandas, pyreadstat, Jupyter,
nbconvert y pypdf para reproducir el notebook y la lectura de PDFs. Streamlit se
agregará cuando se implemente M-05.

Registro: `585f674 feat(I-03): documentar metodologia e indicadores objetivo`
fue pusheado a `origin/main` con `git fetch --all --prune` sin divergencia.
Los cambios de esta sesión posterior al push siguen sin commitear.

Verificación local: `python -m pytest -q` terminó con 19 pruebas en verde y
`python -m compileall -q scripts tests` sin errores; `git diff --check` solo avisa
sobre conversión LF→CRLF, sin conflictos.

Comandos y salidas: README, `docs/metodologia.md`, `docs/diccionario_encovi.csv`,
`docs/indicadores_objetivo.csv`, `docs/fuentes.csv` y `docs/evidencia/`. Los
documentos del ZIP no reemplazan por sí solos el estado de implementación.
