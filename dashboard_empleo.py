"""Vista laboral de agregados nacionales, dominios y ramas ENEIC."""
import altair as alt
import streamlit as st

from dashboard_data import DOMINIOS, MEDIDAS_ENEIC, RAMAS_ENEIC
from dashboard_ui import AZUL, AZUL_CLARO, barras, cifras, descargar_csv, grafico, mostrar_tabla, titulo

RAMAS_CORTAS = dict(zip(RAMAS_ENEIC, (
    'Agricultura', 'Industrias', 'Construcción', 'Comercio y afines', 'Información',
    'Finanzas y seguros', 'Inmobiliarias', 'Profesionales y apoyo', 'Admón., salud y enseñanza',
    'Otros servicios',
)))
METADATOS = [
    alt.Tooltip('unidad:N', title='Unidad'),
    alt.Tooltip('denominador:Q', title='Denominador ponderado', format=',.0f'),
    alt.Tooltip('n:Q', title='Muestra (n)', format=',.0f'),
    alt.Tooltip('cobertura_pct:Q', title='Cobertura (%)', format='.2f'),
    alt.Tooltip('ic95_inf:Q', title='IC95 oficial inferior', format=',.1f'),
    alt.Tooltip('ic95_sup:Q', title='IC95 oficial superior', format=',.1f'),
    alt.Tooltip('referencia:N', title='Boletín'),
]


def mostrar_empleo(datos):
    titulo('Empleo e ingresos', '¿Cuántas personas trabajan en el sector informal y cómo varían los ingresos por dominio?',
           'Guatemala · Octubre–diciembre 2025 · INE, ENEIC')
    nacional = datos[datos.dimension.eq('nacional')].set_index('indicador')
    cifras([
        ('Población ocupada', f'{nacional.at["peso_ocupados", "valor_oficial"]:,.0f}', 'Personas de 15 años o más'),
        ('Ocupación en el sector informal', f'{nacional.at["tasa_sector_informal", "valor_oficial"]:.1f} %', 'De la población ocupada'),
        ('Volumen estimado informal', f'{nacional.at["peso_informal", "valor_oficial"]:,.0f}', 'Personas · conciliación indirecta'),
        ('Ingreso laboral medio', f'Q {nacional.at["media_ingreso", "valor_oficial"]:,.0f}',
         f'Por mes · {nacional.at["media_ingreso", "cobertura_pct"]:.2f} % de cobertura ponderada'),
    ])
    st.subheader('Sector de la unidad económica')
    sectores = nacional.loc[['peso_informal', 'peso_formal']].reset_index()
    sectores['sector'] = ['Informal', 'Formal']
    # La proporción informal procede de la tasa publicada; formal es su complemento visual.
    tasa = nacional.at['tasa_sector_informal', 'valor_oficial']
    sectores['participacion'] = [tasa, 100 - tasa]
    grafico(alt.Chart(sectores).mark_bar(size=20).encode(
        x=alt.X('participacion:Q', stack='zero', title='Participación de los ocupados (%)',
                scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('sector:N', title=None, sort=['Informal', 'Formal'],
                        scale=alt.Scale(domain=['Informal', 'Formal'], range=[AZUL, AZUL_CLARO]),
                        legend=alt.Legend(orient='top')),
        order=alt.Order('sector:N', sort='descending'),
        tooltip=[alt.Tooltip('sector:N', title='Sector'),
                 alt.Tooltip('participacion:Q', title='Participación (%)', format='.1f'),
                 alt.Tooltip('valor_oficial:Q', title='Personas (derivado)', format=',.0f'),
                 alt.Tooltip('denominador:Q', title='Ocupados clasificados', format=',.0f'),
                 alt.Tooltip('n:Q', title='Muestra del sector', format=',.0f')],
    ).properties(height=85))
    st.caption('ENEIC IV-2025 · 21,233 ocupados en la muestra. Los volúmenes por sector se obtuvieron por conciliación indirecta.')
    st.divider()
    st.subheader('Contrastes entre dominios')
    dominios = datos[datos.dimension.eq('dominio')]
    ocupacion, ingreso = st.columns(2)
    for columna, indicador, titulo_grafico, unidad, formato, rango in (
        (ocupacion, 'tasa_sector_informal', 'Ocupación en el sector informal', 'Ocupados del dominio (%)', '.1f', [0, 100]),
        (ingreso, 'media_ingreso', 'Ingreso laboral medio', 'Quetzales por mes', ',.0f', None),
    ):
        with columna:
            st.markdown(f'**{titulo_grafico}**')
            corte = dominios[dominios.indicador.eq(indicador)]
            grafico(barras(corte, 'categoria', 'valor_oficial', unidad, [
                alt.Tooltip('categoria:N', title='Dominio'),
                alt.Tooltip('valor_oficial:Q', title=unidad, format=formato), *METADATOS,
            ], ordenar=list(DOMINIOS), dominio=rango))
    st.caption('INE, ENEIC IV-2025 · Dominios de estimación trimestral. Ingreso medio entre ocupados con dato numérico, incluidos ceros observados.')
    st.divider()
    st.subheader('Ramas de actividad de toda la población ocupada')
    ramas = datos[datos.dimension.eq('rama_ine')].assign(
        rama=lambda d: d.categoria.map(RAMAS_ENEIC), etiqueta=lambda d: d.categoria.map(RAMAS_CORTAS),
    )
    grafico(barras(ramas, 'etiqueta', 'valor_oficial', 'Participación de todos los ocupados (%)', [
        alt.Tooltip('rama:N', title='Rama oficial'),
        alt.Tooltip('valor_oficial:Q', title='Participación (%)', format='.1f'), *METADATOS,
    ]))
    st.caption('INE, ENEIC IV-2025 · Tabla 2 del Boletín 3. Los intervalos disponibles se transcriben del boletín; la muestra de la rama cuenta ocupados observados en esa rama.')
    publicos = datos.assign(
        indicador_etiqueta=datos.indicador.map({k: v[0] for k, v in MEDIDAS_ENEIC.items()}),
        categoria_etiqueta=datos.categoria.map({'GT': 'Nacional', **RAMAS_ENEIC}).fillna(datos.categoria),
    )
    with st.expander('Fichas de cobertura y precisión'):
        st.caption('El denominador es la población de referencia ponderada. En tasas son los ocupados clasificados; en ingresos, los ocupados con dato válido; en composición, todos los ocupados del país.')
        detalle = publicos[['categoria_etiqueta', 'indicador_etiqueta', 'valor_oficial', 'unidad',
                            'n', 'denominador', 'cobertura_pct', 'ic95_inf', 'ic95_sup', 'referencia']]
        mostrar_tabla(detalle.rename(columns={
            'categoria_etiqueta': 'Ámbito o rama', 'indicador_etiqueta': 'Indicador',
            'valor_oficial': 'Valor publicado', 'unidad': 'Unidad', 'n': 'Muestra (n)',
            'denominador': 'Denominador ponderado', 'cobertura_pct': 'Cobertura (%)',
            'ic95_inf': 'IC95 inferior', 'ic95_sup': 'IC95 superior', 'referencia': 'Boletín',
        }))
    descargar_csv(publicos, 'Descargar 21 celdas públicas ENEIC', 'eneic-iv-2025.csv')
