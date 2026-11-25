import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from explorar_encovi import unir_a_hogares, validar_clave


@pytest.mark.parametrize('valores', [[1, 1], [1, None]])
def test_clave_invalida_no_se_repara_eliminando_filas(valores):
    frame = pd.DataFrame({'NO_HOGAR': valores})
    with pytest.raises(ValueError):
        validar_clave(frame, ['NO_HOGAR'])
    assert len(frame) == 2


def test_union_conserva_personas_y_expone_hogares_sin_correspondencia():
    hogares = pd.DataFrame({'NO_HOGAR': [1, 2], 'DEPTO': [1, 2], 'UPM': [10, 20]})
    personas = pd.DataFrame({'NO_HOGAR': [1, 1, 3], 'DEPTO': [1, 1, 3], 'UPM': [10, 10, 30]})
    resultado = unir_a_hogares(personas, hogares, many=True)
    assert resultado['filas_antes'] == resultado['filas_despues'] == 3
    assert resultado['filas_sin_hogar'] == 1
    assert resultado['hogares_sin_registro_hijo'] == 1


def test_union_rechaza_hogares_duplicados_en_vez_de_multiplicar_personas():
    hogares = pd.DataFrame({'NO_HOGAR': [1, 1], 'DEPTO': [1, 1], 'UPM': [10, 10]})
    personas = hogares.iloc[:1].copy()
    with pytest.raises(pd.errors.MergeError):
        unir_a_hogares(personas, hogares, many=True)
