import tkinter as tk
import customtkinter
import subprocess
from validadores import institucional, educativo, comunitario
import sys
from colorama import init, Fore, Style
from PIL import Image, ImageTk
from __version__ import __version__ as version_actual_actual  # Importa la versión actual desde __version__.py

class App(customtkinter.CTk):
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

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Hogar", command=lambda: self.mostrarBases("Hogar"))
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Laboral", command=lambda: self.mostrarBases("laboral"))
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Educativo", command=lambda: self.mostrarBases("Educativo"))
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        
        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="Comunitario", command=lambda: self.mostrarBases("Comunitario"))
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)
        
        self.sidebar_button_5 = customtkinter.CTkButton(self.sidebar_frame, text="Institucional", command=lambda: self.mostrarBases("Institucional"))
        self.sidebar_button_5.grid(row=5, column=0, padx=20, pady=10)
        
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
        self.herramientas_menu.add_command(label="Actualizar Bases", command=self.actualizar_bases_event)

    def nuevo_event(self):
        print("Nuevo seleccionado")
        # Agrega la lógica para "Nuevo" aquí

    def actualizar_todo_event(self):
        print("Actualizar Todo seleccionado")
        # Agrega la lógica para actualizar todo aquí

    def actualizar_bases_event(self):
        print("Actualizar Bases seleccionado")
        # Aquí puedes actualizar las bases como desees
        # Ejemplo: Puedes agregar un método para recargar las bases o cualquier lógica específica que necesites

        
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

        # Define the bases dictionary
        bases = {
            "hogar": ["csa", "implementacion", "apgar", "sesiones_colectivas", "rqc", "srq"],
            "laboral": ["utis", "nna", "sesiones_colectivas", "oms", "findrisc"],
            "educativo": ["prevencion_embarazo", "autocuidado", "sesiones_colectivas", "higiene_bucal", "higiene_manos", "salud_mental", "mascota_verde", "entornos_escolares", "pretest", "entornos_jardines", "jornadas", "escala_abreviada", "tiendas_escolares"],
            "comunitario": ["sesiones_colectivas", "vinculate", "maps", "cami", "zarit", "pcbh", "caldas", "guardianes", "acondicionamiento", "cuidarte", "mujeres", "fortalecimiento", "pid"],
            "institucional": ["sesiones_colectivas", "ead", "hcb", "mascota_verde", "ipa", "pcb", "persona_mayor", "pci", "tamizajes"]
        }

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
        if valor_lower in bases:
            for item in bases[valor_lower]:
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
        
class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, string):
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)  # Scroll to the end of the textbox

    def flush(self):
        pass

if __name__ == "__main__":
    app = App()
    app.mainloop()