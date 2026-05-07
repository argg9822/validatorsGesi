# ── Reglas ────────────────────────────────────────────────────────────────────
# Si Espacio_fic == "04" → ocupación DEBE ser "No aplica" (value "1063")
# Si está incorrecto, se corrige automáticamente.
#
# Si Espacio_fic != "04":
#   1063 "12- No aplica"         → no hay restricción de edad/sexo
#   900  "1- Trabajo formal"     → edad >= 18
#   901  "2- Trabajo informal"   → edad >= 14
#   902  "3- Estudiante"         → sin restricción
#   903  "4- Oficios del hogar"  → sin restricción
#   904  "5- Desempleado(a)"     → edad >= 18
#   905  "6- Pensionado(a)"      → mujer >= 57 | hombre >= 62
#   906  "7- Madre comunitaria"  → sexo mujer y edad >= 16
#   907  "8- Cesante"            → sin restricción
#   908  "9- Empleado(a)"        → edad >= 18
#   1061 "10- Incapacitado..."   → edad >= 18
#                                   + categoría discapacidad != "No aplica"
#                                   + "Discapacidad" seleccionado en población diferencial
#   1062 "11- Ninguno"           → sin restricción
#   otros valores                → sin restricción

from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ── Values de referencia ──────────────────────────────────────────────────────
ESPACIO_FIC_COMUNITARIO      = "04"
OCUPACION_NO_APLICA          = "1063"
OCUPACION_ID                 = "valorControl19401"
CATEGORIA_DISC_NO_APLICA     = "3822"
POBLACION_DISCAPACIDAD_VALUE = "108"
SEXO_MUJER                   = "68"
SEXO_HOMBRE                  = "67"

def _corregirOcupacionNoAplica(driver) -> bool:
    """
    Selecciona 'No aplica' en el select de Ocupación y guarda.
    Retorna True si la corrección fue exitosa, False si falló.
    """
    try:
        select_el = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, OCUPACION_ID))
        )
        Select(select_el).select_by_value(OCUPACION_NO_APLICA)

        # Guardar
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "botonActualizarInformacion"))
        ).click()

        # Confirmar el popup OK si aparece
        try:
            WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[contains(text(), "OK")]')
                )
            ).click()
        except:
            pass  # algunos formularios no muestran popup

        return True

    except Exception as e:
        print(f"   ❌ No se pudo corregir Ocupación: {e}")
        return False


def validarOcupacion(
    driver,
    espacio_fic_value: str,
    ocupacion_value: str,
    ocupacion_texto: str,
    edad: int,
    sexo_value: str,
    categoria_disc_value: str,
    poblacion_diferencial_values: list[str],
) -> list[tuple[str, str, str, str]]:
    """
    Valida el campo Ocupación según las reglas de negocio.
    Si el espacio es comunitario y la ocupación es incorrecta, la corrige.

    Parámetros:
        driver                      : instancia WebDriver (necesario para corregir)
        espacio_fic_value           : value de Espacio_fic
        ocupacion_value             : value del <option> seleccionado en Ocupación
        ocupacion_texto             : texto visible del <option>
        edad                        : edad en años completos
        sexo_value                  : value del <option> seleccionado en Sexo
        categoria_disc_value        : value seleccionado en Categoría discapacidad
        poblacion_diferencial_values: lista de values seleccionados en Población diferencial

    Retorna:
        Lista de tuplas (campo, valor_registrado, mensaje_error, corregido).
        'corregido' es "Sí", "No" o "No aplica".
        Lista vacía si todo está correcto.
    """
    errores = []

    # ── Caso 1: espacio comunitario → ocupación debe ser "No aplica" ──────────
    if espacio_fic_value == ESPACIO_FIC_COMUNITARIO:
        if ocupacion_value != OCUPACION_NO_APLICA:
            corregido = _corregirOcupacionNoAplica(driver)
            errores.append((
                "Ocupación",
                ocupacion_texto,
                f"Espacio comunitario (04) requiere Ocupación 'No aplica', "
                f"pero estaba '{ocupacion_texto}'",
                "Sí" if corregido else "No",
            ))
        return errores  # no hay más validaciones para espacio 04

    # ── Caso 2: espacio != 04 → validar según ocupación ──────────────────────
    # Las tuplas aquí no necesitan corrección → corregido = "No aplica"

    if ocupacion_value == "900":        # Trabajo formal → >= 18
        if edad < 18:
            errores.append((
                "Ocupación", ocupacion_texto,
                f"'Trabajo formal' requiere edad >= 18 años (paciente tiene {edad} años)",
                "No aplica",
            ))

    elif ocupacion_value == "901":      # Trabajo informal → >= 14
        if edad < 14:
            errores.append((
                "Ocupación", ocupacion_texto,
                f"'Trabajo informal' requiere edad >= 14 años (paciente tiene {edad} años)",
                "No aplica",
            ))

    elif ocupacion_value == "904":      # Desempleado(a) → >= 18
        if edad < 18:
            errores.append((
                "Ocupación", ocupacion_texto,
                f"'Desempleado(a)' requiere edad >= 18 años (paciente tiene {edad} años)",
                "No aplica",
            ))

    elif ocupacion_value == "905":      # Pensionado(a)
        if sexo_value == SEXO_MUJER and edad < 57:
            errores.append((
                "Ocupación", ocupacion_texto,
                f"'Pensionado(a)' para mujer requiere edad >= 57 años (paciente tiene {edad} años)",
                "No aplica",
            ))
        elif sexo_value == SEXO_HOMBRE and edad < 62:
            errores.append((
                "Ocupación", ocupacion_texto,
                f"'Pensionado(a)' para hombre requiere edad >= 62 años (paciente tiene {edad} años)",
                "No aplica",
            ))
        elif sexo_value not in (SEXO_MUJER, SEXO_HOMBRE):
            errores.append((
                "Ocupación / Sexo", ocupacion_texto,
                "'Pensionado(a)' requiere sexo Hombre o Mujer para validar edad mínima",
                "No aplica",
            ))

    elif ocupacion_value == "906":      # Madre comunitaria → mujer y >= 16
        if sexo_value != SEXO_MUJER:
            errores.append((
                "Ocupación / Sexo", ocupacion_texto,
                "'Madre comunitaria' solo aplica para sexo Mujer",
                "No aplica",
            ))
        if edad < 16:
            errores.append((
                "Ocupación", ocupacion_texto,
                f"'Madre comunitaria' requiere edad >= 16 años (paciente tiene {edad} años)",
                "No aplica",
            ))

    elif ocupacion_value == "908":      # Empleado(a) → >= 18
        if edad < 18:
            errores.append((
                "Ocupación", ocupacion_texto,
                f"'Empleado(a)' requiere edad >= 18 años (paciente tiene {edad} años)",
                "No aplica",
            ))

    elif ocupacion_value == "1061":     # Incapacitado permanente
        if edad < 18:
            errores.append((
                "Ocupación", ocupacion_texto,
                f"'Incapacitado permanente' requiere edad >= 18 años (paciente tiene {edad} años)",
                "No aplica",
            ))
        if categoria_disc_value == CATEGORIA_DISC_NO_APLICA:
            errores.append((
                "Ocupación / Categoría discapacidad", ocupacion_texto,
                "'Incapacitado permanente' requiere Categoría discapacidad diferente a 'No aplica'",
                "No aplica",
            ))
        if POBLACION_DISCAPACIDAD_VALUE not in poblacion_diferencial_values:
            errores.append((
                "Ocupación / Población diferencial", ocupacion_texto,
                "'Incapacitado permanente' requiere 'Discapacidad' en Población diferencial",
                "No aplica",
            ))

    return errores