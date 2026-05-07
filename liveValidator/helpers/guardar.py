import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


XPATH_BTN_OK = "/html/body/div[2]/div/div[3]/button[1]"


def guardarCambios(driver, log_fn=None) -> bool:
    """
    Hace clic en 'botonActualizarInformacion' y luego en el botón OK del modal.
    Retorna True si guardó correctamente, False si hubo error.

    Parámetros:
        driver : WebDriver
        log_fn : función de log opcional (ej. selfLocal.log)
    """
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "botonActualizarInformacion"))
        ).click()
        time.sleep(0.5)

        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, XPATH_BTN_OK))
        ).click()
        time.sleep(0.5)

        if log_fn:
            log_fn("      💾 Cambio guardado correctamente")
        return True

    except Exception as e:
        if log_fn:
            log_fn(f"      ❌ Error al guardar: {e}")
        return False