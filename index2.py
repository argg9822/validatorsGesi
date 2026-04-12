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
import sys
import tkinter as tk
import customtkinter as ctk
import io
import requests
class RedirectText(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)  # Insertar el texto
        self.text_widget.see(tk.END)  # Desplazar hacia abajo para mostrar siempre el texto más reciente
        self.text_widget.update()  # Actualizar el widget para mostrar los cambios de inmediato


def index_open():

    log_file = "error_log.txt"


    def log_error(error_message):
        # Escribe el error en el archivo de log
        with open(log_file, "a") as log:
            log.write(error_message + "\n")

    try:
        
        #Ruta del archivo JSON donde se guardarán las áreas
        url = "https://www.trakio.pro/areas"

        def cargar_areas():
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Error al cargar áreas: {response.status_code}")
            except Exception as e:
                print(f"Error al cargar las áreas: {e}")
            return {}

        def guardar_areas(nombre_area, datos_area):
            """
            Actualizar una nueva área o agregarla si no existe.
            :param nombre_area: Nombre del área (clave del JSON)
            :param datos_area: Datos de la nueva área (lista vacía o con validadores)
            """
            url_actualizar = f"{url}/{nombre_area}"  # Agregamos el nombre del área en la URL
            try:
                response = requests.put(url_actualizar, json={"area": datos_area})
                if response.status_code in [200, 201]:  # 200: éxito, 201: creado
                    print(f"Área '{nombre_area}' guardada correctamente.")
                else:
                    print(f"Error al guardar área '{nombre_area}': {response.status_code}")
            except Exception as e:
                print(f"Error al guardar el área '{nombre_area}': {e}")

        def eliminar_area(area):
            if messagebox.askyesno("Confirmar", f"¿Desea eliminar el área '{area}'?"):
                # Hacer una solicitud DELETE al servidor para eliminar el área
                url_eliminar = f"{url}/{area}"
                try:
                    response = requests.delete(url_eliminar)
                    if response.status_code == 204:  # 204: No Content, indica que la eliminación fue exitosa
                        del areas[area]  # Eliminar el área del diccionario local
                        guardar_areas()  # Guardar los cambios en el archivo (si es necesario)
                        actualizar_botones_areas()  # Actualizar la interfaz
                        for widget in frame_derecho.winfo_children():
                            widget.destroy()  # Limpiar el panel derecho
                        messagebox.showinfo("Eliminación exitosa", f"El área '{area}' ha sido eliminada.")
                    else:
                        print(f"Error al eliminar el área '{area}': {response.status_code}")
                        messagebox.showerror("Error", f"No se pudo eliminar el área '{area}'.")
                except Exception as e:
                    print(f"Error al eliminar el área '{area}': {e}")
                    messagebox.showerror("Error", f"Se produjo un error al intentar eliminar el área '{area}': {e}")

        def agregar_area():
            nueva_area = ctk.CTkInputDialog(title="Agregar Área", text="Ingrese el nombre del entorno:")
            nueva_area_result = nueva_area.get_input()
            print(nueva_area_result)
            if nueva_area_result:
                if nueva_area_result in areas:  # Validamos si ya existe
                    messagebox.showerror("Error", "El entorno ya existe.")
                    return
                areas[nueva_area_result] = []  # Nueva área comienza con lista vacía de validadores
                guardar_areas(nueva_area_result, areas[nueva_area_result])  # Guardar nueva área
                actualizar_botones_areas()  # Actualizar visualización

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
                return  # Si no se ingresa un nombre, salimos de la función
            
            # Verificamos si el validador ya existe en el área
            if any(validador['nombre'] == nombre_validador_result for validador in areas[area]):
                messagebox.showerror("Error", "El validador ya existe en esta área.")
                return
            
            nuevo_validador = {"nombre": nombre_validador_result, "reglas": []}  # Inicialmente sin reglas
            areas[area].append(nuevo_validador)  # Agregamos el nuevo validador a la lista de validadores del área
            
            # Guardamos las áreas actualizadas
            guardar_areas(area, areas[area])  # Asegúrate de pasar el área y sus validadores actualizados
            seleccionar_area(area)  # Actualiza la visualización de la área seleccionada

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
                crear_regla(tipo_regla, validador, area, areas, guardar_areas, gestionar_validador)

            # Mostrar el modal
            mostrar_modal(tipo_regla_var, callback)

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
                guardar_areas(area, areas[area])
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
            
        def crearhc():
            print('crear fichas hc')
            crear.hc_crear()

                
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
    
        crear_hc_menu.add_command(label="Iniciar Cracion Hc", command=crearhc)
        menu_bar.add_cascade(label="Crear Hc", menu=crear_hc_menu)

        # Crear dos paneles: izquierdo y derecho
        # Crear dos paneles: izquierdo y derecho
        frame_izquierdo = ctk.CTkFrame(ventana, width=200)
        frame_izquierdo.pack(side="left", fill="y", padx=10, pady=10)

        # Cambiar el empaquetado de frame_derecho para que ocupe solo el espacio necesario
        frame_derecho = ctk.CTkScrollableFrame(ventana)
        frame_derecho.pack(side="top", fill="both", expand=True, padx=10, pady=10)  # Cambiar a "top"

        # Crear el widget de texto para la consola
        # Crear widget de texto para la consola con fondo negro y texto blanco
        console_frame = ctk.CTkFrame(ventana)
        console_frame.pack(side="top", fill="x", padx=10, pady=10)

        console_text = tk.Text(console_frame, height=10, wrap=tk.WORD, bg="black", fg="white")
        console_text.pack(fill="both", expand=True)

        # Redirigir stdout a la consola
        sys.stdout = RedirectText(console_text)

        # Ejemplo de uso de print
        print("Odin:")
        # Cargar las áreas y crear los botones en el panel izquierdo
        areas = cargar_areas()
        actualizar_botones_areas()

        ventana.mainloop()

    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(str(e))
            f.write(traceback.format_exc())
        
index_open()