"""Valida las fichas de M-04 antes de exponer una vista o descarga."""
from collections import Counter
import json
from math import isfinite

from dashboard_data import DEPARTAMENTOS, GROUPS, INDICADORES, RESERVA
from dashboard_utils import MIN_MUESTRA, UMBRAL_PUBLICACION
from scripts.radar_rules.export import FIELDS, serialize

ESCENARIOS_POR_REGLA = {'R1': 7, 'R2a': 1, 'R2b': 3, 'R3': 5, 'R4': 5}
PARAMETROS_POR_REGLA = {
    'R1': {'r1_i', 'r1_p', 'r1_y'}, 'R2a': set(), 'R2b': {'r2b_p'},
    'R3': {'r3_percentil', 'r3_i'}, 'R4': {'r4_lq', 'r4_s'},
}

REGLAS = {
    'R1': 'Contrastes territoriales',
    'R2a': 'PIB y ocupación en el sector informal sobre sus medianas',
    'R2b': 'Desacople entre producción, pobreza y ocupación',
    'R3': 'Estructura similar, ocupación distinta',
    'R4': 'Especialización productiva',
}
FUENTE_ENCOVI = 'INE, ENCOVI 2023'
FUENTE_PIB = 'Banguat, cuadro 8, 2023'
FUENTE_VAB = 'Banguat, cuadro 7, VAB a precios corrientes 2023'
MAGNITUDES = {
    'brecha_informalidad_pp': 'Brecha de ocupación en el sector informal',
    'brecha_pobreza_pp': 'Brecha de pobreza total',
    'razon_pib_por_habitante': 'Razón de PIB por habitante',
    'exceso_i_pp': 'Ocupación por encima de la mediana',
    'exceso_p_pp': 'Pobreza por encima de la mediana',
    'exceso_y_q': 'PIB por habitante por encima de la mediana',
    'mediana_i_pct': 'Mediana departamental de ocupación en el sector informal',
    'mediana_p_pct': 'Mediana departamental de pobreza total',
    'mediana_y_q': 'Mediana departamental del PIB por habitante',
    'informalidad_nacional_pct': 'Ocupación en el sector informal nacional',
    'distancia_pp': 'Distancia de estructura productiva',
    'umbral_distancia_pp': 'Umbral de distancia (P25)',
    'lq': 'Cociente de localización (LQ)',
    'participacion_local_pct': 'Participación en el VAB departamental',
    'participacion_agregada_pct': 'Participación en el VAB agregado de los 22 departamentos',
}


def numero(valor):
    return type(valor) is int or (type(valor) is float and isfinite(valor))


def texto(valor):
    return isinstance(valor, str) and bool(valor.strip())


def evidencia_valida(evidencia, codigos):
    campos = {'territorio', 'indicador', 'valor', 'unidad', 'fuente', 'universo', 'diagnostico'}
    if not isinstance(evidencia, dict) or set(evidencia) != campos:
        return False
    diag = evidencia['diagnostico']
    valor = evidencia['valor']
    territorio = evidencia['territorio']
    if (not isinstance(diag, dict) or not numero(valor) or not texto(territorio)
            or not texto(evidencia['universo']) or not texto(evidencia['indicador'])):
        return False

    fuente = evidencia['fuente']
    indicador, unidad = evidencia['indicador'], evidencia['unidad']
    if fuente == FUENTE_ENCOVI:
        campos_diag = {'elegible', 'estado', 'n', 'upm_n', 'cv', 'ic95_inf',
                       'ic95_sup', 'precision', 'ponderador'}
        if set(diag) != campos_diag:
            return False
        cv, inf, sup, n = (diag[k] for k in ('cv', 'ic95_inf', 'ic95_sup', 'n'))
        return (territorio in (*codigos, 'nacional') and indicador in INDICADORES and unidad == '%'
                and diag['elegible'] is True and diag['estado'] == RESERVA
                and type(n) is int and n >= MIN_MUESTRA and type(diag['upm_n']) is int
                and 1 <= diag['upm_n'] <= n and texto(diag['precision'])
                and diag['ponderador'] == ('FACTOR' if indicador == INDICADORES[0] else 'Factor3')
                and all(numero(x) for x in (cv, inf, sup)) and 0 <= cv <= UMBRAL_PUBLICACION
                and 0 <= inf <= valor <= sup <= 100)

    if fuente == FUENTE_PIB:
        return (set(diag) == {'elegible', 'revision'} and diag['elegible'] is True
                and texto(diag['revision']) and territorio in codigos and valor > 0
                and indicador == 'pib_por_habitante' and unidad == 'Q corrientes por habitante')

    if fuente == FUENTE_VAB:
        return (set(diag) == {'revision'} and texto(diag['revision']) and 0 <= valor <= 100
                and territorio in (*codigos, '22_departamentos') and unidad == '%'
                and indicador in {f'participacion_{grupo}' for grupo in GROUPS})
    return False


def ficha_valida(ficha):
    if not isinstance(ficha, dict) or set(ficha) != set(FIELDS):
        return False
    regla, codigos, grupo = (ficha[k] for k in ('regla', 'territorios', 'grupo'))
    if (not texto(regla) or regla not in REGLAS or ficha['anio'] != 2023
            or not isinstance(codigos, list) or not all(isinstance(c, str) and c in DEPARTAMENTOS for c in codigos)
            or len(codigos) != (2 if regla in ('R1', 'R3') else 1)
            or codigos != sorted(set(codigos)) or (grupo not in GROUPS if regla == 'R4' else grupo is not None)):
        return False
    ficha_id = f'{regla}:2023:{"-".join(codigos)}' + (f':{grupo}' if grupo else '')
    descripciones = ('motivo', 'explicacion', 'pregunta', 'evidencia_requerida', 'limitacion')
    magnitudes, robustez, evidencias = (ficha[k] for k in ('magnitudes', 'robustez', 'evidencias'))
    if (ficha['id'] != ficha_id or not all(texto(ficha[k]) for k in descripciones)
            or not isinstance(magnitudes, dict) or not magnitudes
            or not set(magnitudes) <= MAGNITUDES.keys()
            or not all(v is None or numero(v) for v in magnitudes.values())
            or not isinstance(robustez, dict) or set(robustez) != {'presentes', 'escenarios', 'proporcion'}
            or not isinstance(evidencias, list) or not evidencias
            or not all(evidencia_valida(e, codigos) for e in evidencias)):
        return False
    claves_evidencia = {(e['territorio'], e['indicador']) for e in evidencias}
    if (len(claves_evidencia) != len(evidencias)
            or not contiene_evidencias(claves_evidencia, regla, codigos, grupo, ficha['motivo'])):
        return False
    presentes, escenarios, proporcion = (robustez[k] for k in ('presentes', 'escenarios', 'proporcion'))
    return (type(presentes) is int and type(escenarios) is int and 1 <= presentes <= escenarios
            and escenarios == ESCENARIOS_POR_REGLA[regla] and numero(proporcion)
            and 0 < proporcion <= 1 and abs(proporcion - presentes / escenarios) < 1e-9)


def contiene_evidencias(claves, regla, codigos, grupo, motivo):
    ocupacion, pobreza = INDICADORES[:2]
    requeridas = {(c, ocupacion) for c in codigos}
    if regla == 'R1':
        if motivo not in ('ambos', 'solo_pobreza', 'solo_pib'):
            return False
        if motivo in ('ambos', 'solo_pobreza'):
            requeridas.update((c, pobreza) for c in codigos)
        if motivo in ('ambos', 'solo_pib'):
            requeridas.update((c, 'pib_por_habitante') for c in codigos)
    elif regla in ('R2a', 'R2b'):
        requeridas.add((codigos[0], 'pib_por_habitante'))
        if regla == 'R2b':
            requeridas.update({(codigos[0], pobreza), ('nacional', ocupacion)})
    elif regla == 'R3':
        requeridas.update((c, f'participacion_{g}') for c in codigos for g in GROUPS)
    elif regla == 'R4':
        requeridas.update({(codigos[0], pobreza), (codigos[0], f'participacion_{grupo}'),
                           ('22_departamentos', f'participacion_{grupo}')})
    return requeridas <= claves


def validar_radar(datos):
    if (not isinstance(datos, dict) or datos.get('schema_version') != '1.0'
            or datos.get('rules_version') != '1.1' or datos.get('modo') != 'standard'
            or datos.get('filtros') != {'reglas': list(REGLAS), 'departamentos': []}):
        raise ValueError('M-04: se requiere la generación estándar completa de reglas 1.1.')
    fichas, conteos, sensibilidad = (datos.get(k) for k in ('hallazgos', 'conteos', 'sensibilidad'))
    if (not isinstance(fichas, list) or not isinstance(conteos, dict) or set(conteos) != set(REGLAS)
            or not all(type(n) is int and n >= 0 for n in conteos.values())
            or sum(conteos.values()) != len(fichas) or not isinstance(sensibilidad, list)):
        raise ValueError('M-04: conteos o sensibilidad incompatibles.')
    validas = [f for f in fichas if ficha_valida(f)]
    ids = Counter(f['id'] for f in validas)
    validas = [f for f in validas if ids[f['id']] == 1]
    rechazados = len(fichas) - len(validas)
    conteos_publicos = {r: sum(f['regla'] == r for f in validas) for r in REGLAS}
    if not rechazados and conteos != conteos_publicos:
        raise ValueError('M-04: los conteos por regla no concuerdan.')
    escenarios = []
    for escenario in sensibilidad:
        if not escenario_valido(escenario):
            raise ValueError('M-04: escenario de sensibilidad no válido.')
        escenarios.append(escenario)
    distribucion = Counter(e['regla'] for e in escenarios)
    if distribucion != ESCENARIOS_POR_REGLA:
        raise ValueError('M-04: la rejilla debe contener los 21 escenarios versionados.')
    for regla, conteo in conteos.items():
        base = [e for e in escenarios if e['regla'] == regla and e['parametro'] is None]
        if len(base) != 1 or base[0]['conteo'] != conteo:
            raise ValueError('M-04: escenario base incompatible con su regla.')
    return dict(schema_version=datos['schema_version'], rules_version=datos['rules_version'],
                modo='standard', hallazgos=validas, conteos=conteos_publicos,
                sensibilidad=escenarios if not rechazados else [], rechazados=rechazados)


def escenario_valido(escenario):
    if not isinstance(escenario, dict) or set(escenario) != {
        'regla', 'parametro', 'valor', 'conteo', 'aparecen', 'desaparecen',
    }:
        return False
    regla, parametro, valor, conteo, entran, salen = (
        escenario[k] for k in ('regla', 'parametro', 'valor', 'conteo', 'aparecen', 'desaparecen'))
    return (texto(regla) and regla in REGLAS and type(conteo) is int and conteo >= 0
            and ((parametro is None and valor is None and entran == salen == [])
                 or (texto(parametro) and parametro in PARAMETROS_POR_REGLA[regla] and numero(valor)))
            and all(isinstance(ids, list) and all(texto(i) and i.startswith(f'{regla}:2023:') for i in ids)
                    for ids in (entran, salen)))


def cargar_radar(procesados):
    ruta = procesados / 'hallazgos.json'
    return validar_radar(json.loads(ruta.read_text(encoding='utf-8')))


def exportar_radar(radar, ids, formato='json'):
    seleccion = set(ids)
    hallazgos = [f for f in radar['hallazgos'] if f['id'] in seleccion and ficha_valida(f)]
    respuesta = {k: radar[k] for k in ('schema_version', 'rules_version', 'modo')}
    respuesta.update(anio=2023, hallazgos=hallazgos,
                     conteos={r: sum(f['regla'] == r for f in hallazgos) for r in REGLAS})
    return serialize(respuesta, {})[f'hallazgos.{formato}']
