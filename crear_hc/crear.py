from selenium import webdriver
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


import tkinter as tk
from tkinter import messagebox


filesheet = "crear_hc/crearIndividualfinal.xlsx"
wb = load_workbook(filesheet)
hojas = wb.get_sheet_names()
print(hojas)
nombres = wb.get_sheet_by_name('Hoja1')
wb.close()

def usuario_login(self, driver):
    dialog = customtkinter.CTkToplevel()
    dialog.title("Datos de Usuario")
    dialog.transient()
    dialog.grab_set()
    dialog.focus()

    # Labels and entry fields for username and password
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
    # Button to trigger the login function with the entered data
    save_button = customtkinter.CTkButton(dialog, text="Continuar", 
                                          command=lambda: login(user_var.get(), password_var.get(), dialog , driver))
    save_button.grid(row=2, column=0, columnspan=2, pady=10)
    
    dialog.destroy
    
def login(user, password, dialog, driver):
    
    # Close the dialog window after successful login
    dialog.destroy()
    # Use the passed user and password values
    element = driver.find_element("id", 'usuario')
    element.send_keys(user)
    time.sleep(1)
    
    element = driver.find_element("id", 'password')
    element.send_keys(password)
    time.sleep(1)
    
    # Get the security token and continue login
    codigo = driver.find_element("id", 'tokenAcceso').get_attribute('value')
    element = driver.find_element("id", 'valorCodigoSeguridad')
    element.send_keys(codigo)
    time.sleep(2)
    
    time.sleep(1)
    esperacapcha(driver)
    
        
    

def esperacapcha(driver):
    dialog = customtkinter.CTkToplevel()
    dialog.title("Esperando a Captcha")
    dialog.attributes("-topmost", True)
    dialog.transient()  
    dialog.grab_set()   
    label_user = customtkinter.CTkLabel(dialog, text="Por favor complete el capcha")
    label_user.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    label_user = customtkinter.CTkLabel(dialog, text="Una vez completado el capcha oprima (continuar)")
    label_user.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    save_button = customtkinter.CTkButton(dialog, text="Continuar", command=lambda: capchacompletado(driver, dialog))
    save_button.grid(row=2, column=0, columnspan=2, pady=10)
    print("Esperando captcha")
    dialog.wait_window()
    dialog.destroy
    
    

def capchacompletado(driver, dialog):
    next(driver)
    
def hc_crear(self):

    driver = webdriver.Edge()
    driver.get("http://gesiaplicaciones.saludcapital.gov.co/GESI_sistemas/login") 
    time.sleep(2)
    #LOGIN
    element_h=driver.find_element("xpath", '/html/body/div/section/form/div/div/button').click() #DESPLEGAR hERRAMIENTA
    # pagina no segura 
    try:
        # Intenta encontrar el botón
        element_nosegura=driver.find_element("xpath", '/html/body/div/div[2]/button[3]').click() #DESPLEGAR avanzada
        print("El botón se encontró y se hizo clic.")
        
        time.sleep(1)
        element_continuar=driver.find_element("xpath", '/html/body/div/div[3]/p[2]/a').click() #DESPLEGAR continuar
        time.sleep(3)
        usuario_login(self, driver)
    except :
        # Si el botón no se encuentra, pasa a la siguiente parte del código
        print("El botón no se encontró, continúa con el código.")
        usuario_login(self)
    
    
      
    

def next(driver):
    element = driver.find_element("xpath", '/html/body/section/div/div/form/div/div/div[7]/div/div/button').click()
    time.sleep(4)
     #INGRESO HERRAMIENTA DE CONTROL
    element_h=driver.find_element("xpath", '/html/body/div/div/nav/div/div[4]/ul/li[7]').click() #DESPLEGAR hERRAMIENTA
    time.sleep(1)
    element_csa=driver.find_element("xpath", '/html/body/div/div/nav/div/div[4]/ul/li[7]/div/ul/li[1]/a').click() #SELECCIONAR OTRO
    time.sleep(2)
    duplicar_ficha = driver.find_element("xpath", '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[7]/input').click()
    time.sleep(1)
    Ok1 = driver.find_element("xpath", '/html/body/div[2]/div/div[3]/button[1]').click()
    iniciar(driver)
    
def iniciar(driver):
    dialog = customtkinter.CTkToplevel()
    dialog.title("inicar proceso")
    dialog.attributes("-topmost", True)
    dialog.transient()  
    dialog.grab_set()  
    
    label_user = customtkinter.CTkLabel(dialog, text="Para la creacion desea incluir el si digitado")
    label_user.grid(row=0, column=0, padx=10, pady=5, sticky="w")
     
    save_button = customtkinter.CTkButton(dialog, text="Si", command=lambda: si(driver, dialog) )
    save_button.grid(row=1, column=0, columnspan=2, pady=10)
    
    save_button = customtkinter.CTkButton(dialog, text="NO", command=lambda: no(driver, dialog))
    save_button.grid(row=1, column=2, columnspan=2, pady=10)
    dialog.wait_window()
    
    
    
def si(driver, dialog):
    dialog.destroy
    total_filas = nombres.max_row
    for i in range(1, total_filas + 1):
        intento = 0
        max_intentos = 5  # Número máximo de reintentos
        print (f"quedan {max_intentos} intentos")
        exito = False
        while intento < max_intentos and not exito:
            try:
                ficha, fecha, profesional, entorno, base, perfil = nombres[f'A{i}:F{i}'][0]
                ficha1 = ficha.value
                fecha1 = fecha.value
                formato = fecha1.strftime('%d/%m/%Y')
                profesional1 = profesional.value
                Entorno1 = entorno.value
                perfil1 = perfil.value
                base1 = base.value
                Datos = [ficha1, formato, profesional1, Entorno1, base1, perfil1]
                print(f"Se inmgresaron los datos {Datos}")
                DatosCrearSi(Datos, driver)
                exito = True  # Marcar como exitoso si no hay excepciones
            except (NoSuchElementException, TimeoutException, WebDriverException) as e:
                print(f"Error en el procesamiento de los datos para la fila {i}: {e}")
                intento += 1
                if intento < max_intentos:
                    print(f"Reintentando {i}, intento {intento}...")
                    driver.refresh()
                    time.sleep(5)  # Esperar un momento para asegurarse de que la página se recargue
                else:
                    print(f"Error persistente en la fila {i}. No se pudieron procesar los datos después de {max_intentos} intentos.")
    driver.quit() 
    print(f"Se crearon {total_filas} en la herramienta de control")
    
def no(driver, dialog):
    dialog.destroy
    total_filas = nombres.max_row
    for i in range(1, total_filas + 1): 
        intento = 0
        max_intentos = 3  # Número máximo de reintentos
        print (f"quedan {max_intentos} intentos")
        exito = False
        while intento < max_intentos and not exito:
            try:
                ficha, fecha, profesional, entorno, base, perfil = nombres[f'A{i}:F{i}'][0]
                ficha1 = ficha.value
                fecha1 = fecha.value
                formato = fecha1.strftime('%d/%m/%Y')
                profesional1 = profesional.value
                Entorno1 = entorno.value
                perfil1 = perfil.value
                base1 = base.value
                Datos = [ficha1, formato, profesional1, Entorno1, base1, perfil1]
                print(f"Se inmgresaron los datos {Datos}")
                llenar(Datos, driver)
                exito = True  # Marcar como exitoso si no hay excepciones
            except (NoSuchElementException, TimeoutException, WebDriverException) as e:
                print(f"Error en el procesamiento de los datos para la fila {i}: {e}")
                intento += 1
                if intento < max_intentos:
                    print(f"Reintentando {i}, intento {intento}...")
                    driver.refresh()
                    time.sleep(5)  # Esperar un momento para asegurarse de que la página se recargue
                else:
                    print(f"Error persistente en la fila {i}. No se pudieron procesar los datos después de {max_intentos} intentos.")
    print("Proceso completado.")
    
    driver.quit() 
    
    
def DatosCrearSi(Datos, driver):
    intento = 0
    max_intentos = 3
    exito = False
    while intento < max_intentos and not exito:
        try:
            Digitado = Select(driver.find_element("id", 'Digitado'))
            Digitado.select_by_visible_text('Si')
            element_fecha3 = driver.find_element("id", 'Fecha_entrega_tecnologo')
            element_fecha3.send_keys(Datos[1])
            element_fecha3 = driver.find_element("id", 'Fecha_actualizacion')
            element_fecha3.send_keys(Datos[1])
            element_fecha4 = driver.find_element("id", 'Fecha_entrega_digitacion')
            element_fecha4.send_keys(Datos[1])
            element_NoActua = driver.find_element("id", 'Nro_actualizacion')
            element_NoActua.send_keys('1')
            llenar(Datos, driver)
            exito = True
        except (NoSuchElementException, TimeoutException, WebDriverException) as e:
            print(f"Error en DatosCrearSi: {e}")
            intento += 1
            if intento < max_intentos:
                print(f"Reintentando DatosCrearSi, intento {intento}...")
                driver.refresh()
                time.sleep(5)
            else:
                print(f"Error persistente en DatosCrearSi después de {max_intentos} intentos.")

def llenar(Datos, driver):
    intento = 0
    max_intentos = 3
    exito = False
    while intento < max_intentos and not exito:
        try:
            print(Datos[3])
            Espacio = Select(driver.find_element("id", 'Espacio_fic'))
            Espacio.select_by_visible_text(Datos[3])
            element_ficha = driver.find_element("id", 'Ficha_fic')
            element_ficha.send_keys(Datos[0])
            profesional = driver.find_element("id", 'Nombre_profesional')
            profesional.send_keys(Datos[2])
            element_fecha = driver.find_element("id", 'Fecha_ingreso')
            element_fecha.send_keys(Datos[1])
            element_fecha2 = driver.find_element("id", 'Fecha_entrega_profesional')
            element_fecha2.send_keys(Datos[1])
            PERFIL = Select(driver.find_element("id", 'Id_perfil'))
            PERFIL.select_by_visible_text(Datos[5])
            Base = Select(driver.find_element("id", 'Id_Base'))
            Base.select_by_visible_text(Datos[4])
            driver.find_element("xpath", '/html/body/div/div/main/div/div/div/div[2]/form/div[12]/div/center/input').click()
            driver.find_element("xpath", '/html/body/div[2]/div/div[3]/button[1]').click()
            driver.find_element("xpath", '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[5]/input').click()
            time.sleep(2)
            driver.find_element("xpath", '/html/body/div[2]/div/div[3]/button[1]').click()
            exito = True
        except (NoSuchElementException, TimeoutException, WebDriverException) as e:
            print(f"Error en llenar: {e}")
            intento += 1
            if intento < max_intentos:
                print(f"Reintentando llenar, intento {intento}...")
                driver.refresh()
                time.sleep(5)
            else:
                print(f"Error persistente en llenar después de {max_intentos} intentos.")