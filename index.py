"""
index.py  –  ValidatorsGesi  ·  Punto de entrada principal
Diseño compacto, elegante y de alto contraste. Paleta azul cobalto.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import webbrowser
import requests
import time

from crc_princ.analizar_exel import analizar_excel_2

try:
    import customtkinter as ctk
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter", "--quiet"])
    import customtkinter as ctk

from __version__ import __version__
import Updater as updater
import subprocess
import threading
from functools import partial
import socket

server_instance = None


def abrir_validador():
    webbrowser.open("https://www.trakio.pro/validator")


# ── Paleta — alto contraste, oscuro profundo ───────────────────────────────────
COLORS = {
    "bg":          ("#F4F7FB", "#0B1220"),   # fondo página
    "sidebar":     ("#FFFFFF", "#080F1C"),   # sidebar
    "card":        ("#FFFFFF", "#0F1A2E"),   # tarjetas
    "card2":       ("#F0F5FF", "#111D30"),   # tarjetas alternas / hover

    "accent":      ("#1B6ECC", "#4A9EE8"),   # azul principal — contraste alto
    "accent_soft": ("#EBF3FF", "#0D2040"),   # fondo de badge / pill

    "btn":         ("#1B6ECC", "#3B8DD4"),   # botones primarios
    "btn_hover":   ("#1558A8", "#2A78C0"),   # hover botón primario
    "btn2":        ("#E8F0FE", "#142236"),   # botones secundarios
    "btn2_hover":  ("#D4E4FC", "#1B3050"),

    "success":     ("#0F7B4F", "#2ECC8A"),
    "danger":      ("#C0392B", "#E05555"),
    "warning":     ("#B45309", "#F59E0B"),

    # Textos — contraste garantizado sobre bg y card
    "text1":       ("#0A1628", "#EDF2FF"),   # texto principal
    "text2":       ("#3B5070", "#7EA8D4"),   # texto secundario
    "text3":       ("#6B85A0", "#3D6080"),   # texto terciario / placeholders

    "border":      ("#D8E5F5", "#162035"),
    "divider":     ("#E8EFF8", "#111D2E"),
}

# ctk.set_appearance_mode("system")
APP_DIR = Path(__file__).parent.resolve()

# ── Helpers ────────────────────────────────────────────────────────────────────

def _divider(parent, px=16, py=0):
    ctk.CTkFrame(parent, height=1, fg_color=COLORS["divider"],
                 corner_radius=0).pack(fill="x", padx=px, pady=py)


def _label(parent, text, size=12, bold=False, color_key="text1", **pack_kw):
    ctk.CTkLabel(parent, text=text,
                 font=ctk.CTkFont("Segoe UI", size, "bold" if bold else "normal"),
                 text_color=COLORS[color_key]).pack(**pack_kw)


def _section(parent, text):
    """Etiqueta de sección compacta."""
    ctk.CTkLabel(parent, text=text.upper(),
                 font=ctk.CTkFont("Consolas", 9),
                 text_color=COLORS["text3"]).pack(anchor="w", padx=20, pady=(16, 6))


# ═══════════════════════════════════════════════════════════════════════════════
#  Ventana de Actualización
# ═══════════════════════════════════════════════════════════════════════════════
class UpdateWindow(ctk.CTkToplevel):
    def __init__(self, master, remote_version: str):
        super().__init__(master)
        self.title("Actualización disponible")
        self.geometry("460x260")
        self._remote_version = remote_version
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self.after(10, self._center)

        ctk.CTkFrame(self, height=3, fg_color=COLORS["accent"],
                     corner_radius=0).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(body, text="Nueva versión disponible",
                     font=ctk.CTkFont("Segoe UI", 15, "bold"),
                     text_color=COLORS["text1"]).pack(anchor="w")
        ctk.CTkLabel(body, text=f"v{__version__}  →  v{remote_version}",
                     font=ctk.CTkFont("Consolas", 11),
                     text_color=COLORS["text2"]).pack(anchor="w", pady=(4, 16))

        self.status_label = ctk.CTkLabel(body, text="¿Deseas actualizar ahora?",
                                         font=ctk.CTkFont("Segoe UI", 11),
                                         text_color=COLORS["text2"])
        self.status_label.pack(anchor="w")

        self.progress = ctk.CTkProgressBar(body, progress_color=COLORS["accent"],
                                            fg_color=COLORS["card2"])
        self.progress.pack(fill="x", pady=(10, 16))
        self.progress.set(0)

        btns = ctk.CTkFrame(body, fg_color="transparent")
        btns.pack(anchor="w")
        self.btn_update = ctk.CTkButton(btns, text="Actualizar ahora",
                                         fg_color=COLORS["btn"],
                                         hover_color=COLORS["btn_hover"],
                                         font=ctk.CTkFont("Segoe UI", 12, "bold"),
                                         command=self._start_update,
                                         width=160, height=36)
        self.btn_update.pack(side="left")
        ctk.CTkButton(btns, text="Más tarde",
                      fg_color=COLORS["btn2"], hover_color=COLORS["btn2_hover"],
                      text_color=COLORS["text2"],
                      font=ctk.CTkFont("Segoe UI", 12),
                      command=self.destroy, width=110, height=36).pack(side="left", padx=(8, 0))

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    import Updater as updater

    def _start_update(self):
        updater.open_debug_window()
        self.btn_update.configure(state="disabled", text="Actualizando...")
        updater.apply_update_async(
            remote_version=self._remote_version,
            progress_cb=lambda p: self.after(0, lambda: self.progress.set(p/100)),
            status_cb=lambda s: self.after(0, lambda: self.status_label.configure(text=s)),
            done_cb=self._on_done)

    def _on_done(self, success):
        msg = ("¡Listo! Reinicia para aplicar." if success
               else "No se pudo actualizar. Revisa tu conexión.")
        fn = messagebox.showinfo if success else messagebox.showerror
        self.after(0, lambda: fn("Actualización", msg, parent=self))
        self.after(0, self.destroy)


# ═══════════════════════════════════════════════════════════════════════════════
#  Diálogo de Progreso
# ═══════════════════════════════════════════════════════════════════════════════
class ProgressDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Procesando..."):
        super().__init__(master)
        self.title(title)
        self.geometry("400x160")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.grab_set()
        self.after(10, self._center)
        ctk.CTkFrame(self, height=3, fg_color=COLORS["accent"],
                     corner_radius=0).pack(fill="x")
        ctk.CTkLabel(self, text=title,
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=COLORS["text1"]).pack(pady=(18, 4))
        self.label = ctk.CTkLabel(self, text="Iniciando...",
                                   font=ctk.CTkFont("Consolas", 10),
                                   text_color=COLORS["text2"])
        self.label.pack()
        self.bar = ctk.CTkProgressBar(self, progress_color=COLORS["accent"],
                                       fg_color=COLORS["card2"])
        self.bar.pack(fill="x", padx=24, pady=14)
        self.bar.set(0)

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def update_progress(self, pct, msg=""):
        self.bar.set(pct / 100)
        if msg:
            self.label.configure(text=msg)
        self.update()


# ═══════════════════════════════════════════════════════════════════════════════
#  ValidatorCard
# ═══════════════════════════════════════════════════════════════════════════════
class ValidatorCard(ctk.CTkFrame):
    def __init__(self, master, title, description, icon="📋", run_callback=None, **kwargs):
        super().__init__(master, fg_color=COLORS["card"],
                         border_color=COLORS["border"], border_width=1,
                         corner_radius=8, **kwargs)
        self._run_cb = run_callback
        self._file_path = tk.StringVar(value="")

        ctk.CTkFrame(self, width=3, fg_color=COLORS["accent"],
                     corner_radius=0).pack(side="left", fill="y")
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=icon, font=ctk.CTkFont(size=16)).pack(side="left")
        ctk.CTkLabel(top, text=title, font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=COLORS["text1"]).pack(side="left", padx=(6, 0))
        ctk.CTkLabel(body, text=description, font=ctk.CTkFont("Segoe UI", 10),
                     text_color=COLORS["text2"],
                     wraplength=320, justify="left").pack(anchor="w", pady=(4, 8))

        fr = ctk.CTkFrame(body, fg_color="transparent")
        fr.pack(fill="x")
        self.file_entry = ctk.CTkEntry(fr, textvariable=self._file_path,
                                        placeholder_text="Seleccionar archivo Excel...",
                                        fg_color=COLORS["card2"],
                                        border_color=COLORS["border"],
                                        text_color=COLORS["text1"],
                                        font=ctk.CTkFont("Consolas", 10), height=30)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(fr, text="📂", fg_color=COLORS["btn2"], hover_color=COLORS["btn2_hover"],
                      text_color=COLORS["text2"], width=32, height=30,
                      command=self._browse).pack(side="right")
        ctk.CTkButton(body, text="▶  Ejecutar validación",
                      fg_color=COLORS["btn"], hover_color=COLORS["btn_hover"],
                      font=ctk.CTkFont("Segoe UI", 11, "bold"), height=32,
                      command=self._execute).pack(fill="x", pady=(8, 0))

    def _browse(self):
        path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls *.csv"), ("All files", "*.*")])
        if path:
            self._file_path.set(path)

    def _execute(self):
        path = self._file_path.get().strip()
        if not path:
            messagebox.showwarning("Sin archivo", "Por favor selecciona un archivo primero.")
            return
        if not Path(path).exists():
            messagebox.showerror("Archivo no encontrado", f"No se encontró:\n{path}")
            return
        if self._run_cb:
            self._run_cb(path)


# ═══════════════════════════════════════════════════════════════════════════════
#  App principal
# ═══════════════════════════════════════════════════════════════════════════════
class App(ctk.CTk):

    def _run_crear_hc(self):
        try:
            from crear_hc.crear import GesiApp
            # Resaltar sección en el nav
            for k, btn in self._nav_btns.items():
                if k == "execute_HC":
                    btn.configure(fg_color=COLORS["accent_soft"], text_color=COLORS["accent"])
                else:
                    btn.configure(fg_color="transparent", text_color=COLORS["text2"])
            self._set_topbar("", "GESI — Intelligence Automation System")
            # Ocultar el scrollable frame y destruir módulo previo si existe
            self.content.pack_forget()
            if self._module_frame and self._module_frame.winfo_exists():
                self._module_frame.destroy()
            # Embeber GesiApp directamente en el panel derecho
            self._module_frame = GesiApp(self.right_panel)
            self._module_frame.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al cargar módulo: {e}")

    def ejecutarcodeA(self):
        try:
            from liveValidator.index import OPENUI
            for k, btn in self._nav_btns.items():
                if k == "validators":
                    btn.configure(fg_color=COLORS["accent_soft"], text_color=COLORS["accent"])
                else:
                    btn.configure(fg_color="transparent", text_color=COLORS["text2"])
            self._set_topbar("Validadores", "GesiForm — Validación de sesiones")
            self.content.pack_forget()
            if self._module_frame and self._module_frame.winfo_exists():
                self._module_frame.destroy()
            self._module_frame = OPENUI(self.right_panel)
            self._module_frame.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al cargar módulo: {e}")

    def on_close(self):
        global server_instance
        if server_instance:
            try:
                server_instance.shutdown()
                server_instance.server_close()
            except Exception:
                pass
        self.destroy()

    def __init__(self, datos_licencia=None):
        super().__init__()
        self.title(f"Odin  ·  v{__version__}")
        self.geometry("1600x900")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.minsize(780, 520)
        self.configure(fg_color=COLORS["bg"])
        self._center_window()

        self.datos_licencia = datos_licencia or {}
        self.url_api = "https://www.trakio.pro/areas"
        self.areas = self.cargar_areas_api()

        ico = APP_DIR / "img" / "logo.ico"
        if ico.exists():
            try:
                self.iconbitmap(str(ico))
            except Exception:
                pass

        self._build_ui()
        updater.check_update_async(self._on_update_check)

    # ── Layout principal ──────────────────────────────────────────────────────
    def _build_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200,
                                    fg_color=COLORS["sidebar"],
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Divisor sidebar
        ctk.CTkFrame(self, width=1, fg_color=COLORS["border"],
                     corner_radius=0).pack(side="left", fill="y")

        # Columna derecha
        right = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        right.pack(side="left", fill="both", expand=True)
        self.right_panel = right
        self._module_frame = None

        # ── Sidebar interior ──────────────────────────────────────────────────
        # Logo compacto
        logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo.pack(fill="x", padx=16, pady=(22, 16))

        badge = ctk.CTkFrame(logo, fg_color=COLORS["accent_soft"],
                              width=34, height=34, corner_radius=7)
        badge.pack(side="left")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="O",
                     font=ctk.CTkFont("Segoe UI", 16, "bold"),
                     text_color=COLORS["accent"]).place(relx=0.5, rely=0.5, anchor="center")

        txt = ctk.CTkFrame(logo, fg_color="transparent")
        txt.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(txt, text="Odin",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=COLORS["text1"]).pack(anchor="w")
        ctk.CTkLabel(txt, text=f"v{__version__}",
                     font=ctk.CTkFont("Consolas", 9),
                     text_color=COLORS["text3"]).pack(anchor="w")

        _divider(self.sidebar, px=12)

        # Navegación
        ctk.CTkLabel(self.sidebar, text="NAVEGACIÓN",
                     font=ctk.CTkFont("Consolas", 8),
                     text_color=COLORS["text3"]).pack(anchor="w", padx=16, pady=(12, 4))

        nav_items = [
            ("home",       "🏠", "Inicio"),
            ("validators", "✅", "Validadores"),
            ("execute_HC", "▶",  "Ejecutar HC"),
            ("settings",   "⚙️", "Configuración"),
        ]
        self._nav_btns = {}
        for key, icon, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {label}",
                anchor="w",
                font=ctk.CTkFont("Segoe UI", 12),
                fg_color="transparent",
                hover_color=COLORS["card2"],
                text_color=COLORS["text2"],
                height=36, corner_radius=6,
                command=lambda k=key: self._navigate(k))
            btn.pack(fill="x", padx=8, pady=1)
            self._nav_btns[key] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="y", expand=True)

        # Botón actualizar — fondo de la sidebar
        self.btn_update_sidebar = ctk.CTkButton(
            self.sidebar, text="🔄  Actualización",
            font=ctk.CTkFont("Segoe UI", 10),
            fg_color=COLORS["btn2"],
            hover_color=COLORS["btn2_hover"],
            text_color=COLORS["text2"],
            height=28, corner_radius=6,
            command=self._manual_update_check)
        self.btn_update_sidebar.pack(fill="x", padx=12, pady=(0, 14))

        # ── Topbar ────────────────────────────────────────────────────────────
        self.topbar = ctk.CTkFrame(right, fg_color=COLORS["sidebar"],
                                    height=48, corner_radius=0)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        ctk.CTkFrame(right, height=1, fg_color=COLORS["border"],
                     corner_radius=0).pack(fill="x")

        self._tb_title = ctk.CTkLabel(self.topbar, text="Inicio",
                                       font=ctk.CTkFont("Segoe UI", 14, "bold"),
                                       text_color=COLORS["text1"])
        self._tb_title.pack(side="left", padx=20)

        self._tb_sub = ctk.CTkLabel(self.topbar, text="",
                                     font=ctk.CTkFont("Segoe UI", 10),
                                     text_color=COLORS["text3"])
        self._tb_sub.pack(side="left")

        # Badge versión
        vb = ctk.CTkFrame(self.topbar, fg_color=COLORS["accent_soft"],
                           corner_radius=6)
        vb.pack(side="right", padx=16)
        ctk.CTkLabel(vb, text=f"v{__version__}",
                     font=ctk.CTkFont("Consolas", 9),
                     text_color=COLORS["accent"]).pack(padx=10, pady=4)

        # Banner notificación
        self.notif_bar = ctk.CTkFrame(right, fg_color=COLORS["accent"],
                                       corner_radius=0, height=32)
        self.notif_bar.pack_forget()
        self._notif_lbl = ctk.CTkLabel(self.notif_bar, text="",
                                        font=ctk.CTkFont("Segoe UI", 10),
                                        text_color="white")
        self._notif_lbl.pack(side="left", padx=14)
        ctk.CTkButton(self.notif_bar, text="Ver →", width=60, height=22,
                      fg_color="white", text_color=COLORS["accent"],
                      hover_color="#E0E0E0", font=ctk.CTkFont("Segoe UI", 10, "bold"),
                      command=self._show_update_dialog).pack(side="right", padx=10, pady=5)

        # Área de contenido
        self.content = ctk.CTkScrollableFrame(right, fg_color="transparent",
                                               scrollbar_button_color=COLORS["border"])
        self.content.pack(fill="both", expand=True)

        self._remote_version = None
        self._navigate("home")

    def _set_topbar(self, title, subtitle=""):
        self._tb_title.configure(text=title)
        self._tb_sub.configure(text=f"  ·  {subtitle}" if subtitle else "")

    def _navigate(self, key):
        # Destruir módulo embebido si existe y restaurar el área de contenido
        if self._module_frame and self._module_frame.winfo_exists():
            self._module_frame.destroy()
        self._module_frame = None
        if not self.content.winfo_ismapped():
            self.content.pack(fill="both", expand=True)

        for k, btn in self._nav_btns.items():
            if k == key:
                btn.configure(fg_color=COLORS["accent_soft"],
                               text_color=COLORS["accent"])
            else:
                btn.configure(fg_color="transparent",
                               text_color=COLORS["text2"])
        for w in self.content.winfo_children():
            w.destroy()
        {
            "home":       self._page_home,
            "validators": self._page_validators,
            "execute_HC": self._page_execute_hc,
            "settings":   self._page_settings,
        }.get(key, self._page_home)()

    # ── Componente: fila de acción compacta ───────────────────────────────────
    def _action_row(self, parent, title, subtitle, btn_text, cmd,
                    state="normal", icon="▶"):
        row = ctk.CTkFrame(parent, fg_color=COLORS["card"],
                           border_color=COLORS["border"], border_width=1,
                           corner_radius=8, height=60)
        row.pack(fill="x", padx=20, pady=16)
        row.pack_propagate(False)   # altura fija — evita que los hijos la expandan

        ctk.CTkFrame(row, width=3,
                     fg_color=COLORS["accent"] if state == "normal" else COLORS["border"],
                     corner_radius=0).pack(side="left", fill="y")

        # Botón al extremo derecho antes del texto (así fill="x" no lo empuja)
        btn_fg = COLORS["btn"] if state == "normal" else COLORS["btn2"]
        btn_tf = "white" if state == "normal" else COLORS["text3"]
        ctk.CTkButton(row, text=f"{icon}  {btn_text}",
                      fg_color=btn_fg, hover_color=COLORS["btn_hover"],
                      text_color=btn_tf,
                      font=ctk.CTkFont("Segoe UI", 11, "bold"),
                      width=100, height=28, state=state,
                      command=cmd).pack(side="right", padx=12)

        # Texto centrado verticalmente en el espacio restante
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=12)

        ctk.CTkLabel(info, text=title,
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=COLORS["text1"]).pack(anchor="w", pady=(0, 0))
        if subtitle:
            ctk.CTkLabel(info, text=subtitle,
                         font=ctk.CTkFont("Segoe UI", 9),
                         text_color=COLORS["text2"]).pack(anchor="w")

    # ── Componente: métrica compacta ──────────────────────────────────────────
    def _metric(self, parent, col, label, value, sub, color_key="accent"):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"],
                            border_color=COLORS["border"], border_width=1,
                            corner_radius=8)
        card.grid(row=0, column=col, padx=4, pady=0, sticky="nsew")
        ctk.CTkFrame(card, height=2, fg_color=COLORS[color_key],
                     corner_radius=0).pack(fill="x")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)
        ctk.CTkLabel(inner, text=label,
                     font=ctk.CTkFont("Segoe UI", 9),
                     text_color=COLORS["text2"]).pack(anchor="w")
        ctk.CTkLabel(inner, text=value,
                     font=ctk.CTkFont("Segoe UI", 18, "bold"),
                     text_color=COLORS["text1"]).pack(anchor="w", pady=(1, 0))
        ctk.CTkLabel(inner, text=sub,
                     font=ctk.CTkFont("Segoe UI", 9),
                     text_color=COLORS["text2"]).pack(anchor="w")

    # ── Página: Inicio ────────────────────────────────────────────────────────
    def _page_home(self):
        self._set_topbar("Inicio", "Panel principal")
        f = self.content

        # Métricas
        _section(f, "Estado del sistema")
        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x", padx=20, pady=(0, 4))
        g.columnconfigure((0,1,2,3), weight=1, uniform="m")

        self._metric(g, 0, "Módulos",     "4",            "disponibles")
        self._metric(g, 1, "Versión",     f"v{__version__}", "instalada")
        self._metric(g, 2, "Auto-update", "Activo",       "GitHub")
        self._metric(g, 3, "Licencia",    "Válida",       "verificada",
                     color_key="success")

        # Acciones rápidas
        _section(f, "Acceso rápido")

        tiene_hc = self.datos_licencia.get("hc") is True
        tiene_gf = self.datos_licencia.get("gesiform") is True

        self._action_row(f,
            "Creación en herramienta de control",
            "Genera consecutivos automáticamente desde Excel",
            "Abrir", self._run_crear_hc,
            state="normal" if tiene_hc else "disabled")

        self._action_row(f,
            "Ir a Validadores",
            "Módulos de validación de sesiones",
            "Abrir", lambda: self._navigate("validators"),
            state="normal" if tiene_gf else "disabled",
            icon="✅")

        # Info
        _section(f, "Información")
        info = ctk.CTkFrame(f, fg_color=COLORS["card"],
                            border_color=COLORS["border"], border_width=1,
                            corner_radius=8)
        info.pack(fill="x", padx=20, pady=(0, 20))

        rows = [
            ("Sistema",  "ValidatorsGesi Launcher"),
            ("Módulo",   "Odin Core"),
            ("Build",    "2024.1 — Stable"),
        ]
        for i, (k, v) in enumerate(rows):
            r = ctk.CTkFrame(info, fg_color="transparent")
            r.pack(fill="x", padx=14, pady=0)
            ctk.CTkLabel(r, text=k, font=ctk.CTkFont("Consolas", 10),
                         text_color=COLORS["text3"],
                         width=90, anchor="w").pack(side="left", pady=2)
            ctk.CTkLabel(r, text=v, font=ctk.CTkFont("Segoe UI", 11),
                         text_color=COLORS["text1"]).pack(side="left")
            if i < len(rows)-1:
                _divider(info, px=14)

    # ── Página: Ejecutar HC ───────────────────────────────────────────────────
    def _page_execute_hc(self):
        self._set_topbar("Ejecutar HC", "Creación automática de consecutivos")
        f = self.content

        _section(f, "Módulo")

        tiene_hc = self.datos_licencia.get("hc") is True

        card = ctk.CTkFrame(f, fg_color=COLORS["card"],
                            border_color=COLORS["border"], border_width=1,
                            corner_radius=8)
        card.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkFrame(card, height=2,
                     fg_color=COLORS["accent"] if tiene_hc else COLORS["border"],
                     corner_radius=0).pack(fill="x")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=16)

        left = ctk.CTkFrame(body, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(left, text="Módulo Crear HC",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=COLORS["text1"]).pack(anchor="w")
        ctk.CTkLabel(left,
                     text="Genera consecutivos automáticamente en la herramienta\n"
                          "de control a partir de un archivo Excel.",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=COLORS["text2"], justify="left").pack(anchor="w", pady=(4, 12))

        # Badge acceso
        bc = COLORS["success"] if tiene_hc else COLORS["danger"]
        bt = "white" if tiene_hc else COLORS["text3"]
        badge = ctk.CTkFrame(left, fg_color=bc, corner_radius=5)
        badge.pack(anchor="w")
        ctk.CTkLabel(badge,
                     text="Con acceso" if tiene_hc else "Sin acceso",
                     font=ctk.CTkFont("Segoe UI", 9, "bold"),
                     text_color=bt).pack(padx=10, pady=4)

        # Botón
        ctk.CTkButton(body, text="▶  Ejecutar",
                      fg_color=COLORS["btn"] if tiene_hc else COLORS["btn2"],
                      hover_color=COLORS["btn_hover"],
                      text_color="white" if tiene_hc else COLORS["text3"],
                      font=ctk.CTkFont("Segoe UI", 12, "bold"),
                      height=38, width=130,
                      state="normal" if tiene_hc else "disabled",
                      command=self._run_crear_hc).pack(side="right")

    # ── Página: Validadores ───────────────────────────────────────────────────
    def _page_validators(self):
        for w in self.content.winfo_children():
            w.destroy()
        self._set_topbar("Validadores", "Módulos de validación")
        f = self.content

        nuevas = self.cargar_areas_api()
        if nuevas:
            self.areas = nuevas

        _section(f, "Acceso")

        tiene_gf = self.datos_licencia.get("gesiform") is True

        self._action_row(f,
            "Validador web",
            "Abrir en trakio.pro",
            "Abrir", abrir_validador, icon="🌐")

        self._action_row(f,
            "GesiForm SDS",
            "Validación de sesiones",
            "Abrir", self.ejecutarcodeA,
            state="normal" if tiene_gf else "disabled",
            icon="📋")

    # ── Página: Configuración ─────────────────────────────────────────────────
    def _page_settings(self):
        self._set_topbar("Configuración")
        f = self.content

        # Credenciales GesiForm
        _section(f, "Credenciales GesiForm")
        cred_card = ctk.CTkFrame(f, fg_color=COLORS["card"],
                                  border_color=COLORS["border"], border_width=1,
                                  corner_radius=8)
        cred_card.pack(fill="x", padx=20, pady=(0, 4))
        ctk.CTkFrame(cred_card, height=2, fg_color=COLORS["accent"],
                     corner_radius=0).pack(fill="x")
        cb = ctk.CTkFrame(cred_card, fg_color="transparent")
        cb.pack(fill="x", padx=14, pady=12)

        ctk.CTkLabel(cb, text="Usuario y contraseña para iniciar sesión en GesiForm. "
                              "Se almacenan cifrados con tu cuenta de Windows.",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=COLORS["text2"],
                     wraplength=560, justify="left").pack(anchor="w", pady=(0, 10))

        fields = ctk.CTkFrame(cb, fg_color="transparent")
        fields.pack(fill="x")
        fields.columnconfigure(0, weight=1)
        fields.columnconfigure(1, weight=1)

        # Fila usuario
        u_frame = ctk.CTkFrame(fields, fg_color="transparent")
        u_frame.grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=(0, 6))
        ctk.CTkLabel(u_frame, text="Usuario",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=COLORS["text3"]).pack(anchor="w")
        self._cfg_user_var = ctk.StringVar()
        ctk.CTkEntry(u_frame, textvariable=self._cfg_user_var,
                     placeholder_text="usuario@dominio.com",
                     fg_color=COLORS["card2"], border_color=COLORS["border"],
                     text_color=COLORS["text1"],
                     font=ctk.CTkFont("Segoe UI", 11), height=32).pack(fill="x")

        # Fila contraseña
        p_frame = ctk.CTkFrame(fields, fg_color="transparent")
        p_frame.grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=(0, 6))
        ctk.CTkLabel(p_frame, text="Contraseña",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=COLORS["text3"]).pack(anchor="w")
        self._cfg_pass_var = ctk.StringVar()
        ctk.CTkEntry(p_frame, textvariable=self._cfg_pass_var,
                     placeholder_text="••••••••", show="•",
                     fg_color=COLORS["card2"], border_color=COLORS["border"],
                     text_color=COLORS["text1"],
                     font=ctk.CTkFont("Segoe UI", 11), height=32).pack(fill="x")

        # Cargar credenciales guardadas
        try:
            from credentials_store import cargar_credenciales
            _u, _p = cargar_credenciales()
            self._cfg_user_var.set(_u)
            self._cfg_pass_var.set(_p)
        except Exception:
            pass

        # Fila botón + estado
        btn_row = ctk.CTkFrame(cb, fg_color="transparent")
        btn_row.pack(fill="x", pady=(4, 0))
        self._cred_status_lbl = ctk.CTkLabel(btn_row, text="",
                                              font=ctk.CTkFont("Segoe UI", 10),
                                              text_color=COLORS["success"])
        self._cred_status_lbl.pack(side="left")
        ctk.CTkButton(btn_row, text="Guardar credenciales",
                      fg_color=COLORS["btn"], hover_color=COLORS["btn_hover"],
                      font=ctk.CTkFont("Segoe UI", 11, "bold"),
                      height=32, width=170,
                      command=self._guardar_credenciales).pack(side="right")

        # Actualización
        _section(f, "Actualizaciones")
        upd = ctk.CTkFrame(f, fg_color=COLORS["card"],
                           border_color=COLORS["border"], border_width=1,
                           corner_radius=8)
        upd.pack(fill="x", padx=20, pady=(0, 4))
        ctk.CTkFrame(upd, height=2, fg_color=COLORS["accent"],
                     corner_radius=0).pack(fill="x")
        ub = ctk.CTkFrame(upd, fg_color="transparent")
        ub.pack(fill="x", padx=14, pady=12)
        li = ctk.CTkFrame(ub, fg_color="transparent")
        li.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(li, text=f"Versión instalada: v{__version__}",
                     font=ctk.CTkFont("Consolas", 11),
                     text_color=COLORS["text1"]).pack(anchor="w")
        ctk.CTkLabel(li, text="Actualizaciones, sin reinstalar.",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=COLORS["text2"]).pack(anchor="w", pady=(3, 0))
        ctk.CTkButton(ub, text="Verificar",
                      fg_color=COLORS["btn"], hover_color=COLORS["btn_hover"],
                      font=ctk.CTkFont("Segoe UI", 11, "bold"),
                      height=34, width=110,
                      command=self._manual_update_check).pack(side="right")

        # Apariencia
        _section(f, "Apariencia")
        ap = ctk.CTkFrame(f, fg_color=COLORS["card"],
                          border_color=COLORS["border"], border_width=1,
                          corner_radius=8)
        ap.pack(fill="x", padx=20, pady=(0, 4))
        ctk.CTkFrame(ap, height=2, fg_color=COLORS["accent"],
                     corner_radius=0).pack(fill="x")
        ar = ctk.CTkFrame(ap, fg_color="transparent")
        ar.pack(fill="x", padx=14, pady=12)
        ctk.CTkLabel(ar, text="Tema",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=COLORS["text1"]).pack(side="left")
        ctk.CTkOptionMenu(ar, values=["Oscuro", "Claro", "Sistema"],
                          fg_color=COLORS["card2"],
                          button_color=COLORS["btn"],
                          button_hover_color=COLORS["btn_hover"],
                          text_color=COLORS["text1"],
                          font=ctk.CTkFont("Segoe UI", 11),
                          command=self._change_theme).pack(side="right")

        # Licencia
        _section(f, "Permisos de licencia")
        lic = ctk.CTkFrame(f, fg_color=COLORS["card"],
                           border_color=COLORS["border"], border_width=1,
                           corner_radius=8)
        lic.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkFrame(lic, height=2, fg_color=COLORS["success"],
                     corner_radius=0).pack(fill="x")
        lr = ctk.CTkFrame(lic, fg_color="transparent")
        lr.pack(fill="x", padx=14, pady=12)
        for name, key in [("HC", "hc"), ("GesiForm", "gesiform")]:
            active = self.datos_licencia.get(key) is True
            pill = ctk.CTkFrame(lr,
                                fg_color=COLORS["btn"] if active else COLORS["btn2"],
                                corner_radius=5)
            pill.pack(side="left", padx=(0, 8))
            ctk.CTkLabel(pill, text=name,
                         font=ctk.CTkFont("Segoe UI", 10, "bold"),
                         text_color="white" if active else COLORS["text3"]).pack(padx=10, pady=5)

    def _guardar_credenciales(self):
        try:
            from credentials_store import guardar_credenciales
            guardar_credenciales(
                self._cfg_user_var.get().strip(),
                self._cfg_pass_var.get()
            )
            self._cred_status_lbl.configure(
                text="Credenciales guardadas correctamente",
                text_color=COLORS["success"])
        except Exception as e:
            self._cred_status_lbl.configure(
                text=f"Error al guardar: {e}",
                text_color=COLORS["danger"])

    # ── API / lógica (sin cambios) ────────────────────────────────────────────
    def cargar_areas_api(self):
        try:
            r = requests.get(self.url_api, timeout=5)
            return r.json() if r.status_code == 200 else {}
        except Exception as e:
            print(f"Error API: {e}")
            return {}

    def agregar_validador_logic(self, area):
        d = ctk.CTkInputDialog(title="Agregar Validador",
                               text="Ingrese el nombre del validador:")
        res = d.get_input()
        if not res:
            return
        if any(v['nombre'] == res for v in self.areas[area]):
            messagebox.showerror("Error", "El validador ya existe.")
            return
        self.areas[area].append({"nombre": res, "reglas": []})
        self.guardar_areas_api(area, self.areas[area])
        self.seleccionar_entorno_ui(area)

    def eliminar_area_logic(self, area):
        if messagebox.askyesno("Confirmar", f"¿Eliminar el entorno '{area}'?"):
            try:
                r = requests.delete(f"{self.url_api}/{area}")
                if r.status_code in (200, 204):
                    del self.areas[area]
                    self.actualizar_lista_entornos()
                    for w in self.details_panel.winfo_children():
                        w.destroy()
                    messagebox.showinfo("Éxito", "Entorno eliminado.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def editar_regla_logic(self, area, validador, regla):
        print(f"Editando regla: {regla}")

    def guardar_areas_api(self, nombre_area, datos_area):
        try:
            requests.put(f"{self.url_api}/{nombre_area}", json={"area": datos_area})
        except Exception as e:
            print(f"Error al guardar: {e}")

    def actualizar_lista_entornos(self):
        for w in self.env_list_frame.winfo_children():
            w.destroy()
        for nombre in self.areas:
            ctk.CTkButton(self.env_list_frame, text=f"  {nombre}",
                          anchor="w", font=ctk.CTkFont("Segoe UI", 11),
                          fg_color="transparent",
                          hover_color=COLORS["card2"],
                          text_color=COLORS["text1"],
                          height=32, corner_radius=6,
                          command=lambda n=nombre: self.seleccionar_entorno_ui(n)
                          ).pack(fill="x", pady=1)

    def seleccionar_entorno_ui(self, nombre_entorno):
        for w in self.details_panel.winfo_children():
            w.destroy()
        ctk.CTkFrame(self.details_panel, height=2, fg_color=COLORS["accent"],
                     corner_radius=0).pack(fill="x")
        hdr = ctk.CTkFrame(self.details_panel, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        ctk.CTkLabel(hdr, text=nombre_entorno,
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=COLORS["text1"]).pack(side="left")
        ctk.CTkButton(hdr, text="+ Agregar",
                      fg_color=COLORS["btn"], hover_color=COLORS["btn_hover"],
                      font=ctk.CTkFont("Segoe UI", 10, "bold"),
                      height=26, width=80,
                      command=lambda: self.agregar_validador_logic(nombre_entorno)).pack(side="right")
        _divider(self.details_panel, px=14)
        for val in self.areas.get(nombre_entorno, []):
            vr = ctk.CTkFrame(self.details_panel, fg_color=COLORS["card2"],
                              corner_radius=6)
            vr.pack(fill="x", padx=14, pady=3)
            ctk.CTkLabel(vr, text=f"📋  {val['nombre']}",
                         font=ctk.CTkFont("Segoe UI", 11),
                         text_color=COLORS["text1"]).pack(side="left", padx=10, pady=7)
            ctk.CTkButton(vr, text="Ver →",
                          fg_color=COLORS["btn"], hover_color=COLORS["btn_hover"],
                          font=ctk.CTkFont("Segoe UI", 10, "bold"),
                          height=24, width=64,
                          command=lambda v=val: self.gestionar_reglas_ui(
                              nombre_entorno, v)).pack(side="right", padx=8)
        ctk.CTkButton(self.details_panel, text="Eliminar entorno",
                      fg_color="transparent", hover_color=COLORS["card2"],
                      text_color=COLORS["danger"],
                      font=ctk.CTkFont("Segoe UI", 10),
                      height=28,
                      command=lambda: self.eliminar_area_logic(nombre_entorno)
                      ).pack(anchor="w", padx=14, pady=10)

    def agregar_entorno_ui(self):
        d = ctk.CTkInputDialog(text="Nombre del nuevo entorno:", title="Nuevo Entorno")
        res = d.get_input()
        if res and res not in self.areas:
            self.areas[res] = []
            self.actualizar_lista_entornos()

    def gestionar_reglas_ui(self, area, validador):
        for w in self.details_panel.winfo_children():
            w.destroy()
        ctk.CTkFrame(self.details_panel, height=2, fg_color=COLORS["accent"],
                     corner_radius=0).pack(fill="x")
        hdr = ctk.CTkFrame(self.details_panel, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        ctk.CTkLabel(hdr, text=validador['nombre'],
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=COLORS["text1"]).pack(side="left")
        ctk.CTkButton(hdr, text="← Volver",
                      fg_color=COLORS["btn2"], hover_color=COLORS["btn2_hover"],
                      text_color=COLORS["text2"],
                      font=ctk.CTkFont("Segoe UI", 10),
                      height=26, width=76,
                      command=lambda: self.seleccionar_entorno_ui(area)).pack(side="right")
        _divider(self.details_panel, px=14)
        for i, regla in enumerate(validador["reglas"]):
            rr = ctk.CTkFrame(self.details_panel, fg_color=COLORS["card2"], corner_radius=6)
            rr.pack(fill="x", padx=14, pady=2)
            ctk.CTkLabel(rr, text=f"  {i+1}.  {list(regla.values())[0]}",
                         font=ctk.CTkFont("Consolas", 10),
                         text_color=COLORS["text1"]).pack(side="left", padx=8, pady=7)
            ctk.CTkButton(rr, text="✏", fg_color=COLORS["accent_soft"],
                          hover_color=COLORS["btn2_hover"],
                          text_color=COLORS["accent"],
                          width=28, height=24,
                          command=lambda r=regla: self.editar_regla_logic(
                              area, validador, r)).pack(side="right", padx=8)
        ctk.CTkButton(self.details_panel, text="📊  Analizar Excel",
                      fg_color=COLORS["btn"], hover_color=COLORS["btn_hover"],
                      font=ctk.CTkFont("Segoe UI", 12, "bold"), height=36,
                      command=lambda: analizar_excel_2(validador)
                      ).pack(fill="x", padx=14, pady=14)

    # ── Validadores (callbacks sin cambios) ───────────────────────────────────
    def _run_validator(self, file_path, module_name, label):
        dlg = ProgressDialog(self, title=f"Validando: {label}")
        def _work():
            try:
                import importlib
                mod = importlib.import_module(f"validadores.{module_name}")
                dlg.update_progress(10, "Leyendo archivo...")
                result = mod.validate(file_path,
                    progress_cb=lambda p, m: self.after(0, lambda: dlg.update_progress(p, m)))
                self.after(0, dlg.destroy)
                if result.get("ok"):
                    self.after(0, lambda: messagebox.showinfo(
                        "Completo", f"✅ {result.get('message', 'Sin errores.')}"))
                else:
                    self.after(0, lambda: messagebox.showwarning(
                        "Con errores", f"⚠️ {result.get('message', 'Errores encontrados.')}"))
            except ModuleNotFoundError:
                self.after(0, dlg.destroy)
                self.after(0, lambda: messagebox.showerror(
                    "Módulo no encontrado",
                    f"'validadores/{module_name}.py' no existe.\n\n"
                    "def validate(file_path, progress_cb=None) -> dict"))
            except Exception as e:
                self.after(0, dlg.destroy)
                self.after(0, lambda e=e: messagebox.showerror("Error", str(e)))
        threading.Thread(target=_work, daemon=True).start()

    def _run_validator_beneficiarios(self, path):
        self._run_validator(path, "beneficiarios", "Beneficiarios")
    def _run_validator_actividades(self, path):
        self._run_validator(path, "actividades", "Actividades")
    def _run_validator_recursos(self, path):
        self._run_validator(path, "recursos", "Recursos")
    def _run_validator_indicadores(self, path):
        self._run_validator(path, "indicadores", "Indicadores")

    # ── Auto-actualización (sin cambios) ──────────────────────────────────────
    def _on_update_check(self, result):
        if result.get("available"):
            self._remote_version = result["remote_version"]
            self.after(0, self._show_update_banner)

    def _show_update_banner(self):
        self._notif_lbl.configure(
            text=f"🚀  Nueva versión: v{self._remote_version}")
        self.notif_bar.pack(fill="x")
        self.notif_bar.lift()

    def _show_update_dialog(self):
        if self._remote_version:
            UpdateWindow(self, self._remote_version)

    def _manual_update_check(self):
        self.btn_update_sidebar.configure(text="Verificando...", state="disabled")
        def _after(result):
            self.after(0, lambda: self.btn_update_sidebar.configure(
                text="🔄  Actualización", state="normal"))
            if result.get("available"):
                self._remote_version = result["remote_version"]
                self.after(0, self._show_update_dialog)
            elif "error" in result:
                self.after(0, lambda: messagebox.showwarning(
                    "Sin conexión", "No se pudo verificar actualizaciones."))
            else:
                self.after(0, lambda: messagebox.showinfo(
                    "Al día", f"✅ Versión más reciente (v{__version__})."))
        updater.check_update_async(_after)

    def _change_theme(self, choice):
        ctk.set_appearance_mode(
            {"Oscuro": "dark", "Claro": "light"}.get(choice, "system"))
        self._page_settings()

    def _center_window(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = 960, 640   # dimensiones declaradas en __init__
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


# ═══════════════════════════════════════════════════════════════════════════════
def index_open(datos_licencia=None):
    app = App(datos_licencia=datos_licencia)
    app.mainloop()
