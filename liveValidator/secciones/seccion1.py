from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from liveValidator.helpers.camposPorLabel import resolverIDs, LABELS_SECCION_1
from liveValidator.helpers.guardar import guardarCambios
from liveValidator.helpers.validarNombreGrupo import validarNombreGrupo  # ← nuevo

ID_ESPACIO_FIC        = "Espacio_fic"
BARRA_NO_APLICA_VALUE = "4116"
BARRA_NO_APLICA_TEXTO = "10 - No aplica"
ESPACIO_COMUNITARIO   = "04"


def _corregirBarraFutbolera(driver, id_barra: str, log_fn=None) -> bool:
    try:
        el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, id_barra))
        )
        Select(el).select_by_value(BARRA_NO_APLICA_VALUE)
        if log_fn:
            log_fn(f"      🔧 Barra futbolera corregida a '{BARRA_NO_APLICA_TEXTO}'")
        return guardarCambios(driver, log_fn)
    except Exception as e:
        if log_fn:
            log_fn(f"      ❌ Error al corregir barra futbolera: {e}")
        return False


def validarBarraFutbolera(driver, id_barra: str, espacio_fic_value: str,
                           log_fn=None) -> list[tuple]:
    if espacio_fic_value == ESPACIO_COMUNITARIO:
        return []

    if not id_barra:
        return [("Barra futbolera", "", "No se pudo detectar el ID del campo", False)]

    errores = []
    try:
        el           = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, id_barra))
        )
        sel          = Select(el)
        value_actual = sel.first_selected_option.get_attribute("value")
        texto_actual = sel.first_selected_option.text.strip()

        if value_actual != BARRA_NO_APLICA_VALUE:
            if log_fn:
                log_fn(f"      ⚠️  Barra futbolera: '{texto_actual}' — corrigiendo...")
            corregido = _corregirBarraFutbolera(driver, id_barra, log_fn)
            errores.append((
                "Barra futbolera",
                texto_actual,
                f"Espacio '{espacio_fic_value}' requiere '{BARRA_NO_APLICA_TEXTO}' "
                f"pero tenía '{texto_actual}'",
                corregido,
            ))
    except Exception as e:
        if log_fn:
            log_fn(f"      ❌ Error leyendo barra futbolera: {e}")
        errores.append(("Barra futbolera", "", f"No se pudo leer el campo: {e}", False))

    return errores


def validarSeccion1(driver, ficha: str, page_num: int, digitador: str,
                    helpers: dict) -> list[tuple]:
    leerValue = helpers["leerValue"]
    leerTexto = helpers["leerTexto"]
    log_fn    = helpers.get("log")

    ids = resolverIDs(driver, LABELS_SECCION_1, log_fn)

    espacio_fic_value = leerValue(ID_ESPACIO_FIC)
    id_barra          = ids.get("barra_futbolera", "")
    id_nombre_grupo   = ids.get("nombre_grupo", "")

    errores = []

    # ── Validación 1: barra futbolera ─────────────────────────────────────────
    for r in validarBarraFutbolera(driver, id_barra, espacio_fic_value, log_fn):
        errores.append(r)

    # ── Validación 2: nombre del grupo ────────────────────────────────────────
    for r in validarNombreGrupo(
            driver, id_nombre_grupo, espacio_fic_value, leerTexto, log_fn):
        errores.append(r)

    return errores