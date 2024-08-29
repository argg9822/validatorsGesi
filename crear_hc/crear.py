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

import tkinter as tk
from tkinter import messagebox


driver = webdriver.Edge()
driver.get("http://gesiaplicaciones.saludcapital.gov.co/GESI_sistemas/login")
time.sleep(2)

#LOGIN
element_h=driver.find_element("xpath", '/html/body/div/section/form/div/div/button').click() #DESPLEGAR hERRAMIENTA


# pagina no segura 


usu = "monhabell@gmail.com"
element=driver.find_element("id", 'usuario')
element.send_keys(usu)
time.sleep(1)
psw = "GeSi123456*"
element=driver.find_element("id", 'password')
element.send_keys(psw)
time.sleep(1)
codigo = driver.find_element("id", 'tokenAcceso').get_attribute('value')
print(codigo)
element=driver.find_element("id", 'valorCodigoSeguridad')
element.send_keys(codigo)
time.sleep(2)
element=driver.find_element("xpath", '/html/body/div/section/form/div/div/div[6]/input').click()
time.sleep(4)

#INGRESO HERRAMIENTA DE CONTROL
element_h=driver.find_element("xpath", '/html/body/div/div/nav/div/div[4]/ul/li[7]').click() #DESPLEGAR hERRAMIENTA
time.sleep(1)
element_csa=driver.find_element("xpath", '/html/body/div/div/nav/div/div[4]/ul/li[7]/div/ul/li[1]/a').click() #SELECCIONAR OTRO
time.sleep(2)
duplicar_ficha = driver.find_element("xpath", '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[7]/input').click()
time.sleep(1)
Ok1 = driver.find_element("xpath", '/html/body/div[2]/div/div[3]/button[1]').click()


def llenar(Datos):
    print(Datos[3])
    Espacio = Select(driver.find_element("id", 'Espacio_fic'))
    Espacio.select_by_visible_text(Datos[3])#seleccionar Espacio
    element_ficha=driver.find_element("id", 'Ficha_fic')
    
    element_ficha.send_keys(Datos[0])
    profesional=driver.find_element("id", 'Nombre_profesional')
    profesional.send_keys(Datos[2])
    element_fecha=driver.find_element("id", 'Fecha_ingreso')
    element_fecha.send_keys(Datos[1])
    element_fecha2=driver.find_element("id", 'Fecha_entrega_profesional')
    element_fecha2.send_keys(Datos[1])
    
    PERFIL = Select(driver.find_element("id", 'Id_perfil'))
    PERFIL.select_by_visible_text(Datos[5])#seleccionar PERFIL
    
    Base = Select(driver.find_element("id", 'Id_Base'))
    Base.select_by_visible_text(Datos[4])#seleccionar Base
    
    driver.find_element("xpath", '/html/body/div/div/main/div/div/div/div[2]/form/div[12]/div/center/input').click()
    driver.find_element("xpath", '/html/body/div[2]/div/div[3]/button[1]').click()
    driver.find_element("xpath", '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[5]/input').click()
    driver.find_element("xpath", '/html/body/div[2]/div/div[3]/button[1]').click()
    
    

def DatosCrearSi(Datos):
    Digitado = Select(driver.find_element("id", 'Digitado'))
    Digitado.select_by_visible_text('Si')#seleccionar Base
    element_fecha3=driver.find_element("id", 'Fecha_entrega_tecnologo')
    element_fecha3.send_keys(Datos[1])
    element_fecha3=driver.find_element("id", 'Fecha_actualizacion')
    element_fecha3.send_keys(Datos[1])
    element_fecha4=driver.find_element("id", 'Fecha_entrega_digitacion')
    element_fecha4.send_keys(Datos[1])
    element_NoActua=driver.find_element("id", 'Nro_actualizacion')
    element_NoActua.send_keys('1')
    llenar(Datos)
    
filesheet = "./crearIndividual.xlsx"
wb = load_workbook(filesheet)
hojas = wb.get_sheet_names()
print(hojas)
nombres = wb.get_sheet_by_name('Hoja1')
wb.close()

def ejecutar_accion():
    respuesta = messagebox.askyesno("Confirmación", "¿Deseas ejecutar esta acción con el Si Digitado?")
    if respuesta:
        # si la respuesta es "si"
        for i in range(1,895):
            ficha, fecha, profesional,entorno, base, perfil  = nombres[f'A{i}:F{i}'][0]
            print(ficha.value)
            print(fecha.value)
            print(profesional.value)
            print(entorno.value)
            ficha1 = ficha.value
            fecha1 = fecha.value
            format = fecha1.strftime('%d/%m/%Y')
            profesional1 = profesional.value 
            Entorno1 = entorno.value
            perfil1 = perfil.value
            base1 = base.value
            Datos = [ficha1,format,profesional1, Entorno1, base1, perfil1]
            DatosCrearSi(Datos)
    else:
        # Código para la acción si la respuesta es "no"
        for i in range(1,895):
            ficha, fecha, profesional,entorno, base, perfil  = nombres[f'A{i}:F{i}'][0]
            print(ficha.value)
            print(fecha.value)
            print(profesional.value)
            print(entorno.value)
            ficha1 = ficha.value
            fecha1 = fecha.value
            format = fecha1.strftime('%d/%m/%Y')
            profesional1 = profesional.value 
            Entorno1 = entorno.value
            perfil1 = perfil.value
            base1 = base.value
            Datos = [ficha1,format,profesional1, Entorno1, base1, perfil1]
            llenar(Datos)

ventana = tk.Tk()
# Agregar título a la ventana
ventana.title("Creacion de Fichas / Herramienta de control")

# Ajustar el tamaño de la ventana
ventana.geometry("400x200")  # Ancho x Alto

# Obtener el ancho y alto de la pantalla
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()

# Calcular las coordenadas x e y para centrar la ventana
x = (ancho_pantalla - ventana.winfo_reqwidth()) // 2
y = (alto_pantalla - ventana.winfo_reqheight()) // 2

# Configurar la posición inicial de la ventana
ventana.geometry("+{}+{}".format(x, y))

# Crear un botón para ejecutar la acción
boton = tk.Button(ventana, text="Iniciar La Creación", command=ejecutar_accion, width=15, height=2)
boton.place(relx=0.5, rely=0.5, anchor="center")

# Iniciar el bucle de eventos
ventana.mainloop()

driver.close()