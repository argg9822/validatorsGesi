"""
Odin.py – Lanzador Estático de ValidatorsGesi
Splash Screen estilo Adobe/CorelDraw – sin imagen de fondo, diseño puro.
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

DATOS_LICENCIA = {}

APP_NAME     = "Odin"
VERSION      = "1.0.1"
AUTHORS      = "Gabriel Monhabell  ·  Aramis Garcia"
COPYRIGHT    = "© 2024 Trakio"
TRANSPARENT  = "#00c7fc"

S = {
    "bg":            "#0C0202",
    "bg2":           "#130404",
    "bg3":           "#1C0606",
    "border_dark":   "#1E0808",
    "border_mid":    "#3A1010",
    "border_accent": "#6B2020",
    "accent":        "#C0392B",
    "accent_dim":    "#7B241C",
    "accent_deep":   "#4A0E0E",
    "accent_bright": "#E74C3C",
    "accent_light":  "#FF8A80",
    "white":         "#F0E6E6",
    "muted":         "#7A5C5C",
    "dim":           "#3D2525",
}

COLORS = {
    "bg_dark":       ("#F5F5F5", "#0C0202"),
    "bg_card":       ("#FFFFFF", "#130404"),
    "bg_input":      ("#F0F0F0", "#1C0808"),
    "accent":        ("#A93226", "#C0392B"),
    "accent_hover":  ("#922B21", "#A93226"),
    "text_primary":  ("#1A1A1A", "#F0E6E6"),
    "text_muted":    ("#666666", "#7A5C5C"),
    "border":        ("#DDDDDD", "#2A0A0A"),
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
    W  = 580
    H  = 340
    R  = 16
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
        return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

    def _interp(self, c1, c2, t):
        r1,g1,b1 = self._hex_rgb(c1)
        r2,g2,b2 = self._hex_rgb(c2)
        return (int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

    def _round_rect(self, x1,y1,x2,y2, r=12, **kw):
        pts=[x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
             x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
             x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        self.c.create_polygon(pts, smooth=True, **kw)

    def _grad_h(self, x,y,w,h, c1, c2):
        r1,g1,b1 = self._hex_rgb(c1)
        r2,g2,b2 = self._hex_rgb(c2)
        for i in range(w):
            t = i/max(w-1,1)
            col = f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"
            self.c.create_rectangle(x+i,y,x+i+1,y+h, fill=col, outline="")

    def _grad_v(self, x,y,w,h, c1, c2):
        r1,g1,b1 = self._hex_rgb(c1)
        r2,g2,b2 = self._hex_rgb(c2)
        for j in range(h):
            t = j/max(h-1,1)
            col = f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"
            self.c.create_rectangle(x,y+j,x+w,y+j+1, fill=col, outline="")

    def _hex_shape(self, cx, cy, r, **kw):
        pts=[]
        for i in range(6):
            a = math.radians(60*i - 30)
            pts += [cx + r*math.cos(a), cy + r*math.sin(a)]
        self.c.create_polygon(pts, **kw)

    def _build(self):
        W, H = self.W, self.H
        self.c = tk.Canvas(self.root, width=W, height=H,
                           bg=TRANSPARENT, highlightthickness=0)
        self.c.pack()
        self._draw_background(W, H)
        self._draw_left_panel(W, H)
        self._draw_right_info(W, H)
        self._draw_bottom_bar(W, H)
        self._draw_decorations(W, H)

    def _draw_background(self, W, H):
        self._round_rect(8,8,W-8,H-8, r=self.R+2, fill="#060000", outline="")
        self._round_rect(4,4,W-4,H-4, r=self.R,
                         fill=S["bg"], outline=S["border_mid"], width=1)
        self._grad_v(5, 5, 194, H-10, S["bg2"], S["bg3"])
        self.c.create_line(200,6, 200,H-6, fill=S["border_mid"], width=1)
        self.c.create_line(197,20, 197,H-20, fill=S["accent_deep"], width=2)

    def _draw_left_panel(self, W, H):
        cx, cy = 101, H//2 - 8
        self.c.create_oval(cx-74,cy-74,cx+74,cy+74,
                           outline=S["border_dark"], width=1, fill="")
        self.c.create_oval(cx-70,cy-70,cx+70,cy+70,
                           outline=S["border_accent"], width=1, fill="")
        self.c.create_oval(cx-62,cy-62,cx+62,cy+62,
                           fill=S["bg"], outline=S["border_mid"], width=1)

        path = _find("intro.png")
        loaded = False
        if path:
            try:
                img = Image.open(path).convert("RGBA")
                iw, ih = img.size
                side = min(iw, ih)
                img = img.crop(((iw-side)//2,(ih-side)//2,
                                (iw+side)//2,(ih+side)//2))
                img.thumbnail((110, 110), Image.LANCZOS)
                mask = Image.new("L", img.size, 0)
                d = ImageDraw.Draw(mask)
                d.ellipse((0,0)+img.size, fill=255)
                img.putalpha(mask)
                self._logo_img = ImageTk.PhotoImage(img)
                self.c.create_image(cx, cy, image=self._logo_img)
                loaded = True
            except:
                pass

        if not loaded:
            self._hex_shape(cx,cy,50, fill=S["bg3"],
                            outline=S["accent"], width=1)
            self._hex_shape(cx,cy,32, fill=S["accent_dim"],
                            outline=S["accent_bright"], width=1)
            for dx1,dy1,dx2,dy2,lw in [
                (0,-22,0,22,2),(-14,0,14,0,2),
                (-9,-14,9,-14,1),(-9,14,9,14,1)]:
                self.c.create_line(cx+dx1,cy+dy1,cx+dx2,cy+dy2,
                                   fill=S["white"],width=lw,capstyle=tk.ROUND)
            self.c.create_oval(cx-4,cy-4,cx+4,cy+4,
                               fill=S["accent_bright"], outline="")

    def _draw_right_info(self, W, H):
        x0 = 224
        lx = W - 26

        name_y = 54
        self.c.create_text(x0, name_y, text="ODIN",
                           fill=S["white"], font=("Segoe UI", 46, "bold"),
                           anchor="w")
        self.c.create_line(x0, name_y+22, lx, name_y+22,
                           fill=S["border_mid"], width=1)
        self.c.create_text(x0, name_y+38,
                           text="Validators GESI  ·  Trakio Platform",
                           fill=S["muted"], font=("Segoe UI", 10), anchor="w")

        ver_y = name_y + 76
        self.c.create_text(x0, ver_y, text=f"Versión {VERSION}",
                           fill=S["accent"], font=("Segoe UI", 11, "bold"),
                           anchor="w")

        dot_y = ver_y + 22
        for xi in range(x0, lx, 6):
            self.c.create_rectangle(xi,dot_y,xi+2,dot_y+1,
                                    fill=S["dim"], outline="")

        infos = [
            ("Sistema",  "ValidatorsGesi Launcher"),
            ("Módulo",   "Odin Core v1.0"),
            ("Build",    "2024.1 — Stable"),
        ]
        iy = dot_y + 16
        for i,(lbl,val) in enumerate(infos):
            yy = iy + i*20
            self.c.create_text(x0, yy, text=lbl+":",
                               fill=S["dim"], font=("Segoe UI", 9), anchor="w")
            self.c.create_text(x0+70, yy, text=val,
                               fill=S["muted"], font=("Segoe UI", 9), anchor="w")

        self.c.create_text(lx, H-48, text=AUTHORS,
                           fill=S["dim"], font=("Segoe UI", 8), anchor="e")

        self._lbl_status = self.c.create_text(
            x0, H-48, text="Iniciando...",
            fill=S["accent"], font=("Segoe UI", 8, "bold"), anchor="w")

    def _draw_bottom_bar(self, W, H):
        bh = 34
        by = H - bh - 4
        self._round_rect(5,by,W-5,H-5, r=self.R, fill=S["bg2"], outline="")
        self.c.create_line(5,by,W-5,by, fill=S["border_mid"], width=1)

        px, py = 224, by+14
        pw, ph = W-258, 4

        self.c.create_rectangle(px,py,px+pw,py+ph,
                                 fill=S["bg3"], outline=S["border_dark"])
        self._prog_rect = self.c.create_rectangle(
            px,py,px,py+ph, fill=S["accent_dim"], outline="")
        self._prog_dot = self.c.create_oval(
            px-3,py-1,px+3,py+ph+1,
            fill=S["accent_bright"], outline="")
        self._prog_pct = self.c.create_text(
            px+pw+10, py+ph//2, text="0%",
            fill=S["accent"], font=("Consolas", 8, "bold"), anchor="w")

        self._bar = (px, py, pw, ph)

        self.c.create_text(14, by+bh//2, text=COPYRIGHT,
                           fill=S["dim"], font=("Segoe UI", 8), anchor="w")

    def _draw_decorations(self, W, H):
        self._grad_h(5,4, W-10,3, S["accent_dim"], S["accent_bright"])

        m, s = 8, 12
        col  = S["accent_dim"]
        for (ax,ay,bx,by_) in [
            (m,m+s,m,m), (m,m,m+s,m),
            (W-m,m+s,W-m,m), (W-m,m,W-m-s,m),
            (m,H-m-s,m,H-m), (m,H-m,m+s,H-m),
            (W-m,H-m-s,W-m,H-m), (W-m,H-m,W-m-s,H-m),
        ]:
            self.c.create_line(ax,ay,bx,by_, fill=col, width=1, capstyle=tk.ROUND)

        dcy = 12
        self.c.create_polygon(200,dcy-6,206,dcy,200,dcy+6,194,dcy,
                               fill=S["accent_dim"],
                               outline=S["accent"], width=1)

    def _update_progress(self, frac):
        px,py,pw,ph = self._bar
        fw  = int(pw*frac)
        dot = px+fw
        r,g,b = self._interp(S["accent_dim"], S["accent_bright"], frac)
        col   = f"#{r:02x}{g:02x}{b:02x}"
        self.c.coords(self._prog_rect, px,py,px+fw,py+ph)
        self.c.itemconfig(self._prog_rect, fill=col)
        self.c.coords(self._prog_dot, dot-3,py-1,dot+3,py+ph+1)
        self.c.itemconfig(self._prog_pct, text=f"{int(frac*100)}%")
        if frac < 0.3:   status="Iniciando núcleo..."
        elif frac < 0.6: status="Cargando módulos..."
        elif frac < 0.85:status="Verificando licencia..."
        else:            status="Listo"
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


def _open_main_logic():
    try:
        import index
        if hasattr(index, "index_open"):
            # imprimir DATOS_LICENCIA para verificar que se está pasando correctamente
            print("Abriendo aplicación principal con datos de licencia:", DATOS_LICENCIA)
            # Pasamos la variable DATOS_LICENCIA como argumento a la función de apertura
            index.index_open(DATOS_LICENCIA)
    except Exception as e:
        import traceback
        with open(os.path.join(BASE_DIR,"error_log.txt"),"a",encoding="utf-8") as f:
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
    aw,ah = 340,160
    esp.geometry(f"{aw}x{ah}+{(esp.winfo_screenwidth()-aw)//2}+{(esp.winfo_screenheight()-ah)//2}")
    esp.resizable(False,False)
    esp.attributes("-topmost",True)
    esp.configure(fg_color=COLORS["bg_dark"][1])
    fi = ctk.CTkFrame(esp,fg_color="transparent")
    fi.pack(expand=True,fill="both",padx=20,pady=20)
    ctk.CTkLabel(fi,text="VERIFICANDO LICENCIA",
                 font=("Segoe UI",13,"bold"),
                 text_color=COLORS["accent"][1]).pack(pady=(0,10))
    pg = ctk.CTkProgressBar(fi,orientation="horizontal",mode="indeterminate",
                             width=260,progress_color=COLORS["accent"][1],
                             fg_color=COLORS["bg_input"][1])
    pg.pack(pady=10); pg.start()
    ctk.CTkLabel(fi,text="Conectando con el servidor seguro...",
                 font=("Segoe UI",10),
                 text_color=COLORS["text_muted"][1]).pack()
    esp.update()

    try:
        resp = requests.post(API_URL,
                             json={"key":codigo,"program":PROGRAMA_ID},
                             timeout=8,allow_redirects=False)
        try:    data=resp.json()
        except: data={}
        if resp.status_code==200 and data.get("status")=="success":
            with open(lic,"w") as f: f.write(codigo)
            # Guardamos la respuesta del servidor en nuestra variable global
            global DATOS_LICENCIA
            # imprimir en terminal para verificar que se obtiene la información correcta
            print("Datos de licencia obtenidos:", data)
            DATOS_LICENCIA = data

            esp.destroy(); _root.destroy(); return True
            
        
        else:
            esp.destroy()
            messagebox.showerror("Licencia Inválida",
                data.get("message",f"Código inválido (Error: {resp.status_code})"))
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
        messagebox.showerror("Fatal Error",f"Error al iniciar el lanzador: {e}")


if __name__ == "__main__":
    if verificar_licencia():
        main()