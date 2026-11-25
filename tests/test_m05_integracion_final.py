"""Navegación y supresión del dashboard integrado con agregados locales."""
import json
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from dashboard_data import cargar_matriz, cargar_vab
from dashboard_produccion import serie_historica
from dashboard_territorio import datos_mapa
from scripts.empacar_m05 import empacar, leer_generacion

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/processed'


def abrir():
    app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=20).run()
    assert app.title[0].value == 'Empleo e ingresos' and not app.exception
    return app


def ir(app, vista):
    app.radio(key='seccion').set_value(vista).run()
    assert app.title[0].value == vista and not app.exception and not app.error


def test_inicio_y_contratos_inválidos(tmp_path):
    app = abrir()
    assert not app.error
    script = tmp_path / 'app.py'
    script.write_text((ROOT / 'app.py').read_text(), encoding='utf-8')
    procesados = tmp_path / 'data/processed/eneic_iv_2025'
    procesados.mkdir(parents=True)
    (procesados / 'agregados_publicos.csv').write_text('columna_dañada\n1\n', encoding='utf-8')
    incompleta = AppTest.from_file(str(script), default_timeout=20).run()
    assert not incompleta.exception
    assert 'agregados_publicos.csv' in incompleta.error[0].value


def test_cobertura_del_mapa_y_seleccion_territorial():
    mapa = json.loads((ROOT / 'data/reference/departamentos_m05.geojson').read_text())
    matriz, encovi = cargar_matriz(DATA)
    assert {f['properties']['shapeName'] for f in mapa['features']} == set(matriz.departamento)
    vista = datos_mapa(matriz, encovi, 'pobreza_extrema')
    assert len(vista) == 22 and len(vista[vista.valor.isna()]) == 5

    app = abrir()
    ir(app, 'Territorio')
    app.selectbox(key='filtro_indicador_mapa').select('pobreza_extrema').run()
    for codigo, nombre in [('01', 'Guatemala'), ('14', 'Quiché'), ('16', 'Alta Verapaz')]:
        app.selectbox(key='filtro_depto').select(codigo).run()
        assert not app.exception and any(h.value == nombre for h in app.subheader)
    app.selectbox(key='filtro_comparar').select('01').run()
    comparacion = next(t.value for t in app.dataframe if 'Indicador' in t.value and 'Guatemala' in t.value)
    extrema = comparacion.set_index('Indicador').loc['Pobreza extrema']
    assert pd.isna(extrema['Guatemala']) and pd.notna(extrema['Alta Verapaz'])


def test_calidad_interactiva_con_matriz_y_radar():
    app = abrir()
    ir(app, 'Metodología y calidad')
    assert [m.value for m in app.metric] == ['66', '61', '5']
    app.selectbox(key='calidad_clasificacion').select('No publicable').run()
    assert [m.value for m in app.metric] == ['5', '0', '5']
    app.selectbox(key='calidad_departamento').select('Guatemala').run()
    diagnostico = app.dataframe[0].value
    assert list(diagnostico.Departamento) == ['Guatemala']
    assert set(diagnostico) == {'Departamento', 'Indicador', 'Clasificación', 'CV (%)',
                                'Muestra (n)', 'Estado', 'Exceso (pp)'}
    assert diagnostico.iloc[0]['Exceso (pp)'] == pytest.approx(8.60323)
    app.selectbox(key='calidad_indicador').select('Pobreza total').run()
    assert [m.value for m in app.metric] == ['0', '0', '0']
    assert app.info and not app.exception

    ir(app, 'Radar de inteligencia')
    app.selectbox(key='filtro_regla_radar').select('R2a').run()
    assert 'ningún departamento' in app.info[0].value
    app.selectbox(key='filtro_regla_radar').select('R2b').run()
    app.button(key='perfil_06').click().run()
    assert app.title[0].value == 'Territorio' and app.selectbox(key='filtro_depto').value == '06'


def test_produccion_se_dibuja_en_dos_tramos():
    nacional, _ = cargar_vab(DATA)
    serie = nacional[nacional.tipo_precio.eq('corrientes')]
    spec = serie_historica(serie, 'participacion_informal_pct', '%').to_dict()
    assert spec['encoding']['detail']['field'] == 'tramo'
    filas = next(iter(spec['datasets'].values()))
    assert {r['anio'] for r in filas if not r['tramo']} == set(range(2013, 2020))
    assert {r['anio'] for r in filas if r['tramo']} == set(range(2021, 2025))
    ir(abrir(), 'Producción')


def test_zip_solo_contiene_una_generacion_publica(tmp_path):
    salida = tmp_path / 'faro.zip'
    empacar(salida)
    with ZipFile(salida) as archivo:
        assert not any('.radar_m04' in n or '/raw/' in n or 'diagnosticos_internos' in n
                       for n in archivo.namelist())
        for nombre, contenido in leer_generacion(DATA).items():
            assert archivo.read(f'data/processed/{nombre}') == contenido
        assert all((i.external_attr >> 16) & 0o170000 != 0o120000 for i in archivo.infolist())
    with pytest.raises(FileExistsError):
        empacar(salida)


def test_zip_rechaza_valores_restringidos_presentes():
    from scripts.empacar_m05 import AGREGADOS, PROCESADOS, agregados_publicos

    contenido = {f'{PROCESADOS}/{n}': (DATA / n).read_bytes() for n in AGREGADOS}
    archivo = f'{PROCESADOS}/perfiles_hogares.csv'
    datos = pd.read_csv(DATA / 'perfiles_hogares.csv', dtype={'depto_id': str})
    datos.loc[datos.estado.eq('no_publicable'), 'valor'] = 781295
    contenido[archivo] = datos.to_csv(index=False, lineterminator='\n').encode('utf-8')
    with pytest.raises(ValueError, match='M-02: la copia contiene valores restringidos'):
        agregados_publicos(contenido)
