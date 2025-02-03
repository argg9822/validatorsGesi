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
from crc_princ.modal_helper import mostrar_modal

from crc_princ.reglas import crear_regla
from crc_princ.analizar_exel import analizar_excel_2

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
      
        tipo_regla_var = ctk.StringVar(value="longitud")  # Valor predeterminado

        def callback(tipo_regla):
            """
            Callback que se ejecuta al confirmar el tipo de regla.

            Args:
                tipo_regla (str): Tipo de regla seleccionada.
            """
            # Llamar a la función del archivo reglas.py
            crear_regla(tipo_regla, validador, area, guardar_areas, gestionar_validador)

        # Mostrar el modal
        mostrar_modal(tipo_regla_var, callback)

    # Función para editar una regla
    def editar_regla(area, validador, regla):
        indice = validador["reglas"].index(regla)
        # Crear una ventana emergente para editar los campos
        def guardar_ediciones():
            # Actualizar los campos con los valores editados
            for campo, entry in entradas.items():
                validador["reglas"][indice][campo] = entry.get()
            guardar_areas()
            gestionar_validador(area, validador)
            ventana_edicion.destroy()

        # Crear la ventana de edición
        ventana_edicion = ctk.CTkToplevel()
        ventana_edicion.title("Editar Regla de base")
        
        ventana_edicion.lift() 
        ventana_edicion.focus_set()
        # Obtener el tamaño de la pantalla
        ancho_ventana = 400  # Ancho deseado para la ventana emergente
        alto_ventana = 300   # Alto deseado para la ventana emergente

        # Obtener las dimensiones de la pantalla
        screen_width = ventana_edicion.winfo_screenwidth()
        screen_height = ventana_edicion.winfo_screenheight()

        # Calcular la posición centrada
        posicion_x = (screen_width // 2) - (ancho_ventana // 2)
        posicion_y = (screen_height // 2) - (alto_ventana // 2)

        # Establecer la geometría de la ventana emergente (centrada)
        ventana_edicion.geometry(f"{ancho_ventana}x{alto_ventana}+{posicion_x}+{posicion_y}")

        
        # Diccionario para almacenar las entradas de texto
        entradas = {}
        
        # Mostrar los campos de la regla en el cuadro de edición
        for campo, valor in regla.items():
            if isinstance(valor, str):  # Mostrar solo los campos que son strings
                # Crear un label y una entrada para cada campo
                ctk.CTkLabel(ventana_edicion, text=f"Modificar {campo}:").pack(padx=10, pady=5)
                entry = ctk.CTkEntry(ventana_edicion)
                entry.insert(0, valor)  # Colocar el valor actual en la entrada
                entry.pack(padx=10, pady=5)
                entradas[campo] = entry

        # Crear el botón de guardar
        guardar_button = ctk.CTkButton(ventana_edicion, text="Guardar cambios", command=guardar_ediciones)
        guardar_button.pack(padx=10, pady=10)

        # Mostrar la ventana de edición
        ventana_edicion.mainloop()


    def analizar_excel(validador):
        analizar_excel_2(validador)
        
    
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

    frame_derecho = ctk.CTkScrollableFrame(ventana)
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