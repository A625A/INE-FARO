"""Cotejo independiente de muestras de M-05 usando la biblioteca estándar."""
import csv
from collections import Counter
from decimal import Decimal as D
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'data/processed'


def filas(nombre):
    with (DATA / nombre).open(encoding='utf-8', newline='') as archivo:
        return list(csv.DictReader(archivo))


def comprobar(condicion, concepto):
    if not condicion:
        raise ValueError(f'Control no conciliado: {concepto}')


def evaluar():
    matriz = {r['depto_id']: r for r in filas('matriz_departamental.csv')}
    comprobar(len(matriz) == 22 and all(len(r) == 67 for r in matriz.values()), 'matriz')
    radar = json.loads((DATA / 'hallazgos.json').read_text(encoding='utf-8'))
    fichas = {r['id']: r for r in radar['hallazgos']}
    inform = {d: D(r['ocupacion_sector_informal_valor_2023']) for d, r in matriz.items()}
    pobreza = {d: D(r['pobreza_total_valor_2023']) for d, r in matriz.items()}
    pib = {d: D(r['pib_por_habitante_q_2023']) for d, r in matriz.items()}
    grupos = [k for k in matriz['01'] if k.startswith('participacion_') and 'predominante' not in k]
    vab = {d: D(r['vab_total_millones_q_2023']) for d, r in matriz.items()}

    def distancia(a, b):
        return sum(abs(D(matriz[a][c]) - D(matriz[b][c])) for c in grupos) / 2

    def magnitud(id_ficha, clave, esperado):
        publicado = D(str(fichas[id_ficha]['magnitudes'][clave]))
        comprobar(abs(publicado - esperado) <= D('1e-9'), f'{id_ficha} · {clave}')

    magnitud('R1:2023:04-16', 'brecha_informalidad_pp', abs(inform['04'] - inform['16']))
    magnitud('R1:2023:04-16', 'brecha_pobreza_pp', abs(pobreza['04'] - pobreza['16']))
    magnitud('R1:2023:04-16', 'razon_pib_por_habitante', max(pib['04'], pib['16']) / min(pib['04'], pib['16']))
    comprobacion_a = [d for d in matriz if pib[d] > median(pib.values()) and inform[d] > median(inform.values())]
    comprobar(len(comprobacion_a) == radar['conteos']['R2a'] == 0, 'R2a')
    magnitud('R2b:2023:06', 'exceso_p_pp', pobreza['06'] - median(pobreza.values()))
    magnitud('R2b:2023:06', 'exceso_y_q', pib['06'] - median(pib.values()))
    magnitud('R3:2023:04-18', 'distancia_pp', distancia('04', '18'))
    magnitud('R3:2023:04-18', 'brecha_informalidad_pp', abs(inform['04'] - inform['18']))
    distribucion = sorted(distancia(a, b) for a, b in combinations(matriz, 2))
    posicion = D('.25') * (len(distribucion) - 1)
    i = int(posicion)
    p25 = distribucion[i] + (posicion-i) * (distribucion[i+1] - distribucion[i])
    magnitud('R3:2023:04-18', 'umbral_distancia_pp', p25)
    base_a = 100 * sum(D(r['vab_a_millones_q_2023']) for r in matriz.values()) / sum(vab.values())
    local = D(matriz['16']['participacion_a_pct_2023'])
    magnitud('R4:2023:16:A', 'lq', local / base_a)
    magnitud('R4:2023:16:A', 'participacion_local_pct', local)

    conteos = Counter(r['regla'] for r in fichas.values())
    comprobar(dict(conteos, R2a=0) == radar['conteos'] == {'R1': 26, 'R2a': 0, 'R2b': 1, 'R3': 7, 'R4': 10}, 'fichas')
    escenarios = radar['sensibilidad']
    comprobar(len(escenarios) == 21, 'escenarios')
    for f in fichas.values():
        evaluados = [e for e in escenarios if e['regla'] == f['regla']]
        apariciones = sum(f['id'] not in e['desaparecen'] for e in evaluados)
        comprobar((apariciones, len(evaluados)) == (f['robustez']['presentes'], f['robustez']['escenarios']), f['id'])

    eneic = filas('eneic_iv_2025/agregados_publicos.csv')
    nacional = {r['indicador']: r for r in eneic if r['dimension'] == 'nacional'}
    esperados = {'peso_ocupados': 7944838, 'peso_informal': 5214094, 'tasa_sector_informal': D('65.6'), 'media_ingreso': 2842}
    comprobar(len(eneic) == 21 and all(D(nacional[k]['valor_oficial']) == v for k, v in esperados.items()), 'ENEIC')
    comprobar(round(D(nacional['media_ingreso']['cobertura_pct']), 2) == D('94.28'), 'cobertura de ingreso')

    nacional_vab = filas('vab_informal_nacional.csv')
    sectores = filas('vab_informal_grupo.csv')
    comprobar(len(nacional_vab) == 22 and len(sectores) == 374, 'granos del VAB')
    corte = next(r for r in nacional_vab if r['anio'] == '2023' and r['tipo_precio'] == 'corrientes')
    comercio = next(r for r in sectores if r['anio'] == '2023' and r['tipo_precio'] == 'corrientes' and r['grupo_ciiu'] == 'G')
    comprobar(round(100 * D(corte['vab_informal']) / D(corte['vab_total']), 2) == D('22.62'), 'VAB nacional')
    comprobar(round(100 * D(comercio['vab_informal']) / D(corte['vab_informal']), 2) == D('38.55'), 'comercio')
    comprobar('2020' not in {r['anio'] for r in nacional_vab}, 'discontinuidad 2020')

    encovi = filas('indicadores_encovi_2023.csv')
    hogares = filas('perfiles_hogares.csv')
    restringidas = [r for r in encovi if r['estado'] == 'no_publicable']
    restringidos = [r for r in hogares if r['estado'] == 'no_publicable']
    comprobar(len(encovi) == 66 and len(restringidas) == 5 and {r['indicador'] for r in restringidas} == {'pobreza_extrema'}, 'restricciones ENCOVI')
    comprobar(all(not matriz[r['depto_id']][f'pobreza_extrema_{c}_2023'] for r in restringidas
                  for c in ('valor', 'ic95_inf', 'ic95_sup')), 'supresión M-03')
    comprobar(len(hogares) == 207 and len(restringidos) == 14 and all(not r['valor'] for r in restringidos), 'supresión M-02')
    nombres = ('matriz_departamental.csv', 'indicadores_encovi_2023.csv', 'perfiles_hogares.csv',
               'eneic_iv_2025/agregados_publicos.csv', 'vab_informal_nacional.csv', 'vab_informal_grupo.csv', 'hallazgos.json')
    return {
        'controles': {'departamentos': 22, 'encovi': 66, 'encovi_restringidas': 5, 'hogares': 207,
                      'hogares_restringidos': 14, 'eneic': 21, 'vab_nacional': 22, 'vab_grupos': 374,
                      'radar': radar['conteos'], 'escenarios': len(escenarios)},
        'casos_recalculados': ['R1:2023:04-16', 'R2a: universo completo', 'R2b:2023:06', 'R3:2023:04-18', 'R4:2023:16:A'],
        'sha256': {n: sha256((DATA / n).read_bytes()).hexdigest() for n in nombres},
    }


if __name__ == '__main__':
    print(json.dumps(evaluar(), ensure_ascii=False, indent=2))
