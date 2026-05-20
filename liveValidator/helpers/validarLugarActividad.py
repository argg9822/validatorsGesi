from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from liveValidator.helpers.guardar import guardarCambios

ESPACIO_EDUCATIVO  = "03"
MIN_CHARS_LUGAR    = 3

# Values de Tipo de Institución que obligan a dejar Lugar vacío
TIPOS_SIN_LUGAR = {
    "1633",   # 1 - Jardines
    "1634",   # 2 - Colegios
    "1635",   # 3 - Universidades
}


def _borrarLugar(driver, id_lugar: str, log_fn=None) -> bool:
    try:
        el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, id_lugar))
        )
        el.clear()
        if log_fn:
            log_fn("      🔧 Lugar de la actividad borrado")
        return guardarCambios(driver, log_fn)
    except Exception as e:
        if log_fn:
            log_fn(f"      ❌ Error al borrar Lugar de la actividad: {e}")
        return False


def validarLugarActividad(
    driver,
    id_tipo_inst: str,
    id_lugar: str,
    espacio_fic_value: str,
    leerTexto,
    leerValue,
    log_fn=None,
) -> list[tuple]:
    """
    Valida el campo Lugar de la actividad según espacio y tipo de institución.

    Espacio 03 (Educativo):
      - Tipo Jardines / Colegios / Universidades → lugar DEBE estar vacío.
        Si tiene contenido → se borra.
      - Cualquier otro tipo → lugar DEBE tener más de 3 caracteres.

    Cualquier otro espacio:
      → lugar DEBE tener más de 3 caracteres siempre.

    Retorna lista de tuplas (campo, valor_original, mensaje, corregido).
    """
    errores = []

    if not id_lugar:
        return [("Lugar de la actividad", "",
                 "No se pudo detectar el ID del campo", False)]

    lugar_actual = leerTexto(id_lugar).strip()

    if espacio_fic_value == ESPACIO_EDUCATIVO:

        tipo_inst_value = leerValue(id_tipo_inst) if id_tipo_inst else ""
        tipo_inst_texto = leerTexto(id_tipo_inst).strip() if id_tipo_inst else ""

        if tipo_inst_value in TIPOS_SIN_LUGAR:
            # Jardines / Colegios / Universidades → lugar debe estar vacío
            if lugar_actual:
                if log_fn:
                    log_fn(f"      ⚠️  Lugar de la actividad: '{lugar_actual}' "
                           f"debe estar vacío para '{tipo_inst_texto}' — borrando...")
                corregido = _borrarLugar(driver, id_lugar, log_fn)
                errores.append((
                    "Lugar de la actividad",
                    lugar_actual,
                    f"Con '{tipo_inst_texto}' el campo debe estar vacío, "
                    f"pero contenía: '{lugar_actual}'",
                    corregido,
                ))
        else:
            # Otro tipo de institución educativa → debe tener contenido
            if len(lugar_actual) <= MIN_CHARS_LUGAR:
                if log_fn:
                    log_fn(f"      ⚠️  Lugar de la actividad vacío o muy corto "
                           f"para '{tipo_inst_texto}'")
                errores.append((
                    "Lugar de la actividad",
                    lugar_actual,
                    f"Con '{tipo_inst_texto}' el campo debe tener más de "
                    f"{MIN_CHARS_LUGAR} caracteres (actual: '{lugar_actual}')",
                    False,
                ))

    else:
        # Cualquier otro espacio → siempre debe tener contenido
        if len(lugar_actual) <= MIN_CHARS_LUGAR:
            if log_fn:
                log_fn(f"      ⚠️  Lugar de la actividad vacío o muy corto "
                       f"(espacio {espacio_fic_value})")
            errores.append((
                "Lugar de la actividad",
                lugar_actual,
                f"El campo debe tener más de {MIN_CHARS_LUGAR} caracteres "
                f"(actual: '{lugar_actual}')",
                False,
            ))

    return errores