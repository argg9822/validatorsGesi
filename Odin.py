"""
Odin.py  –  Punto de entrada de ValidatorsGesi
Muestra un splash screen moderno y luego abre la aplicación principal (index.py).
La lógica de actualización fue movida a index.py.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# ── Constantes ────────────────────────────────────────────────────────────────
APP_NAME    = "Odin"
VERSION     = "0.0.0.4"
AUTHORS     = "Gabriel Monhabell - Aramis Garcia"
COPYRIGHT   = f"© 2024 {AUTHORS}"
TRANSPARENT = "#00c7fc"          # color transparente para el splash

# ── Rutas de recursos ─────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _find(filename: str) -> str | None:
    """Busca un archivo en varias rutas posibles."""
    candidates = [
        os.path.join(BASE_DIR, "img", filename),
        os.path.join(os.path.dirname(sys.executable), "img", filename),
        os.path.join("img", filename),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


# ═══════════════════════════════════════════════════════════════════════════════
#  Splash Screen
# ═══════════════════════════════════════════════════════════════════════════════
class SplashScreen:
    WIDTH  = 500
    HEIGHT = 500
    DURATION_MS = 3000          # tiempo total del splash en ms

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Iniciando...")
        self.root.overrideredirect(True)          # sin bordes de ventana
        self.root.attributes("-transparentcolor", TRANSPARENT)
        self.root.configure(bg=TRANSPARENT)
        self._center()
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        W, H = self.WIDTH, self.HEIGHT

        self.canvas = tk.Canvas(
            self.root,
            width=W, height=H,
            bg=TRANSPARENT, highlightthickness=0
        )
        self.canvas.pack()

        # Fondo redondeado oscuro
        self._draw_rounded_rect(10, 10, W - 10, H - 10,
                                radius=24, fill="#0D1117", outline="#30363D", width=1)

        # Imagen central (intro.png)
        self._load_intro_image(W, H)

        # Línea divisoria sutil
        self.canvas.create_line(60, H - 72, W - 60, H - 72,
                                fill="#30363D", width=1)

        # Texto de versión y copyright
        self.canvas.create_text(
            W // 2, H - 52,
            text=f"{APP_NAME}  v{VERSION}",
            fill="#00CFFF",
            font=("Consolas", 11, "bold")
        )
        self.canvas.create_text(
            W // 2, H - 32,
            text=COPYRIGHT,
            fill="#8B949E",
            font=("Helvetica", 8)
        )
        
        # Barra de progreso (track gris + barra cyan animada)
        bar_w = 380
        bar_h = 3
        bar_x = (W - bar_w) // 2
        bar_y = H - 14

        self.canvas.create_rectangle(        # track
            bar_x, bar_y,
            bar_x + bar_w, bar_y + bar_h,
            fill="#21262D", outline=""
        )
        self.progress_bar = self.canvas.create_rectangle(  # barra
            bar_x, bar_y,
            bar_x, bar_y + bar_h,
            fill="#00CFFF", outline=""
        )
        self._bar_x   = bar_x
        self._bar_w   = bar_w
        self._bar_y   = bar_y
        self._bar_h   = bar_h

    def _load_intro_image(self, W: int, H: int):
        path = _find("intro.png")
        if path:
            try:
                img = Image.open(path).convert("RGBA")
                # Escalar manteniendo proporción, máximo 340×340
                img.thumbnail((340, 340), Image.LANCZOS)
                self._img_ref = ImageTk.PhotoImage(img)
                self.canvas.create_image(W // 2, H // 2 - 30,
                                         image=self._img_ref)
                return
            except Exception as e:
                print(f"[Splash] No se pudo cargar intro.png: {e}")

        # Fallback: texto grande si no hay imagen
        self.canvas.create_text(
            W // 2, H // 2 - 30,
            text="⚙️",
            fill="#00CFFF",
            font=("Helvetica", 72)
        )
        self.canvas.create_text(
            W // 2, H // 2 + 60,
            text="VALIDADOR\nGesiApp",
            fill="#E6EDF3",
            font=("Helvetica", 22, "bold"),
            justify="center"
        )

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius=20, **kwargs):
        """Dibuja un rectángulo con esquinas redondeadas en el canvas."""
        pts = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        self.canvas.create_polygon(pts, smooth=True, **kwargs)

    def _center(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - self.WIDTH)  // 2
        y = (sh - self.HEIGHT) // 2
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

    # ── Animación de progreso ─────────────────────────────────────────────────
    def _update_progress(self, fraction: float):
        """Actualiza el ancho de la barra (fraction 0.0 → 1.0)."""
        new_x2 = self._bar_x + int(self._bar_w * fraction)
        self.canvas.coords(
            self.progress_bar,
            self._bar_x, self._bar_y,
            new_x2,      self._bar_y + self._bar_h
        )
        self.canvas.update_idletasks()

    def _run_progress(self, steps: int = 60):
        """Programa los 'steps' frames de animación durante DURATION_MS."""
        interval = self.DURATION_MS // steps
        for i in range(1, steps + 1):
            frac = i / steps
            self.root.after(i * interval,
                            lambda f=frac: self._update_progress(f))
        # Al terminar, abre la ventana principal
        self.root.after(self.DURATION_MS + 50, self._launch)

    def _launch(self):
        """Cierra el splash y abre index.py."""
        self.root.destroy()
        _open_main()

    # ── Punto de entrada ──────────────────────────────────────────────────────
    def run(self):
        self._run_progress()
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════════════════════
#  Abrir ventana principal
# ═══════════════════════════════════════════════════════════════════════════════
def _open_main():
    try:
        # En el .exe, index ya está empaquetado como módulo
        import index
        # Si index tiene una función de inicio (ej. principal()), llámala:
        if hasattr(index, 'index_open'):
            index.index_open()
        else:
            # Si index.py ejecuta todo al ser importado, no necesitas hacer más.
            pass
    except Exception as e:
        # Fallback para desarrollo (cuando corres Odin.py suelto)
        try:
            import subprocess
            subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "index.py")])
        except Exception as e2:
            import traceback
            error_msg = f"No se pudo iniciar el módulo principal:\n{e}\n{traceback.format_exc()}"
            messagebox.showerror("Error", error_msg)


def _set_icon(window: tk.Tk):
    path = _find("logo.ico")
    if path:
        try:
            window.wm_iconbitmap(path)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    try:
        splash = SplashScreen()
        splash.run()
    except Exception as e:
        import traceback
        with open(os.path.join(BASE_DIR, "error_log.txt"), "w") as f:
            f.write(f"Error: {e}\n")
            f.write(traceback.format_exc())
        messagebox.showerror("Error de inicio",
                             f"Ocurrió un error al iniciar la aplicación:\n{e}")


if __name__ == "__main__":
    main()