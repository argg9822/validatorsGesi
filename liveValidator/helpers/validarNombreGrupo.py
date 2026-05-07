import random

ESPACIO_EDUCATIVO   = "03"
ESPACIO_COMUNITARIO = "04"

NOMBRES_EDUCATIVOS = [
    "CUARTO", "QUINTO", "SEXTO", "SEPTIMO",
    "OCTAVO", "NOVENO", "DECIMO",
    "PRIMERO", "SEGUNDO", "TERCERO",
]


def validarNombreGrupo(
    driver,
    id_nombre_grupo: str,
    espacio_fic_value: str,
    leerTexto,
    log_fn=None,
) -> list[tuple]:
    """
    Valida y corrige el campo Nombre del Grupo según el espacio:

      Espacio 03 (Educativo)  → si está vacío, inserta un grado aleatorio.
      Espacio 04 (Comunitario)→ si está vacío, inserta "NO APLICA".
      Otros espacios          → no aplica ninguna regla.

    Retorna lista de tuplas (campo, valor_original, mensaje, corregido).
    """
    if espacio_fic_value not in (ESPACIO_EDUCATIVO, ESPACIO_COMUNITARIO):
        return []

    if not id_nombre_grupo:
        return [("Nombre del Grupo", "", "No se pudo detectar el ID del campo", False)]

    errores = []

    valor_actual = leerTexto(id_nombre_grupo).strip()

    if valor_actual:
        return []   # campo ya tiene valor, no hay nada que hacer

    # ── Campo vacío → corregir ────────────────────────────────────────────────
    if espacio_fic_value == ESPACIO_EDUCATIVO:
        valor_nuevo = random.choice(NOMBRES_EDUCATIVOS)
        motivo      = f"Espacio educativo (03): campo vacío, se asignó '{valor_nuevo}'"
    else:
        valor_nuevo = "NO APLICA"
        motivo      = "Espacio comunitario (04): campo vacío, se asignó 'NO APLICA'"

    corregido = _insertarValor(driver, id_nombre_grupo, valor_nuevo, log_fn)
    errores.append(("Nombre del Grupo", "", motivo, corregido))

    return errores


def _insertarValor(driver, element_id: str, valor: str, log_fn=None) -> bool:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from liveValidator.helpers.guardar import guardarCambios

    try:
        el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        el.clear()
        el.send_keys(valor)

        if log_fn:
            log_fn(f"      🔧 Nombre del Grupo → '{valor}'")

        return guardarCambios(driver, log_fn)

    except Exception as e:
        if log_fn:
            log_fn(f"      ❌ Error insertando Nombre del Grupo: {e}")
        return False