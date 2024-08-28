def validarVacias(sheet, CeldasVacias):
    celdas_pintadas_rojo = 0
    ultima_fila = sheet.max_row
    Num_celTexto = len(CeldasVacias["vacias"])
    columns = list(CeldasVacias["vacias"])
    for a in range(Num_celTexto):
        for i in range(2, ultima_fila + 1):
            if sheet.cell(row=i, column=columns[a]).value == " " :  
                    celdas_pintadas_rojo += 1
                    colum["column"] = {columns[a], 2}
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