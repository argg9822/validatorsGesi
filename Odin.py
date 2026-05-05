"""
Odin.py – Lanzador Estático de ValidatorsGesi
Misión: Mostrar Splash Screen y cargar la lógica externa (index.py).
Este archivo NO se reemplaza durante las actualizaciones.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import importlib.util
import datetime
import requests
import customtkinter as ctk

# ── Constantes ────────────────────────────────────────────────────────────────
APP_NAME    = "Odin"
VERSION     = "1.0.1"  # Versión del Lanzador (rara vez cambiará)
AUTHORS     = "Gabriel Monhabell - Aramis Garcia"
COPYRIGHT   = f"© 2024 {AUTHORS}"
TRANSPARENT = "#00c7fc"  # Color para croma de transparencia

COLORS = {
    # Fondo principal: Negro profundo inspirado en la interfaz
    "bg_dark":       ("#F5F5F5", "#080808"), 
    
    # Tarjetas: Un gris muy oscuro para resaltar sobre el fondo
    "bg_card":       ("#FFFFFF", "#121212"), 
    
    # Inputs: Gris oscuro con borde sutil
    "bg_input":      ("#F0F0F0", "#1A1A1A"), 
    
    # Acento Principal: El Rojo Trakio (el color del logo y texto)
    "accent":        ("#E63946", "#FF4D4D"), 
    "accent_hover":  ("#D62839", "#FF6666"), 
    
    # Acento Secundario: Un rojo vino/oscuro (como el resplandor del logo)
    "accent2":       ("#9B1B1B", "#7A0000"), 
    "accent2_hover": ("#B22222", "#A30000"), 
    
    # Peligro y Alerta (mantenidos en la gama de rojos/naranjas)
    "danger":        ("#D00000", "#FF0000"), 
    "warning":       ("#FFBA08", "#FAA300"), 
    
    # Textos: Blanco puro y gris plateado para legibilidad
    "text_primary":  ("#1A1A1A", "#FFFFFF"), 
    "text_muted":    ("#666666", "#A0A0A0"), 
    
    # Bordes: Sutiles, inspirados en las líneas de red del fondo
    "border":        ("#DDDDDD", "#2A0B0B"), 
}
ctk.set_appearance_mode("system")



# ── Gestión de Rutas Dinámicas ────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    # Si es un .exe, la raíz es donde está el ejecutable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si es un .py, la raíz es la carpeta del script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _find(filename: str) -> str | None:
    """Busca recursos en la carpeta img relativa a la base del programa."""
    path = os.path.join(BASE_DIR, "img", filename)
    if os.path.exists(path):
        return path
    return None

# ═══════════════════════════════════════════════════════════════════════════════
#  Splash Screen
# ═══════════════════════════════════════════════════════════════════════════════
class SplashScreen:
    WIDTH  = 500
    HEIGHT = 500
    DURATION_MS = 3000

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Iniciando Odin...")
        self.root.overrideredirect(True)
        self.root.attributes("-transparentcolor", TRANSPARENT)
        self.root.configure(bg=TRANSPARENT)
        self._center()
        self._set_icon()
        self._build()

    def _set_icon(self):
        path = _find("logo.ico")
        if path:
            try: self.root.iconbitmap(path)
            except: pass

    def _center(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - self.WIDTH) // 2
        y = (sh - self.HEIGHT) // 2
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius=20, **kwargs):
        pts = [x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y1+radius, x1, y1]
        self.canvas.create_polygon(pts, smooth=True, **kwargs)

    def _build(self):
        W, H = self.WIDTH, self.HEIGHT
        self.canvas = tk.Canvas(self.root, width=W, height=H, bg=TRANSPARENT, highlightthickness=0)
        self.canvas.pack()

        # Fondo oscuro estilo GitHub/SaaS Premium
        self._draw_rounded_rect(10, 10, W-10, H-10, radius=24, fill="#0D1117", outline="#30363D", width=1)

        # Imagen central
        path_intro = _find("intro.png")
        if path_intro:
            try:
                img = Image.open(path_intro).convert("RGBA")
                img.thumbnail((340, 340), Image.LANCZOS)
                self._img_ref = ImageTk.PhotoImage(img)
                self.canvas.create_image(W // 2, H // 2 - 30, image=self._img_ref)
            except:
                self.canvas.create_text(W//2, H//2-30, text="⚙️", fill="#00CFFF", font=("Helvetica", 72))
        
        # Textos informativos
        self.canvas.create_line(60, H-72, W-60, H-72, fill="#30363D", width=1)
        self.canvas.create_text(W//2, H-52, text=f"{APP_NAME} v{VERSION}", fill="#00CFFF", font=("Consolas", 11, "bold"))
        self.canvas.create_text(W//2, H-32, text=COPYRIGHT, fill="#8B949E", font=("Helvetica", 8))

        # Barra de progreso
        bar_w, bar_h = 380, 3
        bar_x, bar_y = (W - bar_w) // 2, H - 14
        self.canvas.create_rectangle(bar_x, bar_y, bar_x+bar_w, bar_y+bar_h, fill="#21262D", outline="")
        self.progress_bar = self.canvas.create_rectangle(bar_x, bar_y, bar_x, bar_y+bar_h, fill="#00CFFF", outline="")
        
        self._bar_data = (bar_x, bar_y, bar_w, bar_h)

    def _update_progress(self, frac):
        x, y, w, h = self._bar_data
        self.canvas.coords(self.progress_bar, x, y, x + int(w * frac), y + h)
        self.canvas.update_idletasks()

    def _run_animation(self):
        steps = 50
        interval = self.DURATION_MS // steps
        for i in range(1, steps + 1):
            self.root.after(i * interval, lambda f=i/steps: self._update_progress(f))
        self.root.after(self.DURATION_MS + 100, self._launch)

    def _launch(self):
        self.root.destroy()
        _open_main_logic()

    def run(self):
        self._run_animation()
        self.root.mainloop()

# ═══════════════════════════════════════════════════════════════════════════════
#  Carga Dinámica de Lógica (El "Cerebro" Externo)
# ═══════════════════════════════════════════════════════════════════════════════
def _open_main_logic():
    import tkinter as tk
    from tkinter import messagebox, filedialog
    import importlib.util
    import sys
    import os
    import datetime

    index_path = os.path.join(BASE_DIR, "index.py")

    if not os.path.exists(index_path):
        messagebox.showerror("Error Crítico", f"No se encontró: {index_path}")
        sys.exit(1)

    try:
        # 1. Asegurar que la carpeta base sea visible para los archivos locales
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)
        
        # Cambiar el directorio de trabajo a la base para evitar errores de rutas relativas
        os.chdir(BASE_DIR)

        # --- INYECCIÓN DE DEPENDENCIAS CRÍTICAS ---
        # Lista Maestra de librerías empaquetadas en el .exe
        librerias = [
            'setuptools', 'requests', 'customtkinter', 'openpyxl', 
            'selenium', 'webdriver_manager', 'PIL', 'pandas', 'numpy', 
            'flask', 'Updater'
        ]
        
        for lib in librerias:
            try:
                # Importamos el módulo base desde el interior del .exe
                modulo = __import__(lib)
                sys.modules[lib] = modulo
                
                # --- CASOS ESPECIALES (Submódulos que PyInstaller oculta) ---
                
                if lib == 'selenium':
                    import selenium.webdriver
                    import selenium.webdriver.common.by
                    import selenium.webdriver.support.ui
                    import selenium.webdriver.support.expected_conditions
                    sys.modules['selenium.webdriver'] = selenium.webdriver
                    sys.modules['selenium.webdriver.common.by'] = selenium.webdriver.common.by
                    sys.modules['selenium.webdriver.support.ui'] = selenium.webdriver.support.ui
                    sys.modules['selenium.webdriver.support.expected_conditions'] = selenium.webdriver.support.expected_conditions
                
                if lib == 'webdriver_manager':
                    import webdriver_manager.chrome
                    sys.modules['webdriver_manager.chrome'] = webdriver_manager.chrome
                
                if lib == 'PIL':
                    from PIL import Image, ImageTk
                    sys.modules['PIL.Image'] = Image
                    sys.modules['PIL.ImageTk'] = ImageTk

            except ImportError:
                # Si una librería no está instalada en tu entorno de desarrollo al compilar, saltará aquí
                pass

        # Inyecciones específicas para componentes de Tkinter (vital para diálogos de archivos)
        sys.modules["tkinter.filedialog"] = filedialog
        sys.modules["tkinter.messagebox"] = messagebox

        # --- CARGA DEL CEREBRO (index.py) ---
        spec = importlib.util.spec_from_file_location("index", index_path)
        index_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(index_module)

        # Ejecutamos la función de inicio de tu interfaz
        if hasattr(index_module, 'index_open'):
            index_module.index_open()
        
    except Exception as e:
        import traceback
        log_path = os.path.join(BASE_DIR, "error_log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.datetime.now()}] ERROR CRÍTICO AL INICIAR:\n{traceback.format_exc()}\n")
        messagebox.showerror("Error de Aplicación", f"Error al iniciar: {e}\n\nRevisa error_log.txt")
        
        
        
API_URL = "https://www.trakio.pro/api/v1/validate-license"
PROGRAMA_ID = "ODIN" 

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

def verificar_licencia():
    # --- Configuración de rutas ---
    ruta_dir = os.path.join(os.environ['APPDATA'], "ODIN_DATA")
    if not os.path.exists(ruta_dir):
        os.makedirs(ruta_dir)
    archivo_licencia = os.path.join(ruta_dir, "license.key")

    codigo_local = None
    if os.path.exists(archivo_licencia):
        with open(archivo_licencia, "r") as f:
            codigo_local = f.read().strip()

    # --- INPUT CON DISEÑO CTK ---
    if not codigo_local:
        # Usamos el diálogo nativo de CTK para que combine con el tema
        dialogo = ctk.CTkInputDialog(
            text="Ingresa tu código de activación:", 
            title="Activación PAIWEB",
            fg_color=COLORS["bg_card"][1],
            button_fg_color=COLORS["accent"][1],
            button_hover_color=COLORS["accent_hover"][1]
        )
        codigo_local = dialogo.get_input()
        if not codigo_local: sys.exit()

    # --- VENTANA DE CARGA (DISEÑO MEJORADO) ---
    espera = ctk.CTkToplevel()
    espera.title("Paiweb")
    
    # Dimensiones y centrado
    ancho_v, alto_v = 340, 160
    x = int((espera.winfo_screenwidth() / 2) - (ancho_v / 2))
    y = int((espera.winfo_screenheight() / 2) - (alto_v / 2))
    
    espera.geometry(f"{ancho_v}x{alto_v}+{x}+{y}")
    espera.resizable(False, False)
    espera.attributes("-topmost", True)
    espera.configure(fg_color=COLORS["bg_dark"])

    # Contenedor principal para padding interno
    frame_interno = ctk.CTkFrame(espera, fg_color="transparent")
    frame_interno.pack(expand=True, fill="both", padx=20, pady=20)

    # Texto de estado
    lbl_status = ctk.CTkLabel(
        frame_interno, 
        text="VERIFICANDO LICENCIA", 
        font=("Segoe UI", 13, "bold"),
        text_color=COLORS["accent"]
    )
    lbl_status.pack(pady=(0, 10))

    # Barra de progreso estilizada
    progreso = ctk.CTkProgressBar(
        frame_interno, 
        orientation="horizontal",
        mode="indeterminate",
        width=260,
        progress_color=COLORS["accent"],
        fg_color=COLORS["bg_input"]
    )
    progreso.pack(pady=10)
    progreso.start()

    # Subtexto informativo
    ctk.CTkLabel(
        frame_interno, 
        text="Conectando con el servidor seguro...", 
        font=("Segoe UI", 10),
        text_color=COLORS["text_muted"]
    ).pack()

    espera.update() 

    try:
        payload = {"key": codigo_local, "program": PROGRAMA_ID}
        response = requests.post(API_URL, json=payload, timeout=8, allow_redirects=False)
        
        try:
            data = response.json()
        except:
            data = {}

        if response.status_code == 200 and data.get('status') == 'success':
            with open(archivo_licencia, "w") as f:
                f.write(codigo_local)
            espera.destroy()
            return True
        else:
            espera.destroy()
            mensaje = data.get('message', f'Código inválido o vencido (Error: {response.status_code})')
            messagebox.showerror("Licencia Inválida", mensaje)
            if os.path.exists(archivo_licencia): 
                os.remove(archivo_licencia)
            sys.exit()

    except requests.exceptions.RequestException:
        espera.destroy()
        # Si ya había una llave, dejamos pasar (Modo Offline)
        if os.path.exists(archivo_licencia):
            return True 
        
        messagebox.showerror("Error de Conexión", "Se requiere internet para la primera activación.")
        sys.exit()
        
        
# ═══════════════════════════════════════════════════════════════════════════════
#  Ejecución
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    try:
        app = SplashScreen()
        app.run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Error al iniciar el lanzador: {e}")

if __name__ == "__main__":
    if verificar_licencia():
        main()
    
