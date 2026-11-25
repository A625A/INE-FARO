"""Convenciones compartidas de las dos fuentes departamentales."""

import csv
import hashlib
import json
import tempfile
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPARTAMENTOS = dict(enumerate([
    'Guatemala', 'El Progreso', 'Sacatepéquez', 'Chimaltenango', 'Escuintla',
    'Santa Rosa', 'Sololá', 'Totonicapán', 'Quetzaltenango', 'Suchitepéquez',
    'Retalhuleu', 'San Marcos', 'Huehuetenango', 'Quiché', 'Baja Verapaz',
    'Alta Verapaz', 'Petén', 'Izabal', 'Zacapa', 'Chiquimula', 'Jalapa', 'Jutiapa',
], 1))


def normalizar(texto):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFD', str(texto))
                           if not unicodedata.combining(c)).casefold().split())


def codigo_departamento(nombre):
    for codigo, canonico in DEPARTAMENTOS.items():
        if normalizar(nombre) == normalizar(canonico):
            return f'{codigo:02}'
    raise ValueError(f'Departamento desconocido: {nombre!r}')


SECCIONES_CIIU = dict(zip('ABCDEFGHIJKLMNOPQRSTU', [
    'Agricultura, ganadería, silvicultura y pesca',
    'Explotación de minas y canteras', 'Industrias manufactureras',
    'Suministro de electricidad, gas, vapor y aire acondicionado',
    'Suministro de agua; evacuación de aguas residuales, gestión de desechos y descontaminación',
    'Construcción',
    'Comercio al por mayor y al por menor; reparación de vehículos automotores y motocicletas',
    'Transporte y almacenamiento', 'Actividades de alojamiento y de servicio de comidas',
    'Información y comunicaciones', 'Actividades financieras y de seguros',
    'Actividades inmobiliarias', 'Actividades profesionales, científicas y técnicas',
    'Actividades de servicios administrativos y de apoyo',
    'Administración pública y defensa; planes de seguridad social de afiliación obligatoria',
    'Enseñanza', 'Actividades de atención de la salud humana y de asistencia social',
    'Actividades artísticas, de entretenimiento y recreativas', 'Otras actividades de servicios',
    'Actividades de los hogares como empleadores; actividades no diferenciadas de los hogares como productores de bienes y servicios para uso propio',
    'Actividades de organizaciones y órganos extraterritoriales',
]))


def procedencia(path):
    fuentes = json.loads((ROOT / 'data/reference/fuentes_I04_I05.json').read_text())
    fuente = next(f for f in fuentes if Path(f['path']).name == path.name)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {**fuente, 'sha256': digest, 'bytes': path.stat().st_size,
            'coincide_snapshot': digest == fuente['sha256']}


def descargar_fuentes(grupo, destino):
    fuentes = json.loads((ROOT / 'data/reference/fuentes_I04_I05.json').read_text())
    for fuente in fuentes:
        if Path(fuente['path']).parent.name != grupo:
            continue
        path = destino / Path(fuente['path']).name
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest() != fuente['sha256']:
                raise ValueError(f'SHA-256 distinto; no se sobrescribe {path.name}')
            continue
        destino.mkdir(parents=True, exist_ok=True)
        temporal = None
        try:
            request = urllib.request.Request(fuente['url'], headers={'User-Agent': 'INE-FARO/1.0'})
            with tempfile.NamedTemporaryFile(dir=destino, delete=False) as file:
                temporal = Path(file.name)
                with urllib.request.urlopen(request, timeout=90) as response:
                    while bloque := response.read(1024 * 1024):
                        file.write(bloque)
            if hashlib.sha256(temporal.read_bytes()).hexdigest() != fuente['sha256']:
                raise ValueError(f'SHA-256 oficial cambió: {path.name}; revisar la nueva versión')
            temporal.replace(path)
        finally:
            if temporal is not None:
                temporal.unlink(missing_ok=True)


def escribir_csv(path, filas, columnas):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporal = path.with_suffix('.csv.tmp')
    with temporal.open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columnas, lineterminator='\n')
        writer.writeheader()
        writer.writerows(filas)
    temporal.replace(path)


def escribir_json(path, contenido):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporal = path.with_suffix('.json.tmp')
    temporal.write_text(json.dumps(contenido, ensure_ascii=False, indent=2,
                                  allow_nan=False) + '\n')
    temporal.replace(path)
