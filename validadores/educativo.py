import tkinter as tk
from tkinter import filedialog, messagebox
import openpyxl
import re
import shutil
from openpyxl.styles import PatternFill
from openpyxl import load_workbook
import pandas as pd
import tkinter.simpledialog as simpledialog
from colorama import init, Fore, Style
import os
from openpyxl.utils import get_column_letter
from openpyxl.styles import numbers
import datetime
#validadores educativo 

init()

# Declarar el objeto colum inicialmente
colum = {"column": set(), "row": 0}
celTexto = {"ColumText": set()}
Genero = {"Genero": set()}
etniaVal = {"etniaVal": set()}


def loadExcel():
    # Abrir el archivo Excel
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if not file_path:
        return

    global workbook
    workbook = openpyxl.load_workbook(file_path)
    global sheet
    sheet = workbook.active
    


def setBase(base):
    loadExcel()
    chooseBase(base)
    preguntaDescarga()
    
def chooseBase(base):
    switch = {
        "sesiones_colectivas": SesionesCoelctivas,
        "prevencion_embarazo": PrevencionEmbarazo
    }
    execute_validator = switch.get(base)
    execute_validator()

def SesionesCoelctivas():
    # Páginas del archivo Excel cargado
    num_paginas = len(workbook.sheetnames)
    print(f"El archivo Excel tiene {num_paginas} páginas.")

    # Primero, validar la página 1
    if num_paginas >= 1 and workbook.sheetnames[0] in workbook.sheetnames:
        sheet = workbook[workbook.sheetnames[0]]  # Acceder a la página 1
        print("Validando la página 1...")
        validar_pagina1_sesiones(sheet)

    # Luego, validar la página 2 si existe
    if num_paginas >= 2 and workbook.sheetnames[1] in workbook.sheetnames:
        sheet = workbook[workbook.sheetnames[1]]  # Acceder a la página 2
        print("Validando la página 2...")
        validar_pagina2_sesiones(sheet)
    
    # Luego, validar la página 3 si existe
    if num_paginas >= 3 and workbook.sheetnames[2] in workbook.sheetnames:
        sheet = workbook[workbook.sheetnames[2]]  # Acceder a la página 2
        print("Validando la página 3...")
        validar_pagina3_sesiones(sheet)

def validar_pagina1_sesiones(sheet):
    regex = re.compile("^[a-zA-ZÑñáéíóúÁÉÍÓÚ\s]+$")
    patternTel = re.compile(r'^\d{7}(\d{3})?$')
    try:
        remplazarComillas(sheet)
        ultima_fila = sheet.max_row
        celdas_pintadas_rojo = 0
        
        for i in range(2, ultima_fila + 1):
            # Tipo institución
            if len(sheet.cell(i, 8).value.strip()) > 0 and len(sheet.cell(i, 9).value.strip()) > 0:
                celdas_pintadas_rojo += 1
                colum["column"] = {8, 9, 2}
                colum["row"] = i
                pintar(colum, sheet)
                celdas_pintadas_rojo += 1
                
            # Nombre institución
            if not sheet.cell(row=i, column=10).value:
                celdas_pintadas_rojo += 1
                colum["column"] = {10, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            # Barrio
            if not sheet.cell(row=i, column=21).value or not regex.match(sheet.cell(row=i, column=21).value):
                celdas_pintadas_rojo += 1
                colum["column"] = {21, 2}
                colum["row"] = i
                pintar(colum, sheet)
            
            # verificar si es barrio priorizado
            if sheet.cell(i, 24).value == "SI"  and not len(sheet.cell(i, 25).value.strip()) > 0:
                celdas_pintadas_rojo += 1
                colum["column"] = {24, 25, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            # Verifica la condición para el cuarto conjunto de celdas (teléfono)
            telefono = str(sheet.cell(i, 44).value)
            if not patternTel.match(telefono):
                celdas_pintadas_rojo += 1
                colum["column"] = {44, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            if not sheet.cell(i, 10).value:
                celdas_pintadas_rojo += 1
                colum["column"] = {10, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            # Verifica si las celdas contienen números almacenados como texto y convierte a valor numérico si es necesario
            for col_num in [26, 31, 35]:
                cell_value = sheet.cell(row=i, column=col_num).value
                if isinstance(cell_value, str) and cell_value.isdigit():
                    sheet.cell(row=i, column=col_num).value = float(cell_value)

            # Luego, verifica si el valor convertido es mayor a 250 y aplica el formato de relleno rojo si es necesario
            for col_num in [26, 31, 35]:
                cell_value = sheet.cell(row=i, column=col_num).value
                if isinstance(cell_value, (int, float)) and cell_value > 250:
                    sheet.cell(row=i, column=col_num).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                    sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                    celdas_pintadas_rojo += 1
        
        # Mostrar la cantidad de celdas pintadas de rojo
        print(f"Total errores encontrados {celdas_pintadas_rojo}.")

    except Exception as e:
        print("Error", f"Se produjo un error: {str(e)}")    
def validar_pagina2_sesiones(sheet):
    regex = re.compile("^[a-zA-ZÑñáéíóúÁÉÍÓÚ\s]+$")
    patternTel = re.compile(r'^\d{7}(\d{3})?$')
    try:
        remplazarComillas(sheet)
        ultima_fila = sheet.max_row
        celdas_pintadas_rojo = 0

        # Obtener la fecha actual
        fechaActual = datetime.datetime.now()

        # Convertir la fecha actual a un formato de fecha (si solo necesitas la fecha)
        fechaActual = fechaActual.date()
        
        for i in range(2, ultima_fila + 1):
            # Tipo institución
            if not len(sheet.cell(i, 8).value.strip()) > 0 :
                celdas_pintadas_rojo += 1
                colum["column"] = {8, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            # ingresart mas validadores para la pagina dos
                
            if not sheet.cell(row=i, column=14).value or not regex.match(sheet.cell(row=i, column=14).value):
                celdas_pintadas_rojo += 1
                colum["column"] = {14, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            if not sheet.cell(row=i, column=16).value or not regex.match(sheet.cell(row=i, column=16).value):
                celdas_pintadas_rojo += 1
                colum["column"] = {16, 2}
                colum["row"] = i
                pintar(colum, sheet)
            
            if not sheet.cell(row=i, column=18).value or not regex.match(sheet.cell(row=i, column=18).value):
                celdas_pintadas_rojo += 1
                colum["column"] = {18, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            if sheet.cell(i, 13).value < sheet.cell(i, 3).value : 
                celdas_pintadas_rojo += 1
                colum["column"] = {13, 3, 2}
                colum["row"] = i
                pintar(colum, sheet)
            
             # Obtener el valor de la celda y convertirlo a datetime.date si es un string
            
            fecha_celda_texto = sheet.cell(i, 13).value

            # Convertir el texto de la celda a objeto datetime si es un string
            try:
                fecha_celda = datetime.datetime.strptime(fecha_celda_texto, "%Y/%m/%d").date()
            except ValueError:
                # Manejar el caso en que la conversión no sea posible
                #print("La fecha en la celda {} no se pudo convertir. Revisar el formato.".format((i, 13)))
                continue

            # Comparar la fecha en la celda con la fecha actual
            if fecha_celda > fechaActual:
                celdas_pintadas_rojo += 1
                colum["column"] = {13, 3, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
                
                
         # Mostrar la cantidad de celdas pintadas de rojo
        print(f"Total errores encontrados {celdas_pintadas_rojo}.")

    except Exception as e:
        print("Error", f"Se produjo un error: {str(e)}")
def validar_pagina3_sesiones(sheet):
    regex = re.compile("^[a-zA-ZÑñáéíóúÁÉÍÓÚ\s]+$")
    NumeroDocumento = re.compile("^\d{10}$")
    try:
        remplazarComillas(sheet)  
        ultima_fila = sheet.max_row
        celdas_pintadas_rojo = 0
            
        for i in range(2, ultima_fila + 1):
            # Tipo institución
            if sheet.cell(i, 11).value == "2- Mujer" and sheet.cell(i, 12).value != "2- Femenino" :
                celdas_pintadas_rojo += 1
                colum["column"] = {11, 12, 2}
                colum["row"] = i
                pintar(colum, sheet)
            
            if sheet.cell(i, 11).value == "1- Hombre" and sheet.cell(i, 12).value != "1- Masculino" :
                celdas_pintadas_rojo += 1
                colum["column"] = {11, 12, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            if sheet.cell(i, 11).value == "3- Intersexual" and sheet.cell(i, 12).value != "3- Transgénero" :
                celdas_pintadas_rojo += 1
                colum["column"] = {11, 12, 2}
                colum["row"] = i
                pintar(colum, sheet)
        
        #validador de campos por la edad 
        for i in range(2, ultima_fila + 1):
            FechaIntervencion = sheet.cell(i, 3).value
            FechaNacimiento = sheet.cell(i, 14).value
            FechaNacimiento = FechaNacimiento.replace('/', '-')  # Reemplazar '/' por '-'
            FechaNacimiento_format = FechaNacimiento.replace('`', '')  
            FechaIntervencion_format = FechaIntervencion.replace('`', '') 
            edad = calcular_edad(FechaNacimiento_format, FechaIntervencion_format)
            
            if edad >= 0 and edad <= 6 :
                tipodocumento = "2- RC"
                Nacionalidad = "COL"
                
            if edad >= 7 and edad <= 17 :
                tipodocumento = "3- TI"
                Nacionalidad = "COL"
                
            if edad >= 18:
                tipodocumento = "1- CC"
                Nacionalidad = "COL"
                
            if (sheet.cell(i, 10).value != tipodocumento and sheet.cell(i, 10).value != "8- Menor sin ID." and \
                sheet.cell(i, 10).value != "7- Adulto sin ID.") and sheet.cell(i, 16).value == Nacionalidad :
                celdas_pintadas_rojo += 1
                colum["column"] = {10, 16, 14, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
          
            if sheet.cell(i,10).value == tipodocumento and sheet.cell(i,16).value != Nacionalidad:
                celdas_pintadas_rojo += 1
                colum["column"] = {10, 16, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            if edad > 100:
                celdas_pintadas_rojo += 1
                colum["column"] = {14, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            # estado civil
            if edad <= 13 and sheet.cell(i,13).value != "6- No aplica":
                celdas_pintadas_rojo += 1
                colum["column"] = {13, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            #verificar poblacion
            if edad <= 14 and sheet.cell(i,19).value != "Estudiante":
                celdas_pintadas_rojo += 1
                colum["column"] = {17, 19, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            #verificar poblacion
            if edad <= 17 and sheet.cell(i,19).value == "Docente":
                celdas_pintadas_rojo += 1
                colum["column"] = {17, 19, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            numeroDocumento = sheet.cell(i, 9).value
            # Verifica si el número de documento cumple con el patrón y satisface las condiciones adicionales
            if (not NumeroDocumento.match(numeroDocumento) and 
                sheet.cell(i, 10).value not in ["8- Menor sin ID.", "7- Adulto sin ID.", "13- PPT Permiso por Protección Temporal", "5- NUIP"] and 
                edad < 35):
                celdas_pintadas_rojo += 1
                colum["column"] = {9, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            if len(numeroDocumento) < 5: 
                celdas_pintadas_rojo += 1
                colum["column"] = {9, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
        for i in range(2, ultima_fila + 1):          
            if sheet.cell(i, 16).value == "COL" and \
                sheet.cell(i, 10).value not in ["2- RC", "3- TI", "1- CC", "8- Menor sin ID.", "7- Adulto sin ID."]:
                    celdas_pintadas_rojo += 1
                    colum["column"] = {16, 10, 2}
                    colum["row"] = i
                    pintar(colum, sheet)
                    
        for i in range(2, ultima_fila + 1):          
            if sheet.cell(i, 16).value != "COL" and \
                sheet.cell(i, 10).value in ["2- RC", "3- TI", "1- CC"]:
                    celdas_pintadas_rojo += 1
                    colum["column"] = {16, 10, 2}
                    colum["row"] = i
                    pintar(colum, sheet)
                    
            if not sheet.cell(row=i, column=8).value or not regex.match(sheet.cell(row=i, column=8).value):  
                celdas_pintadas_rojo += 1
                colum["column"] = {8, 2}
                colum["row"] = i
                pintar(colum, sheet)   
                      
        # Mostrar la cantidad de celdas pintadas de rojo
        print(f"Total errores encontrados {celdas_pintadas_rojo}.")

    except Exception as e:
        print("Error", f"Se produjo un error: {str(e)}")
   
def PrevencionEmbarazo(): 
    # Páginas del archivo Excel cargado
    num_paginas = len(workbook.sheetnames)
    print(f"El archivo Excel tiene {num_paginas} páginas.")
    # Primero, validar la página 1
    if num_paginas >= 1 and workbook.sheetnames[0] in workbook.sheetnames:
        sheet = workbook[workbook.sheetnames[0]]  # Acceder a la página 1
        print("Validando la página 1...")
        prevencionPag1(sheet) 
        
def prevencionPag1(sheet):
    regex = re.compile("^[a-zA-ZÑñáéíóúÁÉÍÓÚ\s]+$")
    NumeroDocumento = re.compile("^\d{10}$")
    try:
        remplazarComillas(sheet)  
        ultima_fila = sheet.max_row
        celdas_pintadas_rojo = 0
        
        #validador de campos por la edad 
        for i in range(2, ultima_fila + 1):
            FechaIntervencion = sheet.cell(i, 3).value
            FechaNacimiento = sheet.cell(i, 18).value
            FechaNacimiento = FechaNacimiento.replace('/', '-')  # Reemplazar '/' por '-'
            FechaNacimiento_format = FechaNacimiento.replace('`', '')  
            FechaIntervencion_format = FechaIntervencion.replace('`', '')             
            edad = calcular_edad(FechaNacimiento_format, FechaIntervencion_format)
            
            if edad >= 0 and edad <= 6 :
                tipodocumento = "2- RC"
                Nacionalidad = "Colombia"
                
            if edad >= 7 and edad <= 17 :
                tipodocumento = "3- TI"
                Nacionalidad = "Colombia"
                
            if edad >= 18:
                tipodocumento = "1- CC"
                Nacionalidad = "Colombia"
                
            if (sheet.cell(i, 8).value != tipodocumento and sheet.cell(i, 8).value != "8- Menor sin ID." and \
                sheet.cell(i, 8).value != "7- Adulto sin ID.") and sheet.cell(i, 14).value == Nacionalidad :
                celdas_pintadas_rojo += 1
                colum["column"] = {8, 18, 14, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            if sheet.cell(i,8).value == tipodocumento and sheet.cell(i,14).value != Nacionalidad:
                celdas_pintadas_rojo += 1
                colum["column"] = {8, 14, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            if edad > 100:
                celdas_pintadas_rojo += 1
                colum["column"] = {18, 19, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            # estado civil
            if edad <= 13 and sheet.cell(i,17).value != "6- No aplica":
                celdas_pintadas_rojo += 1
                colum["column"] = {17,18, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            numeroDocumento = sheet.cell(i, 9).value
            # Verifica si el número de documento cumple con el patrón y satisface las condiciones adicionales
            if (not NumeroDocumento.match(numeroDocumento) and 
                sheet.cell(i, 8).value not in ["8- Menor sin ID.", "7- Adulto sin ID.", "13- PPT Permiso por Protección Temporal", "5- NUIP"] and 
                edad < 35):
                celdas_pintadas_rojo += 1
                colum["column"] = {9, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            if len(numeroDocumento) < 5: 
                celdas_pintadas_rojo += 1
                colum["column"] = {9, 2}
                colum["row"] = i
                pintar(colum, sheet)
                
        celTexto["ColumText"] = {10, 11, 12, 13, 51}      
        celdas_pintadas_rojo += validarCeldasTexto(sheet, celTexto)
        
        Genero["Genero"]= {15, 16}
        celdas_pintadas_rojo += validadorsexoGenero(sheet, Genero)
        
        etniaVal["etnia"]= {21, 22}
        celdas_pintadas_rojo += Valetnia(sheet, etniaVal)
        
       # Mostrar la cantidad de celdas pintadas de rojo
        print(f"Total errores encontrados {celdas_pintadas_rojo}.")

    except Exception as e:
        print("Error", f"Se produjo un error: {str(e)}")
   
    
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def Valetnia(sheet, etnia):
    celdas_pintadas_rojo = 0
    ultima_fila = sheet.max_row
    columns = list(etnia["etnia"])
    print(columns[0])
    for i in range(2, ultima_fila + 1):
            # Tipo institución
            if sheet.cell(i, columns[0]).value != "6- Ninguno" and sheet.cell(i, columns[1]).value == "-1" :
                celdas_pintadas_rojo += 1
                colum["column"] = {columns[0], columns[1], 2}
                colum["row"] = i
                pintar(colum, sheet)
            elif sheet.cell(i, columns[0]).value == "6- Ninguno" and sheet.cell(i, columns[1]).value != "-1" :
                celdas_pintadas_rojo += 1
                colum["column"] = {columns[0], columns[1], 2}
                colum["row"] = i
                pintar(colum, sheet)
    
    return  celdas_pintadas_rojo  
    
def validadorsexoGenero(sheet, Genero):
    celdas_pintadas_rojo = 0
    ultima_fila = sheet.max_row
    columns = list(Genero["Genero"])
        
    for i in range(2, ultima_fila + 1):
            # Tipo institución
            if sheet.cell(i, columns[-1]).value == "2- Mujer" and sheet.cell(i, columns[0]).value != "2- Femenino" :
                celdas_pintadas_rojo += 1
                colum["column"] = {columns[-1], columns[0], 2}
                colum["row"] = i
                pintar(colum, sheet)
            
            if sheet.cell(i, columns[-1]).value == "1- Hombre" and sheet.cell(i, columns[0]).value != "1- Masculino" :
                celdas_pintadas_rojo += 1
                colum["column"] = {columns[0], columns[1], 2}
                colum["row"] = i
                pintar(colum, sheet)
                
            if sheet.cell(i, columns[-1]).value == "3- Intersexual" and sheet.cell(i, columns[0]).value != "3- Transgénero" :
                celdas_pintadas_rojo += 1
                colum["column"] = {columns[-1], columns[0], 2}
                colum["row"] = i
                pintar(colum, sheet)
                
    return  celdas_pintadas_rojo      
                             
def validarCeldasTexto(sheet, celTexto):
    celdas_pintadas_rojo = 0
    regex = re.compile("^[a-zA-ZÑñáéíóúÁÉÍÓÚ\s]+$")
    ultima_fila = sheet.max_row
    Num_celTexto = len(celTexto["ColumText"])
    columns = list(celTexto["ColumText"])
    for a in range(Num_celTexto):
        for i in range(2, ultima_fila + 1):
            if sheet.cell(row=i, column=columns[a]).value and not regex.match(sheet.cell(row=i, column=columns[a]).value):  
                    celdas_pintadas_rojo += 1
                    colum["column"] = {columns[a], 2}
                    colum["row"] = i
                    pintar(colum, sheet) 
    return  celdas_pintadas_rojo

# funcio para remplazar comillas
def remplazarComillas(sheet):
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value and '`' in cell.value:
                # Elimina las comillas
                cell.value = cell.value.replace('`', '')

                # Verifica si el valor es un número
                if isinstance(cell.value, (int, float)):
                    cell.number_format = numbers.FORMAT_NUMBER
                # Verifica si el valor es una fecha
                elif isinstance(cell.value, datetime.date):
                    cell.number_format = numbers.FORMAT_DATE_XLSX15
                # Verifica si el valor es texto
                else:
                    cell.number_format = numbers.FORMAT_TEXT        
# Función para calcular la edad
def calcular_edad(fecha_nacimiento, fecha_intervencion):
    try :
        nacimiento = datetime.datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
        intervencion = datetime.datetime.strptime(fecha_intervencion, "%Y-%m-%d")
        edad = intervencion.year - nacimiento.year - ((intervencion.month, intervencion.day) < (nacimiento.month, nacimiento.day))
        return edad
    except :
        edad = -50    
        return edad

#funcion para pintar celdas 
def pintar(colum, sheet):
    colorRed = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
    number_colum = len(colum["column"])
    columns = list(colum["column"])
    for i in range(number_colum):
        sheet.cell(row=colum["row"], column=columns[i]).fill = colorRed
  
def saveFile():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        file_path_modificado = file_path.replace('.xlsx', '_errores.xlsx')
        
        # Guardar el libro de trabajo original con los cambios realizados
        workbook.save(file_path)
        # Guardar el archivo modificado con el nombre específico para errores
        workbook.save(file_path_modificado)
        print("Archivo guardado", "El archivo ha sido guardado correctamente.")
        # Preguntar al usuario si desea abrir el archivo guardado
        open_file = messagebox.askquestion("Abrir Archivo", "¿Desea abrir el archivo guardado?")
        if open_file == 'yes':
            os.startfile(file_path_modificado)  # Abre el archivo guardado
    except Exception as e:
        print("Error", f"No se pudo guardar el archivo: {str(e)}")

def preguntaDescarga():
    try:
        respuesta = messagebox.askquestion("Abrir Archivo", "¿Guardar el archivo generado?")
        if respuesta == "yes":
            cadenaGuardar = "Guardando archivo..."
            print(cadenaGuardar)
            saveFile()
        else:
            print("Tu archivo no será descargado")
    except Exception as e:
        print(f"No se pudo guardar el archivo: {str(e)}")
