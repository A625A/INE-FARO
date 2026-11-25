import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from radar_r1 import detectar


def test_limites_y_motivos():
    filas = [dict(depto_id='01', departamento='A', informal=70, pobreza=20, pib=100),
             dict(depto_id='02', departamento='B', informal=73, pobreza=35, pib=150)]
    resultado = detectar(filas, 3, 15, 1.5)
    assert len(resultado) == 1
    assert resultado[0]['motivo'] == ['pobreza', 'pib']
    assert detectar(filas, 2, 15, 1.5) == []


def test_motivo_evaluable_independiente():
    filas = [dict(depto_id='01', departamento='A', informal=70, pobreza=None, pib=100),
             dict(depto_id='02', departamento='B', informal=70, pobreza=35, pib=150)]
    assert detectar(filas, 3, 15, 1.5)[0]['motivo'] == ['pib']
