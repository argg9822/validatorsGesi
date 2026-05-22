# validarComponente.py

import re

# Números de componente (visibles en el texto de la opción) que obligan a
# tener datos en Hombres/Mujeres/Intersexuales.
# El texto tiene la forma "272- Sesiones Educativas_Cuidarte", por lo que
# se extrae el número inicial antes del guion.
NUMEROS_CON_REQUISITO = {"272", "273", "274"}

_RE_NUMERO_INICIAL = re.compile(r"^\s*(\d+)\s*-")

# Cada grupo une un componente con sus 3 campos de género
GRUPOS = [
    {
        "componente":    "componente_1",
        "label_comp":    "Componente (c6)",
        "hombres":       "hombres_1",
        "mujeres":       "mujeres_1",
        "intersexuales": "intersexuales_1",
        "sufijos":       ("c9", "c10", "c11"),
    },
    {
        "componente":    "componente_2",
        "label_comp":    "Componente (c26)",
        "hombres":       "hombres_2",
        "mujeres":       "mujeres_2",
        "intersexuales": "intersexuales_2",
        "sufijos":       ("c29", "c30", "c31"),
    },
    {
        "componente":    "componente_3",
        "label_comp":    "Componente (c46)",
        "hombres":       "hombres_3",
        "mujeres":       "mujeres_3",
        "intersexuales": "intersexuales_3",
        "sufijos":       ("c49", "c50", "c51"),
    },
    {
        "componente":    "componente_4",
        "label_comp":    "Componente (c66)",
        "hombres":       "hombres_4",
        "mujeres":       "mujeres_4",
        "intersexuales": "intersexuales_4",
        "sufijos":       ("c69", "c70", "c71"),
    },
]


def _es_numerico(valor: str) -> bool:
    try:
        int(valor)
        return True
    except ValueError:
        return False


def _numero_componente(texto: str) -> str:
    """Extrae el número inicial del texto de la opción, p.ej. '272- Sesiones...' → '272'."""
    m = _RE_NUMERO_INICIAL.match(texto)
    return m.group(1) if m else ""


def _corregirIntersexuales(driver, element_id: str, log_fn=None) -> bool:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from liveValidator.helpers.guardar import guardarCambios

    try:
        el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        el.clear()
        el.send_keys("0")
        if log_fn:
            log_fn("      🔧 Intersexuales → '0'")
        return guardarCambios(driver, log_fn)
    except Exception as e:
        if log_fn:
            log_fn(f"      ❌ Error corrigiendo Intersexuales: {e}")
        return False


def validarComponente(driver, ids: dict, leerTexto, log_fn=None) -> list[tuple]:
    """
    Para cada uno de los 4 grupos de componente:
      - Extrae el número del texto visible de la opción seleccionada.
      - Si ese número NO es 272, 273 ni 274:
          · Hombres, Mujeres e Intersexuales deben estar vacíos; si tienen valor → error.
      - Si ese número es 272, 273 o 274:
          · Hombres y Mujeres deben tener dato numérico (sin autocorrección).
          · Intersexuales vacío + Hombres y Mujeres numéricos → se corrige a '0'.
          · Intersexuales vacío + algún otro campo incompleto → error sin corregir.
          · Intersexuales no numérico (no vacío) → error sin corregir.

    Retorna lista de tuplas (campo, valor_original, mensaje, corregido).
    """
    errores = []

    for grupo in GRUPOS:
        id_comp = ids.get(grupo["componente"], "")
        if not id_comp:
            continue

        texto_comp = leerTexto(id_comp).strip()
        numero_comp = _numero_componente(texto_comp)

        sc_h, sc_m, sc_i = grupo["sufijos"]
        label_h = f"Hombres ({sc_h})"
        label_m = f"Mujeres ({sc_m})"
        label_i = f"Intersexuales ({sc_i})"

        id_h = ids.get(grupo["hombres"], "")
        id_m = ids.get(grupo["mujeres"], "")
        id_i = ids.get(grupo["intersexuales"], "")

        raw_h = leerTexto(id_h).strip() if id_h else ""
        raw_m = leerTexto(id_m).strip() if id_m else ""
        raw_i = leerTexto(id_i).strip() if id_i else ""

        if numero_comp not in NUMEROS_CON_REQUISITO:
            if texto_comp:
                for label, raw in [(label_h, raw_h), (label_m, raw_m), (label_i, raw_i)]:
                    if raw:
                        msg = (
                            f"Componente '{texto_comp}' no requiere dato en '{label}' "
                            f"pero tiene: '{raw}'"
                        )
                        if log_fn:
                            log_fn(f"      ⚠️  {label}: '{raw}' — debe estar vacío para este componente")
                        errores.append((label, raw, msg, False))
            continue

        if log_fn:
            log_fn(
                f"      🔍 {grupo['label_comp']}: '{texto_comp}' "
                f"→ requiere {label_h} / {label_m} / {label_i}"
            )

        hombres_ok  = bool(raw_h) and _es_numerico(raw_h)
        mujeres_ok  = bool(raw_m) and _es_numerico(raw_m)

        # ── Hombres ───────────────────────────────────────────────────────────
        if not id_h:
            errores.append((label_h, "", f"No se pudo detectar el ID del campo", False))
        elif not hombres_ok:
            msg = (
                f"Componente '{texto_comp}' requiere dato numérico en 'Hombres' "
                f"pero tiene: '{raw_h or '(vacío)'}'"
            )
            if log_fn:
                log_fn(f"      ⚠️  {label_h}: '{raw_h or '(vacío)'}' — no es numérico")
            errores.append((label_h, raw_h, msg, False))

        # ── Mujeres ───────────────────────────────────────────────────────────
        if not id_m:
            errores.append((label_m, "", f"No se pudo detectar el ID del campo", False))
        elif not mujeres_ok:
            msg = (
                f"Componente '{texto_comp}' requiere dato numérico en 'Mujeres' "
                f"pero tiene: '{raw_m or '(vacío)'}'"
            )
            if log_fn:
                log_fn(f"      ⚠️  {label_m}: '{raw_m or '(vacío)'}' — no es numérico")
            errores.append((label_m, raw_m, msg, False))

        # ── Intersexuales ─────────────────────────────────────────────────────
        if not id_i:
            errores.append((label_i, "", "No se pudo detectar el ID del campo", False))
        elif not raw_i:
            if hombres_ok and mujeres_ok:
                if log_fn:
                    log_fn(f"      ⚠️  {label_i}: vacío — corrigiendo a '0'...")
                corregido = _corregirIntersexuales(driver, id_i, log_fn)
                errores.append((
                    label_i, "",
                    f"Componente '{texto_comp}': Intersexuales vacío, se asignó '0'",
                    corregido,
                ))
            else:
                if log_fn:
                    log_fn(f"      ⚠️  {label_i}: vacío — no es numérico")
                errores.append((
                    label_i, "",
                    f"Componente '{texto_comp}' requiere dato numérico en 'Intersexuales' "
                    f"pero está vacío",
                    False,
                ))
        elif not _es_numerico(raw_i):
            msg = (
                f"Componente '{texto_comp}' requiere dato numérico en 'Intersexuales' "
                f"pero tiene: '{raw_i}'"
            )
            if log_fn:
                log_fn(f"      ⚠️  {label_i}: '{raw_i}' — no es numérico")
            errores.append((label_i, raw_i, msg, False))

    return errores
