from openpyxl import load_workbook
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.simpledialog as simpledialog
from colorama import init, Fore, Style
import os
import numpy as np
from openpyxl.styles import PatternFill

init()

bgError = PatternFill(start_color='FFFF0000', end_color='FFFF0000', fill_type='solid')
                
outputResult = 0
totalErrores = 0

def loadExcel():
    global outputResult
    outputResult = 0
    global totalErrores
    totalErrores = 0
    global fileRoute
    fileRoute = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx;*.xls;*.csv")])
    if fileRoute:
        global df
        if fileRoute.endswith(".csv"):
            df = pd.read_csv(fileRoute, header=1, encoding="latin1", delimiter=";")
        else:
            workbook = load_workbook(fileRoute)
            global sheet
            sheet = workbook.active
            data = sheet.values
            cols = next(data)[1:]  # Obtener los encabezados de las columnas (ignorar la primera columna)
            #df = pd.DataFrame(data, columns=cols)
    else:
        print("El archivo no se cargó")
def setBase(base):
    loadExcel()
    print("Validando, por favor espere...")
    chooseBase(base)
    preguntaDescarga()
    
    
##------------------------------------------------------------------------------------    
##---------------------------------VALIDADOR------------------------------------------
##------------------------------------------------------------------------------------

def validarTelefono():
    global outputResult
    global totalErrores
    outputResult = 0
    totalErrores = 0        
    
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=1, max_col=sheet.max_column):
        for cellTelefono in row:
            if cellTelefono.column == '.Teléfono.' and len(str(cellTelefono.value).strip()) not in [7, 10]:
                cellTelefono.fill = bgError
                outputResult += 1
                totalErrores += 1
    
    print("Total errores en teléfono:", outputResult)

def validarNoManzana():
    global outputResult
    global totalErrores
    outputResult = 0
    for index, fila in df.iterrows():
        cellManzana = fila['.Manzana de cuidado.']
        nroManzana = fila['.Nro Manzana.']
        if cellManzana == "SI" and pd.isnull(nroManzana):
            outputResult += 1
            totalErrores += 1
            print("Error en manzana del cuidado encontrado")
    print("Total errores en manzana del cuidado:" + str(outputResult))

##------------------------------------------------------------------------------------
##------------------------------------------------------------------------------------

def sc():
    #validarNoManzana()
    validarTelefono()
    print("\x1b[31mTotal errores "+ str(totalErrores) +"\x1b[0m")

def chooseBase(base):
    switch = {
        "sesiones_colectivas": sc
    }
    execute_validator = switch.get(base)
    execute_validator()

def saveFile():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            file_path_modificado = file_path.replace('.xlsx', '_errores.xlsx')
            with pd.ExcelWriter(file_path_modificado, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            print("El archivo ha sido guardado correctamente!")
            
            # Preguntar al usuario si desea abrir el archivo guardado
            open_file = messagebox.askquestion("Abrir Archivo", "¿Desea abrir el archivo guardado?")
            if open_file == 'yes':
                os.startfile(file_path_modificado)  # Abre el archivo guardado
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

def preguntaDescarga():
    try:
        respuesta = messagebox.askquestion("Abrir Archivo", "¿Guardar el archivo generado?")
        if respuesta == "yes":
            cadenaGuardar = "Guardando archivo..."
            print(cadenaGuardar)
            print(cargandoSave(cadenaGuardar))
            saveFile()
        else:
            print("Tu archivo no será descargado")
    except Exception as e:
        print(f"No se pudo guardar el archivo: {str(e)}")

def cargandoSave(cadena):
    if cadena:
        # Borra el último carácter usando slicing
        nueva_cadena = cadena[:-3]
        return nueva_cadena
    else:
        return cadena