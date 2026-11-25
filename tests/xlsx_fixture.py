"""XLSX mínimos sintéticos y copias alteradas, sólo para probar errores del CLI."""

import shutil
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


def celda(parent, referencia, valor):
    cell = ET.SubElement(parent, f'{{{NS}}}c', r=referencia)
    if isinstance(valor, str):
        cell.set('t', 'inlineStr')
        ET.SubElement(ET.SubElement(cell, f'{{{NS}}}is'), f'{{{NS}}}t').text = valor
    elif valor is not None:
        ET.SubElement(cell, f'{{{NS}}}v').text = str(valor)
    return cell


def xlsx_minimo(path, filas, titulo='Empresas 2023'):
    hoja = ET.Element(f'{{{NS}}}worksheet')
    datos = ET.SubElement(hoja, f'{{{NS}}}sheetData')
    for i, valores in enumerate(filas, 1):
        row = ET.SubElement(datos, f'{{{NS}}}row', r=str(i))
        for j, valor in enumerate(valores):
            celda(row, f'{chr(65+j)}{i}', valor)
    with ZipFile(path, 'w', ZIP_DEFLATED) as out:
        out.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        out.writestr('_rels/.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        out.writestr('xl/workbook.xml', f'<workbook xmlns="{NS}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="{titulo}" sheetId="1" r:id="rId1"/></sheets></workbook>')
        out.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        out.writestr('xl/worksheets/sheet1.xml', ET.tostring(hoja))


def copiar_pib_alterado(origen, destino, cambios):
    destino.mkdir()
    for path in origen.glob('*.xlsx'):
        if path.name != '5_PIB_total_por_departamento.xlsx':
            shutil.copyfile(path, destino / path.name)
            continue
        with ZipFile(path) as source, ZipFile(destino / path.name, 'w', ZIP_DEFLATED) as out:
            for item in source.infolist():
                contenido = source.read(item.filename)
                if item.filename == 'xl/worksheets/sheet2.xml':
                    hoja = ET.fromstring(contenido)
                    for referencia, valor in cambios.items():
                        cell = hoja.find(f'.//{{{NS}}}c[@r="{referencia}"]')
                        cell.clear()
                        cell.set('r', referencia)
                        if isinstance(valor, str):
                            cell.set('t', 'inlineStr')
                            ET.SubElement(ET.SubElement(cell, f'{{{NS}}}is'), f'{{{NS}}}t').text = valor
                        elif valor is not None:
                            ET.SubElement(cell, f'{{{NS}}}v').text = str(valor)
                    contenido = ET.tostring(hoja)
                out.writestr(item, contenido)
