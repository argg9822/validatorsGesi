# validarCoherenciaSesiones.py

from datetime import datetime

FORMATOS_FECHA = ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y")

CLAVES_NUM_SESION = [
    "num_sesion_1", "num_sesion_2", "num_sesion_3", "num_sesion_4"
]
CLAVES_FECHA_SESION = [
    "fecha_sesion_1", "fecha_sesion_2", "fecha_sesion_3", "fecha_sesion_4"
]

LABELS_NUM_SESION = [
    "Número de Sesión (c4)",
    "Número de Sesión (c24)",
    "Número de Sesión (c44)",
    "Número de Sesión (c64)",
]

# Residuo esperado de n % 4 para cada campo (índice 0 = campo 1)
RESIDUOS_NUM_SESION = (1, 2, 3, 0)
LABELS_FECHA_SESION = [
    "Fecha de sesión (c3)",
    "Fecha de sesión (c23)",
    "Fecha de sesión (c43)",
    "Fecha de sesión (c63)",
]


def _parsearFecha(texto: str) -> datetime | None:
    for fmt in FORMATOS_FECHA:
        try:
            return datetime.strptime(texto.strip(), fmt)
        except ValueError:
            continue
    return None


def _leerNums(ids: dict, leerTexto, log_fn) -> tuple[list, list[tuple]]:
    errores = []
    nums = []
    for i, clave in enumerate(CLAVES_NUM_SESION):
        field_id = ids.get(clave, "")
        if not field_id:
            nums.append(None)
            continue
        raw = leerTexto(field_id).strip()
        if not raw:
            nums.append(None)
            continue
        try:
            nums.append(int(raw))
        except ValueError:
            nums.append(None)
            errores.append((
                LABELS_NUM_SESION[i], raw,
                f"No es un número entero válido: '{raw}'",
                False,
            ))
    return nums, errores


def _leerFechas(ids: dict, leerTexto, log_fn) -> tuple[list, list[tuple]]:
    errores = []
    fechas = []
    for i, clave in enumerate(CLAVES_FECHA_SESION):
        field_id = ids.get(clave, "")
        if not field_id:
            fechas.append(None)
            continue
        raw = leerTexto(field_id).strip()
        if not raw:
            fechas.append(None)
            continue
        dt = _parsearFecha(raw)
        if dt is None:
            fechas.append(None)
            errores.append((
                LABELS_FECHA_SESION[i], raw,
                f"No se pudo interpretar la fecha: '{raw}'",
                False,
            ))
        else:
            fechas.append(dt)
    return fechas, errores


def _corregirFecha(driver, element_id: str, valor: str, log_fn=None) -> bool:
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
            log_fn(f"      🔧 Fecha de sesión 1 → '{valor}'")
        return guardarCambios(driver, log_fn)
    except Exception as e:
        if log_fn:
            log_fn(f"      ❌ Error corrigiendo Fecha de sesión 1: {e}")
        return False


def sincronizarFechaSesion1(driver, ids: dict, leerTexto, leerOculto,
                             log_fn=None) -> list[tuple]:
    """
    Si el número de la sesión 1 es 1, verifica que su fecha coincida con el
    campo oculto FechaIntervencion. De no coincidir, la corrige antes de que
    se valide la coherencia entre sesiones.

    Retorna lista de tuplas (campo, valor_original, mensaje, corregido).
    """
    id_num   = ids.get("num_sesion_1", "")
    id_fecha = ids.get("fecha_sesion_1", "")

    if not id_num or not id_fecha:
        return []

    if leerTexto(id_num).strip() != "1":
        return []

    fecha_intervencion = leerOculto("FechaIntervencion").strip()
    fecha_sesion       = leerTexto(id_fecha).strip()

    if not fecha_intervencion:
        return []

    dt_intervencion = _parsearFecha(fecha_intervencion)
    dt_sesion       = _parsearFecha(fecha_sesion)

    if dt_intervencion is None or dt_intervencion == dt_sesion:
        return []

    if log_fn:
        log_fn(
            f"      ⚠️  Fecha sesión 1: '{fecha_sesion}' ≠ "
            f"FechaIntervencion '{fecha_intervencion}' — corrigiendo..."
        )

    corregido = _corregirFecha(driver, id_fecha, fecha_intervencion, log_fn)
    return [(
        LABELS_FECHA_SESION[0],
        fecha_sesion,
        f"Sesión 1: fecha '{fecha_sesion}' no coincide con "
        f"FechaIntervencion '{fecha_intervencion}'",
        corregido,
    )]


def validarCoherenciaSesiones(ids: dict, leerTexto, log_fn=None) -> list[tuple]:
    """
    Valida que los números de sesión estén en orden estrictamente ascendente
    y que las fechas de sesión no sean decrecientes (iguales está permitido)
    entre los 4 campos de sesión de la página actual.

    Ignora los campos vacíos o sin ID; solo compara pares donde ambos tienen valor.

    Retorna lista de tuplas (campo, valor_original, mensaje, corregido).
    """
    errores = []

    # ── Números de sesión ─────────────────────────────────────────────────────
    nums, errs_parse = _leerNums(ids, leerTexto, log_fn)
    errores.extend(errs_parse)

    for i, n in enumerate(nums):
        if n is None:
            continue
        esperado = RESIDUOS_NUM_SESION[i]
        if n % 4 != esperado:
            validos = ", ".join(str(esperado + 4 * k) for k in range(5))
            msg = (
                f"Número de sesión inválido para este campo: {n}. "
                f"Solo se permiten {validos}…"
            )
            if log_fn:
                log_fn(f"      ⚠️  {LABELS_NUM_SESION[i]}: {n} no es válido para este campo")
            errores.append((LABELS_NUM_SESION[i], str(n), msg, False))

    for i in range(len(nums) - 1):
        a, b = nums[i], nums[i + 1]
        if a is None or b is None:
            continue
        if a >= b:
            msg = (
                f"Número de sesión fuera de secuencia: "
                f"campo {i + 2} ({b}) debe ser mayor que campo {i + 1} ({a})"
            )
            if log_fn:
                log_fn(f"      ⚠️  {LABELS_NUM_SESION[i + 1]}: {b} ≤ {a}")
            errores.append((LABELS_NUM_SESION[i + 1], str(b), msg, False))

    # ── Fechas de sesión ──────────────────────────────────────────────────────
    fechas, errs_parse = _leerFechas(ids, leerTexto, log_fn)
    errores.extend(errs_parse)

    for i in range(len(fechas) - 1):
        a, b = fechas[i], fechas[i + 1]
        if a is None or b is None:
            continue
        if a > b:
            fmt_a = a.strftime(FORMATOS_FECHA[0])
            fmt_b = b.strftime(FORMATOS_FECHA[0])
            msg = (
                f"Fecha fuera de secuencia: "
                f"campo {i + 2} ({fmt_b}) no puede ser anterior a campo {i + 1} ({fmt_a})"
            )
            if log_fn:
                log_fn(f"      ⚠️  {LABELS_FECHA_SESION[i + 1]}: {fmt_b} < {fmt_a}")
            errores.append((LABELS_FECHA_SESION[i + 1], fmt_b, msg, False))

    return errores
