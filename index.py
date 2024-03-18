import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as font
import subprocess
from validadores import institucional, educativo
import sys
from colorama import init, Fore, Style

init()

fontTitle = ("Helvetica", 30, "bold")
fontTexts = ("Helvetica", 15)
principalColor = "#041857"
bgColor = "#020C2A"
themeColor = "#F15025"
secondColor = "#647095"
secondColorRgba =(60, 110, 113, 0.5)
secondColorHex = '#%02x%02x%02x' % secondColorRgba[:3]
fontLetter = "#ffffff"

# Función para calcular las dimensiones de la ventana
def calcular_dimensiones_ventana(root):
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()
    ancho_ventana = int(ancho_pantalla * 0.6)
    alto_ventana = int(alto_pantalla * 0.6)
    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2
    root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

def ajustar_ancho_menu(event):
    ancho_marco_menu = int(event.width * 0.3)  # 10% del ancho de la ventana
    marco_menu.config(width=ancho_marco_menu)

def ejecutarValidadorEntornos(script_path, base):
    def callback():
        subprocess.Popen(["python", 'validadores/'+script_path+'.py', base])  # Ejecutar el script cuando se hace clic en el botón
        if script_path == "institucional":
            institucional.setBase(base)
        elif script_path == "educativo":
            educativo.setBase(base)
            
    return callback

def mostrarBases(entorno):
    def callback():
        bases = {
            "hogar": ["csa", "implementacion", "apgar", "sesiones_colectivas", "rqc", "srq"],
            "laboral": ["utis", "nna", "sesiones_colectivas", "oms", "findrisc"],
            "educativo": ["prevencion_embarazo", "autocuidado", "sesiones_colectivas", "higiene_bucal", "higiene_manos", "salud_mental", "mascota_verde", "entornos_escolares", "pretest", "entornos_jardines", "jornadas", "escala_abreviada", "tiendas_escolares"],
            "comunitario": ["sesiones_colectivas", "vinculate", "maps", "cami", "zarit", "pcbh", "caldas", "guardianes", "acondicionamiento", "cuidarte", "mujeres", "fortalecimiento", "pid"],
            "institucional": ["sesiones_colectivas", "ead", "hcb", "mascota_verde", "ipa", "pcb", "persona_mayor", "pci", "tamizajes"]
        }
        print("\x1b[31mEntorno seleccionado:\x1b[0m " + entorno)
        #Vaciar contenedor
        for element in marco_botones_bases.winfo_children():
            element.destroy()

        found = False
        botones = []
        for key, value in bases.items():
            if key == entorno.lower():
                found = True
                for v in value:
                    btn_bases = tk.Button(marco_botones_bases, text=v,  width="20", height="2", borderwidth=2, highlightbackground="white", bg=bgColor, fg="white", command=ejecutarValidadorEntornos(entorno.lower(), v))
                    botones.append(btn_bases)

                for index, boton in enumerate(botones):
                    row = index // 5
                    col = index % 5
                    boton.grid(row=row, column=col, padx="5", pady=5, ipadx="2")
                break
        if not found:
            print("No match found.")
    return callback

def buildGUI():    
    # Crear la interfaz gráfica
    root = tk.Tk()
    root.title("Validador GesiApp")

    # Calcular las dimensiones de la ventana
    calcular_dimensiones_ventana(root)

    # Título en la parte superior
    titulo_label = tk.Label(root, text="Validador GesiApp", font=fontTitle, bg=bgColor, fg=fontLetter, pady="20")
    titulo_label.pack(side="top", fill="x")

    # Marco principal
    marco_principal = tk.Frame(root, bg=bgColor, padx="0")
    marco_principal.pack(expand=True, fill="both")

    # Marco para el menú en la parte izquierda (10% del ancho)
    global marco_menu 
    marco_menu = tk.Frame(marco_principal, bg=bgColor)
    marco_menu.pack(side="left", fill="y", pady=(0, 30))

    # Marco para los botones en la parte derecha (90% del ancho)
    marco_botones_entornos = tk.Frame(marco_menu, bg=secondColor, width=root.winfo_width() * 0.3, padx="30", pady="10")
    marco_botones_entornos.pack(side="left", expand=True, fill="y")

    altura_marco_btnBases = int(marco_principal.winfo_height() * 0.20)
    global marco_botones_bases
    marco_botones_bases = tk.Frame(marco_principal, bg=secondColor, pady="10", padx="10", height=altura_marco_btnBases)
    marco_botones_bases.pack(side="right", expand=True, fill="x")
    marco_botones_bases.place(relx=0.6, rely=0, relwidth=0.82, relheight=0.3, anchor="n")

    preview_message = tk.Message(marco_botones_bases, text="Por favor seleccione un entorno", fg="white", bg=secondColor, font=fontTexts, borderwidth=2, relief="solid", highlightbackground=themeColor)
    preview_message.pack(fill="both", expand=True, anchor="center", padx="20", pady="20")

    marco_resultado = tk.Frame(marco_principal, bg=secondColor, pady="0")
    marco_resultado.pack(side="bottom", expand=True, fill="x")
    marco_resultado.place(relx=0.6, rely=1, relwidth=0.82, relheight=0.7, anchor="s")

    texto_terminal = tk.Text(marco_resultado, bg="#002657", fg="white")
    texto_terminal.pack(side="bottom", expand=True, fill="both")

    # Botones entornos
    entornos = ["Hogar", "Laboral", "Educativo", "Comunitario", "Institucional"]

    for entorno in entornos:
        btn_entorno = tk.Button(marco_botones_entornos, text=entorno,  width="20", height="3", borderwidth=2, highlightbackground="white", bg=bgColor, fg="white", command=mostrarBases(entorno))
        btn_entorno.pack(pady=20)

    # Llamar a la función imprimirResultado después de configurar los botones
    imprimirResultado(texto_terminal)
    print("\x1b[31m!Bienvenido¡\x1b[0m")

    root.mainloop()

def imprimirResultado(text_widget):
    class TerminalRedirect:
        def __init__(self, text_widget):
            self.text_widget = text_widget

        def write(self, message):
            start_index = 0
            while True:
                color_start = message.find('\x1b[', start_index)
                if color_start == -1:
                    self.text_widget.insert(tk.END, message[start_index:])
                    break
                else:
                    self.text_widget.insert(tk.END, message[start_index:color_start])
                    color_end = message.find('m', color_start)
                    if color_end != -1:
                        color_code = message[color_start + 2:color_end].strip()
                        if color_code.isdigit():  # Verificar si es un número
                            self.apply_color(color_code)
                    start_index = color_end + 1

            self.text_widget.see(tk.END)  # Desplazar hacia abajo para mostrar el texto más reciente

        def apply_color(self, color_code):
            color_map = {
                '31': 'red', '32': 'green', '33': 'yellow',
                '34': 'blue', '35': 'magenta', '36': 'cyan', '37': 'white'
            }
            color = color_map.get(color_code, 'black')
            self.text_widget.tag_add('color', 'end - 1c')
            self.text_widget.tag_config('color', foreground=color)

    # Redirigir la salida estándar al widget texto_terminal
    sys.stdout = TerminalRedirect(text_widget)
    sys.stderr = TerminalRedirect(text_widget)

buildGUI()