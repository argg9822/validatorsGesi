import time
import random
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# ── Configuración ─────────────────────────────────────────────────────────────
MUESTRA_MIN     = 5
DOCS_A_VALIDAR  = {"CC", "TI", "RC"}

URL_SUPERSALUD  = "https://superargo.supersalud.gov.co/2/formularioWeb/pqrd.php"
URL_COMPROBADOR = "https://appb.saludcapital.gov.co/comprobadorDeDerechos/Consulta.aspx"

COMP_USUARIO    = "AMGARCIAZ"
COMP_PASSWORD   = "Subrednort3"

TIPO_DOC_SUPERSALUD = {
    "CC":  "0",
    "TI":  "1",
    "RC":  "8",
    "CE":  "2",
    "PA":  "3",
    "PEP": "7",
    "PT":  "13",
}

# XPaths del comprobador — se prueban en orden hasta encontrar datos
XPATHS_COMPROBADOR = [
    {
        "apellido": '/html/body/div/form/div[5]/div/div[1]/div/div[1]/div/table/tbody/tr[2]/td[7]',
        "nombre":   '/html/body/div/form/div[5]/div/div[1]/div/div[1]/div/table/tbody/tr[2]/td[9]',
        "fecha":    '/html/body/div/form/div[5]/div/div[1]/div/div[1]/div/table/tbody/tr[2]/td[11]',
    },
    {
        "apellido": '/html/body/div/form/div[5]/div/div[2]/div/div/table/tbody/tr[2]/td[3]',
        "nombre":   '/html/body/div/form/div[5]/div/div[2]/div/div/table/tbody/tr[2]/td[5]',
        "fecha":    '/html/body/div/form/div[5]/div/div[2]/div/div/table/tbody/tr[2]/td[7]',
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _wait(driver, ident: str, by=By.ID, timeout: int = 8):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, ident))
    )

def _waitClick(driver, ident: str, by=By.ID, timeout: int = 8):
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, ident)))
    el.click()
    return el

def _leerInput(driver, element_id: str) -> str:
    try:
        el = _wait(driver, element_id)
        return (el.get_attribute("value") or el.text or "").strip()
    except:
        return ""

def _leerXpath(driver, xpath: str, timeout: int = 5) -> str:
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return (el.text or "").strip()
    except:
        return ""

def _normalizar(texto: str) -> str:
    return " ".join(texto.upper().split())

def _normalizarFecha(fecha_str: str) -> str:
    """
    Convierte cualquier formato de fecha a dd/mm/aaaa para comparar.
    Soporta: dd/mm/yyyy, yyyy-mm-dd, dd-mm-yyyy, yyyy/mm/dd
    """
    if not fecha_str:
        return ""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(fecha_str.strip(), fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return fecha_str.strip()   # si no se pudo parsear, devolver tal cual

def _primerApellido(apellidos_completos: str) -> str:
    """
    Extrae solo el primer apellido.
    'LEON RODRIGUEZ' -> 'LEON'
    'GARCIA'         -> 'GARCIA'
    """
    if not apellidos_completos:
        return ""
    return apellidos_completos.strip().split()[0].upper()

def _primerNombre(nombres_completos: str) -> str:
    """
    Extrae solo el primer nombre.
    'MARIA JOSE' -> 'MARIA'
    """
    if not nombres_completos:
        return ""
    return nombres_completos.strip().split()[0].upper()

def _compararCampo(campo: str, valor_gesi: str, valor_externo: str) -> tuple[bool, str]:
    if _normalizar(valor_gesi) == _normalizar(valor_externo):
        return True, ""
    return False, f"{campo}: GESI='{valor_gesi}' | fuente='{valor_externo}'"


# ── Supersalud ────────────────────────────────────────────────────────────────

def _consultarSupersalud(driver, tipo_doc_codigo: str, num_doc: str,
                          primer_nombre_gesi: str, primer_apellido_gesi: str,
                          fecha_nac_gesi: str) -> dict:
    resultado = {
        "fuente": "Supersalud", "consultado": False,
        "coincide": None, "detalle": "", "encontrado": False,
    }

    tipo_value = TIPO_DOC_SUPERSALUD.get(tipo_doc_codigo)
    if not tipo_value:
        resultado["detalle"] = f"Tipo '{tipo_doc_codigo}' sin mapeo en Supersalud"
        return resultado

    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])

    try:
        driver.get(URL_SUPERSALUD)
        time.sleep(2)

        # Seleccionar tipo de documento (select oculto)
        select_el = _wait(driver, "tipo_identificacion_afectado")
        Select(select_el).select_by_value(tipo_value)
        time.sleep(0.5)

        # Ingresar número de documento y disparar búsqueda con Tab
        campo_doc = _wait(driver, "id_afectado")
        campo_doc.clear()
        campo_doc.send_keys(num_doc)
        campo_doc.send_keys(Keys.TAB)
        time.sleep(2)

        nombre_ext   = _leerInput(driver, "nombre_afectado_1")
        apellido_ext = _leerInput(driver, "apellidos_afectado_1")
        fecha_ext    = _leerInput(driver, "fecha_nacimiento")

        # Si los campos siguen vacíos, el documento no fue encontrado
        if not nombre_ext and not apellido_ext:
            resultado["detalle"]    = "Documento no encontrado en Supersalud"
            resultado["consultado"] = True
            resultado["encontrado"] = False
            return resultado

        resultado["consultado"] = True
        resultado["encontrado"] = True

        # Normalizar: primer apellido, primer nombre y fecha a dd/mm/yyyy
        apellido_ext_norm = _primerApellido(apellido_ext)
        nombre_ext_norm   = _primerNombre(nombre_ext)
        fecha_ext_norm    = _normalizarFecha(fecha_ext)
        fecha_gesi_norm   = _normalizarFecha(fecha_nac_gesi)

        discrepancias = []
        for campo, val_gesi, val_ext in [
            ("Primer nombre",    primer_nombre_gesi,   nombre_ext_norm),
            ("Primer apellido",  primer_apellido_gesi, apellido_ext_norm),
            ("Fecha nacimiento", fecha_gesi_norm,      fecha_ext_norm),
        ]:
            ok, msg = _compararCampo(campo, val_gesi, val_ext)
            if not ok:
                discrepancias.append(msg)

        resultado["coincide"] = len(discrepancias) == 0
        resultado["detalle"]  = " | ".join(discrepancias) if discrepancias else "OK"

    except Exception as e:
        resultado["detalle"] = f"Error en Supersalud: {e}"

    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return resultado


# ── Comprobador de Derechos ───────────────────────────────────────────────────

_comprobador_logueado = False

def _loginComprobador(driver):
    global _comprobador_logueado
    try:
        _waitClick(driver, "LoginStatus")
        time.sleep(1)
        usuario = _wait(driver, "MainContent_Login_UserName")
        usuario.clear()
        usuario.send_keys(COMP_USUARIO)
        psw = _wait(driver, "MainContent_Login_Password")
        psw.clear()
        psw.send_keys(COMP_PASSWORD)
        _waitClick(driver, "MainContent_Login_LoginButton")
        time.sleep(2)
        _comprobador_logueado = True
    except Exception as e:
        print(f"   ⚠️  Login comprobador falló: {e}")

def _consultarComprobador(driver, num_doc: str,
                           primer_nombre_gesi: str, primer_apellido_gesi: str,
                           fecha_nac_gesi: str) -> dict:
    global _comprobador_logueado

    resultado = {
        "fuente": "Comprobador", "consultado": False,
        "coincide": None, "detalle": "", "encontrado": False,
    }

    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])

    try:
        driver.get(URL_COMPROBADOR)
        time.sleep(2)

        if not _comprobador_logueado:
            _loginComprobador(driver)

        campo_doc = _wait(driver, "MainContent_txtNoId")
        campo_doc.clear()
        campo_doc.send_keys(num_doc)
        _waitClick(driver, "MainContent_cmdConsultar")
        time.sleep(2)

        # Intentar leer datos probando cada conjunto de XPaths
        apellido_ext = nombre_ext = fecha_ext = ""

        for grupo in XPATHS_COMPROBADOR:
            apellido_ext = _leerXpath(driver, grupo["apellido"], timeout=4)
            nombre_ext   = _leerXpath(driver, grupo["nombre"],   timeout=4)
            fecha_ext    = _leerXpath(driver, grupo["fecha"],     timeout=4)
            if apellido_ext or nombre_ext:
                break   # encontró datos en este grupo de XPaths

        if not nombre_ext and not apellido_ext:
            resultado["detalle"]    = "Documento no encontrado en el Comprobador"
            resultado["consultado"] = True
            resultado["encontrado"] = False
            return resultado

        resultado["consultado"] = True
        resultado["encontrado"] = True

        apellido_ext_norm = _primerApellido(apellido_ext)
        nombre_ext_norm   = _primerNombre(nombre_ext)
        fecha_ext_norm    = _normalizarFecha(fecha_ext)
        fecha_gesi_norm   = _normalizarFecha(fecha_nac_gesi)

        discrepancias = []
        for campo, val_gesi, val_ext in [
            ("Primer nombre",    primer_nombre_gesi,   nombre_ext_norm),
            ("Primer apellido",  primer_apellido_gesi, apellido_ext_norm),
            ("Fecha nacimiento", fecha_gesi_norm,      fecha_ext_norm),
        ]:
            ok, msg = _compararCampo(campo, val_gesi, val_ext)
            if not ok:
                discrepancias.append(msg)

        resultado["coincide"] = len(discrepancias) == 0
        resultado["detalle"]  = " | ".join(discrepancias) if discrepancias else "OK"

    except Exception as e:
        resultado["detalle"] = f"Error en Comprobador: {e}"

    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return resultado


# ── Función principal ─────────────────────────────────────────────────────────

def validarDocumentos(
    driver,
    documentos_ficha: list[dict],
    solo_comprobador: bool = False,
) -> list[dict]:
    """
    ...
    """
    candidatos = [
        d for d in documentos_ficha
        if d.get("tipo_doc", "").upper() in DOCS_A_VALIDAR and d.get("num_doc")
    ]
    vistos, unicos = set(), []
    for d in candidatos:
        if d["num_doc"] not in vistos:
            vistos.add(d["num_doc"])
            unicos.append(d)

    muestra    = random.sample(unicos, min(MUESTRA_MIN, len(unicos)))
    resultados = []

    for doc in muestra:
        tipo     = doc["tipo_doc"].upper()
        num      = doc["num_doc"]
        ficha    = doc["ficha"]
        pagina   = doc["pagina"]

        primer_nombre   = _primerNombre(doc.get("primer_nombre", ""))
        primer_apellido = _primerApellido(doc.get("primer_apellido", ""))
        fecha_nac       = doc.get("fecha_nac", "")

        print(f"\n   🔍 Doc {num} ({tipo}) — ficha {ficha} p.{pagina}")

        if solo_comprobador:
            # ── Ir directo al comprobador sin pasar por Supersalud ────────────
            res = _consultarComprobador(driver, num,
                                        primer_nombre, primer_apellido, fecha_nac)
            res.update({"ficha": ficha, "pagina": pagina, "num_doc": num})
            icono = "✅" if res["coincide"] else ("❌" if res["encontrado"] else "⚠️")
            print(f"      Comprobador → {icono} {res['detalle']}")
            resultados.append(res)

        else:
            # ── Flujo normal: Supersalud primero, Comprobador si no encuentra ─
            res = _consultarSupersalud(driver, tipo, num,
                                       primer_nombre, primer_apellido, fecha_nac)
            res.update({"ficha": ficha, "pagina": pagina, "num_doc": num})

            if res["encontrado"]:
                icono = "✅" if res["coincide"] else "❌"
                print(f"      Supersalud  → {icono} {res['detalle']}")
                resultados.append(res)
                continue

            print(f"      Supersalud  → ⚠️  {res['detalle']} — consultando Comprobador...")

            res2 = _consultarComprobador(driver, num,
                                         primer_nombre, primer_apellido, fecha_nac)
            res2.update({"ficha": ficha, "pagina": pagina, "num_doc": num})
            icono = "✅" if res2["coincide"] else ("❌" if res2["encontrado"] else "⚠️")
            print(f"      Comprobador → {icono} {res2['detalle']}")
            resultados.append(res2)

    return resultados