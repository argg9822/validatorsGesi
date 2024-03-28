from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import PatternFill
from openpyxl import load_workbook, Workbook
import pandas as pd
from tkinter import filedialog, messagebox
import os

##------------------------------------------------------------------------------------    
##---------------------CARGUE Y LECTURA DEL ARCHIVO EXCEL-----------------------------
##------------------------------------------------------------------------------------
def setBase(base):
    print(f"Validar >>>{base.upper()}<<<")
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
        print(f"-------------------Página {index+1}-------------------")
        if index == 0:
            df = pd.DataFrame(data, columns=cols)
            totalErroresPg_1 = sc_pg1()
        
        if index == 1:
            df = pd.DataFrame(data, columns=cols)
            totalErroresPg_2 = sc_pg2()
            
        if index == 2:
            df = pd.DataFrame(data, columns=cols)
            totalErroresPg_3 = sc_pg3()
        
    cantErrSc = totalErroresPg_1+totalErroresPg_2+totalErroresPg_3
    print(f"TOTAL ERRORES EN SESIONES COLECTIVAS: {(cantErrSc)}")
    
def hcb():
    print("Entrando a validar HCB")
    
##------------------------------------------------------------------------------------    
##---------------------------------VALIDATOR------------------------------------------
##------------------------------------------------------------------------------------

#----------------------------------GENERAL FUNCTIONS----------------------------------
bgError = 'FFFF0000'
bgSecError = '005FFF'
def setBgError(index, columnName, color):    
    bgError = PatternFill(start_color=color, end_color=color, fill_type='solid')
    cell = sheet.cell(row=index+2, column=df.columns.get_loc(columnName)+1)
    cell.fill = bgError
    
    bgErrorFicha = PatternFill(start_color='FFFF0000', end_color='FFFF0000', fill_type='solid')
    cellFicha = sheet.cell(row=index+2, column=df.columns.get_loc('Ficha_fic')+1)
    cellFicha.fill = bgErrorFicha

def validarTelefono():
    columnName = '.Teléfono.'
    cantErroresTel = 0
    if columnName in df.columns:
        for index, fila in df.iterrows():   
            cellTelefono = int(fila[columnName]) if pd.notna(fila[columnName]) else fila[columnName]
            if len(str(cellTelefono).strip()) not in [7, 10] and pd.notna(cellTelefono):
                cantErroresTel += 1                
                setBgError(index, columnName, bgError)
    else:
        print("No se encuentra la columna Teléfono")
    print(f"Teléfonos con longitud incorrecta: {cantErroresTel}")
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
                setBgError(index, columnNameNroManzana,bgError)
    else:
        print("No se encuentra la columna manzana del cuidado")
    print(f"Errores en manzana del cuidado: {totalErrApple}")
    return totalErrApple

def required_fields(arrayFields):
    totalEmptyFields = 0
    
    for field in arrayFields:
        if field in df.columns:
            for j, fila in df.iterrows():
                cellField = fila[field]
                if pd.isna(cellField):
                    totalEmptyFields += 1
                    setBgError(j, field, bgError)
        else:
            print(f'No se encontró la columna {field}')
    
    print(f"Campos obligatorios vacíos: {totalEmptyFields}")
    return totalEmptyFields

def len_num_doc(columNameTypeDoc, columnNameNumDoc):
    totalErrLenDoc = 0
    # Verificar la existencia de las columnas requeridas
    if columNameTypeDoc not in df.columns or columnNameNumDoc not in df.columns:
        raise ValueError(f'Las columnas {columNameTypeDoc} y/o {columnNameNumDoc} no se encuentran.')
    
    #Filtrar filas que no están vacías
    fill_rows = df[pd.notna(df[columNameTypeDoc]) & pd.notna(df[columnNameNumDoc])]
    errors = fill_rows[(fill_rows[columNameTypeDoc].isin([61,60])) & 
                            (fill_rows[columnNameNumDoc].astype(str).str.len() != 10)]
    
    totalErrLenDoc = len(errors)
    for index in errors.index:
        setBgError(index, columnNameNumDoc, bgError)
        
    print(f'Números de documento con longitud incorrecta: {totalErrLenDoc}')
    return totalErrLenDoc

def age_vs_typedoc(columnNameTypeDoc, columnNameAge):
    totalTypeDocErr = 0
    # Verificar la existencia de las columnas requeridas
    if columnNameTypeDoc not in df.columns or columnNameAge not in df.columns:
        raise ValueError(f'Las columnas {columnNameTypeDoc} y/o {columnNameAge} no se encuentran')
    
    #Filtrar filas que no están vacías
    fill_rows = df[pd.notna(df[columnNameTypeDoc]) & pd.notna(df[columnNameAge])]
    errors = fill_rows[((fill_rows[columnNameAge] < 7) & 
                              (~fill_rows[columnNameTypeDoc].isin([60, 66, 64, 2482, 1638, 1640, 1639]))) |
                         ((fill_rows[columnNameAge] > 7) & (fill_rows[columnNameAge] < 18) &
                              (~fill_rows[columnNameTypeDoc].isin([61, 66, 64, 2482, 1640, 1639, 2482]))) |
                         (fill_rows[columnNameAge] >= 18) &
                              (~fill_rows[columnNameTypeDoc].isin([59, 62, 64, 65, 1637, 1638, 1640, 1639, 2482]))]
    #Cantidad de errores
    totalTypeDocErr = len(errors)
    for index in errors.index:
        setBgError(index, columnNameTypeDoc, bgSecError)
        setBgError(index, columnNameAge, bgSecError)
        
    print(f'Tipos de documento que no corresponden con la edad: {totalTypeDocErr}')
    return totalTypeDocErr

def nac_vs_typedoc(columnNameTypeDoc, columnNameNac):
    totalNacErr = 0
    #Verificar existencia de las columnas
    if columnNameNac not in df.columns or columnNameTypeDoc not in df.columns:
        raise ValueError(f'Las columnas {columnNameTypeDoc} y/o {columnNameNac} no se encuentran')
    
    #Filtrar las filas no vacías
    fill_rows = df[pd.notna(df[columnNameTypeDoc]) & pd.notna(df[columnNameNac])]
    errors = fill_rows[(fill_rows[columnNameTypeDoc].isin([59, 60, 61])) &
                            (fill_rows[columnNameNac] != 'Colombia') | 
                       (~fill_rows[columnNameTypeDoc].isin([59, 60, 61])) &
                            (fill_rows[columnNameNac] == 'Colombia')]
    
    totalNacErr = len(errors)
    for index in errors.index:
        setBgError(index, columnNameNac, bgSecError)
        setBgError(index, columnNameTypeDoc, bgSecError)
        
    print(f'Nacionalidad que no corresponde con el tipo de documento: {totalNacErr}')
    return totalNacErr

#-----------------------------------SESIONES PÁGINA 1---------------------------------
def sc_pg1():
    requiredFieldsPg1 = ['.Nombre de la institución / Establecimiento / Equipo étnico.',
                   '.Zona.', '.Localidad.', '.UPZ/UPR.', '.Barrio.', '.Teléfono.',
                   '.Barrio priorizado.', '.Tipo de Institución.']
    catnErroresPg_1 = (required_fields(requiredFieldsPg1) + validarNoManzana() + validarTelefono())
    return catnErroresPg_1
#-----------------------------------SESIONES PÁGINA 2---------------------------------
def sc_pg2():
    requiredFieldsPg2 = ['.Componente.', '.Línea operativa.', '.Dimensión.', 
                         '.Temática.', '.Número sesión.', '.Fecha.', '.Nombre profesional 1.']
    cantErroresPg_2 = required_fields(requiredFieldsPg2)+sesion_date()
    return cantErroresPg_2

def sesion_date():
    totalErrDate = 0
    for index, fila in df.iterrows():
        columnNameDate = '.Fecha.'
        cellDateSesion = fila[columnNameDate]
        cellDateSesionInter = fila['Fecha_intervencion']
        
        if columnNameDate in df.columns: 
            if pd.notna(cellDateSesion):
                if pd.to_datetime(cellDateSesion) < pd.to_datetime(cellDateSesionInter):
                    setBgError(index, columnNameDate, bgError)
                    totalErrDate += 1
        else:
            print(f'No se encontró la columna {columnNameDate}')
    print(f'Fechas de sesión incorrectas: {totalErrDate}')
    return totalErrDate

#-----------------------------------SESIONES PÁGINA 3---------------------------------
def sc_pg3():
    requiredFieldsPg3 = ['..OMS..', '..FINDRISC..', '..EPOC..', '.Sesiones.', 'IdTipoDocumento',
                         'Documento', 'PrimerNombre','PrimerApellido', 'IdNacionalidad', 'IdSexo',
                         'IdGenero', 'IdEstadoCivil', 'FechaNacimiento', 'IdEtnia', 'PoblacionDiferencialInclusion']
    cantErroresPg_3 = required_fields(requiredFieldsPg3)+len_num_doc('IdTipoDocumento', 'Documento')
    +age_vs_typedoc('IdTipoDocumento', 'Edad')+nac_vs_typedoc('IdTipoDocumento', 'IdNacionalidad')
    return cantErroresPg_3

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