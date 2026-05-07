# ── Reglas ────────────────────────────────────────────────────────────────────
# Documentos colombianos (nacionalidad == Colombia, value="50")
#   CC  -> Colombia, >= 18 años
#   TI  -> Colombia, >= 7 y < 18 años
#   RC  -> Colombia, >= 1 y < 8 años
#
# Documentos extranjeros (nacionalidad != Colombia)
#   CE  -> != Colombia, >= 18 años
#   PA  -> != Colombia, cualquier edad
#   PEP -> != Colombia, cualquier edad
#   (cualquier otro doc no-colombiano se acepta si la nacionalidad no es COL)
#
# Errores cruzados detectados:
#   - Doc colombiano (CC/TI/RC) con nacionalidad extranjera
#   - Doc extranjero (CE/PA/PEP) con nacionalidad Colombia
#   - Rango de edad incorrecto para el documento

COLOMBIA_VALUE = "50"   # value del <option> Colombia en el select de nacionalidad

# Documentos que REQUIEREN nacionalidad colombiana
DOCS_COLOMBIANOS = {"CC", "TI", "RC"}

# Documentos que REQUIEREN nacionalidad extranjera
DOCS_EXTRANJEROS = {"CE", "PA", "PEP", "PT", "MS", "CD", "SC"}

# Rangos de edad por documento (min inclusivo, max exclusivo en años)
RANGOS_EDAD = {
    "CC":  (18, 999),
    "TI":  (7,  18),
    "RC":  (1,  8),
    "CE":  (18, 999),
}
# PA, PEP y otros extranjeros no tienen restricción de edad → no están en RANGOS_EDAD


def extraerCodigoDocumento(tipo_doc_raw: str) -> str:
    """
    '1- CC'  -> 'CC'
    '2- TI'  -> 'TI'
    'CC'     -> 'CC'
    """
    if not tipo_doc_raw:
        return ""
    partes = tipo_doc_raw.split("-")
    return partes[1].strip().upper() if len(partes) > 1 else tipo_doc_raw.strip().upper()


def validarTipoDocumento(tipo_doc_raw: str, nacionalidad_value: str, edad: int) -> tuple[bool, str]:
    """
    Valida la combinación tipo de documento + nacionalidad + edad.

    Parámetros:
        tipo_doc_raw       : texto visible del select de tipo doc  (ej. "1- CC")
        nacionalidad_value : value del <option> seleccionado       (ej. "50" para Colombia)
        edad               : edad calculada en años completos

    Retorna:
        (True, "")          si todo está correcto
        (False, "mensaje")  si hay algún error
    """
    codigo     = extraerCodigoDocumento(tipo_doc_raw)
    es_colombia = (nacionalidad_value == COLOMBIA_VALUE)

    if not codigo:
        return False, "Tipo de documento vacío o no reconocido"

    # ── Cruce nacionalidad ────────────────────────────────────────────────────
    if codigo in DOCS_COLOMBIANOS and not es_colombia:
        return False, (
            f"'{codigo}' es un documento colombiano "
            f"pero la nacionalidad registrada no es Colombia"
        )

    if codigo in DOCS_EXTRANJEROS and es_colombia:
        return False, (
            f"'{codigo}' es un documento extranjero "
            f"pero la nacionalidad registrada es Colombia"
        )

    # ── Rango de edad ─────────────────────────────────────────────────────────
    if codigo in RANGOS_EDAD:
        min_e, max_e = RANGOS_EDAD[codigo]
        if not (min_e <= edad < max_e):
            rango_str = f"{min_e}–{max_e - 1} años" if max_e < 999 else f"{min_e}+ años"
            return False, (
                f"'{codigo}' requiere {rango_str} "
                f"pero el usuario tiene {edad} años"
            )

    return True, ""