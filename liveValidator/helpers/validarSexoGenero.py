# ── Reglas ────────────────────────────────────────────────────────────────────
# Género, Orientación sexual e Identidad de género deben ser "No aplica"
# cuando el paciente tiene MENOS de 14 años.
# Cuando tiene 14 años o más, NINGUNO de los tres puede ser "No aplica".
#
# IDs de los campos:
#   Género            : valorControl19390   (No aplica = value "4513")
#   Orientación sexual: valorControl19391   (No aplica = value "4028")
#   Identidad género  : valorControl19392   (No aplica = value "4020")

EDAD_MINIMA = 14

# Mapeo campo → value que representa "No aplica" en ese select
NO_APLICA_VALUES = {
    "valorControl19390": "4513",   # Género
    "valorControl19391": "4028",   # Orientación sexual
    "valorControl19392": "4020",   # Identidad de género
}

# Nombre legible de cada campo para los mensajes de error
NOMBRE_CAMPO = {
    "valorControl19390": "Género",
    "valorControl19391": "Orientación sexual",
    "valorControl19392": "Identidad de género",
}


def validarSexoGenero(
    genero_value: str,
    orientacion_value: str,
    identidad_value: str,
    edad: int,
    genero_texto: str = "",
    orientacion_texto: str = "",
    identidad_texto: str = "",
) -> list[tuple[str, str, str]]:
    """
    Valida que Género, Orientación sexual e Identidad de género sean
    coherentes con la edad del paciente.

    Retorna:
        Lista de tuplas (nombre_campo, texto_visible, mensaje_error).
        Lista vacía si todo está correcto.
    """
    entradas = {
        "valorControl19390": (genero_value,      genero_texto),
        "valorControl19391": (orientacion_value,  orientacion_texto),
        "valorControl19392": (identidad_value,    identidad_texto),
    }

    errores = []
    menor   = edad < EDAD_MINIMA

    for campo_id, (value, texto) in entradas.items():
        es_no_aplica = (value == NO_APLICA_VALUES[campo_id])
        nombre       = NOMBRE_CAMPO[campo_id]
        display      = texto if texto else value

        if menor and not es_no_aplica:
            errores.append((
                nombre,
                display,
                f"'{nombre}' debe ser 'No aplica' para menores de {EDAD_MINIMA} años "
                f"(Usuario tiene {edad} años)"
            ))

        elif not menor and es_no_aplica:
            errores.append((
                nombre,
                display,
                f"'{nombre}' no puede ser 'No aplica' para pacientes "
                f"de {EDAD_MINIMA} años o más (Usuario tiene {edad} años)"
            ))

    return errores