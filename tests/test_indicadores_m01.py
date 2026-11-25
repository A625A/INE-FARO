"""Pruebas sintéticas de M-01: no dependen de los microdatos confidenciales."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from calcular_indicadores_encovi import estimar_tasa


def encuesta_ejemplo():
    return pd.DataFrame({
        'DEPTO': [1,1,1,1,2,2,2,2],
        'UPM': [10,10,11,11,20,20,21,21],
        'FACTOR': [2,2,1,1,1,1,2,2],
        'caso': [1,1,0,0,0,0,1,1],
        'AREA': [1,1,1,2,2,2,1,1],
    })


def test_estimacion_ponderada_y_precision():
    df=encuesta_ejemplo()
    resultado=estimar_tasa(df, df.caso.eq(1), 'FACTOR')
    assert resultado['valor']==pytest.approx(66.666667, abs=1e-5)
    assert resultado['n']==8
    assert resultado['upm_n']==4
    assert 0<=resultado['ic95_inf']<=resultado['valor']<=resultado['ic95_sup']<=100
    assert resultado['precision'].startswith('aproximada')


def test_dominio_no_descarta_upm_sin_registros():
    df=encuesta_ejemplo()
    resultado=estimar_tasa(df, df.caso.eq(1),'FACTOR',df.AREA.eq(1))
    assert resultado['n']==5
    assert resultado['valor']==pytest.approx(100*8/9, abs=1e-5)
    assert resultado['upm_n']==3


def test_error_peso_invalido():
    df=encuesta_ejemplo()
    df.loc[0,'FACTOR']=-1
    with pytest.raises(ValueError, match='Ponderador'):
        estimar_tasa(df,df.caso.eq(1),'FACTOR')


def test_error_upm_solitario():
    df=encuesta_ejemplo().loc[lambda x:x.UPM.isin([10,20,21])].copy()
    with pytest.raises(ValueError, match='una UPM'):
        estimar_tasa(df,df.caso.eq(1),'FACTOR')