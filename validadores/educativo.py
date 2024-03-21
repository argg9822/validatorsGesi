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
#from datetime import datetime

init()

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
        print("Validando la página 2...")
        validar_pagina3_sesiones(sheet)


def chooseBase(base):
    switch = {
        "sesiones_colectivas": SesionesCoelctivas
    }
    execute_validator = switch.get(base)
    execute_validator()

def setBase(base):
    loadExcel()
    chooseBase(base)
    preguntaDescarga()

def validar_pagina1_sesiones(sheet):
    regex = re.compile("^[a-zA-ZÑñáéíóúÁÉÍÓÚ\s]+$")
    patternTel = re.compile(r'^\d{7}(\d{3})?$')
    try:
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
        
        ultima_fila = sheet.max_row
        celdas_pintadas_rojo = 0
        
        for i in range(2, ultima_fila + 1):
            # Tipo institución
            if len(sheet.cell(i, 8).value.strip()) > 0 and len(sheet.cell(i, 9).value.strip()) > 0:
                sheet.cell(row=i, column=8).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=9).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
                
            # Nombre institución
            if not sheet.cell(row=i, column=10).value:
                sheet.cell(row=i, column=10).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
            # Barrio
            if not sheet.cell(row=i, column=21).value or not regex.match(sheet.cell(row=i, column=21).value):
                sheet.cell(row=i, column=21).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
            
            # verificar si es barrio priorizado
            if sheet.cell(i, 24).value == "SI"  and not len(sheet.cell(i, 25).value.strip()) > 0:
                sheet.cell(row=i, column=24).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=25).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
                
            # Verifica la condición para el cuarto conjunto de celdas (teléfono)
            telefono = str(sheet.cell(i, 44).value)
            if not patternTel.match(telefono):
                sheet.cell(row=i, column=44).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
                
            if not sheet.cell(i, 10).value:
                sheet.cell(row=i, column=10).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                
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
                    sheet.cell(row=i, column=3).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                    celdas_pintadas_rojo += 1
        
        # Mostrar la cantidad de celdas pintadas de rojo
        print(f"Total errores encontrados {celdas_pintadas_rojo}.")

    except Exception as e:
        print("Error", f"Se produjo un error: {str(e)}")
        
def validar_pagina2_sesiones(sheet):
    regex = re.compile("^[a-zA-ZÑñáéíóúÁÉÍÓÚ\s]+$")
    patternTel = re.compile(r'^\d{7}(\d{3})?$')
    try:
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
        
        ultima_fila = sheet.max_row
        celdas_pintadas_rojo = 0
        
        

        # Obtener la fecha actual
        fechaActual = datetime.datetime.now()

        # Convertir la fecha actual a un formato de fecha (si solo necesitas la fecha)
        fechaActual = fechaActual.date()
        
        for i in range(2, ultima_fila + 1):
            # Tipo institución
            if not len(sheet.cell(i, 8).value.strip()) > 0 :
                sheet.cell(row=i, column=8).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
                
            # ingresart mas validadores para la pagina dos
                
            if not sheet.cell(row=i, column=14).value or not regex.match(sheet.cell(row=i, column=14).value):
                sheet.cell(row=i, column=14).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
                
            if not sheet.cell(row=i, column=16).value or not regex.match(sheet.cell(row=i, column=16).value):
                sheet.cell(row=i, column=16).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
            
            if not sheet.cell(row=i, column=18).value or not regex.match(sheet.cell(row=i, column=18).value):
                sheet.cell(row=i, column=18).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
                
            if sheet.cell(i, 13).value < sheet.cell(i, 3).value : 
                sheet.cell(row=i, column=13).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=3).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
            
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
                # Resaltar las celdas si la fecha es mayor que la actual
                sheet.cell(row=i, column=13).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=3).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
                
                
                
         # Mostrar la cantidad de celdas pintadas de rojo
        print(f"Total errores encontrados {celdas_pintadas_rojo}.")

    except Exception as e:
        print("Error", f"Se produjo un error: {str(e)}")
        
def validar_pagina3_sesiones(sheet):
    regex = re.compile("^[a-zA-ZÑñáéíóúÁÉÍÓÚ\s]+$")
    patternTel = re.compile(r'^\d{7}(\d{3})?$')
    try:
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
        
            ultima_fila = sheet.max_row
            celdas_pintadas_rojo = 0
            
            for i in range(2, ultima_fila + 1):
                # Tipo institución
                if sheet.cell(i, 11).value == "2- Mujer" and sheet.cell(i, 12).value != "2- Femenino" :
                    sheet.cell(row=i, column=11).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                    sheet.cell(row=i, column=12).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                    sheet.cell(row=i, column=2).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                    celdas_pintadas_rojo += 1
            
        
      # Mostrar la cantidad de celdas pintadas de rojo
        print(f"Total errores encontrados {celdas_pintadas_rojo}.")

    except Exception as e:
        print("Error", f"Se produjo un error: {str(e)}")
    
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
