# I-05 — Evidencia oficial para la auditoría DINESE 2023–2024

Fecha de consulta: 24/11/2026 (Guatemala). Investigación de fuentes primarias. Este informe no es aún el resultado de ejecutar el auditor sobre todas las filas de los XLSX.

## Controles y definiciones verificadas

| Año de la base | Activas registradas | Con movimiento de ventas | Sin movimiento, calculado por diferencia |
|---|---:|---:|---:|
| 2023 | 425464 | 220903 | 204561 |
| 2024 | 645431 | 338415 | 307016 |

Los controles 2023 proceden de cuadros 4 y 7 (páginas impresas 12 y 16) del [resumen oficial 2023](https://www.ine.gob.gt/wp-content/uploads/2024/12/Resumen-Base-de-datos-DINESE.pdf). Su glosario distingue estatus activo SAT de actividad económica con ventas. Las empresas sin ventas pertenecen al total activo. Control departamental adicional: Guatemala total 209804 y con movimiento 108182. No llamar al primer total «empresas creadas».

Los controles 2024 proceden de cuadros 1 y 6 (páginas impresas 7 y 14) del [resumen oficial 2024](https://www.ine.gob.gt/wp-content/uploads/2026/03/RESUMEN-ESTADISTICO-FORMATO-DINESE.pdf). Guatemala registra 235807 activas y 120141 con movimiento. El informe distingue empresas y establecimientos, clasifica actividad mediante 21 secciones CIIU Rev.4 y presenta comparación anual de registros; eso no prueba entradas/salidas individuales ni causa del aumento. El cuadro 2 muestra una aparente errata: Enseñanza 7073 frente a 2.65%; comprobar contra XLSX antes de adoptar controles sectoriales. El boletín lleva fecha diciembre2025, distinta del año2024 de los datos.

## Cambios administrativos y comparabilidad: hecho e incertidumbre

La [metodología oficial de actualización](https://www.ine.gob.gt/wp-content/uploads/2023/12/METODOLOGIA-DE-ACTUALIZACION-DINESE.pdf), secciones 1.1, 5.1, 5.2.1–5.2.3, documenta interrupción de actualización en 2021 por cambio de autoridades y reanudación a finales2022. Describe solicitud SAT al inicio del año con información del año anterior, depuración de incompletos/códigos inválidos y adaptación de catálogos. Sus antecedentes históricos no demuestran un quiebre específico 2023–2024. No encontré una tabla puente de universos, revisión retrospectiva ni una garantía de persistencia interanual del identificador público CÓDIGO. No atribuir el aumento a creación real ni a esa interrupción histórica. No reinterpretar automáticamente AÑO como AÑO−1: conservar el año de la base y consignar el rezago metodológico separadamente.

## Procedencia y acceso

El [catálogo oficial](https://datos.ine.gob.gt/dataset/directorio-nacional-estadistico-de-empresas-dinese) declara Creative Commons Attribution. Publica ambos XLSX; su fecha de actualización no es año de referencia estadística. El [historial 2023](https://datos.ine.gob.gt/dataset/changes/52fdf6e3-4dfa-4ee7-9055-b2d874383288) registra incorporación el16/12/2024; el [historial 2024](https://datos.ine.gob.gt/dataset/changes/385bc3fa-a7cd-4400-a469-265b9d2c6cc5) registra incorporación el02/03/2026. La fecha de consulta debe acompañar URL, tamaño y hash del archivo usado.

Descargas exactas verificadas como destinos de los enlaces del catálogo:

- 2023: https://datos.ine.gob.gt/dataset/794d0a7e-6c2b-4c21-809f-f23b8936407c/resource/a2acb752-479b-4c1f-8786-d2d7ee7fd4a9/download/dinese-2023.xlsx
- 2024: https://datos.ine.gob.gt/dataset/794d0a7e-6c2b-4c21-809f-f23b8936407c/resource/d6836e3d-c7fe-457b-adbf-26ab462dfb56/download/dinese-2024.xlsx

## Recomendación de implementación y decisión para el MVP

Auditar ambos años, conservar estadísticas descriptivas separadas y habilitar únicamente la capa transversal2023 si reconcilia controles nacionales/departamentales y supera controles estructurales. Excluir del radar principal el «crecimiento empresarial2023–2024», las supuestas altas/bajas y la formalización laboral; la comparabilidad temporal permanece sin acreditar. Es una aplicación de la condición ya acordada del MVP, no un nuevo cambio de alcance.

El comando debería validar: columnas requeridas; año declarado; códigos no vacíos y únicos dentro de cada año; 22 departamentos armonizados; categorías de movimiento; sección CIIU; faltantes y filas descartadas. Debe agregar separadamente total/con/sin movimiento, registrar sumas nacionales, contrastar los cuatro controles oficiales y escribir evidencia legible. Un fallo de control no debe ocultarse como cero ni producir un resumen «válido». CÓDIGO solo sirve como clave dentro de año mientras no se documente persistencia. No unir DINESE con hogares/personas; para Banguat agregar las secciones correspondientes (D+E y R+S+T+U) mediante mapping explícito.

No es necesario consultar al usuario para concluir insuficiencia de evidencia temporal: ya autorizó documentar exclusión sin bloquear I-04.
