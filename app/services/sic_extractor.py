"""Lectura de la lista actual de proveedores propuesta en un SIC DOCX."""

import re
import unicodedata
from typing import TypedDict

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


class SICExtractionError(ValueError):
    """El SIC no permite identificar una lista completa sin ambigüedad."""


class SICProvider(TypedDict):
    nit: str
    company_name: str


def _normalize(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(text.casefold().split())


_SECTION = re.compile(r"^(?:\d+(?:\.\d+)*[.)]?\s+)?seleccion de proveedores\s*:?$")
_LIST = re.compile(r"\blista de proveedores propuesta\b")
_BOUNDARIES = {
    "antecedentes", "banda de precios", "normativa legal/joa",
    "conclusiones", "limite de competencia interna", "proposicion",
    "consideraciones del comite de contratacion",
    "consideraciones adicionales del comite de contrataciones",
    "firma del comite de contratacion",
}


def _is_boundary(paragraph, text):
    title = re.sub(r"^\d+(?:\.\d+)*[.)]?\s+", "", text).rstrip(":")
    if title in _BOUNDARIES:
        return True
    style = paragraph.style
    while style is not None:
        properties = style.element.pPr
        if properties is not None and properties.find(qn("w:outlineLvl")) is not None:
            return True
        style = style.base_style
    return False


def _headers(row):
    result = {}
    seen = set()
    for index, cell in enumerate(row.cells):
        if cell._tc in seen:
            continue
        seen.add(cell._tc)
        text = _normalize(cell.text).strip(" :.")
        key = None
        if re.fullmatch(r"n\.?\s*i\.?\s*t\.?", text):
            key = "nit"
        elif text == "razon social":
            key = "company_name"
        if key:
            if key in result:
                raise SICExtractionError("La tabla contiene encabezados duplicados: " + key)
            result[key] = index
    return result


def _read_table(table, table_number):
    headers = None
    providers = []
    used_nits = set()
    used_cells = set()
    for row_number, row in enumerate(table.rows, start=1):
        cells = row.cells
        if not any(cell.text.strip() for cell in cells):
            continue
        found = _headers(row)
        location = f"Tabla {table_number}, fila {row_number}: "
        if found:
            if set(found) != {"nit", "company_name"}:
                raise SICExtractionError(location + "faltan encabezados NIT o RAZÓN SOCIAL.")
            if headers is not None and found != headers:
                raise SICExtractionError(location + "los encabezados cambian dentro de la tabla.")
            headers = found
            continue
        if headers is None:
            # Admitir un título combinado anterior al encabezado, no filas de datos.
            if len({cell._tc for cell in cells}) == 1 and _LIST.search(_normalize(cells[0].text)):
                continue
            raise SICExtractionError(location + "no se identificaron encabezados NIT y RAZÓN SOCIAL.")
        if max(headers.values()) >= len(cells):
            raise SICExtractionError(location + "la fila tiene menos columnas que el encabezado.")
        nit_cell = cells[headers["nit"]]
        name_cell = cells[headers["company_name"]]
        if nit_cell._tc is name_cell._tc or any(
            cell._tc in used_cells for cell in (nit_cell, name_cell)
        ):
            raise SICExtractionError(location + "celdas combinadas ambiguas entre proveedores o campos.")
        nit = nit_cell.text.strip()
        company_name = name_cell.text  # Conservar puntuación, espacios y saltos originales.
        if not nit or not company_name.strip():
            raise SICExtractionError(location + "proveedor incompleto: falta NIT o razón social.")
        if not re.fullmatch(r"[0-9]+", nit):
            raise SICExtractionError(location + "NIT ambiguo; se esperaba una cadena de dígitos.")
        if nit in used_nits:
            raise SICExtractionError(location + "NIT repetido; revise posibles proveedores duplicados.")
        used_nits.add(nit)
        used_cells.update((nit_cell._tc, name_cell._tc))
        providers.append({"nit": nit, "company_name": company_name})
    if headers is None or not providers:
        raise SICExtractionError(f"Tabla {table_number}: lista sin encabezados suficientes o sin proveedores.")
    return providers


def extract_sic_providers(file_path) -> list[SICProvider]:
    """Devuelve NIT/razón social; lanza SICExtractionError sin resultados parciales.

    Acepta una ruta DOCX o un flujo binario. Solo considera tablas dentro de
    SELECCIÓN DE PROVEEDORES, después de LISTA DE PROVEEDORES PROPUESTA.
    No usa nombres de archivo, índices fijos ni cantidades históricas.
    """
    document = Document(file_path)
    in_section = False
    sections = 0
    list_seen = False
    pending_list = False
    candidates = []
    table_number = 0
    for element in document.element.body:
        if element.tag == qn("w:p"):
            paragraph = Paragraph(element, document)
            text = _normalize(paragraph.text)
            if _SECTION.fullmatch(text):
                sections += 1
                in_section = True
                list_seen = False
                pending_list = False
            elif in_section and _LIST.search(text):
                list_seen = True
                pending_list = True
            elif in_section and _is_boundary(paragraph, text):
                if pending_list:
                    raise SICExtractionError("Referencia a lista propuesta sin una tabla asociada.")
                in_section = False
        elif element.tag == qn("w:tbl"):
            table_number += 1
            if not in_section or not list_seen:
                continue
            table = Table(element, document)
            has_headers = any(_headers(row) for row in table.rows)
            if pending_list or has_headers:
                candidates.append((table_number, table))
                pending_list = False
    if sections != 1:
        raise SICExtractionError(
            "No se encontró una única sección SELECCIÓN DE PROVEEDORES "
            f"(se encontraron {sections})."
        )
    if pending_list:
        raise SICExtractionError("Referencia a lista propuesta sin una tabla asociada.")
    if not candidates:
        raise SICExtractionError("No se encontró la tabla de LISTA DE PROVEEDORES PROPUESTA en la sección actual.")
    if len(candidates) != 1:
        raise SICExtractionError(f"Se encontraron {len(candidates)} listas candidatas; requiere revisión.")
    table_number, table = candidates[0]
    return _read_table(table, table_number)
