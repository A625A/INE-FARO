# INE FARO

Prototipo del Datatón INE Guatemala 2026 para investigar contrastes territoriales
entre ocupación en el sector informal, condiciones de vida y producción.

Esta entrega implementa **I-04 (PIB Banguat)** e **I-05 (auditoría DINESE)**.
Todavía no hay app, indicadores ENCOVI calculados ni radar. Esta sesión preparó main
localmente y no publicó ramas ni integró trabajo remoto. Al cierre aparecieron
main/master remotos por cambios concurrentes del equipo; ver docs/git_integracion.md.

## Instalar y reproducir

Python 3.10 o superior. Desde la raíz del repositorio:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/procesar_pib.py
python scripts/auditar_dinese.py
python -m pytest -q
```

Las ejecuciones sin `--download` funcionan sin red con los XLSX originales de
`data/raw/banguat/` y `data/raw/dinese/`. No requieren credenciales ni nube.
Si faltan, añadir `--download` a cada comando: usa las URL oficiales fijadas en
`data/reference/fuentes_I04_I05.json` y verifica SHA-256. No sobrescribe archivos
existentes distintos ni acepta automáticamente una revisión oficial nueva.
Los binarios ya rastreados se conservan; nuevas descargas quedan ignoradas.

Los comandos admiten `--input-dir`, `--output-dir` y `--evidence-dir`.
El SHA-256 se exige también sin descarga. Una versión nueva requiere revisar
fuentes y controles y actualizar el manifiesto. `--manifest` permite seleccionar
un manifiesto alternativo ya revisado; no valida por sí mismo su origen oficial.
PIB admite `--year` entre 2013 y 2024, por defecto 2023. Al probar otro año usar
otro directorio para conservar los CSV 2023 destinados a ENCOVI.
Cada tarea valida sus insumos completos antes de escribir. Si una ejecución
falla, no usar las salidas de una ejecución previa como si fueran nuevas.

## Resultados y contratos

- `data/processed/pib_departamental.csv`: 22 departamentos, PIB total, 17 grupos
  de valor agregado e impuestos; corrientes y volumen encadenado separados.
- `data/processed/pib_per_capita.csv`: producción por habitante en quetzales.
- `data/processed/pib_conciliacion.csv`: nacional y Extrarregional, fuera del mapa.
- `data/processed/dinese_resumen.csv`: conteos por año/departamento/sección/movimiento.
  Sólo uso descriptivo transversal; crecimiento excluido del radar.
- `docs/evidencia/`: hashes, controles, procedencia y revisión de fuentes oficiales.

Consultar [metadatos PIB](docs/metadata_pib.md), [dictamen DINESE](docs/viabilidad_dinese.md),
[contratos](docs/CONTRATOS_DE_DATOS.md), [especificación](docs/specs/I-04-I-05.md),
[estado](docs/ESTADO_PROYECTO.md) y [preparación Git](docs/git_integracion.md).

Los tests ejercitan los comandos completos con controles oficiales y copias
deliberadamente inválidas. No hay un verificador de tipos configurado; se comprueba
la sintaxis con `python -m compileall -q scripts tests` además de las pruebas.

## Cautelas científicas

PIB no es ingreso ni consumo de hogares. No sumar medidas distintas ni exigir
aditividad a volúmenes encadenados. Las empresas DINESE no son personas ocupadas;
un aumento de registros no prueba creación empresarial ni formalización laboral.

La definición principal acordada es proporción de población ocupada en el sector
informal según ENCOVI 2023. I-02/I-03/M-01 deben verificar universo, denominador,
códigos, pesos y precisión, e intentar reproducir 70.3% nacional antes de usarla.

Fuentes: [Banguat](https://banguat.gob.gt/page/cuadros-estadisticos-por-departamento-2013-2024),
[DINESE](https://datos.ine.gob.gt/dataset/directorio-nacional-estadistico-de-empresas-dinese),
ENCOVI INE. Licencias y condiciones pertenecen a cada fuente; no se presume una
licencia común para todo el repositorio. DINESE declara Creative Commons Attribution.

No hacer push, PR, merges ni cambiar la rama predeterminada sin autorización.
