# camposPorLabel.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ── Labels por sección ────────────────────────────────────────────────────────
# Cada sección declara solo sus propios campos.

LABELS_SECCION_1 = {
    "barra_futbolera": "Barra futbolera",
    "nombre_grupo":     "Nombre del Grupo",
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

# agrega LABELS_SECCION_3, LABELS_SECCION_4... cuando las necesites


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