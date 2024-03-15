from openpyxl import load_workbook
from openpyxl.styles import PatternFill

# Cargar el archivo Excel
wb = load_workbook('SC.xlsx')

hoja = wb.get_sheet_by_name("Institucion")
bgError = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')
    
def validarTelefono ():
    for fila in hoja.iter_rows(min_row=3, max_row=hoja.max_row, min_col=33, max_col=33, values_only=False):
        # Agrega el valor de la celda en la columna A a la lista
        cellTelefono = fila[0]

        # Agrega el valor convertido a la lista de valores enteros
        if len(str(cellTelefono.value)) != 7 and len(str(cellTelefono.value)) != 10:
            cellTelefono.fill = bgError
            cellFicha = hoja.cell(cellTelefono.row, 2)
            cellFicha.fill = bgError
    
    return True

def validarNoManzana ():
    for fila in hoja.iter_rows(min_row=3, max_row=hoja.max_row, min_col=36, max_col=36, values_only=False):
        cellManzana = fila[0]
        nroManzana = hoja.cell(cellManzana.row, 37)        

        if cellManzana.value == "SI" and nroManzana.value is None:            
            nroManzana.fill = bgError
            cellFicha = hoja.cell(cellManzana.row, 2)
            cellFicha.fill = bgError

    return True

validarNoManzana()
validarTelefono()

# Guardar archivo
wb.save('SC.xlsx')