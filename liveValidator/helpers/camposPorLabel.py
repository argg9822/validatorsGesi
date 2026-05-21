# camposPorLabel.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ── Labels por sección ────────────────────────────────────────────────────────
# Cada sección declara solo sus propios campos.

LABELS_SECCION_1 = {
    "barra_futbolera": "Barra futbolera",
    "nombre_grupo":     "Nombre del Grupo",
    "tipo_institucion": "Tipo de Institución o Establecimiento educativo o Tipo de colectivo",
    "lugar_actividad":  "Lugar de la actividad",
    "num_sesion_1":   "Número de Sesión (c4)",
    "num_sesion_2":   "Número de Sesión (c24)",
    "num_sesion_3":   "Número de Sesión (c44)",
    "num_sesion_4":   "Número de Sesión (c64)",
    "fecha_sesion_1": "Fecha de sesión (c3)",
    "fecha_sesion_2": "Fecha de sesión (c23)",
    "fecha_sesion_3": "Fecha de sesión (c43)",
    "fecha_sesion_4": "Fecha de sesión (c63)",
    # Componentes y sus campos de género asociados
    "componente_1":    "Componente (c6)",
    "componente_2":    "Componente (c26)",
    "componente_3":    "Componente (c46)",
    "componente_4":    "Componente (c66)",
    "hombres_1":       "Hombres (c9)",
    "mujeres_1":       "Mujeres (c10)",
    "intersexuales_1": "Intersexuales (c11)",
    "hombres_2":       "Hombres (c29)",
    "mujeres_2":       "Mujeres (c30)",
    "intersexuales_2": "Intersexuales (c31)",
    "hombres_3":       "Hombres (c49)",
    "mujeres_3":       "Mujeres (c50)",
    "intersexuales_3": "Intersexuales (c51)",
    "hombres_4":       "Hombres (c69)",
    "mujeres_4":       "Mujeres (c70)",
    "intersexuales_4": "Intersexuales (c71)",
}

LABELS_SECCION_2 = {
    "tipo_doc":         "Tipo de documento",
    "num_doc":          "Número de Documento",
    "fecha_nac":        "Fecha de nacimiento",
    "nacionalidad":     "Nacionalidad",
    "genero":           "Género",
    "orientacion":      "Orientación sexual",
    "identidad_genero": "Identidad de Género",
    "sexo":             "Sexo",
    "ocupacion":        "Ocupación",
    "categoria_disc":   "Categoría discapacidad",
    "pob_diferencial":  "Población Diferencial y de Inclusión",
    "primer_nombre":    "Nombres",
    "primer_apellido":  "Apellidos",
}

LABELS_SECCION_3 = {
    "num_doc": "Número de Documento",
    # agregar más campos de tamizaje aquí según los labels visibles en el formulario
}


def obtenerIdPorLabel(driver, texto_label: str, timeout: int = 6) -> str:
    """
    Busca un <td> cuyo texto contenga 'texto_label' y extrae el ID del control
    desde el atributo 'title' del mismo <td>.
    Retorna el ID del control o "" si no lo encuentra.
    """
    try:
        xpath_td = (
            f'//td[contains(@title,"Control:") and contains(text(),"{texto_label}")]'
        )
        td = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath_td))
        )
        title = td.get_attribute("title") or ""
        for parte in title.split("|"):
            parte = parte.strip()
            if parte.startswith("Control:"):
                return parte.replace("Control:", "").strip()
    except:
        pass   # silencioso — el llamador decide si loguear el faltante
    return ""


def resolverIDs(driver, labels: dict, log_fn=None) -> dict:
    """
    Resuelve solo los IDs del dict 'labels' recibido.
    Cada sección pasa su propio LABELS_SECCION_X, así no busca
    campos de otras secciones que no están visibles.

    Parámetros:
        driver  : WebDriver
        labels  : dict {clave_semántica: texto_label_visible}
        log_fn  : función de log opcional

    Retorna:
        dict {clave_semántica: id_del_control}
    """
    ids           = {}
    no_encontrados = []

    for clave, label in labels.items():
        field_id = obtenerIdPorLabel(driver, label)
        if field_id:
            ids[clave] = field_id
        else:
            ids[clave] = ""
            no_encontrados.append(f"{clave} ('{label}')")

    if no_encontrados and log_fn:
        log_fn(f"   ⚠️  Labels no encontrados: {', '.join(no_encontrados)}")

    return ids