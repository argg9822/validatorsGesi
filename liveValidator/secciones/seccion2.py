# camposPorLabel.py
from liveValidator.helpers.camposPorLabel import resolverIDs, LABELS_SECCION_2
from liveValidator.helpers.validarTipoDocumento import validarTipoDocumento, extraerCodigoDocumento
from liveValidator.helpers.validarSexoGenero import validarSexoGenero
from liveValidator.helpers.validarOcupacion import validarOcupacion
from liveValidator.helpers.validarPoblacionDiferencial import validarPoblacionDiferencial

ID_ESPACIO_FIC = "Espacio_fic"


def validarSeccion2(driver, ficha: str, page_num: int, digitador: str,
                    documentos_ficha: list, helpers: dict) -> list:
    leerTexto          = helpers["leerTexto"]
    leerValue          = helpers["leerValue"]
    leerOculto         = helpers["leerOculto"]
    leerMultipleValues = helpers["leerMultipleValues"]
    leerMultipleTextos = helpers["leerMultipleTextos"]
    calcularEdad       = helpers["calcularEdad"]
    parsearFecha       = helpers["parsearFecha"]
    log_fn             = helpers.get("log")

    # Solo busca los campos de sección 2
    ids = resolverIDs(driver, LABELS_SECCION_2, log_fn)

    if not any(ids.values()):
        return [("Formulario", "", "No se pudieron detectar los IDs del formulario")]

    tipo_doc_raw       = leerTexto(ids.get("tipo_doc", ""))
    fecha_nac_str      = leerTexto(ids.get("fecha_nac", ""))
    fecha_int_str      = leerOculto("FechaIntervencion")
    nacionalidad_value = leerValue(ids.get("nacionalidad", ""))
    nacionalidad_texto = leerTexto(ids.get("nacionalidad", ""))
    num_doc            = leerTexto(ids.get("num_doc", ""))
    primer_nombre      = leerTexto(ids.get("primer_nombre", ""))
    primer_apell       = leerTexto(ids.get("primer_apellido", ""))
    genero_value       = leerValue(ids.get("genero", ""))
    orientacion_value  = leerValue(ids.get("orientacion", ""))
    identidad_value    = leerValue(ids.get("identidad_genero", ""))
    genero_texto       = leerTexto(ids.get("genero", ""))
    orientacion_texto  = leerTexto(ids.get("orientacion", ""))
    identidad_texto    = leerTexto(ids.get("identidad_genero", ""))
    sexo_value         = leerValue(ids.get("sexo", ""))
    espacio_fic_value  = leerValue(ID_ESPACIO_FIC)
    ocupacion_value    = leerValue(ids.get("ocupacion", ""))
    ocupacion_texto    = leerTexto(ids.get("ocupacion", ""))
    categoria_disc_val = leerValue(ids.get("categoria_disc", ""))
    pob_difer_values   = leerMultipleValues(ids.get("pob_diferencial", ""))
    pob_difer_textos   = leerMultipleTextos(ids.get("pob_diferencial", ""))

    documentos_ficha.append({
        "ficha":           ficha,
        "pagina":          page_num,
        "tipo_doc":        extraerCodigoDocumento(tipo_doc_raw),
        "num_doc":         num_doc,
        "primer_nombre":   primer_nombre,
        "primer_apellido": primer_apell,
        "fecha_nac":       fecha_nac_str,
    })

    if not tipo_doc_raw or not fecha_nac_str or not fecha_int_str:
        return [("Datos generales", "",
                 "Campos obligatorios incompletos (tipo doc / fecha nac / fecha int)")]

    fecha_nac = parsearFecha(fecha_nac_str)
    fecha_int = parsearFecha(fecha_int_str)

    if not fecha_nac or not fecha_int:
        return [("Fechas", f"{fecha_nac_str} / {fecha_int_str}",
                 "Formato de fecha no reconocido")]

    edad   = calcularEdad(fecha_nac, fecha_int)
    errores = []

    ok, msg = validarTipoDocumento(tipo_doc_raw, nacionalidad_value, edad)
    if not ok:
        errores.append((
            "Tipo de documento / Nacionalidad / Edad",
            f"{tipo_doc_raw} | {nacionalidad_texto} | {edad} años",
            msg
        ))

    for campo, valor, msg in validarSexoGenero(
            genero_value, orientacion_value, identidad_value, edad,
            genero_texto, orientacion_texto, identidad_texto):
        errores.append((campo, valor, msg))

    for campo, valor, msg, corregido in validarOcupacion(
            espacio_fic_value, ocupacion_value, ocupacion_texto,
            edad, sexo_value, categoria_disc_val, pob_difer_values):
        errores.append((campo, valor, msg, corregido))

    for campo, valor, msg in validarPoblacionDiferencial(
            pob_difer_values, pob_difer_textos,
            categoria_disc_val, nacionalidad_value):
        errores.append((campo, valor, msg))

    return errores