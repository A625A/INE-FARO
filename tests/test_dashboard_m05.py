"""Pruebas de los contratos de datos de la interfaz, sin servidor Streamlit."""
from pathlib import Path
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dashboard_utils import cargar_tablero


def escribir_pib(d):
    pd.DataFrame({
        'depto_id':[f'{i:02}' for i in range(1,23)],
        'departamento':[f'Departamento {i}' for i in range(1,23)],
        'anio':[2023]*22,
        'pib_per_capita':[10000+i*1000 for i in range(1,23)],
        'tipo_precio':['corrientes']*22,
        'unidad':['quetzales_por_habitante']*22,
    }).to_csv(d/'pib_per_capita.csv',index=False)


def test_sin_m01_solo_pib_real(tmp_path):
    escribir_pib(tmp_path)
    df, disponible=cargar_tablero(tmp_path)
    assert len(df)==22 and not disponible
    assert 'ocupacion_sector_informal' not in df


def test_con_m01_cruce_uno_a_uno(tmp_path):
    escribir_pib(tmp_path)
    pd.DataFrame([{'depto_id':f'{i:02}', 'anio':2023, 'indicador':nombre,
        'valor':50.0, 'unidad':'porcentaje', 'estado':'publicable_con_reserva', 'cv':5.0}
        for i in range(1,23) for nombre in ('ocupacion_sector_informal','pobreza_total','pobreza_extrema')]
    ).to_csv(tmp_path/'indicadores_encovi_2023.csv',index=False)
    df, disponible=cargar_tablero(tmp_path)
    assert disponible and len(df)==22
    assert df.pobreza_total.eq(50).all()


def test_rechaza_encovi_incompleto(tmp_path):
    escribir_pib(tmp_path)
    pd.DataFrame([{'depto_id':'01','anio':2023,'indicador':'pobreza_total',
                   'valor':45,'unidad':'porcentaje','estado':'publicable_con_reserva','cv':5}]
    ).to_csv(tmp_path/'indicadores_encovi_2023.csv',index=False)
    with pytest.raises(ValueError,match='22 departamentos'):
        cargar_tablero(tmp_path)


def test_rechaza_depto_duplicado_pib(tmp_path):
    escribir_pib(tmp_path)
    path=tmp_path/'pib_per_capita.csv'
    df=pd.read_csv(path,dtype={'depto_id':str})
    df.loc[1,'depto_id']='01'
    df.to_csv(path,index=False)
    with pytest.raises(ValueError,match='22 departamentos'):
        cargar_tablero(tmp_path)


def test_rechaza_indicador_no_publicable(tmp_path):
    escribir_pib(tmp_path)
    pd.DataFrame([{'depto_id':f'{i:02}', 'anio':2023, 'indicador':nombre,
        'valor':50, 'unidad':'porcentaje',
        'estado':'no_publicable' if i==1 else 'publicable_con_reserva', 'cv':35 if i==1 else 5}
        for i in range(1,23) for nombre in ('ocupacion_sector_informal','pobreza_total','pobreza_extrema')]
    ).to_csv(tmp_path/'indicadores_encovi_2023.csv',index=False)
    with pytest.raises(ValueError,match='no publicables'):
        cargar_tablero(tmp_path)