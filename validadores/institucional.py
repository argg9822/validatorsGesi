import datetime
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import PatternFill
from openpyxl import load_workbook, Workbook
import pandas as pd
from tkinter import filedialog, messagebox
import tkinter.simpledialog as simpledialog
import os
import csv

##------------------------------------------------------------------------------------    
##---------------------CARGUE Y LECTURA DEL ARCHIVO EXCEL-----------------------------
##------------------------------------------------------------------------------------
def setBase(base):
    print(f"Validar {base}")
    loadFilesFromFolder()
    chooseBase(base)
    saveFile()
    
def loadFilesFromFolder():
    print("Cargando y consolidando archivos...")
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        merge_files(folder_selected)

def merge_files(folder_path):    
    # Crea un nuevo libro de Excel
    wb_combined = Workbook() 
    # Itera sobre todos los archivos en la carpeta seleccionada
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            sheet_name = os.path.splitext(file_name)[0]
            ws = wb_combined.create_sheet(title=sheet_name)
            df = pd.read_csv(folder_path+"/"+file_name, header=1, encoding="latin-1", delimiter=";")
        
            for r in dataframe_to_rows(df, index=False, header=True):
                ws.append(r)
                
    # Eliminar la hoja predeterminada creada al inicio
    wb_combined.remove(wb_combined['Sheet'])
    
    # Guarda el nuevo libro combinado
    global fileRoute
    fileRoute = folder_path+'/consolidado.xlsx'
    wb_combined.save(fileRoute)

    # Verifica si el archivo se guardó correctamente
    if os.path.isfile(fileRoute):
        loadExcel()
    else:
        print(f"ERROR: No se pudo guardar el archivo '{fileRoute}'.")
                
def loadExcel():
    global totalErrores
    totalErrores = 0
    if fileRoute:
        global workbook
        workbook = load_workbook(fileRoute)
    else:
        print("El archivo no se cargó")
        
##------------------------------------------------------------------------------------    
##---------------------------SWICTH PARA LAS BASES------------------------------------
##------------------------------------------------------------------------------------
def chooseBase(base):
    switch = {
        "sesiones_colectivas": sc,
        "hcb": hcb
    }
    execute_validator = switch.get(base)
    execute_validator()
    
##------------------------------------------------------------------------------------    
##--------------------------FUNCIONES PARA CADA BASE----------------------------------
##------------------------------------------------------------------------------------
def sc():
    for index, sheet_name in enumerate(workbook.sheetnames):
        global sheet
        sheet = workbook[sheet_name]
        data = sheet.values
        cols = next(data) # Obtener los encabezados de las columnas (ignorar la primera columna)
        global df
        print(f"------------Validación página {index+1}------------")
        if index == 0:
            df = pd.DataFrame(data, columns=cols)
            totalErroresPg_1 = sc_pg1()
        
        if index == 1:
            df = pd.DataFrame(data, columns=cols)
            totalErroresPg_2 = sc_pg2()
        
    cantErrSc = totalErroresPg_1+totalErroresPg_2
    print(f"TOTAL ERRORES EN SESIONES COLECTIVAS: {(cantErrSc)}")

def sc_pg1():
    requiredFieldsPg1 = ['.Nombre de la institución / Establecimiento / Equipo étnico.',
                   '.Zona.', '.Localidad.', '.UPZ/UPR.', '.Barrio.', '.Teléfono.',
                   '.Barrio priorizado.', '.Tipo de Institución.']
    catnErroresPg_1 = (requiredFields(requiredFieldsPg1) + validarNoManzana() + validarTelefono())
    return catnErroresPg_1

def sc_pg2():
    requiredFieldsPg2 = ['.Componente.', '.Línea operativa.', '.Dimensión.', 
                         '.Temática.', '.Número sesión.', '.Fecha.', '.Nombre profesional 1.']
    catnErroresPg_2 = requiredFields(requiredFieldsPg2)+sesionDate()
    return catnErroresPg_2

def hcb():
    print("Entrando a validar HCB")
    
##------------------------------------------------------------------------------------    
##---------------------------------VALIDADOR------------------------------------------
##------------------------------------------------------------------------------------

#----------------------------------FUNCIONES GENERALES--------------------------------
def setBgError(index, columnName):    
    bgError = PatternFill(start_color='FFFF0000', end_color='FFFF0000', fill_type='solid')
    
    cell = sheet.cell(row=index+2, column=df.columns.get_loc(columnName)+1)
    cell.fill = bgError
    
    cellFicha = sheet.cell(row=index+2, column=df.columns.get_loc('Ficha_fic')+1)
    cellFicha.fill = bgError

def validarTelefono():
    columnName = '.Teléfono.'
    cantErroresTel = 0
    if columnName in df.columns:
        for index, fila in df.iterrows():   
            cellTelefono = int(fila[columnName]) if pd.notna(fila[columnName]) else fila[columnName]
            if len(str(cellTelefono).strip()) not in [7, 10] and pd.notna(cellTelefono):
                cantErroresTel += 1                
                setBgError(index, columnName)
    else:
        print("No se encuentra la columna Teléfono")
    print(f"Total errores en teléfono: {cantErroresTel}")
    return cantErroresTel

def validarNoManzana():
    columnNameManzana = '.Manzana de cuidado.'
    columnNameNroManzana = '.Nro Manzana.'
    totalErrApple = 0
    
    if columnNameManzana in df.columns:
        for index, fila in df.iterrows():
            cellManzana = fila[columnNameManzana]
            nroManzana = fila[columnNameNroManzana]
            if cellManzana == "SI" and pd.isna(nroManzana):                
                totalErrApple += 1
                setBgError(index, columnNameNroManzana)
    else:
        print("No se encuentra la columna manzana del cuidado")
    print(f"Total errores en manzana del cuidado: {totalErrApple}")
    return totalErrApple

def requiredFields(arrayFields):
    totalEmptyFields = 0
    
    for field in arrayFields:
        if field in df.columns:
            for j, fila in df.iterrows():
                cellField = fila[field]
                if pd.isna(cellField):
                    totalEmptyFields += 1
                    setBgError(j, field)
        else:
            print('No se encontró la columna')
    
    print(f"Campos obligatorios vacíos: {totalEmptyFields}")
    return totalEmptyFields
#-----------------------------------SESIONES PÁGINA 2---------------------------------
def sesionDate():
    totalErrDate = 0
    for index, fila in df.iterrows():
        columnNameDate = '.Fecha.'
        cellDateSesion = fila[columnNameDate]
        cellDateSesionInter = fila['Fecha_intervencion']
        
        if pd.notna(cellDateSesion):
            if pd.to_datetime(cellDateSesion) < pd.to_datetime(cellDateSesionInter):
                setBgError(index, columnNameDate)
                totalErrDate += 1
    return totalErrDate
        
    
##------------------------------------------------------------------------------------
##------------------------------------------------------------------------------------

def saveFile():
    response_save = messagebox.askquestion("Guardar archivo", "¿Guardar el archivo generado?")
    if response_save == "yes":
        cadenaGuardar = "Guardando archivo..."
        print(cadenaGuardar)
        
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            file_path_modificado = file_path.replace('.xlsx', '_errores.xlsx')
            workbook.save(file_path)
            workbook.save(file_path_modificado)
            
            print("¡El archivo ha sido guardado correctamente!")
            # Preguntar al usuario si desea abrir el archivo guardado
            open_file = messagebox.askquestion("Abrir Archivo", "¿Desea abrir el archivo guardado?")
            if open_file == 'yes':
                os.startfile(file_path_modificado)# Abre el archivo guardado
                print(f"El archivo quedó guardado en la ruta {file_path_modificado}")
        except Exception as e:
            print("Error", f"No se pudo guardar el archivo: {str(e)}")
    else:
            print("Tu archivo no se guardará")
#En prueba para los tres puntos cargando
def cargandoSave(cadena):
    if cadena:
        # Borra el último carácter usando slicing
        nueva_cadena = cadena[:-3]
        return nueva_cadena
    else:
        return cadena