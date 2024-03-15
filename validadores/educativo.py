import tkinter as tk
from tkinter import filedialog, messagebox
import openpyxl
import re
import shutil
from openpyxl.styles import PatternFill
from openpyxl import load_workbook

def validar_pagina1_sesiones():
    regex = re.compile("^[a-zA-ZÑñáéíóúÁÉÍÓÚ\s]+$")
    patternTel = re.compile(r'^\d{7}(\d{3})?$')
    try:
        # Abrir el archivo Excel
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        
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
        
        file_path_modificado = file_path.replace('.xlsx', '_errores.xlsx')
        workbook.save(file_path_modificado)
        
        # Mostrar la cantidad de celdas pintadas de rojo
        messagebox.showinfo("Celdas Pintadas de Rojo", f"Se han pintado {celdas_pintadas_rojo} celdas de rojo.")

    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error: {str(e)}")

def descargar_archivo():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        if not file_path.endswith('.xlsx'):
            file_path += '.xlsx'
        file_path_modificado = file_path.replace('.xlsx', '_errores.xlsx')
        
        # Verificar si hay celdas pintadas en rojo
        workbook = openpyxl.load_workbook(file_path_modificado)
        sheet = workbook.active
        hay_celdas_rojas = False
        for row in sheet.iter_rows():
            for cell in row:
                if cell.fill.start_color.index == 'FFFF0000':  # Rojo
                    hay_celdas_rojas = True
                    break
            if hay_celdas_rojas:
                break
        
        if hay_celdas_rojas:
            shutil.move(file_path_modificado, file_path)
        else:
            # Crear un nuevo archivo solo con los títulos
            workbook_nuevo = openpyxl.Workbook()
            sheet_nuevo = workbook_nuevo.active
            for row in sheet.iter_rows(min_row=1, max_row=1):
                for cell in row:
                    sheet_nuevo[cell.coordinate].value = cell.value
            workbook_nuevo.save(file_path)
        
        messagebox.showinfo("Archivo guardado", "El archivo ha sido guardado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo: {str(e)}")

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Validador de sesiones - Datos institución")

# Botón para iniciar la validación
btn_validar = tk.Button(root, text="Ejecutar", command=validar_pagina1_sesiones)
btn_validar.pack(pady=10)

# Botón para descargar el archivo generado
btn_descargar = tk.Button(root, text="Descargar archivo generado", command=descargar_archivo)
btn_descargar.pack(pady=10)

root.mainloop()