"""Exploración de fichas públicas y sensibilidad precalculada."""
import pandas as pd
import streamlit as st

from dashboard_data import DEPARTAMENTOS, NOMBRES_ENCOVI, PIB
from dashboard_radar import FUENTE_ENCOVI, MAGNITUDES, REGLAS, exportar_radar
from dashboard_territorio import ACTIVIDADES
from dashboard_ui import CONTRASTE_DESTACADO, SECCIONES, cifras, mostrar_tabla, navegar, selector, titulo

CATEGORIAS = {
    'R1': 'Informalidad similar, realidades diferentes',
    'R2a': 'Alta producción y alta informalidad',
    'R2b': 'Alta producción con pobreza e informalidad elevadas',
    'R3': 'Estructura productiva similar, informalidad diferente',
    'R4': 'Especialización productiva y vulnerabilidad social',
}
DESCRIPCIONES = {
    'R1': 'Compara pares con hasta 3 puntos de diferencia en ocupación en el sector informal. La pobreza total difiere al menos 15 puntos o el PIB por habitante de uno alcanza al menos 1.5 veces el del otro.',
    'R2a': 'El PIB por habitante y la ocupación en el sector informal superan sus respectivas medianas departamentales.',
    'R2b': 'El PIB por habitante supera la mediana departamental, la pobreza total excede su mediana en al menos 15 puntos y la ocupación en el sector informal alcanza o supera la tasa nacional.',
    'R3': 'Compara pares en el cuarto de menor distancia entre sus 17 participaciones productivas, con al menos 10 puntos de diferencia en ocupación en el sector informal.',
    'R4': 'Una actividad aporta al menos el 10 % del valor agregado local y pesa al menos 1.5 veces lo que pesa en el conjunto del país. La pobreza y la ocupación en el sector informal superan sus medianas departamentales.',
}

MOTIVOS = {
    'ambos': 'Brechas de pobreza y PIB por habitante',
    'solo_pobreza': 'Brecha de pobreza',
    'solo_pib': 'Razón de PIB por habitante',
    'pib_e_informalidad_sobre_medianas': 'PIB y ocupación en el sector informal sobre sus medianas',
    'pib_pobreza_e_informalidad': 'PIB y pobreza sobre la mediana, con alta ocupación en el sector informal',
    'estructura_similar_y_brecha_laboral': 'Estructura productiva similar con brecha de ocupación',
    'especializacion_sectorial': 'Especialización productiva con tasas sobre las medianas',
}
PARAMETROS = {
    'r1_i': 'Tolerancia ocupación (pp)', 'r1_p': 'Brecha de pobreza (pp)',
    'r1_y': 'Razón de PIB por habitante', 'r2b_p': 'Margen de pobreza (pp)',
    'r3_percentil': 'Percentil de distancia', 'r3_i': 'Brecha de ocupación (pp)',
    'r4_lq': 'Cociente de localización', 'r4_s': 'Participación local (%)',
}
NOMBRES = {**DEPARTAMENTOS, 'nacional': 'Guatemala · nacional', '22_departamentos': '22 departamentos'}


def rotulo(ficha):
    nombres = ' y '.join(DEPARTAMENTOS[c] for c in ficha['territorios'])
    actividad = f' · {ACTIVIDADES[ficha["grupo"]]}' if ficha['grupo'] else ''
    return f'{CATEGORIAS[ficha["regla"]]} · {nombres}{actividad}'


def nombre_escenario(uid):
    regla, _, detalle = uid.split(':', 2)
    territorios, _, grupo = detalle.partition(':')
    return rotulo({'regla': regla, 'territorios': territorios.split('-'), 'grupo': grupo})


def filtrar_radar(radar, regla, depto):
    return [f for f in radar['hallazgos'] if (regla == 'Todas' or f['regla'] == regla)
            and (not depto or depto in f['territorios'])]


def mostrar_radar(radar):
    titulo('Radar de inteligencia', '¿Qué contrastes territoriales ameritan una investigación?',
           'Corte estándar · 2023 · ENCOVI y Banguat · Reglas M-04 v1.1')
    if radar['rechazados']:
        st.warning(f'{radar["rechazados"]} fichas excluidas por evidencia o estructura inválida.')
    izquierda, derecha = st.columns(2)
    regla = selector('Regla', ['Todas', *REGLAS], 'regla_radar',
                     formato=lambda r: CATEGORIAS.get(r, r), contenedor=izquierda)
    depto = selector('Departamento del radar', ['', *DEPARTAMENTOS], 'depto_radar',
                     formato=lambda d: DEPARTAMENTOS.get(d, 'Todos los departamentos'), contenedor=derecha)
    if regla != 'Todas':
        st.caption(DESCRIPCIONES[regla])
    with st.expander('Cómo se identifican los cinco tipos de hallazgo'):
        for codigo in REGLAS:
            st.markdown(f'**{CATEGORIAS[codigo]}** · {radar["conteos"][codigo]} hallazgos')
            st.write(DESCRIPCIONES[codigo])
    seleccion = filtrar_radar(radar, regla, depto)
    st.caption(f'{len(seleccion)} de {len(radar["hallazgos"])} hallazgos válidos en la selección.')
    if regla == 'R2a' and not radar['conteos']['R2a']:
        st.info('En esta categoría, ningún departamento supera simultáneamente ambas medianas en el corte estándar.')
    elif not seleccion:
        st.info('La combinación de filtros no tiene hallazgos. Cambia la regla o el departamento.')
    if seleccion:
        vistas = {f['id']: f for f in seleccion}
        ficha_id = selector('Hallazgo', list(vistas), 'ficha_radar', default=CONTRASTE_DESTACADO,
                            formato=lambda i: rotulo(vistas[i]))
        mostrar_ficha(radar, vistas[ficha_id])
        with st.expander('Listado de la selección'):
            mostrar_tabla(pd.DataFrame([
                {'Hallazgo': rotulo(f), 'Motivo': MOTIVOS.get(f['motivo'], f['motivo']),
                 'Escenarios con el hallazgo': f'{f["robustez"]["presentes"]}/{f["robustez"]["escenarios"]}'} for f in seleccion
            ]))
    descargas = st.columns(2)
    ids = [f['id'] for f in seleccion]
    for columna, formato, mime in zip(descargas, ('csv', 'json'), ('text/csv', 'application/json')):
        columna.download_button(f'Descargar selección ({formato.upper()})', exportar_radar(radar, ids, formato),
                               f'radar-seleccion.{formato}', mime, on_click='ignore')
    st.divider()
    mostrar_sensibilidad(radar, regla)


def valor_magnitud(campo, valor):
    if valor is None:
        return 'No evaluable'
    if campo.endswith('_q'):
        return f'Q {valor:,.2f}'
    unidad = ' pp' if campo.endswith('_pp') else ' %' if campo.endswith('_pct') else ' ×'
    return f'{valor:,.2f}{unidad}'


def mostrar_ficha(radar, ficha):
    destacada = ficha['id'] == CONTRASTE_DESTACADO
    evidencias = tabla_evidencias(ficha['evidencias'])
    with st.container(border=True, key='contraste-destacado' if destacada else None):
        st.subheader(rotulo(ficha))
        st.caption(MOTIVOS.get(ficha['motivo'], ficha['motivo']))
        if destacada:
            mostrar_comparacion_destacada(ficha, evidencias)
            st.markdown('#### ¿Qué investigar ahora?')
        st.write(ficha['explicacion'])
        robustez = ficha['robustez']
        st.markdown(f'**Robustez frente a umbrales** · Presente en {robustez["presentes"]} de {robustez["escenarios"]} escenarios de su regla.')
        if not destacada:
            mostrar_tabla(pd.DataFrame([
                {'Magnitud': MAGNITUDES[k], 'Resultado': valor_magnitud(k, v)}
                for k, v in ficha['magnitudes'].items()
            ]))
        st.markdown('**Pregunta de investigación**')
        st.write(ficha['pregunta'])
        st.markdown('**Evidencia adicional requerida**')
        st.write(ficha['evidencia_requerida'])
        st.caption(f'Limitación · {ficha["limitacion"]}')
        with st.expander('Evidencias estadísticas', expanded=destacada):
            mostrar_tabla(evidencias)
            st.caption('Los CV e IC95 de ENCOVI son aproximados por DEPTO/UPM. Las revisiones identifican el corte de cuentas departamentales.')
        columnas = st.columns(len(ficha['territorios']))
        for columna, depto in zip(columnas, ficha['territorios']):
            columna.button(f'Abrir perfil de {DEPARTAMENTOS[depto]}', key=f'perfil_{depto}',
                           on_click=navegar, args=(SECCIONES[1],), kwargs={'depto': depto})
        st.download_button('Descargar esta ficha (JSON)', exportar_radar(radar, [ficha['id']]),
                           f'{ficha["id"].replace(":", "-")}.json', 'application/json',
                           on_click='ignore')


def mostrar_comparacion_destacada(ficha, evidencias):
    cifras([
        ('Brecha de pobreza total', valor_magnitud('brecha_pobreza_pp', ficha['magnitudes'].get('brecha_pobreza_pp')), ''),
        ('Brecha de ocupación en el sector informal',
         valor_magnitud('brecha_informalidad_pp', ficha['magnitudes'].get('brecha_informalidad_pp')), ''),
        ('Razón de PIB por habitante',
         valor_magnitud('razon_pib_por_habitante', ficha['magnitudes'].get('razon_pib_por_habitante')), ''),
    ])
    nombres = [DEPARTAMENTOS[d] for d in ficha['territorios']]
    valores = evidencias.assign(
        Resultado=[f'{valor} %' if unidad == '%' else f'Q {valor}'
                   for valor, unidad in zip(evidencias.Valor, evidencias.Unidad)],
    )
    orden = [NOMBRES_ENCOVI['ocupacion_sector_informal'], NOMBRES_ENCOVI['pobreza_total'], PIB]
    comparacion = valores.pivot(index='Indicador', columns='Territorio', values='Resultado')
    st.table(comparacion.reindex(index=orden, columns=nombres).fillna('No evaluable').reset_index())
    st.caption('Estimaciones puntuales de ENCOVI y Banguat, 2023. PIB en quetzales corrientes por habitante.')
    depto, comparar = ficha['territorios']
    st.button('Abrir comparación en Territorio', key='comparar_contraste_destacado',
              on_click=navegar, args=(SECCIONES[1],),
              kwargs={'depto': depto, 'comparar': comparar, 'indicador_mapa': 'pobreza_total'})


def tabla_evidencias(evidencias):
    filas = []
    for evidencia in evidencias:
        diag = evidencia['diagnostico']
        indicador = evidencia['indicador']
        if indicador.startswith('participacion_'):
            grupo = indicador.removeprefix('participacion_')
            nombre = f'Participación · {ACTIVIDADES[grupo]}'
        else:
            nombre = NOMBRES_ENCOVI.get(indicador, PIB)
        calidad = (f'Publicable con reserva · n={diag["n"]:,} · CV {diag["cv"]:.2f} % · '
                   f'IC95 [{diag["ic95_inf"]:.2f}, {diag["ic95_sup"]:.2f}] · {diag["ponderador"]}'
                   if evidencia['fuente'] == FUENTE_ENCOVI else diag['revision'].capitalize())
        filas.append({
            'Territorio': NOMBRES[evidencia['territorio']], 'Indicador': nombre,
            'Valor': f'{evidencia["valor"]:,.2f}', 'Unidad': evidencia['unidad'],
            'Universo': evidencia['universo'], 'Calidad': calidad, 'Fuente': evidencia['fuente'],
        })
    return pd.DataFrame(filas)


def mostrar_sensibilidad(radar, regla):
    st.subheader('Sensibilidad de las reglas')
    if not radar['sensibilidad']:
        st.info('La sensibilidad se omite cuando el corte contiene fichas inválidas.')
        return
    st.caption('21 escenarios precalculados en el universo completo. El filtro de departamento modifica las fichas visibles. La robustez mide estabilidad frente a umbrales y no es una probabilidad estadística.')
    escenarios = [e for e in radar['sensibilidad'] if regla == 'Todas' or e['regla'] == regla]
    renglones = pd.DataFrame([{
        'Categoría': CATEGORIAS[e['regla']], 'Escenario': PARAMETROS.get(e['parametro'], 'Base estándar'),
        'Valor': e['valor'], 'Hallazgos': e['conteo'], 'Entran': len(e['aparecen']),
        'Salen': len(e['desaparecen']),
    } for e in escenarios])
    mostrar_tabla(renglones)
    alternativos = [e for e in escenarios if e['parametro']]
    if alternativos:
        with st.expander('Fichas que entran o salen por escenario'):
            i = st.selectbox('Escenario alternativo', range(len(alternativos)), format_func=lambda i:
                             f'{CATEGORIAS[alternativos[i]["regla"]]} · {PARAMETROS[alternativos[i]["parametro"]]} = {alternativos[i]["valor"]:g}')
            escenario = alternativos[i]
            cambios = [(etiqueta, nombre_escenario(uid)) for campo, etiqueta in (('aparecen', 'Entra'), ('desaparecen', 'Sale'))
                       for uid in escenario[campo]]
            if cambios:
                mostrar_tabla(pd.DataFrame(cambios, columns=['Cambio', 'Hallazgo']))
            else:
                st.info('Este escenario conserva el mismo conjunto de hallazgos.')
