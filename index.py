import tkinter as tk
import customtkinter
import subprocess
from validadores import institucional, educativo, comunitario
import sys
from colorama import init, Fore, Style
from PIL import Image, ImageTk
from __version__ import __version__ as version_actual_actual  # Importa la versión actual desde __version__.py
import os
import tkinter as tk
import customtkinter
from tkinter import simpledialog

import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox

class App(customtkinter.CTk):
    
    
    bases = {
            "educativo": ["prevencion_embarazo", "autocuidado", "sesiones_colectivas", "higiene_bucal", "higiene_manos", "salud_mental", "mascota_verde", "entornos_escolares", "pretest", "entornos_jardines", "jornadas", "escala_abreviada", "tiendas_escolares"],
            "comunitario": ["sesiones_colectivas", "vinculate", "maps", "cami", "zarit", "pcbh", "caldas", "guardianes", "acondicionamiento", "cuidarte", "mujeres", "fortalecimiento", "pid"],
            "institucional": ["sesiones_colectivas", "ead", "hcb", "mascota_verde", "ipa", "pcb", "persona_mayor", "pci", "tamizajes"]
        }
    
    
    
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Validador Gesiapp")
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
        
        
        self.textbox.insert("1.0", "Bienvenido a la línea de registro Gesiapp\n")
        self.textbox.insert("1.0", "...\n")
        
        

        # Initialize tabs dictionary
        self.tabs = {}
        
         # Create menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        # Add "Archivo" menu
        self.archivo_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Archivo", menu=self.archivo_menu)
        self.archivo_menu.add_command(label="Nuevo", command=self.nuevo_event)
        self.archivo_menu.add_command(label="Actualizar Todo", command=self.actualizar_todo_event)
        self.archivo_menu.add_separator()
        self.archivo_menu.add_command(label="Salir", command=self.quit)

        # Add "Herramientas" menu
        self.herramientas_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Herramientas", menu=self.herramientas_menu)
        self.herramientas_menu.add_command(label="Editar Bases", command=self.editar_bases_event)
        
         # Agregar menú Codigos
        self.codigo_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Codigos", menu=self.codigo_menu)
        
        # Agregar comandos para archivos en la carpeta validadores
        self.cargar_codigos()

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
        
        # Crear campos de entrada para cada categoría
        self.entries = {}
        for i, (category, items) in enumerate(self.bases.items()):
            label = customtkinter.CTkLabel(dialog, text=f"{category}:")
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            
            entry = customtkinter.CTkEntry(dialog)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entry.insert(0, ", ".join(items))
            self.entries[category] = entry
        
        # Botón para guardar cambios
        save_button = customtkinter.CTkButton(dialog, text="Guardar", command=self.save_changes)
        save_button.grid(row=len(self.bases), column=0, columnspan=2, pady=10)

        # Crear campos de entrada para agregar una nueva categoría
        self.new_category_name = customtkinter.CTkEntry(dialog, placeholder_text="Nueva categoría")
        self.new_category_name.grid(row=len(self.bases) + 1, column=0, padx=10, pady=5, sticky="ew")
        
        self.new_category_items = customtkinter.CTkEntry(dialog, placeholder_text="Ítems (separados por comas)")
        self.new_category_items.grid(row=len(self.bases) + 1, column=1, padx=10, pady=5, sticky="ew")
        
        # Botón para agregar nueva categoría
        add_button = customtkinter.CTkButton(dialog, text="Agregar Categoría", command=self.add_category)
        add_button.grid(row=len(self.bases) + 2, column=0, columnspan=2, pady=10)

    def save_changes(self):
        # Actualizar el diccionario con los nuevos valores
        for category, entry in self.entries.items():
            new_items = entry.get().split(", ")
            self.bases[category] = new_items
        print("Bases actualizadas:", self.bases)
    
    def add_category(self):
        # Obtener el nombre y los ítems de la nueva categoría
        new_category = self.new_category_name.get().strip()
        new_items = self.new_category_items.get().split(", ")
        
        if new_category and new_items:
            # Agregar la nueva categoría al diccionario
            self.bases[new_category] = new_items
            print(f"Categoría añadida: {new_category} con ítems: {new_items}")
            
            # Limpiar los campos de entrada
            self.new_category_name.delete(0, tk.END)
            self.new_category_items.delete(0, tk.END)
            
            # Volver a mostrar el diálogo con la nueva categoría incluida
            self.editar_bases_event()
            
            # Crear archivo en la carpeta validadores con el nombre de la categoría
            validator_file_path = os.path.join("validadores", f"{new_category}.py")
            with open(validator_file_path, "w") as f:
                f.write("#inserta codigo para crear validador\n")  # crear archivo con muetra de codigo 
            
            # Abrir el archivo en el bloque de notas
            os.startfile(validator_file_path)
        else:
            print("El nombre de la categoría o los ítems no pueden estar vacíos.")

    def update_bases(self, base):
        # Aquí puedes agregar lógica para editar las bases
        new_value = simpledialog.askstring("Editar Bases", f"Editar base {base}:")
        if new_value:
            print(f"Base actualizada: {base} -> {new_value}")
            # Actualiza la base en el diccionario
            # Ejemplo: self.bases[base] = new_value
            self.mostrarBases(base)  # Refresca la vista


    def nuevo_event(self):
        print("Nuevo seleccionado")
        # Agrega la lógica para "Nuevo" aquí



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
                button = customtkinter.CTkButton(tab_frame, text=item, width=200, height=25, corner_radius=10, command=self.ejecutarValidadorEntornos(valor_lower, item))
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

            elif script_path == "comunitario":
                print(f"Inicializando la base de: {base} \n Por favor espere..."  )
                comunitario.setBase(base)
                

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