from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl import Workbook
from datetime import datetime, date
import time

# ── importar validadores ──────────────────────────────────────────────────────
from liveValidator.validadores.validarTipoDocumento import validarTipoDocumento
from liveValidator.validadores.validarSexoGenero import validarSexoGenero      # próximo validador
from liveValidator.validadores.validarOcupacion import validarOcupacion
from liveValidator.validadores.validarPoblacionDiferencial import validarPoblacionDiferencial
from liveValidator.validadores.validarDocumentos import validarDocumentos
# from liveValidator.validadores.validar_etnia import validar as validarEtnia           # próximo validador

# ── IDs de los campos ─────────────────────────────────────────────────────────
ID_TIPO_DOC    = "valorControl19387"
ID_FECHA_NAC   = "valorControl19393"
ID_FECHA_INT   = "FechaIntervencion"
ID_NACIONALIDAD= "valorControl19394"
ID_GENERO      = "valorControl19390"
ID_ORIENTACION = "valorControl19391"
ID_IDENTIDAD   = "valorControl19392"
ID_OCUPACION        = "valorControl19401"
ID_ESPACIO_FIC      = "Espacio_fic"
ID_SEXO             = "valorControl19389"
ID_CATEGORIA_DISC   = "valorControl19399"
ID_POBLACION_DIFER  = "valorControl19397"
ID_NUM_DOC       = "valorControl19388"   # número de documento
ID_PRIMER_NOMBRE = "valorControl19385"   # primer nombre
ID_PRIMER_APELL  = "valorControl19386"   # primer apellido
ID_USUARIO_XPATH = "/html/body/div/div/main/div/div/div/div[2]/div[2]/div[1]/table/tbody/tr/td[9]"

FICHAS = []  # lista global de fichas a procesar
PAGES_PER_ROW = 20

reporte = []   # lista global de registros
reporte_documentos = [] 


# ── utilidades de fecha ───────────────────────────────────────────────────────

def calcularEdad(fecha_nac: date, fecha_int: date) -> int:
    edad = fecha_int.year - fecha_nac.year
    if (fecha_int.month, fecha_int.day) < (fecha_nac.month, fecha_nac.day):
        edad -= 1
    return edad

def parsearFecha(valor: str):
    if not valor:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(valor.strip(), fmt).date()
        except ValueError:
            continue
    return None

# ── selenium helpers ──────────────────────────────────────────────────────────

def waitElement(ident: str, click: bool = False, find_by: str = 'id'):
    for attempt in range(1, 4):
        try:
            locator = (By.ID, ident) if find_by == 'id' else (By.XPATH, ident)
            el = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator))
            if click:
                el.click()
            return el
        except:
            selfLocal.log(f"⚠️ Intento {attempt}/3 — '{ident}'")
            if attempt < 3:
                time.sleep(1)
    selfLocal.log(f"❌ No se encontró '{ident}'")
    return None

def insertValueToInput(value: str, input_id: str):
    try:
        el = waitElement(input_id)
        el.clear()
        if value:
            el.send_keys(value)
    except:
        selfLocal.log(f"❌ Error en input '{input_id}'")

def leerTextoElemento(element_id: str) -> str:
    el = waitElement(element_id)
    if not el:
        return ""
    if el.tag_name.lower() == "select":
        return Select(el).first_selected_option.text.strip()
    return (el.get_attribute("value") or "").strip()

def leerValueElemento(element_id: str) -> str:
    """Lee el value del <option> seleccionado en un select."""
    el = waitElement(element_id)
    if not el:
        return ""
    if el.tag_name.lower() == "select":
        return Select(el).first_selected_option.get_attribute("value").strip()
    return (el.get_attribute("value") or "").strip()

def leerValorOculto(element_id: str) -> str:
    try:
        el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        return (el.get_attribute("value") or "").strip()
    except:
        return ""

def leerValuesMultiple(element_id: str) -> list[str]:
    """Retorna lista de values de todas las opciones seleccionadas en un select múltiple."""
    try:
        el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        sel = Select(el)
        return [opt.get_attribute("value") for opt in sel.all_selected_options]
    except:
        selfLocal.log(f"❌ No se pudo leer el select múltiple '{element_id}'")
        return []

def leerTextosMultiple(element_id: str) -> list[str]:
    """Retorna lista de textos visibles de todas las opciones seleccionadas."""
    try:
        el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        sel = Select(el)
        return [opt.text.strip() for opt in sel.all_selected_options]
    except:
        selfLocal.log(f"❌ No se pudo leer textos del select múltiple '{element_id}'")
        return []
    
def extraerUsuario() -> str:
    try:
        el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, ID_USUARIO_XPATH))
        )
        return (el.text or "").strip()
    except:
        return ""

def enterEnvironmentAndFormat():
    driver.find_element("xpath", '/html/body/div/div/nav/div/div[4]/ul/li[4]/a').click()
    time.sleep(1)
    driver.find_element("xpath", '/html/body/div/div/nav/div/div[4]/ul/li[4]/div/ul/form[5]/li/a').click()


# ── paginador ─────────────────────────────────────────────────────────────────

def getPageButtonXpath(page_num: int) -> str:
    zero_based = page_num - 1
    tr_index   = (zero_based // PAGES_PER_ROW) + 1
    td_index   = (zero_based % PAGES_PER_ROW) * 2 + 1
    BASE = '//*[@id="main_body"]/div/div/main/div/div/div/div[2]/div[3]/div/center/table/tbody/tr/td[3]/table/tbody'
    return f'{BASE}/tr[{tr_index}]/td[{td_index}]/input'

def contarPaginas() -> int:
    total, tr_index = 0, 1
    BASE = '//*[@id="main_body"]/div/div/main/div/div/div/div[2]/div[3]/div/center/table/tbody/tr/td[3]/table/tbody'
    while True:
        encontro = False
        td_index = 1
        while True:
            try:
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f'{BASE}/tr[{tr_index}]/td[{td_index}]/input'))
                )
                total += 1
                encontro = True
                td_index += 2
            except:
                break
        if not encontro:
            break
        tr_index += 1
    return max(total, 1)

def navegarAPagina(page_num: int) -> bool:
    btn = waitElement(getPageButtonXpath(page_num), find_by="xpath")
    if not btn:
        return False
    btn.click()
    time.sleep(0.7)
    return True


# ── registro de errores ───────────────────────────────────────────────────────

def registrarError(ficha: str, page_num: int, digitador: str, campo: str,
                   valor: str, error: str, datos_extra: dict = None):
    """
    Agrega una fila al reporte. Se llama una vez por cada error encontrado
    en la página, permitiendo múltiples errores por página.
    """
    reg = {
        "ficha":     ficha,
        "pagina":    page_num,
        "digitador": digitador,
        "campo":     campo,
        "valor":     valor,
        "error":     error,
        "estado":    "Error",
    }
    if datos_extra:
        reg.update(datos_extra)
    reporte.append(reg)
    selfLocal.log(f"   ❌ p.{page_num} [{campo}]: {error}")


# ── validación por página ─────────────────────────────────────────────────────

def validarPaginaActual(ficha: str, page_num: int, digitador: str, documentos_ficha: list):
    """
    Lee todos los campos necesarios y llama a cada validador.
    Cada validador puede agregar 0 o más errores al reporte.
    Si la página no tiene ningún error, agrega una fila OK.
    """
    # Leer campos de la página
    tipo_doc_raw       = leerTextoElemento(ID_TIPO_DOC)
    fecha_nac_str      = leerTextoElemento(ID_FECHA_NAC)
    fecha_int_str      = leerValorOculto(ID_FECHA_INT)
    nacionalidad_value = leerValueElemento(ID_NACIONALIDAD)
    nacionalidad_texto = leerTextoElemento(ID_NACIONALIDAD)
    num_doc        = leerTextoElemento(ID_NUM_DOC)
    primer_nombre  = leerTextoElemento(ID_PRIMER_NOMBRE)
    primer_apell   = leerTextoElemento(ID_PRIMER_APELL)
    
    from liveValidator.validadores.validarTipoDocumento import extraerCodigoDocumento
    codigo_doc = extraerCodigoDocumento(tipo_doc_raw)
    documentos_ficha.append({
        "ficha":           ficha,
        "pagina":          page_num,
        "tipo_doc":        codigo_doc,
        "num_doc":         num_doc,
        "primer_nombre":   primer_nombre,
        "primer_apellido": primer_apell,
        "fecha_nac":       fecha_nac_str,
    })

    errores_pagina = []

    # ── Verificar datos mínimos ───────────────────────────────────────────────
    if not tipo_doc_raw or not fecha_nac_str or not fecha_int_str:
        registrarError(ficha, page_num, digitador,
                       campo="Datos generales",
                       valor="",
                       error="Campos obligatorios incompletos (tipo doc / fecha nac / fecha int)")
        return

    fecha_nac = parsearFecha(fecha_nac_str)
    fecha_int = parsearFecha(fecha_int_str)

    if not fecha_nac or not fecha_int:
        registrarError(ficha, page_num, digitador,
                       campo="Fechas",
                       valor=f"{fecha_nac_str} / {fecha_int_str}",
                       error="Formato de fecha no reconocido")
        return

    edad = calcularEdad(fecha_nac, fecha_int)

    # ── Validador 1: tipo de documento ────────────────────────────────────────
    ok, msg = validarTipoDocumento(tipo_doc_raw, nacionalidad_value, edad)
    if not ok:
        errores_pagina.append(("Tipo de documento / Nacionalidad / Edad",
                                f"{tipo_doc_raw} | {nacionalidad_texto} | {edad} años",
                                msg))

    # ── Validador 2: género, orientación sexual, identidad de género ──────────
    genero_value      = leerValueElemento(ID_GENERO)
    orientacion_value = leerValueElemento(ID_ORIENTACION)
    identidad_value   = leerValueElemento(ID_IDENTIDAD)

    errores_genero = validarSexoGenero(genero_value, orientacion_value, identidad_value, edad)
    for campo_id, valor, msg in errores_genero:
        errores_pagina.append((f"Género/Orientación/Identidad [{campo_id}]", valor, msg))

    # ── Validador 3: ocupación ────────────────────────────────────────────────
    espacio_fic_value    = leerValueElemento(ID_ESPACIO_FIC)
    ocupacion_value      = leerValueElemento(ID_OCUPACION)
    ocupacion_texto      = leerTextoElemento(ID_OCUPACION)
    sexo_value           = leerValueElemento(ID_SEXO)
    categoria_disc_value = leerValueElemento(ID_CATEGORIA_DISC)
    pob_difer_values     = leerValuesMultiple(ID_POBLACION_DIFER)

    errores_ocupacion = validarOcupacion(
        espacio_fic_value, ocupacion_value, ocupacion_texto,
        edad, sexo_value, categoria_disc_value, pob_difer_values
    )
    for campo, valor, msg in errores_ocupacion:
        errores_pagina.append((campo, valor, msg))

    # ── Validador 4: población diferencial ───────────────────────────────────
    pob_difer_textos = leerTextosMultiple(ID_POBLACION_DIFER)

    errores_pob = validarPoblacionDiferencial(
        pob_difer_values,       # ya leído en validador anterior
        pob_difer_textos,
        categoria_disc_value,   # ya leído en validador anterior
        nacionalidad_value,     # ya leído en validador anterior
    )
    for campo, valor, msg in errores_pob:
        errores_pagina.append((campo, valor, msg))

    # ── Registrar resultados ──────────────────────────────────────────────────
    if errores_pagina:
        for campo, valor, error in errores_pagina:
            registrarError(ficha, page_num, digitador, campo, valor, error,
                           datos_extra={"edad": edad, "fecha_nac": fecha_nac_str,
                                        "fecha_int": fecha_int_str})
    else:
        reporte.append({
            "ficha":     ficha,
            "pagina":    page_num,
            "digitador": digitador,
            "campo":     "",
            "valor":     "",
            "error":     "",
            "estado":    "OK",
            "edad":      edad,
            "fecha_nac": fecha_nac_str,
            "fecha_int": fecha_int_str,
        })
        selfLocal.log(f"   ✅ p.{page_num}: sin errores")


# ── flujo por ficha ───────────────────────────────────────────────────────────

def procesarFicha(ficha: str):
    selfLocal.log(f"\n🗂️  Ficha {ficha}")
    insertValueToInput(str(ficha), 'valorFiltro')
    waitElement('BtnSearchRegs', click=True)

    digitador = extraerUsuario()

    edit_btn = waitElement('btnEditReg')
    if not edit_btn:
        selfLocal.log(f"   ⚠️  Ficha {ficha} no encontrada.")
        reporte.append({
            "ficha": ficha, "pagina": "-", "digitador": digitador,
            "campo": "-", "valor": "-",
            "error": "Ficha no encontrada en el sistema",
            "estado": "No encontrada"
        })
        return

    edit_btn.click()
    waitElement('controlBotonSeccion319', click=True)
    time.sleep(1)

    total_paginas = contarPaginas()
    selfLocal.log(f"   📄 Páginas detectadas: {total_paginas}")
    
    documentos_ficha = []
    
    validarPaginaActual(ficha, 1, digitador, documentos_ficha)

    for page_num in range(2, total_paginas + 1):
        selfLocal.log(f"   🔎 Navegando a página {page_num}...")
        if not navegarAPagina(page_num):
            selfLocal.log(f"   ❌ No se pudo navegar a página {page_num}.")
            continue
        validarPaginaActual(ficha, page_num, digitador, documentos_ficha)

    if documentos_ficha:
            resultados_docs = validarDocumentos(driver, documentos_ficha)
            reporte_documentos.extend(resultados_docs)
            
    waitElement(
        '//*[@id="main_body"]/div/div/main/div/div/div/div[1]/div/div[2]/table/tbody/tr/td/form/button',
        click=True, find_by="xpath"
    )
    selfLocal.log(f"   🚪 Ficha {ficha} completada.")


# ── reporte Excel ─────────────────────────────────────────────────────────────

def exportarReporte():
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte validación"

    thin   = Side(style="thin", color="DDDDDD")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal="center", vertical="center")
    left   = Alignment(horizontal="left",   vertical="center")

    FILLS = {
        "OK":            PatternFill("solid", fgColor="E2EFDA"),
        "Error":         PatternFill("solid", fgColor="FDDCDC"),
        "Incompleto":    PatternFill("solid", fgColor="FFF2CC"),
        "No encontrada": PatternFill("solid", fgColor="F2F2F2"),
    }

    headers    = ["Ficha", "Página", "Digitador", "Campo con error",
                  "Valor registrado", "Error detectado", "Estado",
                  "Edad", "Fecha nac.", "Fecha int."]
    col_widths = [16, 7, 18, 30, 35, 55, 14, 7, 14, 14]

    for col, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill      = PatternFill("solid", fgColor="1F3864")
        cell.font      = Font(color="FFFFFF", bold=True, size=11)
        cell.alignment = center
        cell.border    = border
        ws.column_dimensions[cell.column_letter].width = w

    ws.row_dimensions[1].height = 22
    ws.freeze_panes = "A2"

    for row_idx, reg in enumerate(reporte, 2):
        estado = reg.get("estado", "OK")
        fill   = FILLS.get(estado, FILLS["OK"])
        valores = [
            reg.get("ficha"),   reg.get("pagina"),    reg.get("digitador"),
            reg.get("campo"),   reg.get("valor"),      reg.get("error"),
            estado,             reg.get("edad", ""),   reg.get("fecha_nac", ""),
            reg.get("fecha_int", "")
        ]
        for col, val in enumerate(valores, 1):
            cell = ws.cell(row=row_idx, column=col, value=val)
            cell.fill      = fill
            cell.border    = border
            cell.alignment = center if col in (2, 7, 8) else left

    # Resumen
    total      = len(reporte)
    n_ok       = sum(1 for r in reporte if r["estado"] == "OK")
    n_error    = sum(1 for r in reporte if r["estado"] == "Error")
    n_inc      = sum(1 for r in reporte if r["estado"] == "Incompleto")
    n_noenc    = sum(1 for r in reporte if r["estado"] == "No encontrada")

    res_row = total + 3
    for i, (label, val, color) in enumerate([
        ("Total registros",      total,   None),
        ("Sin errores",          n_ok,    "E2EFDA"),
        ("Con error",            n_error, "FDDCDC"),
        ("Datos incompletos",    n_inc,   "FFF2CC"),
        ("Fichas no encontradas",n_noenc, "F2F2F2"),
    ]):
        c1 = ws.cell(row=res_row + i, column=1, value=label)
        c2 = ws.cell(row=res_row + i, column=2, value=val)
        c1.font = Font(bold=True)
        if color:
            c1.fill = PatternFill("solid", fgColor=color)
            c2.fill = PatternFill("solid", fgColor=color)
    
    # ── Hoja 2: validación de documentos externos ─────────────────────────────
    ws2 = wb.create_sheet("Validación documentos")
    headers2    = ["Ficha", "Página", "Número doc", "Fuente",
                "Consultado", "Coincide", "Detalle discrepancias"]
    col_widths2 = [16, 7, 16, 14, 11, 10, 65]

    for col, (h, w) in enumerate(zip(headers2, col_widths2), 1):
        cell = ws2.cell(row=1, column=col, value=h)
        cell.fill      = PatternFill("solid", fgColor="1F3864")
        cell.font      = Font(color="FFFFFF", bold=True, size=11)
        cell.alignment = center
        cell.border    = border
        ws2.column_dimensions[cell.column_letter].width = w

    for row_idx, res in enumerate(reporte_documentos, 2):
        coincide = res.get("coincide")
        if coincide is True:
            fill2 = PatternFill("solid", fgColor="E2EFDA")   # verde
        elif coincide is False:
            fill2 = PatternFill("solid", fgColor="FDDCDC")   # rojo
        else:
            fill2 = PatternFill("solid", fgColor="FFF2CC")   # amarillo (no consultado)

        valores2 = [
            res.get("ficha"),     res.get("pagina"),
            res.get("num_doc"),   res.get("fuente"),
            "Sí" if res.get("consultado") else "No",
            "Sí" if coincide is True else ("No" if coincide is False else "N/A"),
            res.get("detalle", ""),
        ]
        for col, val in enumerate(valores2, 1):
            cell = ws2.cell(row=row_idx, column=col, value=val)
            cell.fill      = fill2
            cell.border    = border
            cell.alignment = center if col in (2, 5, 6) else left

    nombre = f"reporte_validacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    # Preguntar dónde guardar el archivo
    from tkinter import filedialog
    save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=nombre,
                                             filetypes=[("Archivos de Excel", "*.xlsx")])
    if save_path:
        wb.save(save_path)
        selfLocal.log(f"\n{'─'*50}\n📋 {save_path}\n   ✅ OK: {n_ok}  ❌ Error: {n_error}  ⚠️ Inc: {n_inc}  — No enc: {n_noenc}")
    else:
        selfLocal.log("\n❌ Guardado cancelado. El reporte no se ha guardado.")


# ── ejecución ─────────────────────────────────────────────────────────────────
def ejecutarValidacion(self):
    global selfLocal
    selfLocal = self  # para acceder desde funciones internas

    global driver
    driver = self.driver

    FICHAS = [f.strip() for f in self.fichas if f.strip()]

    if not FICHAS:
        selfLocal.log("❌ No hay fichas para procesar")
        exit()

    enterEnvironmentAndFormat()

    selfLocal.log(f"\n📋 Total fichas a procesar: {len(FICHAS)}")

    for ficha in FICHAS:
        procesarFicha(ficha)

    exportarReporte()

# def main():
#     ejecutarValidacion()

# if __name__ == "__main__":
#     main()