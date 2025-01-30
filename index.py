import traceback
import customtkinter as ctk
from tkinter import Menu, simpledialog, messagebox, filedialog
import pandas as pd
import json
import os
import pandas as pd
from tkinter import filedialog, messagebox
import openpyxl
from openpyxl.styles import PatternFill
from datetime import datetime
import time
from tkinter import PhotoImage

import tkinter as tk
import customtkinter
import subprocess
from validadores import  educativo
from crear_hc import crear
import sys
from colorama import init, Fore, Style
from PIL import Image, ImageTk
from __version__ import __version__ as version_actual_actual  # Importa la versión actual desde __version__.py
import os
import tkinter as tk
import customtkinter
from tkinter import simpledialog
import json
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import PhotoImage
import win32com.client as win32
import time

log_file = "error_log.txt"

def log_error(error_message):
    # Escribe el error en el archivo de log
    with open(log_file, "a") as log:
        log.write(error_message + "\n")

try:

    # Ruta del archivo JSON donde se guardarán las áreas
    archivo_json = "areas.json"

    # Función para cargar las áreas desde el archivo JSON
    def cargar_areas():
        if os.path.exists(archivo_json):
            with open(archivo_json, "r") as archivo:
                return json.load(archivo)
        return {}

    # Función para guardar las áreas en el archivo JSON
    def guardar_areas():
        with open(archivo_json, "w") as archivo:
            json.dump(areas, archivo, indent=4)

    # Función para agregar un área
    def agregar_area():
        nueva_area =ctk.CTkInputDialog(title="Agregar Área", text="Ingrese el nombre del entorno:")
        
        nueva_area_result = nueva_area.get_input()
        print(nueva_area_result)
        if nueva_area_result:
            if nueva_area in areas:
                messagebox.showerror("Error", "El entorno ya existe.")
                return
            areas[nueva_area_result] = []  # Cada área comienza con una lista vacía de validadores
            guardar_areas()
            actualizar_botones_areas()

    # Función para actualizar los botones de áreas en el panel izquierdo
    def actualizar_botones_areas():
        # Limpiar el panel izquierdo
        for widget in frame_izquierdo.winfo_children():
            widget.destroy()

        # Botón para agregar una nueva área
        btn_agregar_area = ctk.CTkButton(
            frame_izquierdo,
            text="+",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=50,
            height=50,
            command=agregar_area
        )
        btn_agregar_area.pack(pady=10)

        # Botones para las áreas existentes
        for area_nombre in areas:
            btn_area = ctk.CTkButton(
                frame_izquierdo,
                text=area_nombre,
                command=lambda nombre=area_nombre: seleccionar_area(nombre)
            )
            btn_area.pack(pady=5, fill="x")

    # Función para mostrar opciones del área seleccionada
    def seleccionar_area(area):
        # Limpiar el contenido del panel derecho
        for widget in frame_derecho.winfo_children():
            widget.destroy()
        
        # Mostrar las opciones para el área seleccionada
        ctk.CTkLabel(
            frame_derecho,
            text=f"Validadores del Entorno: {area}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Mostrar los validadores existentes como botones
        for validador in areas[area]:
            ctk.CTkButton(
                frame_derecho,
                text=validador["nombre"],
                command=lambda v=validador: gestionar_validador(area, v)
            ).pack(pady=5, fill="x")
        
        # Botón para agregar un nuevo validador
        ctk.CTkButton(
            frame_derecho,
            text="Agregar Validador",
            command=lambda: agregar_validador(area)
        ).pack(pady=10)
        
        # Botón para eliminar el área actual
        ctk.CTkButton(
            frame_derecho,
            text="Eliminar Entorno",
            fg_color="red",
            command=lambda: eliminar_area(area)
        ).pack(pady=10)

    # Función para agregar un validador a un área
    def agregar_validador(area):
        nombre_validador = ctk.CTkInputDialog(title="Agregar Validador", text="Ingrese el nombre del validador:")
        
        nombre_validador_result = nombre_validador.get_input()
        if not nombre_validador_result:
            return
        
        nuevo_validador = {"nombre": nombre_validador_result, "reglas": []}  # Inicialmente sin reglas
        areas[area].append(nuevo_validador)
        guardar_areas()
        seleccionar_area(area)

    # Función para gestionar las reglas de un validador
    def gestionar_validador(area, validador):
        # Limpiar el panel derecho
        for widget in frame_derecho.winfo_children():
            widget.destroy()
        
        # Título del validador
        ctk.CTkLabel(
            frame_derecho,
            text=f"Reglas para el validador: {validador['nombre']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Mostrar las reglas existentes
        for i, regla in enumerate(validador["reglas"]):
            ctk.CTkButton(
                frame_derecho,
                text=f"Regla {i + 1}: {regla}",
                command=lambda r=regla: editar_regla(area, validador, r)
            ).pack(pady=5, fill="x")
        
        # Botón para agregar una nueva regla
        ctk.CTkButton(
            frame_derecho,
            text="Agregar Regla",
            command=lambda: agregar_regla(area, validador)
        ).pack(pady=10)
        
        # Botón para analizar un archivo Excel
        ctk.CTkButton(
            frame_derecho,
            text="Analizar Excel",
            command=lambda: analizar_excel(validador)
        ).pack(pady=10)
        
        # Botón para volver a la lista de validadores
        ctk.CTkButton(
            frame_derecho,
            text="Volver",
            command=lambda: seleccionar_area(area)
        ).pack(pady=10)

    # Función para agregar una regla a un validador
    def agregar_regla(area, validador):
        
    
        
        # Crear una ventana modal
        modal = ctk.CTkToplevel()
        modal.title("Seleccionar Tipo de Regla")
        modal.geometry("300x200")
        modal.grab_set()  # Bloquea la ventana principal hasta que se cierre esta

        tipo_regla_var = ctk.StringVar(value="longitud")  # Valor predeterminado

        ctk.CTkLabel(modal, text="Seleccione el tipo de regla:").pack(pady=10)
        tipo_regla_menu = ctk.CTkOptionMenu(
            modal, 
            values=["longitud", "numerico", "patron", "unico", "dependiente_positivo", "dependiente_error" ,"no_vacio", "dependiente longitud", "dependiente edad positivo", "dependiente edad error"], 
            variable=tipo_regla_var
        )
        tipo_regla_menu.pack(pady=10)

        def confirmar_tipo_regla():
            tipo_regla = tipo_regla_var.get()
            modal.destroy()  # Cerrar la ventana modal
            
            if tipo_regla == "longitud":
                
                columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar por longitud (por ejemplo, Cedula):")
                columna_result = columna.get_input()

                # Verificar si no se ingresó nada
                if not columna_result:
                    return
                
                condicion2 = ctk.CTkInputDialog(title="Longitud", text="Ingrese la longitud máxima (ejemplo: 10):")
                columna_result2 = condicion2.get_input()

                if not columna_result2:
                    return
                
                nueva_regla = {"columna": columna_result, "tipo": "longitud", "condicion": f"<= {columna_result2}"}
            
            elif tipo_regla == "numerico":
                
                columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar numerico (por ejemplo, Telefono):")
                columna_result = columna.get_input()
                if not columna_result:
                    return
                
                condicion2 = ctk.CTkInputDialog(title="Numerico", text="Ingrese la condición (ejemplo: 'mayor  5'):")
                condicion2_result = condicion2.get_input()
                if not condicion2_result:
                    return
                nueva_regla = {"columna": columna_result, "tipo": "numerico", "condicion": condicion2_result}
            
            elif tipo_regla == "patron":
                columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar para que no tenga caracteres especiales (por ejemplo, Nombres):")
                columna_result = columna.get_input()
                if not columna_result:
                    return
                
                patron = ctk.CTkInputDialog(title="Expresión Regular", text="Ingrese el patrón regex (ejemplo: \\d{3}-\\d{2}-\\d{4}):")
                patron_result = patron.get_input()
                if not patron_result:
                    return
                
                nueva_regla = {"columna": columna_result, "tipo": "patron", "patron": patron_result}
            
            elif tipo_regla == "unico":
                columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar para qvalores unicos (por ejemplo, Nombres):")
                columna_result = columna.get_input()
                if not columna_result:
                    return
                nueva_regla = {"columna": columna_result, "tipo": "unico"}
            
            elif tipo_regla == "dependiente_positivo":
                columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar  (por ejemplo, Telefono):")
                columna_result = columna.get_input()
                if not columna_result:
                    return
                
                columna_dependiente = ctk.CTkInputDialog(title="Columna Dependiente", text="¿De qué columna depende esta regla? (por ejemplo, A):")
                columna_dependiente_result = columna_dependiente.get_input()
                
                if not columna_dependiente_result:
                    return
                
                valor_dependiente = ctk.CTkInputDialog(title="Valor Dependiente", text="¿Qué valor debe tener la columna dependiente? (ejemplo: 50):")
                valor_dependiente_result = valor_dependiente.get_input()
                if not valor_dependiente_result:
                    return
                
                valor_dependiente = float(valor_dependiente_result) if valor_dependiente_result.replace('.', '', 1).isdigit() else valor_dependiente
                
                valor_esperado = ctk.CTkInputDialog(title="Valor Esperado", text="¿Qué valor debe tener la columna a validar si la columna dependiente tiene este valor? (ejemplo: 51):")
                valor_esperado_result = valor_esperado.get_input()
                if not valor_esperado_result:
                    return
                
                nueva_regla = {
                    "columna": columna_result, 
                    "tipo": "dependiente positivo", 
                    "columna_dependiente": columna_dependiente_result, 
                    "valor_dependiente": valor_dependiente, 
                    "valor_esperado": valor_esperado_result
                }
                
            elif tipo_regla == "dependiente_error":
                columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar numerico (por ejemplo, Telefono):")
                columna_result = columna.get_input()
                if not columna_result:
                    return
                
                columna_dependiente = ctk.CTkInputDialog(title="Columna Dependiente", text="¿De qué columna depende esta regla? (por ejemplo, A):")
                columna_dependiente_result = columna_dependiente.get_input()
                if not columna_dependiente_result:
                    return
                
                valor_dependiente = ctk.CTkInputDialog(title="Valor Dependiente", text="¿Qué valor debe tener la columna dependiente? (ejemplo: VEN):")
                valor_dependiente_result = valor_dependiente.get_input()
                if not valor_dependiente_result:
                    return
                
                valor_dependiente_result = float(valor_dependiente_result) if valor_dependiente_result.replace('.', '', 1).isdigit() else valor_dependiente_result
                
                valor_esperado = ctk.CTkInputDialog(title="Valor Esperado", text="¿Qué valor debe tener la columna a validar si la columna dependiente tiene este valor? (ejemplo: NO APLICA):")
                valor_esperado_result = valor_esperado.get_input()

                if not valor_esperado_result:
                    return
                
                nueva_regla = {
                    "columna": columna_result, 
                    "tipo": "dependiente_error", 
                    "columna_dependiente": columna_dependiente_result, 
                    "valor_dependiente": valor_dependiente_result, 
                    "valor_esperado": valor_esperado_result
                }
                
                
            elif tipo_regla == "no_vacio":
                columnas = ctk.CTkInputDialog(
                    title="No Vacío", 
                    text="Ingrese las columnas que no pueden estar vacías, separadas por comas (ejemplo: A, B, C):"
                )
                columnas_resultado = columnas.get_input()

                if not columnas_resultado:
                    return
                
                columna = "Ficha_fic"
                columnas_resultado = [col.strip() for col in columnas_resultado.split(",") if col.strip()]
                nueva_regla = {"columna": columna, "tipo": "no_vacio", "columnas": columnas_resultado}

            
            elif tipo_regla == "dependiente longitud":
                columna = ctk.CTkInputDialog(
                    title="Agregar Regla", 
                    text="Ingrese la columna a validar (por ejemplo, DOCUMENTO):"
                )
                columna_resultado = columna.get_input()
                if not columna_resultado:
                    return
                
                columna_dependiente = ctk.CTkInputDialog(
                    title="Columna Dependiente", 
                    text="¿De qué columna depende esta regla? (por ejemplo, TIPO DOCUMENTO):"
                )
                columna_dependiente_resultado = columna_dependiente.get_input()
                if not columna_dependiente_resultado:
                    return

                valor_dependiente = ctk.CTkInputDialog(
                    title="Valor Dependiente", 
                    text="¿Qué valor debe tener la columna dependiente? (ejemplo: 3- TI):"
                )
                valor_dependiente_resultado = valor_dependiente.get_input()
                if not valor_dependiente_resultado:
                    return

                valor_esperado = ctk.CTkInputDialog(
                    title="Valor Esperado", 
                    text="¿Qué cantidad de dígitos debe tener la columna a validar (por ejemplo: 10)?"
                )
                valor_esperado_resultado = valor_esperado.get_input()
                if not valor_esperado_resultado:
                    return

                nueva_regla = {
                    "columna": columna_resultado,
                    "tipo": "dependiente longitud",
                    "columna_dependiente": columna_dependiente_resultado,
                    "valor_dependiente": valor_dependiente_resultado,
                    "valor_esperado": f"<= {valor_esperado_resultado}"
                }

            elif tipo_regla == "dependiente edad positivo":
                columna = ctk.CTkInputDialog(
                    title="Agregar Regla", 
                    text="Ingrese la columna a validar (por ejemplo, ESTADO CIVIL):"
                )
                columna_resultado = columna.get_input()
                if not columna_resultado:
                    return
                
                columna_dependiente = ctk.CTkInputDialog(
                    title="Columna Dependiente", 
                    text="¿De qué columna depende esta regla? (por ejemplo, FECHA DE NACIMIENTO):"
                )
                columna_dependiente_resultado = columna_dependiente.get_input()
                if not columna_dependiente_resultado:
                    return

                valor_dependiente = ctk.CTkInputDialog(
                    title="Valor Dependiente", 
                    text="Indique la edad o rango de edades separados por coma (por ejemplo: 7,17):"
                )
                valor_dependiente_resultado = valor_dependiente.get_input()
                if not valor_dependiente_resultado:
                    return

                valor_esperado = ctk.CTkInputDialog(
                    title="Valor Esperado", 
                    text="Valor esperado según la edad:"
                )
                valor_esperado_resultado = valor_esperado.get_input()
                if not valor_esperado_resultado:
                    return

                Columna_para_fecha = ctk.CTkInputDialog(
                    title="Agregar Regla", 
                    text="Ingrese la columna sobre la cual se calculará la edad (por ejemplo, Fecha_intervencion):"
                )
                Columna_para_fecha_resultado = Columna_para_fecha.get_input()
                if not Columna_para_fecha_resultado:
                    return
                
                nacionalidad = ctk.CTkInputDialog(
                    title="Agregar Regla", 
                    text="Ingrese la nacionalidad (por ejemplo, Col):"
                )
                
                nacionalidad_resultado = nacionalidad.get_input()
                if not nacionalidad_resultado:
                    return
                    

                nueva_regla = {
                    "columna": columna_resultado,
                    "nacionalidad": nacionalidad_resultado,
                    "tipo": "dependiente edad positivo",
                    "Fecha_int": Columna_para_fecha_resultado,
                    "columna_dependiente": columna_dependiente_resultado,
                    "valor_dependiente": valor_dependiente_resultado,
                    "valor_esperado": valor_esperado_resultado
                }

                
            elif tipo_regla == "dependiente edad error":
                columna = ctk.CTkInputDialog(
                    title="Agregar Regla", 
                    text="Ingrese la columna a validar (por ejemplo, ESTADO CIVIL):"
                )
                columna_resultado = columna.get_input()
                if not columna_resultado:
                    return
                
                columna_dependiente = ctk.CTkInputDialog(
                    title="Columna Dependiente", 
                    text="¿De qué columna depende esta regla? (por ejemplo, FECHA DE NACIMIENTO):"
                )
                columna_dependiente_resultado = columna_dependiente.get_input()
                if not columna_dependiente_resultado:
                    return

                valor_dependiente = ctk.CTkInputDialog(
                    title="Valor Dependiente", 
                    text="Indique la edad o rango de edades separados por coma (por ejemplo: 7,17):"
                )
                valor_dependiente_resultado = valor_dependiente.get_input()
                if not valor_dependiente_resultado:
                    return

                valor_esperado = ctk.CTkInputDialog(
                    title="Valor Esperado", 
                    text="Ingrese el valor que es error:"
                )
                valor_esperado_resultado = valor_esperado.get_input()
                if not valor_esperado_resultado:
                    return

                Columna_para_fecha = ctk.CTkInputDialog(
                    title="Agregar Regla", 
                    text="Ingrese la columna sobre la cual se calculará la edad (por ejemplo, Fecha_intervencion):"
                )
                Columna_para_fecha_resultado = Columna_para_fecha.get_input()
                if not Columna_para_fecha_resultado:
                    return
                
                nacionalidad = ctk.CTkInputDialog(
                    title="Agregar Regla", 
                    text="Ingrese la nacionalidad (por ejemplo, colombia):"
                )
                
                nacionalidad_resultado = nacionalidad.get_input()
                if not nacionalidad_resultado:
                    return
                  

                nueva_regla = {
                    "columna": columna_resultado,
                    "tipo": "dependiente edad error",
                    "nacionalidad": nacionalidad_resultado,
                    "Fecha_int": Columna_para_fecha_resultado,
                    "columna_dependiente": columna_dependiente_resultado,
                    "valor_dependiente": valor_dependiente_resultado,
                    "valor_esperado": valor_esperado_resultado
                }
     
            else:
                messagebox.showerror("Error", "Tipo de regla no reconocido.")
                return

            validador["reglas"].append(nueva_regla)
            guardar_areas()
            gestionar_validador(area, validador)

        # Botón para confirmar la selección
        confirmar_btn = ctk.CTkButton(modal, text="Confirmar", command=confirmar_tipo_regla)
        confirmar_btn.pack(pady=20)

        modal.protocol("WM_DELETE_WINDOW", modal.destroy)  # Permite cerrar la ventana con la 'X'


    # Función para editar una regla
    def editar_regla(area, validador, regla):
        nueva_regla = ctk.CTkInputDialog(title="Editar Regla", text=f"Modificar regla: {regla}")
        nueva_regla_input = nueva_regla.get_input()
        if nueva_regla_input:
            indice = validador["reglas"].index(regla)
            validador["reglas"][indice] = nueva_regla
            guardar_areas()
            gestionar_validador(area, validador)


    def analizar_excel(validador):
        archivo_excel = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if archivo_excel:
            try:
                # Leer el archivo Excel
                df = pd.read_excel(archivo_excel)

                # Cargar el archivo Excel en openpyxl para aplicar formato
                wb = openpyxl.load_workbook(archivo_excel)
                ws = wb.active

                # Color de fondo rojo para las celdas que no cumplen con la condición
                rojo_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")

                for regla in validador["reglas"]:
                    columna = regla.get("columna")
                
                    
                    tipo = regla.get("tipo")

                    if columna in df.columns:
                        col_idx = df.columns.get_loc(columna) + 1  # Obtener el índice de la columna en openpyxl (1-based)
                        
                        if tipo == "longitud":
                            max_longitud = int(regla["condicion"].split("<= ")[1])
                            violaciones = df[columna][df[columna].astype(str).str.len() > max_longitud]
                            for idx in violaciones.index:
                                # Marcar en rojo las celdas que violan la regla de longitud
                                ws.cell(row=idx + 2, column=col_idx).fill = rojo_fill  # +2 por el encabezado
                                ws.cell(row=idx + 2, column=2).fill = rojo_fill  # Marcar en rojo
                                

                        elif tipo == "numerico":
                            try:
                                operador, valor = regla["condicion"].split(" ")
                                valor = int(valor)
                                print(operador)
                                print(valor)
                                
                                # Convertir la columna a numérico, forzando errores a NaN
                                df[columna] = pd.to_numeric(df[columna], errors='coerce')
                                
                                if operador == "mayor":
                                    violaciones = df[columna][df[columna] > valor]
                                elif operador == "menor":
                                    violaciones = df[columna][df[columna] < valor]

                                for idx in violaciones.index:
                                    ws.cell(row=idx + 2, column=col_idx).fill = rojo_fill  # Marcar en rojo
                                    ws.cell(row=idx + 2, column=2).fill = rojo_fill  # Marcar en rojo
                                    

                            except ValueError:
                                pass

                        elif tipo == "patron":
                            patron = regla["patron"]
                            # Normalizar los datos
                            df[columna] = df[columna].astype(str).str.strip()
                            
                            # Filtrar las filas que no cumplen con el patrón
                            violaciones = df[columna][df[columna].str.fullmatch(patron) == False]
                            
                            for idx in violaciones.index:
                                ws.cell(row=idx + 2, column=col_idx).fill = rojo_fill  # Marcar en rojo
                                ws.cell(row=idx + 2, column=2).fill = rojo_fill  # Marcar en rojo
                                

                        elif tipo == "unico":
                            duplicados = df[columna][df[columna].duplicated()]
                            for idx in duplicados.index:
                                ws.cell(row=idx + 2, column=col_idx).fill = rojo_fill
                                ws.cell(row=idx + 2, column=2).fill = rojo_fill  # Marcar en rojo
                                # Marcar en rojo

                        elif tipo == "dependiente positivo":
                            columna_dependiente = regla.get("columna_dependiente")
                            valor_dependiente = regla.get("valor_dependiente")
                            valor_esperado = regla.get("valor_esperado")
                            columna_dependiente1 = regla.get("columna_dependiente")
                            idx_dependiente1 = df.columns.get_loc(columna_dependiente1) + 1

                            if columna_dependiente in df.columns:
                                # Filtrar las filas donde la columna dependiente tenga el valor esperado
                                filas_dependientes = df[df[columna_dependiente] == valor_dependiente]

                                # Filtrar las filas que NO cumplen con el valor esperado en la columna principal
                                violaciones = filas_dependientes[filas_dependientes[columna] != valor_esperado]

                                # Solo marcar en rojo las filas que no cumplen con la condición
                                for idx in violaciones.index:
                                    # Marcar en rojo las celdas que no cumplen la condición (solo las filas con violaciones)
                                    ws.cell(row=idx + 2, column=2).fill = rojo_fill  # Marcar en rojo
                                    ws.cell(row=idx + 2, column=col_idx).fill = rojo_fill  
                                    ws.cell(row=idx + 2, column=idx_dependiente1).fill = rojo_fill
                                    
                                    
                            else:
                                messagebox.showinfo("Advertencia", f"Columna dependiente '{columna_dependiente}' no encontrada en el archivo Excel.")
                                
                        elif tipo == "no_vacio":
                            columnas = regla.get("columnas")
                            print("Columnas a verificar:", columnas)  # Imprimir para verificar las columnas

                            # Asegúrate de que 'columna' sea una lista
                            if isinstance(columnas, str):  # Si 'columna' es una cadena en lugar de lista
                                columnas = [columnas]  # Convertirla en una lista
                            
                            for columna in columnas:
                                if columna in df.columns:
                                    col_idx = df.columns.get_loc(columna) + 1  # Obtener el índice de la columna en openpyxl (1-based)
                                    print(f"Índice de columna '{columna}': {col_idx}")
                                    # Filtrar las filas que tienen valores vacíos en la columna
                                    violaciones = df[df[columna].isnull() | (df[columna] == "")]
                                    print(f"Violaciones encontradas en columna '{columna}': {violaciones.index.tolist()}")
                                    for idx in violaciones.index:
                                        print(f"Marcando fila {idx} en columna {columna}")  # Imprimir para depurar
                                        # Marcar en rojo las celdas que tienen valores vacíos en la columna principal
                                        ws.cell(row=idx + 2, column=2).fill = rojo_fill  # Marcar en rojo
                                        ws.cell(row=idx + 2, column=col_idx).fill = rojo_fill  # Marcar en rojo otra celda relacionada, si es necesario
                                else:
                                    messagebox.showinfo("Advertencia", f"Columna '{columna}' no encontrada en el archivo Excel.")

                        elif tipo == "dependiente_error":
                        
                            columna_dependiente = regla.get("columna_dependiente")
                            valor_dependiente = regla.get("valor_dependiente")
                            valor_esperado = regla.get("valor_esperado")
                            columna_dependiente1 = regla.get("columna_dependiente")
                            idx_dependiente1 = df.columns.get_loc(columna_dependiente1) + 1

                            if columna_dependiente in df.columns:
                                # Filtrar las filas donde la columna dependiente tenga el valor esperado
                                filas_dependientes = df[df[columna_dependiente] == valor_dependiente]

                                # Filtrar las filas que NO cumplen con el valor esperado en la columna principal
                                violaciones = filas_dependientes[filas_dependientes[columna] == valor_esperado]

                                # Solo marcar en rojo las filas que no cumplen con la condición
                                for idx in violaciones.index:
                                    # Marcar en rojo las celdas que no cumplen la condición (solo las filas con violaciones)
                                    ws.cell(row=idx + 2, column=2).fill = rojo_fill  # Marcar en rojo
                                    ws.cell(row=idx + 2, column=col_idx).fill = rojo_fill
                                    ws.cell(row=idx + 2, column=idx_dependiente1).fill = rojo_fill
                                    
                                
                                    
                            else:
                                messagebox.showinfo("Advertencia", f"Columna dependiente '{columna_dependiente}' no encontrada en el archivo Excel.")
                            
                        elif tipo == "dependiente longitud":
                        
                            columna_dependiente = regla.get("columna_dependiente")
                            valor_dependiente = regla.get("valor_dependiente")
                            valor_esperado = regla.get("valor_esperado")
                            columna_dependiente1 = regla.get("columna_dependiente")
                            idx_dependiente1 = df.columns.get_loc(columna_dependiente1) + 1

                            if columna_dependiente in df.columns:
                                # Filtrar las filas donde la columna dependiente tenga el valor esperado
                                filas_dependientes = df[df[columna_dependiente] == valor_dependiente]
                                
                                max_longitud = int(regla["valor_esperado"].split("<= ")[1])
                                
                                violaciones = filas_dependientes[filas_dependientes[columna] .astype(str).str.len() > max_longitud]
                                
                                for idx in violaciones.index:
                                    # Marcar en rojo las celdas que violan la regla de longitud
                                    ws.cell(row=idx + 2, column=col_idx).fill = rojo_fill  # +2 por el encabezado
                                    ws.cell(row=idx + 2, column=2).fill = rojo_fill  # Marcar en rojo
                                    ws.cell(row=idx + 2, column=idx_dependiente1).fill = rojo_fill
        
                            else:
                                messagebox.showinfo("Advertencia", f"Columna dependiente '{columna_dependiente}' no encontrada en el archivo Excel.")
                                
                        elif tipo == "dependiente edad positivo":
                            columna_dependiente = regla.get("columna_dependiente")  # Fecha de nacimiento
                            valor_dependiente = regla.get("valor_dependiente")  # Rango o edad específica
                            valor_esperado = regla.get("valor_esperado")  # Valor esperado en la columna principal
                            fecha_intervencion = regla.get("Fecha_int")  # Columna con la fecha de referencia
                            nacionalidad = regla.get("nacionalidad")  # Columna para filtrar primero por nacionalidad 

                            # Verificar que las columnas necesarias estén en el DataFrame
                            if columna in df.columns and columna_dependiente in df.columns and fecha_intervencion in df.columns:
                                # Filtrar por nacionalidad si es que se ha especificado
                                if nacionalidad and nacionalidad in df.columns:
                                    df = df[df[nacionalidad] == valor_dependiente]  # Filtrar por la nacionalidad deseada

                                # Convertir las columnas a datetime si no lo están
                                df[columna_dependiente] = pd.to_datetime(df[columna_dependiente], errors='coerce')
                                df[fecha_intervencion] = pd.to_datetime(df[fecha_intervencion], errors='coerce')

                                # Calcular la edad usando la fecha de referencia
                                df["edad_calculada"] = df.apply(
                                    lambda row: calcular_edad(row[columna_dependiente], row[fecha_intervencion]) 
                                    if pd.notnull(row[columna_dependiente]) and pd.notnull(row[fecha_intervencion]) else None, axis=1
                                )

                                # Identificar filas que no cumplen con la regla
                                if "," in valor_dependiente:  # Rango de edades (e.g., "0,13")
                                    min_edad, max_edad = map(int, valor_dependiente.split(","))
                                    violaciones = df[
                                        (df["edad_calculada"] >= min_edad) &
                                        (df["edad_calculada"] <= max_edad) &
                                        (df[columna] != valor_esperado)
                                    ]
                                else:  # Edad específica (e.g., "14")
                                    edad_especifica = int(valor_dependiente)
                                    violaciones = df[
                                        (df["edad_calculada"] == edad_especifica) &
                                        (df[columna] != valor_esperado)
                                    ]

                                # Marcar las celdas que no cumplen con la regla
                                for idx in violaciones.index:
                                    ws.cell(row=idx + 2, column=df.columns.get_loc(columna) + 1).fill = rojo_fill
                                    ws.cell(row=idx + 2, column=df.columns.get_loc(columna_dependiente) + 1).fill = rojo_fill
                                    ws.cell(row=idx + 2, column=df.columns.get_loc(fecha_intervencion) + 1).fill = rojo_fill
                                    ws.cell(row=idx + 2, column=2).fill = rojo_fill  # Marcar en rojo

                            else:
                                # Mostrar mensaje de advertencia si las columnas no existen
                                print(f"Advertencia: Una de las columnas especificadas no existe en el archivo Excel.")

                                            
                        elif tipo == "dependiente edad error":
                            
                            columna_dependiente = regla.get("columna_dependiente")  # Fecha de nacimiento
                            valor_dependiente = regla.get("valor_dependiente" ) # Rango o edad específica
                            valor_esperado = regla.get("valor_esperado")  # Valor esperado en la columna principal
                            fecha_intervencion = regla.get("Fecha_int")  # Columna con la fecha de referencia
                        
                            # Verificar que las columnas necesarias estén en el DataFrame
                            if columna in df.columns and columna_dependiente in df.columns and fecha_intervencion in df.columns:
                                # Convertir las columnas a datetime si no lo están
                                df[columna_dependiente] = pd.to_datetime(df[columna_dependiente], errors='coerce')
                                df[fecha_intervencion] = pd.to_datetime(df[fecha_intervencion], errors='coerce')

                                # Calcular la edad usando la fecha de referencia
                                df["edad_calculada"] = df.apply(
                                    lambda row: calcular_edad(row[columna_dependiente], row[fecha_intervencion]) 
                                    if pd.notnull(row[columna_dependiente]) and pd.notnull(row[fecha_intervencion]) else None, axis=1
                                )

                                # Identificar filas que no cumplen con la regla
                                if "," in valor_dependiente:  # Rango de edades (e.g., "0,13")
                                    min_edad, max_edad = map(int, valor_dependiente.split(","))
                                    violaciones = df[
                                        (df["edad_calculada"] >= min_edad) &
                                        (df["edad_calculada"] <= max_edad) &
                                        (df[columna] == valor_esperado)
                                    ]
                                else:  # Edad específica (e.g., "14")
                                    edad_especifica = int(valor_dependiente)
                                    violaciones = df[
                                        (df["edad_calculada"] == edad_especifica) &
                                        (df[columna] == valor_esperado)
                                    ]

                                # Marcar las celdas que no cumplen con la regla
                                for idx in violaciones.index:
                                    ws.cell(row=idx + 2, column=df.columns.get_loc(columna) + 1).fill = rojo_fill
                                    ws.cell(row=idx + 2, column=df.columns.get_loc(columna_dependiente) + 1).fill = rojo_fill
                                    ws.cell(row=idx + 2, column=df.columns.get_loc(fecha_intervencion) + 1).fill = rojo_fill
                                    ws.cell(row=idx + 2, column=2).fill = rojo_fill  # Marcar en rojo
                                    
                            else:
                                # Mostrar mensaje de advertencia si las columnas no existen
                                print(f"Advertencia: Una de las columnas especificadas no existe en el archivo Excel.")
                                                            
                    else: 
                        messagebox.showinfo("Advertencia", f"Columna '{columna}' no encontrada en el archivo Excel.")

                # Guardar el nuevo archivo Excel con las celdas marcadas
                nuevo_archivo = filedialog.asksaveasfilename(
                    title="Guardar archivo Excel con validaciones",
                    defaultextension=".xlsx",
                    filetypes=[("Archivos Excel", "*.xlsx")]
                )

                if nuevo_archivo:
                    wb.save(nuevo_archivo)
                    messagebox.showinfo("Éxito", "Se ha creado un nuevo archivo con las validaciones marcadas en rojo.")

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo analizar el archivo Excel:\n{e}")




    def calcular_edad(fecha_nacimiento, fecha_referencia):
    
        edad = fecha_referencia.year - fecha_nacimiento.year
        if (fecha_referencia.month, fecha_referencia.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
            edad -= 1
            
        return edad


    # Función para eliminar un área
    def eliminar_area(area):
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar el área '{area}'?"):
            del areas[area]
            guardar_areas()
            actualizar_botones_areas()
            for widget in frame_derecho.winfo_children():
                widget.destroy()  # Limpiar el panel derecho



    def crearhc():
        #print('crear fichas hc')
        crear.hc_crear()

    def openxcel():

        # Especifica la ruta relativa al archivo Excel
        file_path = os.path.join(os.path.dirname(__file__), 'crear_hc', 'crearIndividualfinal.xlsx')
        
        # Verifica si el archivo existe antes de intentar abrirlo
        if os.path.exists(file_path):
            # Abre Excel y el archivo especificado
            excel = win32.Dispatch('Excel.Application')
            workbook = excel.Workbooks.Open(file_path)
            
            # Haz visible Excel para que el usuario pueda editar el archivo
            excel.Visible = True

            # Mostrar ventana de confirmación usando tkinter
            root = tk.Tk()
            root.withdraw()  # Oculta la ventana principal
            
            # Abre un cuadro de diálogo que espera confirmación
            messagebox.showinfo("Edición de Excel", "Por favor, edite el archivo y presione OK cuando termine.")
            
            time.sleep(1)

            # Guarda el archivo (sobrescribiendo el existente) y cierra Excel
            try:
                workbook.Save()  # Esto sobrescribe el archivo actual, no crea uno nuevo
                workbook.Close()
                excel.Quit()
                print(f"Archivo guardado y cerrado correctamente: {file_path}")
            except Exception as e:
                print(f"Error al guardar el archivo: {e}")
                workbook.Close(False)  # Cierra sin guardar si hay un error
                excel.Quit()
        else:
            print(f"El archivo no existe en la ruta: {file_path}")

            
    # Configuración inicial de la ventana principal
    ctk.set_appearance_mode("Dark")  # Modo oscuro
    customtkinter.deactivate_automatic_dpi_awareness() # escalado automatico
    ventana = ctk.CTk()
    ventana.title("Odin Validadores")
    ventana.geometry("800x600")
    
    # Cambiar el ícono de la ventana
    icon = PhotoImage(file="img/logo.png")  # Ruta a tu ícono personalizado
    ventana.iconphoto(False, icon)
    
    ventana.iconbitmap("img/logo.ico")

    # Crear un menú
    menu_bar = Menu(ventana)
    ventana.config(menu=menu_bar)

    # Menú "Archivo"
    menu_archivo = Menu(menu_bar, tearoff=0)
    menu_archivo.add_separator()
    menu_archivo.add_command(label="Salir", command=ventana.quit)
    menu_bar.add_cascade(label="Archivo", menu=menu_archivo)

    # Menú "Crear_Hc"
    crear_hc_menu = Menu(menu_bar, tearoff=0)
    icon = PhotoImage(file="img/icons/icono_excel.png")  
    crear_hc_menu.add_command(label="Editar",  command=openxcel, image=icon)
    crear_hc_menu.add_command(label="Ejecutar", command=crearhc)
    menu_bar.add_cascade(label="Crear Hc", menu=crear_hc_menu)

    # Crear dos paneles: izquierdo y derecho
    frame_izquierdo = ctk.CTkFrame(ventana, width=200)
    frame_izquierdo.pack(side="left", fill="y", padx=10, pady=10)

    frame_derecho = ctk.CTkFrame(ventana)
    frame_derecho.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Cargar las áreas y crear los botones en el panel izquierdo
    areas = cargar_areas()
    actualizar_botones_areas()

    ventana.mainloop()

except Exception as e:
    import traceback
    with open("error_log.txt", "w") as f:
        f.write(str(e))
        f.write(traceback.format_exc())