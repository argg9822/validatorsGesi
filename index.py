import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as font
import subprocess
from validadores import institucional

fontTitle = ("Helvetica", 30, "bold")
fontTexts = ("Helvetica", 15)
principalColor = "#191919"
themeColor = "#F15025"
secondColor = "#36373B"

# Función para calcular las dimensiones de la ventana
def calcular_dimensiones_ventana(root):
    ancho_pantalla = root.winfo_screenwidth()
    alto_pantalla = root.winfo_screenheight()
    ancho_ventana = int(ancho_pantalla * 0.8)
    alto_ventana = int(alto_pantalla * 0.8)
    x = (ancho_pantalla - ancho_ventana) // 2
    y = (alto_pantalla - alto_ventana) // 2
    root.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

def ajustar_ancho_menu(event):
    ancho_marco_menu = int(event.width * 0.3)  # 10% del ancho de la ventana
    marco_menu.config(width=ancho_marco_menu)

def ejecutarValidadorEntornos(script_path, base):
    def callback():
        subprocess.Popen(["python", 'validadores/'+script_path+'.py', base])  # Ejecutar el script cuando se hace clic en el botón
        institucional.setBase(base)
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

        #Vaciar contenedor
        for element in marco_botones_bases.winfo_children():
            element.destroy()

        found = False
        botones = []
        for key, value in bases.items():
            if key == entorno.lower():
                found = True
                for v in value:
                    btn_bases = tk.Button(marco_botones_bases, text=v,  width="20", height="2", borderwidth=2, highlightbackground="white", bg=themeColor, fg="white", command=ejecutarValidadorEntornos(entorno.lower(), v))
                    botones.append(btn_bases)

                for index, boton in enumerate(botones):
                    row = index // 5
                    col = index % 5
                    boton.grid(row=row, column=col, padx="5", pady=5, ipadx="2")
                break
        if not found:
            print("No match found.")
    return callback

def buildGUI ():    
    # Crear la interfaz gráfica
    root = tk.Tk()
    root.title("Validador GesiApp")

    # Calcular las dimensiones de la ventana
    calcular_dimensiones_ventana(root)

    # Título en la parte superior
    titulo_label = tk.Label(root, text="Validador GesiApp", font=fontTitle, bg=principalColor, fg=themeColor, pady="20")
    titulo_label.pack(side="top", fill="x")

    # Marco principal
    marco_principal = tk.Frame(root, bg=principalColor, padx="10")
    marco_principal.pack(expand=True, fill="both")

    # Marco para el menú en la parte izquierda (10% del ancho)
    global marco_menu 
    marco_menu = tk.Frame(marco_principal, bg=secondColor)
    marco_menu.pack(side="left", fill="y", pady=(0, 30))

    # Marco para los botones en la parte derecha (90% del ancho)
    marco_botones_entornos = tk.Frame(marco_menu, bg=secondColor, width=root.winfo_width() * 0.3, padx="50", pady="30")
    marco_botones_entornos.pack(side="left", expand=True, fill="y")

    altura_marco_btnBases = int(marco_principal.winfo_height() * 0.20)
    global marco_botones_bases
    marco_botones_bases = tk.Frame(marco_principal, bg=secondColor, pady="20", padx="10", height=altura_marco_btnBases)
    marco_botones_bases.pack(side="right",expand=True, fill="x")
    marco_botones_bases.place(relx=0.6, rely=0, relwidth=0.7, relheight=0.5, anchor="n")

    preview_message = tk.Message(marco_botones_bases, text="Por favor seleccione un entorno", fg="white", bg=secondColor, font=fontTexts, borderwidth=2, relief="solid", highlightbackground=themeColor)
    preview_message.pack(fill="both", expand=True, anchor="center", padx="20", pady="20")

    marco_resultado = tk.Frame(marco_principal, bg=secondColor, pady="20")
    marco_resultado.pack(side="bottom",expand=True, fill="x")

    # Botones entornos
    entornos = ["Hogar", "Laboral", "Educativo", "Comunitario", "Institucional"]

    for entorno in entornos:
        btn_entorno = tk.Button(marco_botones_entornos, text=entorno,  width="20", height="3", borderwidth=2, highlightbackground="white", bg=themeColor, fg="white", command=mostrarBases(entorno))
        btn_entorno.pack(pady=20)

    root.mainloop()
    
buildGUI()