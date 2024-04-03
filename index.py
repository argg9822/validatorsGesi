import tkinter as tk
import tkinter.font as font
import subprocess
from validadores import institucional, educativo
import sys
from colorama import init, Fore, Style
from PIL import Image, ImageTk

init()

fontTitle = ("Helvetica", 30, "bold")
fontTexts = ("Helvetica", 15)
bgColor = "#001B36"
themeColor = "#F15025"
secondColor = "#000D1C"
neonBlue = "#00FFFF"
neonPink = "#DA00A5"
secondColorRgba =(60, 110, 113, 0.5)
secondColorHex = '#%02x%02x%02x' % secondColorRgba[:3]
fontLetter = "#ffffff"
imgLogo = Image.open("img/logo.png")

# Función para calcular las dimensiones de la ventana
def calcular_dimensiones_ventana(root):
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()
    ancho_ventana = int(ancho_pantalla * 0.72)
    alto_ventana = int(alto_pantalla * 0.75)
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
        bordes = []
        botones = []
        for key, value in bases.items():
            if key == entorno.lower():
                found = True
                for v in value:
                    border_buttons_bases = tk.Frame(marco_botones_bases, bg=neonPink)
                    border_buttons_bases.grid(column=1, row=1, pady=5)
                    bordes.append(border_buttons_bases)
                    
                    btn_bases = tk.Button(border_buttons_bases, text=v,  width="25", height="1", borderwidth=0, highlightbackground="white", bg=bgColor, fg="white", command=ejecutarValidadorEntornos(entorno.lower(), v))                    
                    btn_bases.grid(row=0, column=0, padx=2, pady=2, ipady=5)
                    botones.append(btn_bases)
                    
                for index, borde in enumerate(bordes):
                    row = index // 3
                    col = index % 3
                    padLeft = 30 if index in [0,3,6,9,12] else 30
                    padTop = 25 if index in [0,1,2] else 5
                    borde.grid(row=row, column=col, padx=(padLeft, 5), pady=(padTop, 5))
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
    
    # Marco principal
    marco_principal = tk.Frame(root, padx="0")
    marco_principal.pack(expand=True, fill="both")
    
    # Marco para el menú en la parte izquierda (10% del ancho)
    global marco_menu 
    marco_menu = tk.Frame(marco_principal)
    marco_menu.pack(side="left", fill="y")
    
    # Marco para los botones en la parte derecha (90% del ancho)
    capa_2_botones_entornos = tk.Frame(marco_menu, bg=secondColor, width=root.winfo_width() * 0.4, padx=40)
    capa_2_botones_entornos.pack(side="left", expand=True, fill="y")
    
    marco_botones_entornos = tk.Frame(capa_2_botones_entornos, bg=secondColor)
    marco_botones_entornos.pack(side="bottom", pady=(0, 40))
    
    fontButtonsEntornos = ('Helvetica', 10, 'bold')
    
    # Botones entornos
    entornos = ["Hogar", "Laboral", "Educativo", "Comunitario", "Institucional"]

    for entorno in entornos:
        border_buttons_entornos = tk.Frame(marco_botones_entornos, bg=neonBlue, pady="0")
        border_buttons_entornos.pack(pady="19")

        btn_entorno = tk.Button(border_buttons_entornos, text=entorno,  width="25", height="1", borderwidth=0, relief="solid", bg=secondColor, fg="white", command=mostrarBases(entorno), font=fontButtonsEntornos)
        btn_entorno.pack(pady=1, padx=1, ipady=5)        
        
    logoGesiApp = ImageTk.PhotoImage(imgLogo)
    label_logo = tk.Label(marco_botones_entornos, bg=secondColor, image=logoGesiApp, width=capa_2_botones_entornos.winfo_width() * 0.06)
    label_logo.pack(side="bottom", pady=(20, 0))
    
    # #Contenedor de la parte derecha
    container_right = tk.Frame(marco_principal, width=marco_principal.winfo_width() * 0.6, bg=bgColor)
    container_right.pack(side="right", fill="both", expand=True)
    
    # #Container título
    container_title = tk.Label(container_right, bg=bgColor)
    container_title.pack(pady=(30, 0))
    
    # Título en la parte superior
    title_label = tk.Label(container_title, text="VALIDADOR", font=fontTitle, fg=fontLetter, bg=bgColor)
    title_label.pack()
    
    font_sub_title = ('Helvetica', 16)
    sub_label = tk.Label(container_title, text="GesiApp", font=font_sub_title, fg=neonBlue, bg=bgColor)
    sub_label.pack()

    global marco_botones_bases
    marco_botones_bases = tk.Frame(container_right, bg=secondColor)
    marco_botones_bases.pack(side="top", expand=True, fill="x")
    marco_botones_bases.place(relx=0.05, rely=0.22, relwidth=0.9, relheight=0.41)

    container_init_text = tk.Frame(marco_botones_bases, bg=neonBlue)
    container_init_text.pack(fill="both", expand=True, pady=15, padx=20)
    initial_text = "Por favor seleccione un entorno para continuar"
    preview_message = tk.Label(container_init_text, text=initial_text, fg="white", bg=secondColor, font=fontTexts)
    preview_message.pack(fill="both", expand=True, pady=1, padx=1)
        
    marco_resultado = tk.Frame(container_right, bg=bgColor)
    marco_resultado.pack(side="bottom", expand=True, fill="x")
    marco_resultado.place(relx=0.05, rely=0.65, relwidth=0.9, relheight=0.3)

    texto_terminal = tk.Text(marco_resultado, bg=bgColor, fg="white", borderwidth=0, relief="solid")
    texto_terminal.pack(side="bottom", expand=True, fill="both", pady="5")

    # Llamar a la función imprimirResultado después de configurar los botones
    imprimirResultado(texto_terminal)
    print("\x1b[31m¡Bienvenido!\x1b[0m")

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
            self.text_widget.tag_add('color', 'end - 1c')
            self.text_widget.tag_config('color', foreground="white", background='')

    # Redirigir la salida estándar al widget texto_terminal
    sys.stdout = TerminalRedirect(text_widget)
    sys.stderr = TerminalRedirect(text_widget)

buildGUI()