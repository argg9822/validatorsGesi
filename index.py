import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.font as font
import subprocess

fontTitle = ("Helvetica", 30, "bold")
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

def ejecutarValidadorEntornos(script_path):
    def callback():
        subprocess.Popen(["python", script_path])  # Ejecutar el script cuando se hace clic en el botón
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

        found = False
        for key, value in bases.items():
            print("Entró")
            if key == entorno.lower():
                print(f"Match found in category '{key}':")
                print(value)
                found = True
                break
        if not found:
            print("No match found.")
    return callback

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
marco_menu = tk.Frame(marco_principal, bg=secondColor)
marco_menu.pack(side="left", fill="y", pady=(0, 30))

# Marco para los botones en la parte derecha (90% del ancho)
marco_botones = tk.Frame(marco_menu, bg=secondColor, width=root.winfo_width() * 0.3, padx="50", pady="30")
marco_botones.pack(side="left", expand=True, fill="y")

# Botones entornos
entornos = ["Hogar", "Laboral", "Educativo", "Comunitario", "Institucional"]

for entorno in entornos:
    btn_entorno = tk.Button(marco_botones, text=entorno,  width="20", height="3", borderwidth=2, highlightbackground="white", bg=themeColor, fg="white", command=mostrarBases(entorno))
    btn_entorno.pack(pady=20)

root.mainloop()