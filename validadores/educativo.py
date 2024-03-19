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

def chooseBase(base):
    switch = {
        "sesiones_colectivas": validar_pagina1_sesiones
    }
    execute_validator = switch.get(base)
    execute_validator()

def setBase(base):
    loadExcel()
    chooseBase(base)
    preguntaDescarga()

def validar_pagina1_sesiones():
    regex = re.compile("^[a-zA-ZÑñáéíóúÁÉÍÓÚ\s]+$")
    patternTel = re.compile(r'^\d{7}(\d{3})?$')
    try:
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value and '`' in cell.value:
                    cell.value = cell.value.replace('`', '')
        
        ultima_fila = sheet.max_row
        celdas_pintadas_rojo = 0
        
        for i in range(2, ultima_fila + 1):
            # Tipo institución
            if len(sheet.cell(i, 9).value.strip()) > 0 and len(sheet.cell(i, 10).value.strip()) > 0:
                sheet.cell(row=i, column=9).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=10).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=3).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
            # Nombre institución
            if not sheet.cell(row=i, column=11).value:
                sheet.cell(row=i, column=11).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=3).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
            # Barrio
            if not sheet.cell(row=i, column=22).value or not regex.match(sheet.cell(row=i, column=22).value):
                sheet.cell(row=i, column=22).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(row=i, column=3).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
        
        # Mostrar la cantidad de celdas pintadas de rojo
        print(f"Total errores {celdas_pintadas_rojo}.")

    except Exception as e:
        print("Error", f"Se produjo un error: {str(e)}")

def saveFile():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        file_path_modificado = file_path.replace('.xlsx', '_errores.xlsx')
        workbook.save(file_path_modificado)
        print("Archivo guardado", "El archivo ha sido gusdfado correctamente.")
        print("Archivo guardado", "El archivo ha sido guardado correctamente.")
    except Exception as e:
        print("Error", f"No se pudo guardar el archivo: {str(e)}")

def preguntaDescarga():
    try:
        respuesta = simpledialog.askstring("Descargar archivo", "¿Desea descargar el archivo generado? (Y/N):")
        if respuesta:
            respuesta = respuesta.upper()
            if respuesta == "Y":
                print("Guardando archivo")
                saveFile()
            elif respuesta == "N":
                print("Tu archivo no será descargado")
            else:
                print("Respuesta no válida. Por favor, responda con 'Y' para descargar o 'N' para no descargar.")
    except Exception as e:
        print(f"No se pudo guardar el archivo: {str(e)}")
