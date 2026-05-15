from liveValidator.helpers.camposPorLabel import resolverIDs, LABELS_SECCION_3
from liveValidator.helpers.validarTamizajes import validarNumDocContraSeccion2


def validarSeccion3(
    driver,
    ficha: str,
    page_num: int,
    digitador: str,
    documentos_ficha: list,
    helpers: dict,
) -> list:
    """
    Valida la sección 3 (tamizajes) de una ficha para la página page_num.

    documentos_ficha: lista acumulada por la sección 2, cada entrada tiene
        {"ficha", "pagina", "num_doc", ...}.  La página page_num de esta lista
        es la que debe coincidir con la página actual de sección 3.
    """
    leerTexto = helpers["leerTexto"]
    log_fn    = helpers.get("log")

    ids = resolverIDs(driver, LABELS_SECCION_3, log_fn)

    num_doc_s3 = leerTexto(ids.get("num_doc", ""))

    # Buscar el registro de sección 2 que corresponde a esta página
    s2_entry   = next((d for d in documentos_ficha if d["pagina"] == page_num), None)
    num_doc_s2 = s2_entry["num_doc"] if s2_entry else ""

    if s2_entry is None and log_fn:
        log_fn(f"   ⚠️  Sección 3 p.{page_num}: no hay registro de sección 2 para comparar")

    errores = []

    for campo, valor, msg in validarNumDocContraSeccion2(num_doc_s3, num_doc_s2, page_num):
        errores.append((campo, valor, msg))

    # Aquí agregar más validaciones de tamizaje en el futuro
    # for campo, valor, msg in validarOtraRegla(...):
    #     errores.append((campo, valor, msg))

    return errores
