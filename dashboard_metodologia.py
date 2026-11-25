"""Glosario, contratos y diagnóstico de precisión del prototipo."""
import streamlit as st

from dashboard_data import NOMBRES_ENCOVI
from dashboard_precision import mostrar_calidad
from dashboard_ui import titulo


def mostrar_metodologia(encovi):
    titulo('Metodología y calidad', '¿Qué mide cada fuente y con qué precisión puede interpretarse?',
           'Guatemala · Fuentes y trazabilidad')
    st.markdown('''
| Medición | Universo, unidad y ponderación |
| --- | --- |
| Ocupación en el sector informal · ENEIC IV-2025 | Ocupados de 15 años o más clasificados según su unidad económica. Tasa de personas con condición válida y media entre ocupados con ingreso numérico, incluidos ceros. FACTOR trimestral. Los intervalos disponibles son oficiales y proceden del boletín. |
| Ocupación en el sector informal · ENCOVI 2023 | Personas ocupadas de 15 años o más. FACTOR. CV e IC95 aproximados por DEPTO/UPM. |
| Pobreza total y extrema · ENCOVI 2023 | Personas representadas por hogares con consumo y clasificación válidos. Se usa el consumo anual por persona y Factor3. CV e IC95 aproximados por DEPTO/UPM. |
| Perfiles de hogares · ENCOVI 2023 | Personas, hogares o dominios de respuesta según el indicador. FACTOR para remesas y negocios del hogar; Factor3 para consumo. Los horizontes y límites se indican en la ficha y la descarga. |
| PIB departamental · Banguat 2023 | Cuadro 8. PIB a precios corrientes dividido por población departamental proyectada. El cociente mide producción por persona. |
| Estructura departamental · Banguat 2023 | Cuadro 7. Participación de cada actividad en el VAB territorial corriente de 17 grupos, sin impuestos netos sobre productos. |
| Producción informal · Banguat 2013–2024 | Cuadros 12 y 5.103. Millones de quetzales. Participaciones con denominadores corrientes; volumen encadenado con referencia 2013. Ausencia en 2020 y cifras preliminares en 2023–2024. |
| Radar · M-04, corte 2023 | Contrastes de estimaciones puntuales de ENCOVI y cuentas departamentales. Las referencias se calculan en el universo elegible antes de aplicar filtros visuales. |
''')
    st.caption('La comparación entre ENEIC IV-2025 y ENCOVI 2023 requiere considerar sus diferentes períodos, diseños y granos. Los registros DINESE describen empresas registradas. Las diferencias de cobertura impiden interpretar 2023–2024 como crecimiento empresarial o formalización.')
    st.divider()
    mostrar_calidad(encovi, NOMBRES_ENCOVI)
    st.divider()
    with st.expander('Glosario y límites de interpretación', expanded=True):
        st.markdown('''
- **Ocupación en el sector informal**. Clasifica a los ocupados por características de su unidad económica y categoría ocupacional.
- **Empleo informal**. Se refiere a la naturaleza y protección del puesto. Requiere una medición independiente de la unidad.
- **Producción informal**. Valor agregado generado por el sector informal en un período y ámbito.
- **pp**. Puntos porcentuales, diferencia entre dos porcentajes.
- **CV**. Coeficiente de variación, error estándar como porcentaje de la estimación.
- **IC95**. Intervalo de confianza al 95 %. El de ENCOVI es aproximado por DEPTO/UPM. El de ENEIC se transcribe cuando existe.
- **VAB**. Valor agregado bruto. Producción menos consumo intermedio.
- **PIB**. VAB más impuestos netos de subvenciones sobre los productos.
- **LQ**. Cociente de localización, participación local de una actividad dividida por su participación agregada de referencia.
- **CAGR**. Tasa compuesta de crecimiento anual. Su cálculo exige extremos positivos y una serie comparable.
''')
    with st.expander('Trazabilidad de cada vista'):
        st.markdown('''
- Empleo e ingresos · `agregados_publicos.csv` · `docs/ENEIC_CONTRATO_M05.md`
- Territorio · `matriz_departamental.csv` · `docs/M03_CONTRATO_MATRIZ.md`
- Hogares · `perfiles_hogares.csv` · `docs/hallazgos_hogares.md`
- Producción · `vab_informal_nacional.csv`, `vab_informal_grupo.csv` · `docs/VAB_CONTRATO_M05.md`
- Radar · `hallazgos.json` · `docs/reglas_radar.md`
''')
