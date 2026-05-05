# ── Reglas ────────────────────────────────────────────────────────────────────
# Si Espacio_fic == "04" → ocupación DEBE ser "No aplica" (value "1063")
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

# ── Values de referencia ──────────────────────────────────────────────────────
ESPACIO_FIC_COMUNITARIO       = "04"
OCUPACION_NO_APLICA           = "1063"
CATEGORIA_DISC_NO_APLICA      = "3822"
POBLACION_DISCAPACIDAD_VALUE  = "108"   # "2- Discapacidad" en el select múltiple
SEXO_MUJER                    = "68"
SEXO_HOMBRE                   = "67"


def validarOcupacion(
    espacio_fic_value: str,
    ocupacion_value: str,
    ocupacion_texto: str,
    edad: int,
    sexo_value: str,
    categoria_disc_value: str,
    poblacion_diferencial_values: list[str],   # lista de values seleccionados
) -> list[tuple[str, str, str]]:
    """
    Valida el campo Ocupación según las reglas de negocio.

    Parámetros:
        espacio_fic_value           : value de Espacio_fic
        ocupacion_value             : value del <option> seleccionado en Ocupación
        ocupacion_texto             : texto visible del <option> (para el mensaje)
        edad                        : edad en años completos
        sexo_value                  : value del <option> seleccionado en Sexo
        categoria_disc_value        : value del <option> seleccionado en Categoría discapacidad
        poblacion_diferencial_values: lista de values seleccionados en Población diferencial

    Retorna:
        Lista de tuplas (campo, valor_registrado, mensaje_error).
        Lista vacía si todo está correcto.
    """
    errores = []

    # ── Caso 1: espacio comunitario → solo se acepta "No aplica" ─────────────
    if espacio_fic_value == ESPACIO_FIC_COMUNITARIO:
        if ocupacion_value != OCUPACION_NO_APLICA:
            errores.append((
                "Ocupación",
                ocupacion_texto,
                f"El espacio es Comunitario (04), por lo tanto Ocupación "
                f"debe ser 'No aplica', pero está '{ocupacion_texto}'"
            ))
        return errores   # no hay más validaciones para espacio 04

    # ── Caso 2: espacio != 04 → validar según ocupación ─────────────────────

    # Trabajo formal → >= 18
    if ocupacion_value == "900":
        if edad < 18:
            errores.append((
                "Ocupación",
                ocupacion_texto,
                f"'Trabajo formal' requiere edad >= 18 años (paciente tiene {edad} años)"
            ))

    # Trabajo informal → >= 14
    elif ocupacion_value == "901":
        if edad < 14:
            errores.append((
                "Ocupación",
                ocupacion_texto,
                f"'Trabajo informal' requiere edad >= 14 años (paciente tiene {edad} años)"
            ))

    # Desempleado(a) → >= 18
    elif ocupacion_value == "904":
        if edad < 18:
            errores.append((
                "Ocupación",
                ocupacion_texto,
                f"'Desempleado(a)' requiere edad >= 18 años (paciente tiene {edad} años)"
            ))

    # Pensionado(a) → mujer >= 57 | hombre >= 62
    elif ocupacion_value == "905":
        if sexo_value == SEXO_MUJER and edad < 57:
            errores.append((
                "Ocupación",
                ocupacion_texto,
                f"'Pensionado(a)' para mujer requiere edad >= 57 años (paciente tiene {edad} años)"
            ))
        elif sexo_value == SEXO_HOMBRE and edad < 62:
            errores.append((
                "Ocupación",
                ocupacion_texto,
                f"'Pensionado(a)' para hombre requiere edad >= 62 años (paciente tiene {edad} años)"
            ))
        elif sexo_value not in (SEXO_MUJER, SEXO_HOMBRE):
            errores.append((
                "Ocupación / Sexo",
                ocupacion_texto,
                f"'Pensionado(a)' requiere sexo Hombre o Mujer para validar edad mínima"
            ))

    # Madre comunitaria → mujer y >= 16
    elif ocupacion_value == "906":
        if sexo_value != SEXO_MUJER:
            errores.append((
                "Ocupación / Sexo",
                ocupacion_texto,
                "'Madre comunitaria' solo aplica para sexo Mujer"
            ))
        if edad < 16:
            errores.append((
                "Ocupación",
                ocupacion_texto,
                f"'Madre comunitaria' requiere edad >= 16 años (paciente tiene {edad} años)"
            ))

    # Empleado(a) → >= 18
    elif ocupacion_value == "908":
        if edad < 18:
            errores.append((
                "Ocupación",
                ocupacion_texto,
                f"'Empleado(a)' requiere edad >= 18 años (paciente tiene {edad} años)"
            ))

    # Incapacitado permanente para trabajar → >= 18 + discapacidad
    elif ocupacion_value == "1061":
        if edad < 18:
            errores.append((
                "Ocupación",
                ocupacion_texto,
                f"'Incapacitado permanente' requiere edad >= 18 años (paciente tiene {edad} años)"
            ))

        if categoria_disc_value == CATEGORIA_DISC_NO_APLICA:
            errores.append((
                "Ocupación / Categoría discapacidad",
                ocupacion_texto,
                "'Incapacitado permanente' requiere que Categoría discapacidad "
                "sea diferente a 'No aplica'"
            ))

        if POBLACION_DISCAPACIDAD_VALUE not in poblacion_diferencial_values:
            errores.append((
                "Ocupación / Población diferencial",
                ocupacion_texto,
                "'Incapacitado permanente' requiere que 'Discapacidad' esté "
                "seleccionado en Población diferencial"
            ))

    return errores