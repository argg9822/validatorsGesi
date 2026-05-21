"""
Odin.py – Lanzador Estático de ValidatorsGesi
Splash Screen estilo Minimalista V3 – barra lateral azul, tipografía grande.
Este archivo NO se reemplaza durante las actualizaciones.
"""

import os
import sys
import math
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import requests
import customtkinter as ctk
import index
import __version__

DATOS_LICENCIA = {}

APP_NAME  = "Odin"
VERSION   = __version__.__version__.split('.')
VERSION   = '.'.join(VERSION)
AUTHORS   = "Gabriel Monhabell  ·  Aramis Garcia"
COPYRIGHT = "© 2024 Trakio"
TRANSPARENT = "#00c7fc"

# ── Paleta azul cobalto ────────────────────────────────────────────────────────
S = {
    "bg":            "#030e1d",
    "bg2":           "#04101f",
    "bg3":           "#061828",
    "border_dark":   "#071d38",
    "border_mid":    "#0C2D4A",
    "border_accent": "#185FA5",
    "accent":        "#378ADD",
    "accent_dim":    "#0C447C",
    "accent_deep":   "#042C53",
    "accent_bright": "#85B7EB",
    "accent_light":  "#B5D4F4",
    "white":         "#E6F1FB",
    "muted":         "#185FA5",
    "dim":           "#071d38",
}

COLORS = {
    "bg_dark":      ("#F5F5F5", "#030e1d"),
    "bg_card":      ("#FFFFFF", "#04101f"),
    "bg_input":     ("#F0F0F0", "#061828"),
    "accent":       ("#185FA5", "#378ADD"),
    "accent_hover": ("#0C447C", "#185FA5"),
    "text_primary": ("#1A1A1A", "#E6F1FB"),
    "text_muted":   ("#666666", "#185FA5"),
    "border":       ("#DDDDDD", "#0C2D4A"),
}

ctk.set_appearance_mode("system")

def resource_path(rel):
    try:    base = sys._MEIPASS
    except: base = os.path.abspath(".")
    return os.path.join(base, rel)

BASE_DIR = (os.path.dirname(sys.executable)
            if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.abspath(__file__)))

def _find(filename):
    p = resource_path(os.path.join("img", filename))
    return p if os.path.exists(p) else None


class SplashScreen:
    W  = 680
    H  = 400
    R  = 14
    MS = 3200

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Odin")
        self.root.overrideredirect(True)
        self.root.attributes("-transparentcolor", TRANSPARENT)
        self.root.configure(bg=TRANSPARENT)
        self._center()
        self._set_icon()
        self._build()

    def _set_icon(self):
        p = _find("logo.ico")
        if p:
            try: self.root.iconbitmap(p)
            except: pass

    def _center(self):
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}")

    def _hex_rgb(self, h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def _interp(self, c1, c2, t):
        r1, g1, b1 = self._hex_rgb(c1)
        r2, g2, b2 = self._hex_rgb(c2)
        return (int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

    def _round_rect(self, x1, y1, x2, y2, r=12, **kw):
        pts = [x1+r, y1,  x2-r, y1,  x2, y1,  x2, y1+r,
               x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
               x1, y2,   x1, y2-r, x1, y1+r, x1, y1]
        self.c.create_polygon(pts, smooth=True, **kw)

    def _grad_v(self, x, y, w, h, c1, c2):
        r1, g1, b1 = self._hex_rgb(c1)
        r2, g2, b2 = self._hex_rgb(c2)
        for j in range(h):
            t = j / max(h-1, 1)
            col = f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"
            self.c.create_rectangle(x, y+j, x+w, y+j+1, fill=col, outline="")

    def _grad_h(self, x, y, w, h, c1, c2):
        r1, g1, b1 = self._hex_rgb(c1)
        r2, g2, b2 = self._hex_rgb(c2)
        for i in range(w):
            t = i / max(w-1, 1)
            col = f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"
            self.c.create_rectangle(x+i, y, x+i+1, y+h, fill=col, outline="")

    def _build(self):
        W, H = self.W, self.H
        self.c = tk.Canvas(self.root, width=W, height=H,
                           bg=TRANSPARENT, highlightthickness=0)
        self.c.pack()
        self._draw_background(W, H)
        self._draw_left_bar(W, H)
        self._draw_top_labels(W, H)
        self._draw_main_title(W, H)
        self._draw_module_cards(W, H)
        self._draw_bottom_bar(W, H)
        self._draw_decorations(W, H)

    # ── Fondo principal ────────────────────────────────────────────────────────
    def _draw_background(self, W, H):
        # Sombra exterior
        self._round_rect(6, 6, W-6, H-6, r=self.R+2,
                         fill="#010810", outline="")
        # Marco principal
        self._round_rect(3, 3, W-3, H-3, r=self.R,
                         fill=S["bg"], outline=S["border_mid"], width=1)
        # Línea horizontal superior sutil
        self.c.create_line(4, 68, W-4, 68, fill=S["border_dark"], width=1)
        # Línea horizontal inferior
        self.c.create_line(4, H-46, W-4, H-46, fill=S["border_dark"], width=1)

    # ── Barra vertical izquierda animada ───────────────────────────────────────
    def _draw_left_bar(self, W, H):
        bx = 44
        # Barra estática con degradado vertical
        self._grad_v(bx, 4, 3, H-8, S["accent_deep"], S["accent"])
        # Overlay luminoso animado (glide)
        self._bar_glow_y = 60
        self._bar_glow = self.c.create_rectangle(
            bx, self._bar_glow_y, bx+3, self._bar_glow_y+70,
            fill=S["accent_bright"], outline="")
        self._animate_glow(H)

    def _animate_glow(self, H):
        def _step():
            self._bar_glow_y += 4
            if self._bar_glow_y > H - 10:
                self._bar_glow_y = 4
            self.c.coords(self._bar_glow,
                          44, self._bar_glow_y,
                          47, self._bar_glow_y + 70)
            self.root.after(30, _step)
        self.root.after(30, _step)

    # ── Etiquetas superiores ───────────────────────────────────────────────────
    def _draw_top_labels(self, W, H):
        lx = 64
        self.c.create_text(lx, 28, text="ODIN  ·  TRAKIO PLATFORM",
                           fill=S["accent_dim"], font=("Consolas", 8),
                           anchor="w")
        self.c.create_text(lx, 46, text="SISTEMA DE AUTOMATIZACIÓN INTELIGENTE",
                           fill=S["muted"], font=("Consolas", 8),
                           anchor="w")

    # ── Tipografía gigante ─────────────────────────────────────────────────────
    def _draw_main_title(self, W, H):
        lx = 64
        self.c.create_text(lx, 138, text="ODIN",
                           fill=S["white"], font=("Segoe UI", 74, "bold"),
                           anchor="w")
        self.c.create_text(lx, 210, text=f"Versión  {VERSION}",
                           fill=S["accent"], font=("Segoe UI", 14),
                           anchor="w")
        # Línea decorativa debajo del subtítulo
        self.c.create_line(lx, 226, lx+280, 226,
                           fill=S["border_mid"], width=1)
        # Descripción
        self.c.create_text(lx, 248, text="ValidatorsGesi Launcher",
                           fill=S["muted"], font=("Segoe UI", 9),
                           anchor="w")
        self.c.create_text(lx, 264, text=AUTHORS,
                           fill=S["white"], font=("Segoe UI", 8),
                           anchor="w")

    # ── Tarjetas de módulos (columna derecha) ──────────────────────────────────
    def _draw_module_cards(self, W, H):
        modules = [
            ("ODIN",      "Validación Excel"),
            ("GESI",      "Motor digitación"),
            ("ANÁLISIS",  "Cruce variables"),
            ("VALIDADOR", "Calidad del dato"),
        ]
        cx = W - 144   # x inicio de tarjetas
        cw = 126       # ancho tarjeta
        ch = 42        # alto tarjeta
        gap = 8
        start_y = 78

        # Separador vertical entre contenido y tarjetas
        self.c.create_line(W-170, 68, W-170, H-46,
                           fill=S["border_dark"], width=1)

        # Etiqueta sección
        self.c.create_text(cx, start_y - 12,
                           text="MÓDULOS", fill=S["accent_dim"],
                           font=("Consolas", 7), anchor="w")

        for i, (name, desc) in enumerate(modules):
            y = start_y + i * (ch + gap)
            # Última tarjeta resaltada
            border_col = S["accent"] if i == 3 else S["accent_dim"]
            border_w   = 1 if i < 3 else 1

            self.c.create_rectangle(cx, y, cx+cw, y+ch,
                                    fill=S["bg2"],
                                    outline=border_col, width=border_w)
            self.c.create_text(cx+10, y+12, text=name,
                               fill=S["accent_bright"],
                               font=("Segoe UI", 10, "bold"), anchor="w")
            self.c.create_text(cx+10, y+28, text=desc,
                               fill=S["muted"],
                               font=("Segoe UI", 8), anchor="w")

    # ── Barra inferior: progreso + copyright ───────────────────────────────────
    def _draw_bottom_bar(self, W, H):
        by = H - 44
        lx = 64

        # Etiqueta de estado
        self._lbl_status = self.c.create_text(
            lx, by + 6, text="Iniciando...",
            fill=S["accent"], font=("Consolas", 8, "bold"), anchor="w")

        # Barra de progreso
        px, py = lx, by + 20
        pw, ph = W - 210, 2

        self.c.create_rectangle(px, py, px+pw, py+ph,
                                 fill=S["bg3"], outline=S["border_dark"])
        self._prog_rect = self.c.create_rectangle(
            px, py, px, py+ph, fill=S["accent_dim"], outline="")
        self._prog_dot = self.c.create_oval(
            px-3, py-2, px+3, py+ph+2,
            fill=S["accent"], outline="")
        self._prog_pct = self.c.create_text(
            px+pw+10, py+ph//2, text="0%",
            fill=S["accent_dim"], font=("Consolas", 8, "bold"), anchor="w")

        self._bar = (px, py, pw, ph)

        # Copyright
        self.c.create_text(W-14, by+28, text=COPYRIGHT,
                           fill=S["dim"], font=("Segoe UI", 7), anchor="e")

    # ── Decoraciones finales ───────────────────────────────────────────────────
    def _draw_decorations(self, W, H):
        # Franja superior con degradado horizontal
        self._grad_h(4, 4, W-8, 2, S["accent_dim"], S["accent"])

        # Esquinas HUD
        m, s = 8, 10
        col = S["accent_dim"]
        corners = [
            (m, m+s, m, m), (m, m, m+s, m),
            (W-m, m+s, W-m, m), (W-m, m, W-m-s, m),
            (m, H-m-s, m, H-m), (m, H-m, m+s, H-m),
            (W-m, H-m-s, W-m, H-m), (W-m, H-m, W-m-s, H-m),
        ]
        for ax, ay, bx, by_ in corners:
            self.c.create_line(ax, ay, bx, by_,
                               fill=col, width=1, capstyle=tk.ROUND)

    # ── Animación de progreso ──────────────────────────────────────────────────
    def _update_progress(self, frac):
        px, py, pw, ph = self._bar
        fw  = int(pw * frac)
        dot = px + fw
        r, g, b = self._interp(S["accent_dim"], S["accent_bright"], frac)
        col = f"#{r:02x}{g:02x}{b:02x}"
        self.c.coords(self._prog_rect, px, py, px+fw, py+ph)
        self.c.itemconfig(self._prog_rect, fill=col)
        self.c.coords(self._prog_dot, dot-3, py-2, dot+3, py+ph+2)
        self.c.itemconfig(self._prog_pct, text=f"{int(frac*100)}%")
        if frac < 0.3:    status = "Iniciando núcleo..."
        elif frac < 0.6:  status = "Cargando módulos..."
        elif frac < 0.85: status = "Verificando licencia..."
        else:             status = "Listo"
        self.c.itemconfig(self._lbl_status, text=status)
        self.c.update_idletasks()

    def _run_animation(self):
        steps = 64
        ivl   = self.MS // steps
        for i in range(1, steps+1):
            self.root.after(i*ivl, lambda f=i/steps: self._update_progress(f))
        self.root.after(self.MS+200, self._launch)

    def _launch(self):
        self.root.destroy()
        _open_main_logic()

    def run(self):
        self._run_animation()
        self.root.mainloop()


# ── Lógica de apertura principal ───────────────────────────────────────────────
def _open_main_logic():
    try:
        import index
        if hasattr(index, "index_open"):
            print("Abriendo aplicación principal con datos de licencia:", DATOS_LICENCIA)
            index.index_open(DATOS_LICENCIA)
    except Exception as e:
        import traceback
        with open(os.path.join(BASE_DIR, "error_log.txt"), "a", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        messagebox.showerror("Error", f"No se pudo iniciar el sistema:\n\n{e}")


API_URL     = "https://www.trakio.pro/api/v1/validate-license"
PROGRAMA_ID = "ODIN"


def verificar_licencia():
    _root = tk.Tk()
    _root.withdraw()

    ruta  = os.path.join(os.environ["APPDATA"], "ODIN_DATA")
    os.makedirs(ruta, exist_ok=True)
    lic   = os.path.join(ruta, "license.key")

    codigo = None
    if os.path.exists(lic):
        with open(lic) as f: codigo = f.read().strip()

    if not codigo:
        d = ctk.CTkInputDialog(
            text="Ingresa tu código de activación:",
            title="Activación ODIN",
            fg_color=COLORS["bg_card"][1],
            button_fg_color=COLORS["accent"][1],
            button_hover_color=COLORS["accent_hover"][1])
        codigo = d.get_input()
        if not codigo: _root.destroy(); sys.exit()

    esp = ctk.CTkToplevel()
    esp.title("Odin")
    aw, ah = 340, 160
    esp.geometry(f"{aw}x{ah}+{(esp.winfo_screenwidth()-aw)//2}+{(esp.winfo_screenheight()-ah)//2}")
    esp.resizable(False, False)
    esp.attributes("-topmost", True)
    esp.configure(fg_color=COLORS["bg_dark"][1])
    fi = ctk.CTkFrame(esp, fg_color="transparent")
    fi.pack(expand=True, fill="both", padx=20, pady=20)
    ctk.CTkLabel(fi, text="VERIFICANDO LICENCIA",
                 font=("Segoe UI", 13, "bold"),
                 text_color=COLORS["accent"][1]).pack(pady=(0, 10))
    pg = ctk.CTkProgressBar(fi, orientation="horizontal", mode="indeterminate",
                             width=260, progress_color=COLORS["accent"][1],
                             fg_color=COLORS["bg_input"][1])
    pg.pack(pady=10); pg.start()
    ctk.CTkLabel(fi, text="Conectando con el servidor seguro...",
                 font=("Segoe UI", 10),
                 text_color=COLORS["text_muted"][1]).pack()
    esp.update()

    try:
        resp = requests.post(API_URL,
                             json={"key": codigo, "program": PROGRAMA_ID},
                             timeout=8, allow_redirects=False)
        try:    data = resp.json()
        except: data = {}
        if resp.status_code == 200 and data.get("status") == "success":
            with open(lic, "w") as f: f.write(codigo)
            global DATOS_LICENCIA
            print("Datos de licencia obtenidos:", data)
            DATOS_LICENCIA = data
            esp.destroy(); _root.destroy(); return True
        else:
            esp.destroy()
            messagebox.showerror("Licencia Inválida",
                data.get("message", f"Código inválido (Error: {resp.status_code})"))
            if os.path.exists(lic): os.remove(lic)
            _root.destroy(); sys.exit()
    except requests.exceptions.RequestException:
        esp.destroy()
        if os.path.exists(lic): _root.destroy(); return True
        messagebox.showerror("Error de Conexión",
                             "Se requiere internet para la primera activación.")
        _root.destroy(); sys.exit()


def main():
    try:
        SplashScreen().run()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Error al iniciar el lanzador: {e}")


if __name__ == "__main__":
    if verificar_licencia():
        main()