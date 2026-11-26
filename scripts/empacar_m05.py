"""Empaca la demo pública con archivos regulares, incluso para Windows."""
import argparse
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

if __name__ == '__main__' and not __package__:
    raise SystemExit('Ejecuta desde la raíz: python -m scripts.empacar_m05 --output faro-m05.zip')

from dashboard_data import cargar_eneic, cargar_hogares, cargar_matriz, cargar_vab
from dashboard_radar import validar_radar
from scripts.radar_rules.export import serialize

ROOT = Path(__file__).resolve().parents[1]
PROCESADOS = 'data/processed'
RADAR = ('hallazgos.csv', 'hallazgos.json', 'radar_fuentes.json')
FECHA_ZIP = (2026, 11, 25, 0, 0, 0)
ARCHIVOS = (
    'app.py', 'dashboard_data.py', 'dashboard_empleo.py', 'dashboard_metodologia.py',
    'dashboard_precision.py', 'dashboard_produccion.py', 'dashboard_radar.py',
    'dashboard_radar_ui.py', 'dashboard_territorio.py', 'dashboard_ui.py', 'dashboard_utils.py',
    '.streamlit/config.toml', '.superdesign/design-system.md', 'README.md', 'requirements.txt',
    'static/faro.css', 'static/ine-horizontal-rgb.png', 'static/UbuntuSans.ttf', 'static/UbuntuSans-LICENSE.txt',
    'docs/M05_IMPLEMENTACION.md', 'docs/ENEIC_CONTRATO_M05.md', 'docs/M03_CONTRATO_MATRIZ.md',
    'docs/VAB_CONTRATO_M05.md', 'docs/hallazgos_hogares.md', 'docs/reglas_radar.md',
    'docs/evaluation/m05_final/INFORME.md', 'docs/evaluation/m05_final/HANDOFF_M06.md',
    'docs/fuentes.csv', 'docs/caso_demostracion.md', 'docs/guion_demo.md',
    'docs/ESTADO_PROYECTO.md', 'docs/M01_IMPLEMENTACION.md', 'docs/revision_final.md',
    'docs/checklist_entrega.md', 'docs/evaluation/radar_evaluation.md', 'presentacion.pdf',
    'docs/evidencia/M-05/final/01-empleo.png', 'docs/evidencia/M-05/final/02-territorio.png',
    'docs/evidencia/M-05/final/07-calidad.png', 'docs/evidencia/M-05/final/08-contraste-r1.png',
    'scripts/comun.py', 'scripts/radar_rules/__init__.py', 'scripts/radar_rules/export.py',
    'scripts/radar_rules/inputs.py', 'scripts/radar_rules/r1.py', 'scripts/radar_rules/r2.py',
    'scripts/radar_rules/r3.py', 'scripts/radar_rules/r4.py', 'scripts/radar_rules/evidence.py',
    'data/reference/departamentos_m05.geojson',
)
AGREGADOS = ('eneic_iv_2025/agregados_publicos.csv', 'matriz_departamental.csv',
             'perfiles_hogares.csv', 'vab_informal_nacional.csv', 'vab_informal_grupo.csv')


def leer_generacion(procesados):
    almacen = procesados / '.radar_m04'
    puntero = almacen / 'actual'
    generacion = puntero.resolve(strict=True) if puntero.is_symlink() else procesados.resolve()
    if puntero.is_file() and not puntero.is_symlink():
        # Git para Windows materializa el destino como texto con core.symlinks=false.
        nombre = puntero.read_text(encoding='ascii')
        if len(nombre) != 64 or any(c not in '0123456789abcdef' for c in nombre):
            raise ValueError('Puntero de generación M-04 inválido.')
        generacion = (almacen / nombre).resolve(strict=True)
    if (puntero.is_symlink() or puntero.is_file()) and generacion.parent != almacen.resolve():
        raise ValueError('El puntero M-04 debe apuntar a una generación local.')
    archivos = {}
    for nombre in RADAR:
        ruta = generacion / nombre
        if ruta.is_symlink():
            raise ValueError('La generación M-04 debe contener archivos regulares.')
        archivos[nombre] = ruta.read_bytes()
    datos = json.loads(archivos['hallazgos.json'])
    if validar_radar(datos)['rechazados']:
        raise ValueError('Se encontraron fichas no aptas en la generación M-04.')
    manifiesto = json.loads(archivos['radar_fuentes.json'])
    huellas = manifiesto.get('archivos_brutos') if isinstance(manifiesto, dict) else None
    if not isinstance(huellas, dict) or serialize(datos, huellas) != archivos:
        raise ValueError('El JSON, CSV y manifiesto no corresponden a la misma salida M-04.')
    if generacion != procesados.resolve():
        digest = sha256()
        for nombre, contenido in sorted(archivos.items()):
            digest.update(nombre.encode() + b'\0' + sha256(contenido).digest())
        if digest.hexdigest() != generacion.name:
            raise ValueError('La huella de generación M-04 no coincide.')
    return archivos


def agregados_publicos(contenido):
    """Comprueba los mismos bytes que se incorporarán al ZIP."""
    with TemporaryDirectory(prefix='faro-m05-') as directorio:
        procesados = Path(directorio)
        for nombre in AGREGADOS:
            ruta = procesados / nombre
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_bytes(contenido[f'{PROCESADOS}/{nombre}'])
        cargar_eneic(procesados)
        cargar_vab(procesados)
        _, encovi = cargar_matriz(procesados)
        hogares = cargar_hogares(procesados)

    def filas(nombre):
        texto = contenido[f'{PROCESADOS}/{nombre}'].decode('utf-8')
        return list(csv.DictReader(io.StringIO(texto)))

    matriz = {f['depto_id']: f for f in filas('matriz_departamental.csv')}
    for r in encovi[encovi.estado.eq('no_publicable')].itertuples():
        raw = matriz[r.depto_id]
        if any(raw[f'{r.indicador}_{campo}_2023'] for campo in ('valor', 'ic95_inf', 'ic95_sup')):
            raise ValueError('M-03: la copia contiene valores restringidos.')
    for r, raw in zip(hogares.itertuples(), filas('perfiles_hogares.csv')):
        if r.estado == 'no_publicable' and (raw['valor'] or raw['cv']):
            raise ValueError('M-02: la copia contiene valores restringidos.')


def empacar(salida, raiz=ROOT):
    radar = leer_generacion(raiz / PROCESADOS)
    contenido = {f'{PROCESADOS}/{nombre}': datos for nombre, datos in radar.items()}
    for nombre in (*ARCHIVOS, *(f'{PROCESADOS}/{p}' for p in AGREGADOS)):
        contenido[nombre] = (raiz / nombre).read_bytes()
    agregados_publicos(contenido)
    # Un empaquetado interrumpido se elimina. Un archivo previo se conserva.
    with salida.open('xb') as destino:
        try:
            with ZipFile(destino, 'w') as archivo:
                for nombre, datos in sorted(contenido.items()):
                    entrada = ZipInfo(nombre, date_time=FECHA_ZIP)
                    entrada.create_system = 3
                    entrada.external_attr = 0o100644 << 16
                    archivo.writestr(entrada, datos, compress_type=ZIP_DEFLATED, compresslevel=9)
        except BaseException:
            destino.close()
            salida.unlink()
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        empacar(args.output)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'No se pudo empacar M-05: {exc}\n')
    print(args.output)
