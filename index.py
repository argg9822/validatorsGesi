import tkinter as tk
import customtkinter
import subprocess
from validadores import institucional, educativo, comunitario
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


class App(customtkinter.CTk):
    
   
    def codigoejem(self, valuebase, basejson):
        
        print(basejson)
        
        with open('codigoInsert.py', 'r') as plantilla_file:
            codigo_plantilla = plantilla_file.read()
        
        # Reemplazo manual del marcador de posición
        codigo_personalizado = codigo_plantilla.replace("{PLACEHOLDER}", repr(valuebase))
        
        #  crear funciones nesaciarias 
        self.funcionesgenerales(self, basejson)
        
        return codigo_personalizado


    def funcionesgenerales(self, valuebase,):
        print ("Gener codigo para insertar parametros" )
     
    def __init__(self):
        
        
        super().__init__()
        
        try:
            with open('bases.json', 'r') as f:
                self.bases = json.load(f)
        except FileNotFoundError:
            self.bases = {}
            
        
       
        # Configure window
        self.title("Odin")
        self.geometry(f"{1010}x{450}")

        # Configure grid layout
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure((2), weight=1)
        self.grid_rowconfigure((1), weight=1)

        # Create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Validar Bases", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Crear botones dinámicamente según las categorías en el diccionario
        for i, category in enumerate(self.bases.keys(), start=1):
            button = customtkinter.CTkButton(
                self.sidebar_frame, 
                text=category.capitalize(), 
                command=lambda cat=category: self.mostrarBases(cat)
            )
            button.grid(row=i, column=0, padx=20, pady=10, sticky="ew")
        
        # Appearance options
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # Create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=250, height=250)
        self.textbox.grid(row=1, column=2, padx=(20, 20), pady=(10, 10), sticky="nsew")
        
         # Redirect stdout to the CTkTextbox
        sys.stdout = TextRedirector(self.textbox)

        # Create tabview
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=1, column=1, padx=(20, 0), pady=(5, 10), sticky="nsew")
        
        self.textbox.configure(
            font=("Consolas", 12)  # Fuente monoespaciada
        )
        
        
        self.textbox.insert("1.0", "Bienvenido a la línea de registro Odin\n")
        self.textbox.insert("1.0", "...\n")
        self.textbox.insert("end", "...\n")
        
        # Initialize tabs dictionary
        self.tabs = {}
        
         # Create menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        # Add "Archivo" menu
        self.archivo_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Archivo", menu=self.archivo_menu)
        self.archivo_menu.add_command(label="Actualizar Todo", command=self.actualizar_todo_event)
        self.archivo_menu.add_separator()
        self.archivo_menu.add_command(label="Salir", command=self.quit)

        # Add "Herramientas" menu
        self.herramientas_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Herramientas", menu=self.herramientas_menu)
        
        # Agregar el comando "Crear_Hc"
        self.crear_hc_menu = tk.Menu(self.herramientas_menu, tearoff=0)
        self.herramientas_menu.add_cascade(label="Crear_Hc", menu=self.crear_hc_menu)
        
        # Agregar opciones al submenú "Crear_Hc"
        self.icon = PhotoImage(file="img/icons/icono_excel.png")  
        self.crear_hc_menu.add_command(label="Editar",  command=self.openxcel, image=self.icon, compound=tk.LEFT)
        self.crear_hc_menu.add_command(label="Ejecutar", command=self.crearhc)
        
        self.herramientas_menu.add_command(label="Editar Bases", command=self.editar_bases_event)
        self.obsiones_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Opciones", menu=self.obsiones_menu)
        self.codigo_menu = tk.Menu(self.herramientas_menu, tearoff=0)
        self.obsiones_menu.add_cascade(label="Codigos", menu=self.codigo_menu)
        self.addvalidador_menu = tk.Menu(self.obsiones_menu, tearoff=0)
        self.obsiones_menu.add_cascade(label="Agregar validador", menu=self.addvalidador_menu)
        
         
        for i, category in enumerate(self.bases.keys(), start=1):
            self.addvalidador_menu.add_command(
                label=category,
                command=lambda cat=category: self.aventanaadd(cat)
            )

        # Agregar comandos para archivos en la carpeta validadores
        self.cargar_codigos()


    #////////////////////////////////////////////////////////////////////////
    #///////////////////////////////////////////////////////////////////////
    
    def crearhc(self):
        print('crear fichas hc')
        crear.hc_crear(self)
    
    def openxcel(self):
        # Especifica la ruta relativa al archivo Excel
        file_path = os.path.join(os.path.dirname(__file__), 'crear_hc', 'crearIndividualfinal.xlsx')
        
        # Abre el archivo con el programa predeterminado (Excel)
        os.startfile(file_path)
        
        
    def aventanaadd(self, cat):
        print('ejecutar nueva ventana')
        # Crear una ventana de diálogo para editar el diccionario
        dialog = customtkinter.CTkToplevel(self)
        dialog.title(f"Agregar nueva validacion para {cat}")
        
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus()
        
        label = customtkinter.CTkLabel(dialog, text=f"Nombre de la base para agregar nuevo parametro")
        label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # crear select
        opciones = ["sesiones pagina 1", "sesiones pagina 2", "Osesiones pagina 3"]  # reemplaza con tu lista de opciones
        opcion_seleccionada = tk.StringVar()
        combobox = customtkinter.CTkComboBox(dialog, values=opciones)
        combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        label = customtkinter.CTkLabel(dialog, text=f"Funciones prestablecidas")
        label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        opciones = ["","Vacias", "Calcular edad", "Texto", "Sexo - Genero", "etnia","afiliacion", "No. placas", "telefono" , "Manzana Priorizada", "Ninguna"]
        combobox_condicion = customtkinter.CTkComboBox(dialog, values=opciones)
        combobox_condicion.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        label = customtkinter.CTkLabel(dialog, text=f"ingrese numero de columnas (Ej: A = 1 B = 2)")
        label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
        texto_ingresado = tk.StringVar()
        entry = customtkinter.CTkEntry(dialog, textvariable=texto_ingresado)
        entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        dialog.update
            
        
        def save_changes():
            # Obtener los valores seleccionados en la ventana
            opcion_seleccionada_valor = combobox.get()
            combobox_condicion_valor = combobox_condicion.get()
            texto_ingresado_valor = texto_ingresado.get()
            
            # Llamar a la función que tomará decisiones con los parámetros seleccionados
            self.tomar_decisiones(opcion_seleccionada_valor, combobox_condicion_valor, texto_ingresado_valor, cat)
        
        save_button = customtkinter.CTkButton(dialog, text="Guardar", command=save_changes)
        save_button.grid(row=len(self.bases), column=0, columnspan=2, pady=10)

    def tomar_decisiones(self, opcion_seleccionada, combobox_condicion, texto_ingresado, cat):
        # Aquí puedes implementar la lógica para tomar decisiones con los parámetros seleccionados
        print(f"Opción seleccionada: {opcion_seleccionada}")
        print(f"Condición seleccionada: {combobox_condicion}")
        print(f"Texto ingresado: {texto_ingresado}")
        self.vacias(texto_ingresado,cat)
        
        
    def vacias(self,texto_ingresado, entorno):
        codigo = f"""
            # Codigo generado automaticamente
            # valor para validar vacias
            CeldasVacias['vacias'] = {{{texto_ingresado}}}
            celdas_pintadas_rojo += validarVacias(sheet, CeldasVacias)
            
    """ 
        print(f"Codigo ingresado: \n {codigo}")
        
        ruta_hogar = f'validadores/{entorno}.py'  # Cambia esta ruta según corresponda
        
        print(ruta_hogar)

        # Leer el contenido actual de hogar.py
        with open(ruta_hogar, 'r') as archivo:
            contenido = archivo.readlines()
            
         # Buscar el inicio de la función sesiones_pagina1 y la ubicación para insertar el código
        inicio_funcion = None
        ubicacion_insercion = None
        
        print(self.bases)
        
        # Buscar la función sesiones_pagina1 y el bloque de código donde insertar el nuevo código
        for i, linea in enumerate(contenido):
            if 'def csapag1(' in linea:
                inicio_funcion = i
            if inicio_funcion is not None:
                if '#////////////////////////////// Codigo para actualizar progreso de validacion NO QUITAR  //////////////////////////////////////////' in linea:
                    ubicacion_insercion = i
                    break

        if inicio_funcion is None:
            print("No se encontró la función sesiones_pagina1.")
            raise ValueError("No se encontró la función sesiones_pagina1.")

        if ubicacion_insercion is None:
            raise ValueError("No se encontró el lugar adecuado para insertar el código.")

        # Insertar el nuevo texto antes de la línea específica
        contenido.insert(ubicacion_insercion, codigo)

        # Guardar el contenido modificado en hogar.py
        with open(ruta_hogar, 'w') as archivo:
            archivo.writelines(contenido)
        
        print(f"nuevo parametro insertado en {ruta_hogar} exitosamente.")  
            
                    
    def cargar_codigos(self):
        carpeta = "validadores"

        # Verifica si la carpeta existe
        if not os.path.exists(carpeta):
            messagebox.showerror("Error", "La carpeta no existe")
            return

        # Limpiar el menú antes de agregar nuevos comandos
        self.codigo_menu.delete(0, tk.END)

        # Agregar comandos para cada archivo en la carpeta
        for archivo in os.listdir(carpeta):
            if os.path.isfile(os.path.join(carpeta, archivo)):
                # Añadir un comando al menú por cada archivo
                self.codigo_menu.add_command(label=archivo, command=lambda f=archivo: self.pedir_contrasena_y_abrir(f))

    def pedir_contrasena_y_abrir(self, archivo):
        # Pedir nombre de usuario y contraseña
        usuario = simpledialog.askstring("Usuario", "Ingresa tu nombre de usuario:")
        contrasena = simpledialog.askstring("Contraseña", "Ingresa tu contraseña:", show='*')

        # Verificar las credenciales
        if self.verificar_credenciales(usuario, contrasena):
            self.abrir_archivo(archivo)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def verificar_credenciales(self, usuario, contrasena):
        # Definir el usuario y contraseña correctos
        usuario_correcto = "admin"
        contrasena_correcta = "1234456"

        return usuario == usuario_correcto and contrasena == contrasena_correcta

    def abrir_archivo(self, archivo):
        # Lógica para abrir el archivo
        filepath = os.path.join("validadores", archivo)
        # Abre el archivo en el Bloc de notas (solo en Windows)
        try:
            subprocess.Popen(['notepad.exe', filepath])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

        
         
    def actualizar_todo_event(self):
        for widget in self.sidebar_frame.winfo_children():
            widget.destroy()

        # Recrea los widgets del sidebar
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Validar Bases", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Recrea los botones dinámicamente según las categorías en el diccionario
        for i, category in enumerate(self.bases.keys(), start=1):
            button = customtkinter.CTkButton(
                self.sidebar_frame, 
                text=category.capitalize(), 
                command=lambda cat=category: self.mostrarBases(cat)
            )
            button.grid(row=i, column=0, padx=20, pady=10, sticky="ew")

        # Actualiza las opciones de apariencia y escala
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                    command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                            command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        
        # Si usas un TextRedirector para redirigir stdout a un CTkTextbox, asegúrate de reiniciarlo si es necesario
        sys.stdout = TextRedirector(self.textbox)
        print('Ventana actualizada.'.format(Fore.RED, Style.RESET_ALL))
        
    # Primero, destruye todos los widgets dentro del sidebar_frame para limpiar
        
   
    def editar_bases_event(self):
        # Crear una ventana de diálogo para editar el diccionario
        dialog = customtkinter.CTkToplevel(self)
        dialog.title("Editar Bases")
        
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus()
        
        # Crear campos de entrada para cada categoría
        self.entries = {}
        
        for i, (category, items) in enumerate(self.bases.items()):
            label = customtkinter.CTkLabel(dialog, text=f"{category}:")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            # Formatear los ítems como "nombre (páginas)"
            formatted_items = [f"{item['nombre']} ({item['paginas']})" for item in items]
            entry = customtkinter.CTkEntry(dialog)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entry.insert(0, ", ".join(formatted_items))
            self.entries[category] = entry
        
        # Botón para guardar cambios
        save_button = customtkinter.CTkButton(dialog, text="Guardar", command=self.save_changes)
        save_button.grid(row=len(self.bases), column=0, columnspan=2, pady=10)

        # Crear campos de entrada para agregar una nueva categoría
        self.new_category_name = customtkinter.CTkEntry(dialog, placeholder_text="Nueva categoría")
        self.new_category_name.grid(row=len(self.bases) + 1, column=0, padx=10, pady=5, sticky="ew")
        
        self.new_category_items = customtkinter.CTkEntry(dialog, placeholder_text="Ítems (separados por comas)")
        self.new_category_items.grid(row=len(self.bases) + 1, column=1, padx=10, pady=5, sticky="ew")
        
        self.new_category_pag = customtkinter.CTkEntry(dialog, placeholder_text="Numero de paginas que desea validar")
        self.new_category_pag.grid(row=len(self.bases) + 1, column=2, padx=10, pady=5, sticky="ew")
        
    
        # Botón para agregar nueva categoría
        add_button = customtkinter.CTkButton(dialog, text="Agregar Categoría", command=self.add_category)
        add_button.grid(row=len(self.bases) + 2, column=0, columnspan=2, pady=10)
      

    def save_changes(self):
        # Actualizar el diccionario con los nuevos valores
        for category, entry in self.entries.items():
            # Obtener el texto del campo de entrada y dividirlo en ítems
            items_text = entry.get()
            # Limpiar el texto y dividirlo en ítems basados en el formato "nombre (páginas)"
            item_entries = items_text.split(", ")
            
            # Procesar cada ítem para extraer nombre y páginas
            updated_items = []
            for item_entry in item_entries:
                try:
                    # Separar el nombre y el número de páginas
                    name, pages = item_entry.rsplit(" (", 1)
                    pages = int(pages.rstrip(")"))  # Eliminar el paréntesis y convertir a entero
                    updated_items.append({"nombre": name.strip(), "paginas": pages})
                except ValueError:
                    # Manejar el caso donde el formato es incorrecto
                    print(f"Error al procesar el ítem: {item_entry}")
                    continue
            
            # Actualizar la categoría en el diccionario
            self.bases[category] = updated_items

        print("Bases actualizadas:", self.bases)
        
        self.save_data()
        
    def save_data(self):
        with open('bases.json', 'w') as f:
            json.dump(self.bases, f, indent=4)
            
    def add_category(self):
        # Obtener el nombre de la nueva categoría
        new_category = self.new_category_name.get().strip()

        # Obtener los ítems y el número de páginas
        new_items_text = self.new_category_items.get().strip()
        new_pag_text = self.new_category_pag.get().strip()
        
        # Validar que los campos no estén vacíos
        if new_category and new_items_text and new_pag_text:
            # Dividir los ítems basados en la coma
            item_entries = new_items_text.split(", ")

            # Crear una lista de ítems en formato JSON
            new_items = []
            for item_name in item_entries:
                try:
                    # Crear un diccionario para cada ítem con el nombre y número de páginas
                    new_items.append({"nombre": item_name.strip(), "paginas": int(new_pag_text)})
                except ValueError:
                    print(f"Error al procesar el número de páginas: {new_pag_text}")
                    continue

            # Agregar la nueva categoría al diccionario
            self.bases[new_category] = new_items
            print(f"Categoría añadida: {new_category} con ítems: {new_items}")
            
            # Limpiar los campos de entrada
            self.new_category_name.delete(0, tk.END)
            self.new_category_items.delete(0, tk.END)
            self.new_category_pag.delete(0, tk.END)
            
            # Volver a mostrar el diálogo con la nueva categoría incluida
            self.editar_bases_event()
            
            # Crear archivo en la carpeta validadores con el nombre de la categoría
            validator_file_path = os.path.join("validadores", f"{new_category}.py")
            
            # Generar el código
            codigo_generado = self.codigoejem(new_category, self.bases)
            
            print(f"codigo generado {codigo_generado}")
            
            # Escribir el código en el archivo
            with open(validator_file_path, "w") as f:
                 f.write(codigo_generado)  # Crear archivo con muestra de código
            
            # Abrir el archivo en el bloc de notas
            print(f"Ruta del archivo: {validator_file_path}")
            subprocess.Popen(['notepad.exe', validator_file_path])
            os.startfile(validator_file_path)
            
            # Guardar los datos actualizados
            self.save_data()
        else:
            print("El nombre de la categoría, los ítems o el número de páginas no pueden estar vacíos.")

   


    def update_bases(self, base):
        # Aquí puedes agregar lógica para editar las bases
        new_value = simpledialog.askstring("Editar Bases", f"Editar base {base}:")
        if new_value:
            print(f"Base actualizada: {base} -> {new_value}")
            # Actualiza la base en el diccionario
            # Ejemplo: self.bases[base] = new_value
            self.mostrarBases(base)  # Refresca la vista


    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

    def mostrarBases(self, valor):
        print(f"Activando validadores de: {valor}")

        # Convert valor to lowercase to match dictionary keys
        valor_lower = valor.lower()

        # Check if the tab already exists
        if valor_lower in self.tabs:
            tab_name = self.tabs[valor_lower]
        else:
            tab_name = "Bases " + valor
            self.tabview.add(tab_name)
            self.tabs[valor_lower] = tab_name

        # Get the frame for the tab
        tab_frame = self.tabview.tab(tab_name)

        # Clear existing widgets in the tab
        for widget in tab_frame.winfo_children():
            widget.destroy()

        # Add new buttons to the tab using customtkinter.CTkButton
        if valor_lower in self.bases:
            for item in self.bases[valor_lower]:
                button = customtkinter.CTkButton(tab_frame, text=item['nombre'], width=200, height=25, corner_radius=10, command=self.ejecutarValidadorEntornos(valor_lower, item['nombre']))
                button.pack(pady=1)
        else:
            print("No se encontraron bases coincidentes.")

    def ejecutarValidadorEntornos(self, script_path, base):
        
        def callback():
            subprocess.Popen(["python", f'validadores/{script_path}.py', base])  # Ejecutar el script cuando se hace clic en el botón
            # Aquí deberías agregar tu lógica específica para cada script_path
            if script_path == "institucional":
                print(f"Inicializando la base de: {base} \n Por favor espere..."  )
                institucional.setBase(base)
            elif script_path == "educativo":
                print(f"Inicializando la base de: {base} \n Por favor espere..."  )
                educativo.setBase(base)
                print(f"Inicializando la base de: {base} \n Por favor espere..."  )
            elif script_path == "laboral":
                print(f"Inicializando la base de: {base} \n Por favor espere..."  )
                laboral.setBase(base)

        return callback

    def update_bases(self):
        # Logic to update the bases dictionary
        # This could be a dialog that asks the user to enter new data, or you could load it from a file
        print("Update Bases menu item clicked")
        
class TextRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        if string.startswith('\x1b[31m'):  # Verificar si la cadena comienza con el código ANSI para el color rojo
            self.widget.insert(tk.INSERT, string[7:], 'error')  # Eliminar el código ANSI e insertar con la etiqueta 'error'
        elif string.startswith('\x1b[0m'):  # Verificar si la cadena comienza con el código ANSI para el color de reset
            self.widget.insert(tk.INSERT, string[4:])  # Eliminar el código ANSI e insertar normalmente
        else:
            self.widget.insert(tk.INSERT, string)
        self.widget.see(tk.END)

    def flush(self):
        pass

if __name__ == "__main__":
    app = App()
    app.mainloop()