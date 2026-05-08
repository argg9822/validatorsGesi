import random

ESPACIO_EDUCATIVO   = "03"
ESPACIO_COMUNITARIO = "04"

TIPOS_CON_GRADO = {
    "1633",   # 1 - Jardines
    "1634",   # 2 - Colegios
    "1635",   # 3 - Universidades
}

NOMBRES_EDUCATIVOS = [
    "CUARTO", "QUINTO", "SEXTO", "SEPTIMO",
    "OCTAVO", "NOVENO", "DECIMO",
    "PRIMERO", "SEGUNDO", "TERCERO",
]


def validarNombreGrupo(
    driver,
    id_nombre_grupo: str,
    id_tipo_inst: str,
    espacio_fic_value: str,
    leerTexto,
    leerValue,
    log_fn=None,
) -> list[tuple]:
    """
    Espacio 03 (Educativo):
      - Tipo Jardines/Colegios/Universidades → inserta grado aleatorio si está vacío.
      - Cualquier otro tipo                  → inserta 'NO APLICA' si está vacío.
      - Si ya tiene valor                    → no toca nada.

    Espacio 04 (Comunitario):
      - Vacío  → inserta 'NO APLICA'.
      - Lleno  → no toca nada.

    Otros espacios → no aplica ninguna regla.

    Retorna lista de tuplas (campo, valor_original, mensaje, corregido).
    """
    if espacio_fic_value not in (ESPACIO_EDUCATIVO, ESPACIO_COMUNITARIO):
        return []

    if not id_nombre_grupo:
        return [("Nombre del Grupo", "", "No se pudo detectar el ID del campo", False)]

    valor_actual = leerTexto(id_nombre_grupo).strip()

    # ── Espacio comunitario ───────────────────────────────────────────────────
    if espacio_fic_value == ESPACIO_COMUNITARIO:
        if valor_actual:
            return []   # lleno → no tocar
        corregido = _insertarValor(driver, id_nombre_grupo, "NO APLICA", log_fn)
        return [(
            "Nombre del Grupo", "",
            "Espacio comunitario (04): campo vacío, se asignó 'NO APLICA'",
            corregido,
        )]

    # ── Espacio educativo ─────────────────────────────────────────────────────
    if valor_actual:
        return []   # lleno → no tocar

    tipo_inst_value = leerValue(id_tipo_inst).strip() if id_tipo_inst else ""
    tipo_inst_texto = leerTexto(id_tipo_inst).strip() if id_tipo_inst else ""

    if tipo_inst_value in TIPOS_CON_GRADO:
        valor_nuevo = random.choice(NOMBRES_EDUCATIVOS)
        motivo = (
            f"Espacio educativo (03) con '{tipo_inst_texto}': "
            f"campo vacío, se asignó '{valor_nuevo}'"
        )
    else:
        valor_nuevo = "NO APLICA"
        motivo = (
            f"Espacio educativo (03) con '{tipo_inst_texto}': "
            f"campo vacío, se asignó 'NO APLICA'"
        )

    corregido = _insertarValor(driver, id_nombre_grupo, valor_nuevo, log_fn)
    return [("Nombre del Grupo", "", motivo, corregido)]


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