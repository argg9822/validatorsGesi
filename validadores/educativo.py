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
from tqdm import tqdm
import time

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
    regex_telefono = re.compile("^\d{7}(\d{3})?$")
    try:
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value and '`' in cell.value:
                    cell.value = cell.value.replace('`','')
        
        ultima_fila = sheet.max_row
        celdas_pintadas_rojo = 0

        # Configuración de tqdm     
        
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

            if sheet.cell(i, 17).value == "2- Rural" and sheet.cell(i, 42).value == " ": 
                sheet.cell(i, 17).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 42).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 43).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 3).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
        
            if sheet.cell(i, 17).value == "2- Rural" and sheet.cell(i, 43).value == " ": 
                sheet.cell(i, 17).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 42).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 43).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 3).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1
            
            if sheet.cell(i, 17).value == "2- Rural" and sheet.cell(i, 44).value == " ": 
                sheet.cell(i, 17).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 42).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 43).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 3).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                celdas_pintadas_rojo += 1

            if sheet.cell(i, 24).value == "SI" and sheet.cell(i, 25).value.strip() == " ":
                sheet.cell(i, 25).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 24).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
                sheet.cell(i, 3).fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

               
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
