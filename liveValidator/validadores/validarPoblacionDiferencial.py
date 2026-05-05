# ── Values de referencia ──────────────────────────────────────────────────────
POB_DISCAPACIDAD         = "108"   # 2- Discapacidad
POB_NO_APLICA            = "2620"  # 14- No Aplica
POB_MIGRANTE             = "4051"  # 17- Migrante Internacional

CATEGORIA_DISC_NO_APLICA = "3822"  # 8- No aplica en categoría discapacidad
COLOMBIA_VALUE           = "50"    # COL - Colombia en nacionalidad


def validarPoblacionDiferencial(
    pob_difer_values: list[str],
    pob_difer_textos: list[str],
    categoria_disc_value: str,
    nacionalidad_value: str,
) -> list[tuple[str, str, str]]:
    """
    Retorna:
        Lista de tuplas:
        (campo, valor_registrado, mensaje_error)
    """

    errores = []
    resumen_sel = ", ".join(pob_difer_textos) if pob_difer_textos else "Sin selección"

    # ── Regla 1: No aplica no puede coexistir con otros valores ──────────────
    if POB_NO_APLICA in pob_difer_values and len(pob_difer_values) > 1:
        otros = [
            t for v, t in zip(pob_difer_values, pob_difer_textos)
            if v != POB_NO_APLICA
        ]

        errores.append((
            "Población diferencial",
            resumen_sel,
            f"'No aplica' está seleccionado junto con otros valores: "
            f"{', '.join(otros)}"
        ))

    # ── Regla 2: Discapacidad requiere categoría válida ──────────────────────
    if POB_DISCAPACIDAD in pob_difer_values:
        if categoria_disc_value == CATEGORIA_DISC_NO_APLICA:
            errores.append((
                "Población diferencial / Categoría discapacidad",
                resumen_sel,
                "'Discapacidad' está seleccionado, "
                "pero Categoría discapacidad está en 'No aplica'."
            ))

    # ── Regla 3: Migrante Internacional requiere nacionalidad != Colombia ───
    if POB_MIGRANTE in pob_difer_values:
        if nacionalidad_value == COLOMBIA_VALUE:
            errores.append((
                "Población diferencial / Nacionalidad",
                resumen_sel,
                "'Migrante Internacional' está seleccionado, "
                "pero la nacionalidad es Colombia."
            ))

    # ── Regla 4: Nacionalidad extranjera requiere Migrante Internacional ─────
    if nacionalidad_value != COLOMBIA_VALUE:
        if POB_MIGRANTE not in pob_difer_values:
            errores.append((
                "Población diferencial / Nacionalidad",
                resumen_sel,
                "La nacionalidad es diferente a Colombia, "
                "por lo tanto debe seleccionarse "
                "'Migrante Internacional' en Población diferencial."
            ))

    return errores