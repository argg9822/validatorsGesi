import shutil
from openpyxl import load_workbook
import openpyxl
from openpyxl.styles import PatternFill
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from io import BytesIO

bgError = '#FF0000'

def loadExcel ():
    global fileRoute
    fileRoute = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
    if fileRoute:
        global df
        df = pd.read_excel(fileRoute, sheet_name=0, header=1)

def setBase(base):
    loadExcel()
    chooseBase(base)
    
def validarTelefono ():
    for index, fila in df.iterrows():
        # Agrega el valor de la celda en la columna A a la lista
        cellTelefono = fila['Telefono']
        # Agrega el valor convertido a la lista de valores enteros
        if len(str(cellTelefono).strip()) != 7 and len(str(cellTelefono).strip()) != 10:
            df['Telefono'] = df['Telefono'].astype('object')
            df.at[index, 'Telefono'] = '<span style="color: {};">{}</span>'.format(bgError, cellTelefono)
            # cellTelefono.fill = bgError
            # cellFicha = df.cell(cellTelefono.row, 2)
            # cellFicha.fill = bgError
    
    return True

def validarNoManzana ():
    for index, fila in df.iterrows():
        cellManzana = fila['.Manzana de cuidado.']
        nroManzana = fila['.Nro Manzana.']        

        if cellManzana == "SI" and nroManzana is None:    
            print("Error en manzana")        
            # nroManzana.fill = bgError
            # cellFicha = df.cell(cellManzana.row, 2)
            # cellFicha.fill = bgError

    return True

def sc():
    validarTelefono()
    validarNoManzana()
    
def chooseBase(base):
    swicth = {
        "sesiones_colectivas":sc
    }

    ejexute_validator = swicth.get(base)
    ejexute_validator()
    saveFile()


def saveFile():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'
        file_path_modificado = file_path.replace('.xlsx', '_errores.xlsx')
        workbook_nuevo = openpyxl.Workbook()
        workbook_nuevo.save(file_path_modificado)
        
        messagebox.showinfo("Archivo guardado", "El archivo ha sido guardado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

    # bio.seek(0)
    # workbook = bio.read()