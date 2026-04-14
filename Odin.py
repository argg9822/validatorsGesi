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

# ── Constantes ────────────────────────────────────────────────────────────────
APP_NAME    = "Odin"
VERSION     = "1.0.1"  # Versión del Lanzador (rara vez cambiará)
AUTHORS     = "Gabriel Monhabell - Aramis Garcia"
COPYRIGHT   = f"© 2024 {AUTHORS}"
TRANSPARENT = "#00c7fc"  # Color para croma de transparencia

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
    """
    Importa y ejecuta el archivo index.py ubicado en la carpeta del programa.
    Inyecta librerías críticas para evitar errores de importación en el .exe
    """
    import tkinter as tk
    from tkinter import messagebox, filedialog
    
    index_path = os.path.join(BASE_DIR, "index.py")

    if not os.path.exists(index_path):
        messagebox.showerror("Error Crítico", 
            f"No se encontró el archivo de lógica:\n{index_path}\n\nReinstala la aplicación.")
        sys.exit(1)

    try:
        # 1. Asegurar que el directorio base esté en el path
        if BASE_DIR not in sys.path:
            sys.path.insert(0, BASE_DIR)

        # 2. Configurar la carga dinámica del módulo
        spec = importlib.util.spec_from_file_location("index", index_path)
        index_module = importlib.util.module_from_spec(spec)
        
        # 3. TRUCO DE PRODUCCIÓN: Inyectar librerías ya cargadas por el .exe
        # Esto evita el error "cannot import name 'filedialog' from 'tkinter'"
        sys.modules["tkinter.filedialog"] = filedialog
        sys.modules["tkinter.messagebox"] = messagebox

        # 4. Cargar y ejecutar el código de index.py
        spec.loader.exec_module(index_module)

        # 5. Ejecutar punto de entrada si existe
        if hasattr(index_module, 'index_open'):
            index_module.index_open()
        
    except Exception as e:
        import traceback
        error_info = traceback.format_exc()
        
        # Guardar log de error detallado
        log_path = os.path.join(BASE_DIR, "error_log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.datetime.now()}] ERROR DE CARGA DINÁMICA:\n{error_info}\n")
            
        messagebox.showerror("Error en Aplicación", 
            f"No se pudo iniciar la lógica actualizada:\n{e}\n\nRevisa error_log.txt")

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
    main()