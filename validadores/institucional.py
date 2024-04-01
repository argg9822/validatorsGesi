from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import PatternFill, Font
from openpyxl import load_workbook, Workbook
import pandas as pd
from tkinter import filedialog, messagebox
import os
import re
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
            df = pd.read_csv(os.path.join(folder_path, file_name), header=1, encoding='latin-1', delimiter=";")
    
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
        "hcb": hcb,
        "mascota_verde": mv
        
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
        df = pd.DataFrame(data, columns=cols)
        global df_modified
        df_modified = list_pages()
        print(f"-------------------Página {index+1}-------------------")
        if index == 0:
            totalErroresPg_1 = sc_pg1()
        
        if index == 1:
            totalErroresPg_2 = sc_pg2()
            
        if index == 2:
            totalErroresPg_3 = sc_pg3()
            print("----------------------------------------------")
            
    cantErrSc = totalErroresPg_1+totalErroresPg_2+totalErroresPg_3
    print(f">>TOTAL ERRORES EN SESIONES COLECTIVAS: {(cantErrSc)}") 
    
def hcb():
    for index, sheet_name in enumerate(workbook.sheetnames):
        global sheet
        sheet = workbook[sheet_name]
        data = sheet.values
        cols = next(data) # Obtener los encabezados de las columnas (ignorar la primera columna)
        global df
        df = pd.DataFrame(data, columns=cols)
        global df_modified
        df_modified = list_pages()
        print(f"-------------------Página {index+1}-------------------")
        if index == 0:
            totalErroresPg_1 = hcb_pg1()
            
        if index == 1:
            totalErroresPg_2 = hcb_pg2()
            print("----------------------------------------------")
            
    cantErrHcb = totalErroresPg_1+totalErroresPg_2
    print(f">>TOTAL ERRORES EN HCB: {(cantErrHcb)}")
    
def mv():
    for index, sheet_name in enumerate(workbook.sheetnames):
        global sheet
        sheet = workbook[sheet_name]
        data = sheet.values
        cols = next(data) # Obtener los encabezados de las columnas (ignorar la primera columna)
        global df
        df = pd.DataFrame(data, columns=cols)
        global df_modified
        df_modified = list_pages()
        print(f"-------------------Página {index+1}-------------------")
        if index == 1:
            totalErroresPg_2 = mv_pg2()
            print("----------------------------------------------")
            
    cantErrMv = totalErroresPg_2
    print(f">>TOTAL ERRORES EN MASCOTA VERDE: {(cantErrMv)}")

##------------------------------------------------------------------------------------    
##------------------------------GENERAL FUNCTIONS-------------------------------------
##------------------------------------------------------------------------------------

bgError = 'FFFF0000'
bgSecError = '005FFF'
def setBgError(index, columnName, color):    
    bgError = PatternFill(start_color=color, end_color=color, fill_type='solid')
    cell = sheet.cell(row=index+2, column=df_modified.columns.get_loc(columnName)+1)
    cell.fill = bgError
    
    bgErrorFicha = PatternFill(start_color='FFFF0000', end_color='FFFF0000', fill_type='solid')
    cellFicha = sheet.cell(row=index+2, column=df_modified.columns.get_loc('Ficha_fic')+1)
    cellFicha.fill = bgErrorFicha
    
    bgUsr = PatternFill(start_color='00ba4a', end_color='00ba4a', fill_type='solid')
    cellUsr = sheet.cell(row=index+2, column=df_modified.columns.get_loc('Red_fic')+1)
    cellUsr.fill = bgUsr
    cellUsr.font = Font(bold=True)
    
def validarTelefono(columnName):
    cantErroresTel = 0
    if columnName in df_modified.columns:
        for index, fila in df_modified.iterrows():   
            cellTelefono = int(fila[columnName]) if pd.notna(fila[columnName]) else fila[columnName]
            if len(str(cellTelefono).strip()) not in [7, 10] and pd.notna(cellTelefono):
                cantErroresTel += 1                
                setBgError(index, columnName, bgError)
    else:
        print("No se encuentra la columna Teléfono")
        
    if cantErroresTel > 0:
        print(f"Teléfonos con longitud incorrecta: {cantErroresTel}")
    return cantErroresTel

def validarNoManzana(columnNameManzana, columnNameNroManzana):
    totalErrApple = 0
    
    if columnNameManzana in df_modified.columns:
        for index, fila in df_modified.iterrows():
            cellManzana = fila[columnNameManzana]
            nroManzana = fila[columnNameNroManzana]
            if cellManzana == "SI" and pd.isna(nroManzana):                
                totalErrApple += 1
                setBgError(index, columnNameNroManzana,bgError)
    else:
        print("No se encuentra la columna manzana del cuidado")
        
    if totalErrApple > 0:
        print(f"Errores en manzana del cuidado: {totalErrApple}")
    return totalErrApple

def required_fields(arrayFields=[], type=1, cantNextColumn=1):
    totalEmptyFields = 0
    if type == 1:
        for field in arrayFields:
            if field in df_modified.columns:
                for j, fila in df_modified.iterrows():
                    cellField = fila[field]
                    if pd.isna(cellField):
                        totalEmptyFields += 1
                        setBgError(j, field, bgError)
            else:
                print(f'No se encontró la columna {field}')
    elif type == 2:
        for field in arrayFields:
            if field in df_modified.columns:
                column_index = df_modified.columns.get_loc(field) + cantNextColumn  # Obtener el índice de la columna actual y sumar 1
                if column_index < len(df_modified.columns):  # Verificar si el índice está dentro de los límites
                    next_field = df_modified.columns[column_index]  # Obtener el nombre de la siguiente columna
                    for j, fila in df_modified.iterrows():
                        cellField = fila[next_field]  # Acceder a la siguiente columna
                        if pd.isna(cellField):
                            totalEmptyFields += 1
                            setBgError(j, next_field, bgError) 
                else:
                    print(f'No hay siguiente columna después de {field}')
            else:
                print(f'No se encontró la columna {field}')
            
    if totalEmptyFields > 0:
        print(f"Campos obligatorios vacíos: {totalEmptyFields}")
    return totalEmptyFields

def difference_dates(date_interv, date2):   
    result = pd.to_datetime(date_interv) - pd.to_datetime(date2)
    return result

def calculate_age(birth_date, intervention_date):
    return (pd.to_datetime(intervention_date) - pd.to_datetime(birth_date)).days // 365.25

def type_institution(columnNameType, columnNameOther):
    totalErrTypeInst = 0
    if columnNameType not in df_modified.columns or columnNameOther not in df_modified.columns:
        raise ValueError(f"La columna {columnNameType} y/o {columnNameOther} no se encuentran")
    
    fill_rows = df_modified[pd.notna(df_modified[columnNameType]) & pd.notna(df_modified[columnNameOther])]
    
    errors = fill_rows[(fill_rows[columnNameType] == '12 Otra Institución') & 
                       (fill_rows[columnNameOther].str.len() < 9) |
                       (fill_rows[columnNameOther].str.len() >= 9) & 
                        (fill_rows[columnNameType] != '12 Otra Institución')]
    
    totalErrTypeInst = len(errors)
        
    for index in errors.index:
        setBgError(index, columnNameOther, bgSecError)
        setBgError(index, columnNameType, bgSecError)
        
    if totalErrTypeInst > 0:
        print(f'Errores en tipo de institución {totalErrTypeInst}')
        
    return totalErrTypeInst

def list_pages():
    for num in df['Ficha_fic'].unique():
        indices = df.index[df['Ficha_fic'] == num].tolist()
        
        for i, idx in enumerate(indices):
            cell = sheet.cell(row=idx+2, column=df.columns.get_loc('Red_fic')+1)
            cell.value = i + 1
    return df
##------------------------------------------------------------------------------------    
##-----------------------------POBLATIONAL FUNCTIONS----------------------------------
##------------------------------------------------------------------------------------

def len_num_doc(columNameTypeDoc, columnNameNumDoc):
    totalErrLenDoc = 0
    # Verificar la existencia de las columnas requeridas
    if columNameTypeDoc not in df_modified.columns or columnNameNumDoc not in df_modified.columns:
        raise ValueError(f'Las columnas {columNameTypeDoc} y/o {columnNameNumDoc} no se encuentran.')
    
    #Filtrar filas que no están vacías
    fill_rows = df_modified[pd.notna(df_modified[columNameTypeDoc]) & pd.notna(df_modified[columnNameNumDoc])]
    errors = fill_rows[(fill_rows[columNameTypeDoc].isin([61,60])) & 
                            (fill_rows[columnNameNumDoc].astype(str).str.len() != 10)]
    
    totalErrLenDoc = len(errors)
    for index in errors.index:
        setBgError(index, columnNameNumDoc, bgError)
        
    if totalErrLenDoc > 0:
        print(f'Números de documento con longitud incorrecta: {totalErrLenDoc}')
    return totalErrLenDoc

def age_vs_typedoc(columnNameTypeDoc, columnNameAge):
    totalTypeDocErr = 0
    # Verificar la existencia de las columnas requeridas
    if columnNameTypeDoc not in df_modified.columns or columnNameAge not in df_modified.columns:
        raise ValueError(f'Las columnas {columnNameTypeDoc} y/o {columnNameAge} no se encuentran')
    
    #Filtrar filas que no están vacías
    fill_rows = df_modified[pd.notna(df_modified[columnNameTypeDoc]) & pd.notna(df_modified[columnNameAge])]
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
        
    if totalTypeDocErr > 0:
        print(f'Tipos de documento que no corresponden con la edad: {totalTypeDocErr}')
    return totalTypeDocErr

def nac_vs_typedoc(columnNameTypeDoc, columnNameNac):    
    #Verificar existencia de las columnas
    if columnNameNac not in df_modified.columns or columnNameTypeDoc not in df_modified.columns:
        raise ValueError(f'Las columnas {columnNameTypeDoc} y/o {columnNameNac} no se encuentran')
    
    #Filtrar las filas no vacías
    fill_rows = df_modified[pd.notna(df_modified[columnNameTypeDoc]) & pd.notna(df_modified[columnNameNac])]
    errors = fill_rows[(fill_rows[columnNameTypeDoc].isin([59, 60, 61])) &
                            (fill_rows[columnNameNac] != 'Colombia') | 
                       (~fill_rows[columnNameTypeDoc].isin([59, 60, 61, 66, 63])) &
                            (fill_rows[columnNameNac] == 'Colombia')]
    
    totalNacErr = len(errors)
    for index in errors.index:
        setBgError(index, columnNameNac, bgSecError)
        setBgError(index, columnNameTypeDoc, bgSecError)
        
    if totalNacErr>0:
        print(f'Nacionalidad que no corresponde con el tipo de documento: {totalNacErr}')
    return totalNacErr

def gen_vs_sex(columnNameSex, columnNameGen):
    if columnNameGen not in df_modified.columns or columnNameSex not in df_modified.columns:
        raise ValueError(f"Las columnas {columnNameGen} y/o {columnNameSex} no se encuentran")
    
    fill_rows = df_modified[pd.notna(df_modified[columnNameGen]) & pd.notna(df_modified[columnNameSex])]
    errors = fill_rows[(fill_rows[columnNameSex] == '1- Hombre') & (fill_rows[columnNameGen] == '2- Femenino') |
                       (fill_rows[columnNameSex] == '2- Mujer') & (fill_rows[columnNameGen] == '1- Masculino')]
    
    totalGenErr = len(errors)
    for index in errors.index:
        setBgError(index, columnNameGen, bgSecError)
        setBgError(index, columnNameSex, bgSecError)
    
    if totalGenErr > 0:
        print(f'Errores en sexo y/o género: {totalGenErr}')
    return totalGenErr

def age_vs_maritalStatus(columnNameInterventionDate, columnNameBirthDay, columnNameMarital):
    if columnNameBirthDay not in df_modified.columns or columnNameMarital not in df_modified.columns or columnNameInterventionDate not in df_modified.columns:
        raise ValueError(f"Las columnas {columnNameBirthDay}, {columnNameInterventionDate} y/o {columnNameMarital} no se encuentran")

    fill_rows = df_modified[pd.notna(df_modified[columnNameBirthDay]) & pd.notna(df_modified[columnNameMarital])]
    fill_rows['Edad'] = fill_rows.apply(lambda row: calculate_age(row[columnNameBirthDay], row[columnNameInterventionDate]), axis=1)
    errors = fill_rows[(fill_rows['Edad'] < 14.0) & (fill_rows[columnNameMarital] != '6- No aplica') |
                       (fill_rows['Edad'] >= 14.0) & (fill_rows[columnNameMarital] == '6- No aplica')]
    
    totalErrMarital = len(errors)
    for index in errors.index:
        setBgError(index, columnNameMarital, bgError)
    
    if totalErrMarital > 0:
        print(f'Estado civil no concuerda con la edad: {totalErrMarital}')
    return totalErrMarital

def nac_vs_pdi(columnNameNac, columnNamePdi):
    if columnNameNac not in df_modified.columns or columnNamePdi not in df_modified.columns:
        raise ValueError(f'Las columnas {columnNameNac} y/o {columnNamePdi} no se encuentran')
    
    fill_rows = df_modified[pd.notna(df_modified[columnNameNac]) & pd.notna(df_modified[columnNamePdi])]
    
    pattern = re.compile(r'\bMigrante\b', flags=re.IGNORECASE)# Expresión regular
    errors = fill_rows[(fill_rows[columnNameNac] == 'Colombia') & (fill_rows[columnNamePdi].apply(lambda x: bool(pattern.search(str(x))))) |
                       (fill_rows[columnNameNac] != 'Colombia') & (~fill_rows[columnNamePdi].apply(lambda x: bool(pattern.search(str(x)))))]

    totalErrNacPdi = len(errors)
    
    for index in errors.index:
        setBgError(index, columnNamePdi, bgError)
    
    if totalErrNacPdi > 0:
        print(f'Errores en población diferencial: {totalErrNacPdi}')
    return totalErrNacPdi

def et_vs_lang(columnNameEt, columNameLang):
    if columnNameEt not in df_modified.columns or columNameLang not in df_modified.columns:
        raise ValueError(f'Las columnas {columnNameEt} y/o {columNameLang} no se encuentran')
    
    fill_rows = df_modified[pd.notna(df_modified[columnNameEt]) & pd.notna(df_modified[columNameLang])]
    errors = fill_rows[(fill_rows[columnNameEt] != '6- Ninguno') & (fill_rows[columNameLang] == -1)]
    totalErrEt = len(errors)
    
    for index in errors.index:
        setBgError(index, columNameLang, bgError)
    
    if totalErrEt > 0:
        print(f'Errores en habla español: {totalErrEt}')
    return totalErrEt

def validate_only_text(*columnsName):
    totalErrText = 0
    pattern =re.compile(r'^[^0-9.,:]+$')
    for columnName in columnsName:
        if columnName not in df_modified.columns:
            raise ValueError(f'La columna {columnName} no se encuentra')
        
        fill_rows = df_modified[pd.notna(df_modified[columnName])]
        errors = fill_rows[~fill_rows[columnName].apply(lambda x: bool(pattern.search(str(x))))]
        
        totalErrText += len(errors)
        for index in errors.index:
            setBgError(index, columnName, bgError)
        
    if totalErrText > 0:
        print(f'Texto mal escrito: {totalErrText}')
    return totalErrText

def validate_only_text_inst_barr(*columnsName):
    totalErrText = 0
    pattern =re.compile(r'^[^,:;|/()=$%&*-_]+$')
    
    for columnName in columnsName:
        if columnName not in df_modified.columns:
            raise ValueError(f'La columna {columnName} no se encuentra')
        
        fill_rows = df_modified[pd.notna(df_modified[columnName])]
        errors = fill_rows[fill_rows[columnName].apply(lambda x: bool(pattern.search(str(x))))]
        
        totalErrText += len(errors)
        for index in errors.index:
            setBgError(index, columnName, bgError)
        
    if totalErrText > 0:
        print(f'Texto mal escrito: {totalErrText}')
    return totalErrText

def validate_only_number(*columnsName):
    totalErrNumber = 0
    pattern =re.compile(r'^[^0-9]+$')
    for columnName in columnsName:
        if columnName not in df_modified.columns:
            raise ValueError(f'La columna {columnName} no se encuentra')
        
        fill_rows = df_modified[pd.notna(df_modified[columnName])]
        errors = fill_rows[fill_rows[columnName].apply(lambda x: bool(pattern.search(str(x))))]
        
        totalErrNumber += len(errors)
        for index in errors.index:
            setBgError(index, columnName, bgError)
        
    if totalErrNumber > 0:
        print(f'Números con símbolos y/o caracteres: {totalErrNumber}')
    return totalErrNumber

def validate_address(addressComponents):
    totalErrAddress = 0
    for component in addressComponents:
        if addressComponents[component] not in df_modified.columns:
            raise ValueError(f'La columna {addressComponents[component]} no se encuentra')
    
    fill_rows = df_modified[pd.notna(df_modified[addressComponents['columnNameZone']])]
    errors_urban = fill_rows[(fill_rows[addressComponents['columnNameZone']].str.startswith('1')) &
                            ((pd.isna(fill_rows[addressComponents['columnNameAx1']])) |
                            (pd.isna(fill_rows[addressComponents['columnNameNumber']])) |
                            (pd.isna(fill_rows[addressComponents['columnNameAx2']])) |
                            (pd.isna(fill_rows[addressComponents['columnNamePlate']])) |
                            (pd.notna(fill_rows[addressComponents['columnNameTrail']])) |
                            (pd.notna(fill_rows[addressComponents['columnNameX']])) |
                            (pd.notna(fill_rows[addressComponents['columnNameY']])))]
    
    errors_rural = fill_rows[(fill_rows[addressComponents['columnNameZone']].str.startswith('2')) &
                            ((pd.notna(fill_rows[addressComponents['columnNameAx1']])) |
                            (pd.notna(fill_rows[addressComponents['columnNameNumber']])) |
                            (pd.notna(fill_rows[addressComponents['columnNameAx2']])) |
                            (pd.notna(fill_rows[addressComponents['columnNamePlate']])) |
                            (pd.isna(fill_rows[addressComponents['columnNameTrail']])) |
                            (pd.isna(fill_rows[addressComponents['columnNameX']])) |
                            (pd.isna(fill_rows[addressComponents['columnNameY']])))]
    
    totalErrAddress = (len(errors_urban) + len(errors_rural))
    final_errors_urb = errors_urban[errors_urban.isna().any(axis=1)]
    
    for index in final_errors_urb.index:
        if final_errors_urb.loc[index].isna().any():
            setBgError(index, addressComponents['columnNameZone'], bgError)
    
    if totalErrAddress > 0:
        print(f'Errores en dirección: {totalErrAddress}')
    return totalErrAddress
    
#-----------------------------------SESIONES PÁGINA 1---------------------------------
def sc_pg1():
    requiredFieldsPg1 = ['.Nombre de la institución / Establecimiento / Equipo étnico.',
                   '.Zona.', '.Localidad.', '.UPZ/UPR.', '.Barrio.', '.Teléfono.',
                   '.Barrio priorizado.', '.Tipo de Institución.', '.Manzana de cuidado.']
    
    addressComponents = {
        'columnNameZone': '.Zona.',
        'columnNameAx1': '.Eje Principal.',
        'columnNameNumber':'.Número.',
        'columnNameAx2':'.Eje generador.',
        'columnNamePlate':'.Placa.',
        'columnNameTrail':'.Vereda.',
        'columnNameX':'.Coordenadas X.',
        'columnNameY':'.Coordenadas Y.'
    }
     
    catnErroresPg_1 = (required_fields(requiredFieldsPg1) + validarNoManzana(requiredFieldsPg1[8], '.Nro Manzana.') + validarTelefono(requiredFieldsPg1[5])
                       +validate_only_text_inst_barr(requiredFieldsPg1[0], requiredFieldsPg1[4])
                       +validate_address(addressComponents))+type_institution(requiredFieldsPg1[7], '.Otra. ¿Cual? (Tipo de Institución).')
    if catnErroresPg_1 == 0:
        print('Sin errores en la primera página')
    return catnErroresPg_1
#-----------------------------------SESIONES PÁGINA 2---------------------------------
def sc_pg2():
    requiredFieldsPg2 = ['.Componente.', '.Línea operativa.', '.Dimensión.', 
                         '.Temática.', '.Número sesión.', '.Fecha.', '.Nombre profesional 1.']
    cantErroresPg_2 = (required_fields(requiredFieldsPg2)+sesion_date()+validate_only_number('.Número sesión.'))
    if cantErroresPg_2 == 0:
        print('Sin errores en la segunda página')
    return cantErroresPg_2

def sesion_date():
    totalErrDate = 0
    for index, fila in df_modified.iterrows():
        columnNameDate = '.Fecha.'
        cellDateSesion = fila[columnNameDate]
        cellDateSesionInter = fila['Fecha_intervencion']
        if columnNameDate in df_modified.columns: 
            if pd.notna(cellDateSesion):
                if pd.to_datetime(cellDateSesion) < pd.to_datetime(cellDateSesionInter):
                    setBgError(index, columnNameDate, bgError)
                    totalErrDate += 1
        else:
            print(f'No se encontró la columna {columnNameDate}')
    if totalErrDate > 0:
        print(f'Fechas de sesión incorrectas: {totalErrDate}')
    return totalErrDate

#-----------------------------------SESIONES PÁGINA 3---------------------------------
def sc_pg3():
    reqFieldsPg3 = ['..OMS..', '..FINDRISC..', '..EPOC..', '.Sesiones.', 'IdTipoDocumento',
                         'Documento', 'PrimerNombre','PrimerApellido', 'IdNacionalidad', 'IdSexo',
                         'IdGenero', 'IdEstadoCivil', 'FechaNacimiento', 'IdEtnia', 'PoblacionDiferencialInclusion']
    
    cantErroresPg_3 = (required_fields(reqFieldsPg3)+len_num_doc(reqFieldsPg3[4], reqFieldsPg3[5])
                       +age_vs_typedoc(reqFieldsPg3[4], 'Edad')+nac_vs_typedoc(reqFieldsPg3[4], reqFieldsPg3[8])
                       +gen_vs_sex(reqFieldsPg3[9], reqFieldsPg3[10])+age_vs_maritalStatus('Fecha_intervencion',reqFieldsPg3[12],reqFieldsPg3[11])
                       +nac_vs_pdi(reqFieldsPg3[8], reqFieldsPg3[14])+et_vs_lang(reqFieldsPg3[13], 'HablaEspaniol')
                       +validate_only_text(reqFieldsPg3[6], reqFieldsPg3[7], 'SegundoNombre', 'SegundoApellido'))
    if cantErroresPg_3 == 0:
        print('Sin errores en la tercera página')
    return cantErroresPg_3

#-------------------------------------HCB PÁGINA 2-----------------------------------
def hcb_pg1():
    reqFieldsPg1 = ['.Zona.', '.Localidad.', '.UPZ/UPR.', '.Barrio.', '.Manzana de cuidado.', '.Barrio priorizado.', 
                    '.Estrato.', '.Nombre de la Asociación de madres comunitarias:.', '.Nombre del HCB.',
                    '.Teléfono 1.', '.¿Ha participado previamente en la estrategia AIEPI Comunitario?.',
                    '.¿Ha implementado la estrategia Mi Mascota Verde?.', '.¿Cuenta con huerta casera?.',
                    '.¿Cuenta con espacios de reunión periódica con los padres de familia?.', '.Lugar de Funcionamiento.',
                    '.¿De que servicios dispone?.']
    
    reqFieldsPg1Sec2 = ['.HCB en un lugar seguro (sin: remoción en masa, inundaciones - ronda hídrica, avalanchas).',
                        '.Paredes y techos sin grietas, huecos, humedades.','.Adecuado manejo de combustibles (sólidos, líquidos, gaseosos).',
                        '.Las áreas habitacionales de la vivienda están separadas entre sí (baño, cocinas y habitaciones).',
                        '.Preparación de alimentos con leña.','.La vivienda tiene iluminación y ventilación adecuada.',
                        '.Se fuma en la vivienda.','.Las condiciones físicas y locativas del baño son adecuadas.']
    cantErrorsPg_1 = (required_fields(reqFieldsPg1)+required_fields(reqFieldsPg1Sec2, 2, 1)+validarTelefono(reqFieldsPg1[9]))
    if cantErrorsPg_1 == 0:
        print("Sin errores en la primera página")
    return cantErrorsPg_1
    
def hcb_pg2():
    reqFieldsPg2 = ['IdTipoDocumento','Documento', 'PrimerNombre','PrimerApellido', 'IdNacionalidad', 'IdSexo',
                    'IdGenero', 'IdEstadoCivil', 'FechaNacimiento', 'IdEtnia', 'PoblacionDiferencialInclusion',
                    'IdAfiliacionSGSSS', 'NombreEAPB', 'IdNivelEducativo', 'Ocupacion']
    cantErroresPg_2 = (required_fields(reqFieldsPg2)+len_num_doc(reqFieldsPg2[0],reqFieldsPg2[1])
                       +age_vs_typedoc(reqFieldsPg2[0], 'Edad')+nac_vs_typedoc(reqFieldsPg2[0], reqFieldsPg2[4])
                       +gen_vs_sex(reqFieldsPg2[5],reqFieldsPg2[6])+age_vs_maritalStatus('Fecha_intervencion',reqFieldsPg2[8],reqFieldsPg2[7])
                       +nac_vs_pdi(reqFieldsPg2[4], reqFieldsPg2[10])+et_vs_lang(reqFieldsPg2[9], 'HablaEspaniol'))
    if cantErroresPg_2 == 0:
        print("Sin errores en la segunda página")
    return cantErroresPg_2

#------------------------------MASCOTA VERDE PÁGINA 2---------------------------------
def mv_pg2():
    reqFieldsPg2 = ['IdTipoDocumento','Documento', 'PrimerNombre','PrimerApellido', 'IdNacionalidad', 'IdSexo',
                    'IdGenero', 'IdEstadoCivil', 'FechaNacimiento', 'IdEtnia', 'PoblacionDiferencialInclusion']
    cantErroresPg_2 = (required_fields(reqFieldsPg2)+len_num_doc(reqFieldsPg2[0],reqFieldsPg2[1])
                       +age_vs_typedoc(reqFieldsPg2[0], 'Edad')+nac_vs_typedoc(reqFieldsPg2[0], reqFieldsPg2[4])
                       +gen_vs_sex(reqFieldsPg2[5],reqFieldsPg2[6])+age_vs_maritalStatus('Fecha_intervencion', reqFieldsPg2[8],reqFieldsPg2[7])
                       +nac_vs_pdi(reqFieldsPg2[4], reqFieldsPg2[10])+et_vs_lang(reqFieldsPg2[9], 'HablaEspaniol'))
    if cantErroresPg_2 == 0:
        print("Sin errores en la segunda página")
    return cantErroresPg_2

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