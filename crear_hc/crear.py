from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
from openpyxl import load_workbook
import time
import datetime
import customtkinter
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tkinter import filedialog
import tkinter as tk
from tkinter import messagebox

nombres = None  # Variable global para almacenar la hoja de Excel

def seleccionar_archivo():
    global nombres
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo de Excel",
        filetypes=[("Archivos de Excel", "*.xlsx;*.xls")]
    )
    
    if archivo:
        try:
            wb = load_workbook(archivo)
            hojas = wb.sheetnames
            print(hojas)
            nombres = wb['Hoja1']
            wb.close()
            messagebox.showinfo("Éxito", "Archivo cargado correctamente")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")
            return False
    else:
        messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo.")
        return False

def wait_for_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value)))
    except TimeoutException:
        raise Exception(f"Elemento no encontrado: {by}={value}")

def usuario_login(driver):
    dialog = customtkinter.CTkToplevel()
    dialog.title("Datos de Usuario")
    dialog.transient()
    dialog.grab_set()
    dialog.focus()

    label_user = customtkinter.CTkLabel(dialog, text="Nombre Usuario")
    label_user.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    user_var = tk.StringVar()
    entry_user = customtkinter.CTkEntry(dialog, textvariable=user_var)
    entry_user.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    
    label_password = customtkinter.CTkLabel(dialog, text="Password")
    label_password.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    
    password_var = tk.StringVar()
    entry_password = customtkinter.CTkEntry(dialog, textvariable=password_var, show="*")
    entry_password.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    
    save_button = customtkinter.CTkButton(dialog, text="Continuar", 
                                      command=lambda: login(user_var.get(), password_var.get(), dialog, driver))
    save_button.grid(row=2, column=0, columnspan=2, pady=10)

def login(user, password, dialog, driver):
    try:
        dialog.destroy()
        
        wait_for_element(driver, By.ID, 'usuario').send_keys(user)
        time.sleep(1)
        
        wait_for_element(driver, By.ID, 'password').send_keys(password)
        time.sleep(1)
        
        codigo = wait_for_element(driver, By.ID, 'tokenAcceso').get_attribute('value')
        wait_for_element(driver, By.ID, 'valorCodigoSeguridad').send_keys(codigo)
        time.sleep(2)
        
        esperacapcha(driver)
    except Exception as e:
        messagebox.showerror("Error", f"Fallo en el login: {e}")
        driver.quit()

def esperacapcha(driver):
    dialog = customtkinter.CTkToplevel()
    dialog.title("Esperando a Captcha")
    dialog.attributes("-topmost", True)
    dialog.transient()  
    dialog.grab_set()   
    
    label_user = customtkinter.CTkLabel(dialog, text="Por favor complete el capcha")
    label_user.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    label_user = customtkinter.CTkLabel(dialog, text="Una vez completado el capcha oprima (continuar)")
    label_user.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    
    save_button = customtkinter.CTkButton(dialog, text="Continuar", 
                                      command=lambda: capchacompletado(driver, dialog))
    save_button.grid(row=2, column=0, columnspan=2, pady=10)
    
    dialog.wait_window()

def capchacompletado(driver, dialog):
    dialog.destroy()
    next(driver)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def hc_crear():
    if not seleccionar_archivo():
        return
    
    try:
        # Configuración para Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        
        # Inicializar Chrome con WebDriver Manager (instala automáticamente el driver correcto)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        driver.get("http://gesiaplicaciones.saludcapital.gov.co/GESI_sistemas/login") 
        time.sleep(2)
        
        # El resto de tu código permanece igual...
        wait_for_element(driver, By.XPATH, '/html/body/div/section/form/div/div/button').click()
        
        try:
            wait_for_element(driver, By.XPATH, '/html/body/div/div[2]/button[3]').click()
            time.sleep(1)
            wait_for_element(driver, By.XPATH, '/html/body/div/div[3]/p[2]/a').click()
            time.sleep(3)
        except:
            print("El botón no se encontró, continúa con el código.")
        
        usuario_login(driver)
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo iniciar el navegador: {e}")
        if 'driver' in locals():
            driver.quit()

def next(driver):
    wait_for_element(driver, By.XPATH, '/html/body/section/div/div/form/div/div/div[7]/div/div/button').click()
    time.sleep(4)
    
    wait_for_element(driver, By.XPATH, '/html/body/div/div/nav/div/div[4]/ul/li[7]').click()
    time.sleep(1)
    
    wait_for_element(driver, By.XPATH, '/html/body/div/div/nav/div/div[4]/ul/li[7]/div/ul/li[1]/a').click()
    time.sleep(2)
    
    wait_for_element(driver, By.XPATH, '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[7]/input').click()
    time.sleep(1)
    
    wait_for_element(driver, By.XPATH, '/html/body/div[2]/div/div[3]/button[1]').click()
    
    iniciar(driver)

def iniciar(driver):
    dialog = customtkinter.CTkToplevel()
    dialog.title("Iniciar proceso")
    dialog.attributes("-topmost", True)
    dialog.transient()  
    dialog.grab_set()  
    
    label_user = customtkinter.CTkLabel(dialog, text="Para la creación desea incluir el si digitado")
    label_user.grid(row=0, column=0, padx=10, pady=5, sticky="w")
     
    save_button = customtkinter.CTkButton(dialog, text="Si", 
                                      command=lambda: [si(driver, dialog), dialog.destroy()])
    save_button.grid(row=1, column=0, columnspan=2, pady=10)
    
    no_button = customtkinter.CTkButton(dialog, text="No", 
                                     command=lambda: [dialog.destroy(), driver.quit()])
    no_button.grid(row=2, column=0, columnspan=2, pady=10)

def si(driver, dialog):
    dialog.destroy()
    total_filas = nombres.max_row
    
    try:
        for i in range(1, total_filas + 1):
            ficha, fecha, profesional, entorno, base, perfil = nombres[f'A{i}:F{i}'][0]
            ficha1 = ficha.value
            fecha1 = fecha.value
            formato = fecha1.strftime('%d/%m/%Y')
            profesional1 = profesional.value
            Entorno1 = entorno.value
            perfil1 = perfil.value
            base1 = base.value
            Datos = [ficha1, formato, profesional1, Entorno1, base1, perfil1]
            print(f"Ingresando ficha: {ficha1}")
            
            DatosCrearSi(Datos, driver)               
            
            wait_for_element(driver, By.XPATH, '/html/body/div[2]/div/div[3]/button[1]').click()
            
            wait_for_element(driver, By.XPATH, '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[5]/input').click()
            
            wait_for_element(driver, By.XPATH, '/html/body/div[2]/div/div[3]/button[1]').click()
        
        messagebox.showinfo("Éxito", "Proceso completado correctamente")
        
    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar las fichas: {e}")
    finally:
        driver.quit()

def DatosCrearSi(Datos, driver):
    try:
        Select(wait_for_element(driver, By.ID, 'Digitado')).select_by_visible_text('Si')
        
        fecha_fields = ['Fecha_entrega_tecnologo', 'Fecha_actualizacion', 'Fecha_entrega_digitacion']
        for field in fecha_fields:
            wait_for_element(driver, By.ID, field).send_keys(Datos[1])
        
        wait_for_element(driver, By.ID, 'Nro_actualizacion').send_keys('1')
        
        llenar(Datos, driver)
        
        wait_for_element(driver, By.XPATH, '/html/body/div/div/main/div/div/div/div[2]/form/div[12]/div/center/input').click()
        
    except Exception as e:
        raise Exception(f"Error al crear ficha con digitado: {e}")

def llenar(Datos, driver):
    try:
        element_ficha = wait_for_element(driver, By.ID, 'Ficha_fic')
        element_ficha.clear()
        element_ficha.send_keys(Datos[0])
        
        profesional = wait_for_element(driver, By.ID, 'Nombre_profesional')
        profesional.clear()
        profesional.send_keys(Datos[2])
        
        fecha_fields = ['Fecha_ingreso', 'Fecha_entrega_profesional']
        for field in fecha_fields:
            element = wait_for_element(driver, By.ID, field)
            element.clear()
            element.send_keys(Datos[1])
        
        Select(wait_for_element(driver, By.ID, 'Id_perfil')).select_by_visible_text(Datos[5])
        
        # Manejo del select Espacio con reintento
        for attempt in range(10):
            try:
                espacio = Select(wait_for_element(driver, By.ID, 'Espacio_fic'))
                espacio.select_by_visible_text('1 -Hogar')
                time.sleep(1)
                espacio.select_by_visible_text(Datos[3])
                time.sleep(1)
                break
            except NoSuchElementException:
                print(f"Intento {attempt + 1} fallido: 'Espacio_fic' no encontrado.")
                time.sleep(1)
        
        Select(wait_for_element(driver, By.ID, 'Id_Base')).select_by_visible_text(Datos[4])
        
    except Exception as e:
        raise Exception(f"Error al llenar el formulario: {e}")

# Ejecutar la función principal
if __name__ == "__main__":
    hc_crear()