def validarNumDocContraSeccion2(
    num_doc_s3: str,
    num_doc_s2: str,
    page_num: int,
) -> list[tuple[str, str, str]]:
    """
    Valida que el número de documento de la sección 3 (tamizaje, página page_num)
    coincida con el registrado en la sección 2 para esa misma página.

    Retorna lista de tuplas (campo, valor, mensaje_error).
    Lista vacía si todo está correcto.
    """
    if not num_doc_s3:
        return [(
            "Número de Documento",
            "",
            f"Número de documento vacío en sección 3 (página {page_num})",
        )]

    if not num_doc_s2:
        return [(
            "Número de Documento",
            num_doc_s3,
            f"No hay número de documento en sección 2 para la página {page_num} "
            "con el que comparar",
        )]

    if num_doc_s3.strip() != num_doc_s2.strip():
        return [(
            "Número de Documento",
            num_doc_s3,
            f"No coincide con sección 2 — "
            f"S2: '{num_doc_s2}' | S3 (tamizaje): '{num_doc_s3}'",
        )]

    return []
