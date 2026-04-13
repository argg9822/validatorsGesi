"""
index.py  –  ValidatorsGesi  ·  Punto de entrada principal
Interfaz moderna con CustomTkinter + auto-actualización desde GitHub
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import requests

# ── CustomTkinter (instala si no existe) ──────────────────────────────────────
try:
    import customtkinter as ctk
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter", "--quiet"])
    import customtkinter as ctk

from __version__ import __version__
import Updater as updater

import subprocess

# ── Paleta de colores ─────────────────────────────────────────────────────────
# Definición de colores que soportan ambos temas
COLORS = {
    "bg_dark":      ("#F2F2F2", "#0D1117"),
    "bg_card":      ("#FFFFFF", "#161B22"),
    "bg_input":     ("#EBEBEB", "#21262D"),
    "accent":       ("#238636", "#238636"),
    "accent_hover": ("#2EA043", "#2EA043"),
    "accent2":      ("#1F6FEB", "#1F6FEB"),
    "accent2_hover":("#388BFD", "#388BFD"), # <--- Esta es la que te falta ahora
    "danger":       ("#DA3633", "#DA3633"),
    "warning":      ("#D29922", "#D29922"),
    "text_primary": ("#1A1A1A", "#E6EDF3"),
    "text_muted":   ("#636363", "#8B949E"),
    "border":       ("#D1D1D1", "#30363D"),
}

ctk.set_appearance_mode("system")

APP_DIR = Path(__file__).parent.resolve()

# ═══════════════════════════════════════════════════════════════════════════════
#  Ventana de Actualización
# ═══════════════════════════════════════════════════════════════════════════════
class UpdateWindow(ctk.CTkToplevel):
    def __init__(self, master, remote_version: str):
        super().__init__(master)
        self.title("Nueva Actualización Disponible")
        self.geometry("460x300")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.grab_set()

        # Centrar
        self.after(10, self._center)

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="🚀  Actualización Disponible",
                     font=ctk.CTkFont("Segoe UI", 18, "bold"),
                     text_color=COLORS["text_primary"]).pack(pady=18, padx=20, anchor="w")

        # ── Body ──────────────────────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(body,
                     text=f"Versión instalada:   v{__version__}\n"
                          f"Nueva versión:        v{remote_version}",
                     font=ctk.CTkFont("Consolas", 13),
                     text_color=COLORS["text_muted"],
                     justify="left").pack(anchor="w", pady=(0, 12))

        self.status_label = ctk.CTkLabel(body, text="¿Deseas actualizar ahora?",
                                         font=ctk.CTkFont("Segoe UI", 12),
                                         text_color=COLORS["text_primary"])
        self.status_label.pack(anchor="w")

        self.progress = ctk.CTkProgressBar(body, width=400, progress_color=COLORS["accent2"])
        self.progress.pack(fill="x", pady=(12, 0))
        self.progress.set(0)

        # ── Botones ───────────────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(0, 20))

        self.btn_update = ctk.CTkButton(btn_frame, text="Actualizar ahora",
                                        fg_color=COLORS["accent2"],
                                        hover_color=COLORS["accent2_hover"],
                                        font=ctk.CTkFont("Segoe UI", 13, "bold"),
                                        command=self._start_update, width=180, height=38)
        self.btn_update.pack(side="left")

        ctk.CTkButton(btn_frame, text="Más tarde",
                      fg_color=COLORS["bg_input"],
                      hover_color=COLORS["border"],
                      font=ctk.CTkFont("Segoe UI", 13),
                      command=self.destroy, width=120, height=38).pack(side="left", padx=(10, 0))

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _start_update(self):
        self.btn_update.configure(state="disabled", text="Actualizando...")
        updater.apply_update_async(
            progress_cb=lambda p: self.after(0, lambda: self.progress.set(p / 100)),
            status_cb=lambda s: self.after(0, lambda: self.status_label.configure(text=s)),
            done_cb=self._on_done
        )

    def _on_done(self, success: bool):
        if success:
            self.after(0, lambda: messagebox.showinfo(
                "Actualización lista",
                "¡Actualización aplicada!\nReinicia la aplicación para usar la nueva versión.",
                parent=self
            ))
        else:
            self.after(0, lambda: messagebox.showerror(
                "Error",
                "No se pudo aplicar la actualización.\nVerifica tu conexión a internet.",
                parent=self
            ))
        self.after(0, self.destroy)


# ═══════════════════════════════════════════════════════════════════════════════
#  Diálogo de Progreso de Validación
# ═══════════════════════════════════════════════════════════════════════════════
class ProgressDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Procesando..."):
        super().__init__(master)
        self.title(title)
        self.geometry("400x160")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.grab_set()
        self.after(10, self._center)

        ctk.CTkLabel(self, text=title,
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=COLORS["text_primary"]).pack(pady=(24, 8))
        self.label = ctk.CTkLabel(self, text="Iniciando...",
                                  font=ctk.CTkFont("Segoe UI", 12),
                                  text_color=COLORS["text_muted"])
        self.label.pack()
        self.bar = ctk.CTkProgressBar(self, width=340, progress_color=COLORS["accent"])
        self.bar.pack(pady=14)
        self.bar.set(0)

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def update_progress(self, pct: float, msg: str = ""):
        self.bar.set(pct / 100)
        if msg:
            self.label.configure(text=msg)
        self.update()


# ═══════════════════════════════════════════════════════════════════════════════
#  Tarjeta de Validador
# ═══════════════════════════════════════════════════════════════════════════════
class ValidatorCard(ctk.CTkFrame):
    """Tarjeta reutilizable para cada módulo de validación"""

    def __init__(self, master, title: str, description: str,
                 icon: str = "📋", run_callback=None, **kwargs):
        super().__init__(master,
                         fg_color=COLORS["bg_card"],
                         border_color=COLORS["border"],
                         border_width=1,
                         corner_radius=10,
                         **kwargs)
        self._run_cb = run_callback
        self._file_path = tk.StringVar(value="")

        # ── Header de tarjeta ─────────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 4))

        ctk.CTkLabel(top, text=icon, font=ctk.CTkFont(size=22)).pack(side="left")
        ctk.CTkLabel(top, text=title,
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=COLORS["text_primary"]).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(self, text=description,
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=COLORS["text_muted"],
                     wraplength=380, justify="left").pack(anchor="w", padx=16, pady=(0, 10))

        # ── Selector de archivo ───────────────────────────────────────────────
        file_row = ctk.CTkFrame(self, fg_color="transparent")
        file_row.pack(fill="x", padx=16, pady=(0, 4))

        self.file_entry = ctk.CTkEntry(file_row,
                                       textvariable=self._file_path,
                                       placeholder_text="Seleccionar archivo Excel...",
                                       fg_color=COLORS["bg_input"],
                                       border_color=COLORS["border"],
                                       font=ctk.CTkFont("Consolas", 11),
                                       height=34)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(file_row, text="📂 Abrir",
                      fg_color=COLORS["bg_input"],
                      hover_color=COLORS["border"],
                      font=ctk.CTkFont("Segoe UI", 12),
                      width=80, height=34,
                      command=self._browse).pack(side="right")

        # ── Botón ejecutar ────────────────────────────────────────────────────
        ctk.CTkButton(self, text="▶  Ejecutar validación",
                      fg_color=COLORS["accent"],
                      hover_color=COLORS["accent_hover"],
                      font=ctk.CTkFont("Segoe UI", 13, "bold"),
                      height=36,
                      command=self._execute).pack(fill="x", padx=16, pady=(4, 14))

    def _browse(self):
        path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls *.csv"), ("All files", "*.*")]
        )
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
#  Ventana Principal
# ═══════════════════════════════════════════════════════════════════════════════
class App(ctk.CTk):

    def _run_crear_hc(self):
        try:
            from crear_hc.crear import GesiApp
            # USAR 'self.nueva_ventana' en lugar de una variable local
            # Esto mantiene la ventana viva en la memoria
            self.nueva_ventana = GesiApp(self) 
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al abrir ventana: {e}")
            
            
            
    def __init__(self):
        super().__init__()
        self.title(f"Odin  ·  v{__version__}")
        self.geometry("860x680")
        self.minsize(720, 560)
        self.configure(fg_color=COLORS["bg_dark"])
        self._center_window()

        self.url_api = "https://www.trakio.pro/areas"
        self.areas = self.cargar_areas_api()

        # Ícono (si existe)
        ico = APP_DIR / "img" / "logo.ico"
        if ico.exists():
            try:
                self.iconbitmap(str(ico))
            except Exception:
                pass

        self._build_ui()
        # Verificar actualizaciones al arrancar (sin bloquear)
        updater.check_update_async(self._on_update_check)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=COLORS["bg_card"],
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / marca
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(24, 0))
        ctk.CTkLabel(logo_frame, text="⚙️",
                     font=ctk.CTkFont(size=32)).pack()
        ctk.CTkLabel(logo_frame, text="Validators\nGesi",
                     font=ctk.CTkFont("Segoe UI", 16, "bold"),
                     text_color=COLORS["text_primary"],
                     justify="center").pack()
        ctk.CTkLabel(logo_frame, text=f"v{__version__}",
                     font=ctk.CTkFont("Consolas", 10),
                     text_color=COLORS["text_muted"]).pack(pady=(2, 16))

        ctk.CTkFrame(self.sidebar, height=1,
                     fg_color=COLORS["border"]).pack(fill="x", padx=16)

        # Navegación
        nav_items = [
            ("🏠  Inicio",         "home"),
            ("✅  Validadores",    "validators"),
            ("▶  Ejecutar HC",         "execute_HC"),
            ("📊  Reportes",       "reports"),
            ("⚙️  Configuración",  "settings"),
        ]
        self._nav_btns = {}
        for label, key in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w",
                font=ctk.CTkFont("Segoe UI", 13),
                fg_color="transparent",
                hover_color=COLORS["bg_input"],
                text_color=COLORS["text_primary"],
                height=40,
                command=lambda k=key: self._navigate(k)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._nav_btns[key] = btn

        # Espacio flexible
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="y", expand=True)

        # Botón actualizar en sidebar
        self.btn_update_sidebar = ctk.CTkButton(
            self.sidebar, text="🔄  Buscar actualización",
            font=ctk.CTkFont("Segoe UI", 11),
            fg_color=COLORS["bg_input"],
            hover_color=COLORS["border"],
            text_color=COLORS["text_muted"],
            height=34,
            command=self._manual_update_check
        )
        self.btn_update_sidebar.pack(fill="x", padx=12, pady=(0, 20))

        # ── Área de contenido ─────────────────────────────────────────────────
        self.content = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                              scrollbar_button_color=COLORS["border"])
        self.content.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        # Banner de notificación
        self.notif_bar = ctk.CTkFrame(self, fg_color=COLORS["accent2"],
                                      corner_radius=0, height=36)
        self.notif_bar.pack_forget()  # oculto por defecto
        self._notif_label = ctk.CTkLabel(self.notif_bar,
                                         text="",
                                         font=ctk.CTkFont("Segoe UI", 12),
                                         text_color="white")
        self._notif_label.pack(side="left", padx=16)
        ctk.CTkButton(self.notif_bar, text="Ver →", width=80, height=26,
                      fg_color="white", text_color=COLORS["accent2"],
                      hover_color="#E0E0E0",
                      command=self._show_update_dialog).pack(side="right", padx=12, pady=4)

        self._remote_version = None
        self._navigate("home")

    # ── Navegación ────────────────────────────────────────────────────────────
    def _navigate(self, key: str):
        for k, btn in self._nav_btns.items():
            btn.configure(fg_color=COLORS["accent2"] if k == key else "transparent")

        for w in self.content.winfo_children():
            w.destroy()

        pages = {
            "home":       self._page_home,
            "validators": self._page_validators,
            "reports":    self._page_reports,
            "settings":   self._page_settings,
            "execute_HC": self._page_execute_hc,
        }
        pages.get(key, self._page_home)()


    def _page_execute_hc(self):
        frame = self.content

        ctk.CTkLabel(frame, text="Creación en Herramienta de control",
                     font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=28, pady=(28, 4))
        
        ctk.CTkLabel(frame, text="Carga tu archivo para la creación automática de consecutivos en la herramienta de control.",
                     font=ctk.CTkFont("Segoe UI", 12),
                     text_color=COLORS["text_muted"]).pack(anchor="w", padx=28, pady=(0, 20))

        # Tarjeta de ejecución
        card = ctk.CTkFrame(frame, fg_color=COLORS["bg_card"], 
                            border_color=COLORS["border"], border_width=1, corner_radius=10)
        card.pack(fill="x", padx=24, pady=10)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=20, pady=20)

        ctk.CTkLabel(inner, text="🚀", font=ctk.CTkFont(size=40)).pack()
        ctk.CTkLabel(inner, text="Módulo Crear HC", 
                     font=ctk.CTkFont("Segoe UI", 16, "bold")).pack(pady=(10, 5))
        ctk.CTkLabel(inner, text="Al presionar el botón se abrirá una nueva ventana\npara gestionar la creación de consecutivos.",
                     font=ctk.CTkFont("Segoe UI", 12), text_color=COLORS["text_muted"],
                     justify="center").pack(pady=(0, 20))

        ctk.CTkButton(inner, text="Ejecutar",
                      fg_color=COLORS["accent2"],
                      hover_color=COLORS["accent2_hover"],
                      font=ctk.CTkFont("Segoe UI", 13, "bold"),
                      height=40, width=280,
                      command=self._run_crear_hc).pack()

    # ── Página: Inicio ────────────────────────────────────────────────────────
    def _page_home(self):
        frame = self.content

        ctk.CTkLabel(frame, text="Bienvenido a Odin",
                     font=ctk.CTkFont("Segoe UI", 22, "bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=28, pady=(28, 4))

        ctk.CTkLabel(frame, text="Valida y depura tus archivos Excel con reglas de negocio.",
                     font=ctk.CTkFont("Segoe UI", 13),
                     text_color=COLORS["text_muted"]).pack(anchor="w", padx=28, pady=(0, 24))

        # Tarjetas de resumen rápido
        grid = ctk.CTkFrame(frame, fg_color="transparent")
        grid.pack(fill="x", padx=24)
        grid.columnconfigure((0, 1, 2), weight=1, uniform="col")

        stats = [
            ("📂", "Validadores", "módulos\ndisponibles", COLORS["accent2"]),
            ("✅", "Versión",     f"v{__version__}\nactualizado", COLORS["accent"]),
            ("🔄", "Auto-update", "GitHub\nintegrado", COLORS["warning"]),
        ]
        for col, (icon, title, val, color) in enumerate(stats):
            card = ctk.CTkFrame(grid, fg_color=COLORS["bg_card"],
                                border_color=color, border_width=1, corner_radius=10)
            card.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=26)).pack(pady=(16, 4))
            ctk.CTkLabel(card, text=title,
                         font=ctk.CTkFont("Segoe UI", 13, "bold"),
                         text_color=COLORS["text_primary"]).pack()
            ctk.CTkLabel(card, text=val,
                         font=ctk.CTkFont("Segoe UI", 11),
                         text_color=COLORS["text_muted"],
                         justify="center").pack(pady=(2, 16))

        # Acceso rápido
        ctk.CTkLabel(frame, text="Acceso rápido",
                     font=ctk.CTkFont("Segoe UI", 15, "bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=28, pady=(28, 8))

        
        ctk.CTkButton(frame, text="▶ Creacion en herramienta de control",
                      fg_color=COLORS["accent"],
                      hover_color=COLORS["accent2_hover"],
                      font=ctk.CTkFont("Segoe UI", 13, "bold"),
                      height=40, width=280,
                      command=self._run_crear_hc).pack(anchor="w", padx=28, pady=(28, 8))

        ctk.CTkButton(frame, text="▶  Ir a Validadores",
                      fg_color=COLORS["accent"],
                      hover_color=COLORS["accent_hover"],
                      font=ctk.CTkFont("Segoe UI", 13, "bold"),
                      height=42, width=240,
                      command=lambda: self._navigate("validators")).pack(anchor="w", padx=28)
    # ── Página: Validadores ───────────────────────────────────────────────────
    def _page_validators(self):
        # Limpiar frame principal
        for widget in self.content.winfo_children():
            widget.destroy()
            
        frame = self.content
        
        # Intentar recargar áreas por si hubo cambios en el servidor
        nuevas_areas = self.cargar_areas_api()
        if nuevas_areas: 
            self.areas = nuevas_areas

        # Layout: Izquierda (Entornos) | Derecha (Gestión)
        # Usamos un Frame normal para el container, no el scrollable directamente 
        # para que el diseño no se rompa
        container = ctk.CTkFrame(frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # --- PANEL IZQUIERDO (ENTORNOS) ---
        self.env_sidebar = ctk.CTkFrame(container, width=220, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        self.env_sidebar.pack(side="left", fill="y", padx=(0, 15))
        self.env_sidebar.pack_propagate(False)

        ctk.CTkLabel(self.env_sidebar, text="ENTORNOS", font=("Segoe UI", 14, "bold")).pack(pady=15)
        
        ctk.CTkButton(self.env_sidebar, text="+ Nuevo Entorno", fg_color=COLORS["accent"], 
                     hover_color=COLORS["accent_hover"], command=self.agregar_entorno_ui).pack(fill="x", padx=10, pady=5)

        # Scrollable interno para los botones de entornos
        self.env_list_frame = ctk.CTkScrollableFrame(self.env_sidebar, fg_color="transparent")
        self.env_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- PANEL DERECHO (DETALLES) ---
        self.details_panel = ctk.CTkScrollableFrame(container, fg_color=COLORS["bg_card"], border_width=1, border_color=COLORS["border"])
        self.details_panel.pack(side="right", fill="both", expand=True)
        
        self.lbl_empty = ctk.CTkLabel(self.details_panel, text="Seleccione un entorno para gestionar", text_color=COLORS["text_muted"])
        self.lbl_empty.pack(pady=100)

        # Ahora sí, llenar la lista
        self.actualizar_lista_entornos()
    
    def cargar_areas_api(self):
        try:
            # Importa requests si no lo has hecho arriba
            import requests 
            response = requests.get(self.url_api, timeout=5)
            if response.status_code == 200:
                print("API: Áreas cargadas correctamente")
                return response.json()
            else:
                print(f"API Error: Código {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error de conexión API: {e}")
            return {}
    def agregar_validador_logic(self, area):
        nombre_validador = ctk.CTkInputDialog(title="Agregar Validador", text="Ingrese el nombre del validador:")
        nombre_validador_result = nombre_validador.get_input()
        
        if not nombre_validador_result:
            return
        
        # Verificar si ya existe
        if any(v['nombre'] == nombre_validador_result for v in self.areas[area]):
            messagebox.showerror("Error", "El validador ya existe.")
            return
        
        nuevo_validador = {"nombre": nombre_validador_result, "reglas": []}
        self.areas[area].append(nuevo_validador)
        
        # Guardar en la API y refrescar
        self.guardar_areas_api(area, self.areas[area])
        self.seleccionar_entorno_ui(area)

    def eliminar_area_logic(self, area):
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar el entorno '{area}'?"):
            try:
                response = requests.delete(f"{self.url_api}/{area}")
                if response.status_code == 204 or response.status_code == 200:
                    del self.areas[area]
                    self.actualizar_lista_entornos()
                    # Limpiar panel derecho
                    for widget in self.details_panel.winfo_children():
                        widget.destroy()
                    messagebox.showinfo("Éxito", "Entorno eliminado.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def editar_regla_logic(self, area, validador, regla):
        # Aquí puedes implementar la ventana emergente de edición 
        # que tenías en tu código anterior
        print(f"Editando regla: {regla}")

    def guardar_areas_api(self, nombre_area, datos_area):
        try:
            url_actualizar = f"{self.url_api}/{nombre_area}"
            requests.put(url_actualizar, json={"area": datos_area})
        except Exception as e:
            print(f"Error al guardar en API: {e}")
    def actualizar_lista_entornos(self):
        print(f"Debug: Áreas actuales -> {self.areas}") # Mira esto en tu consola
        for widget in self.env_list_frame.winfo_children():
            widget.destroy()
            
        for nombre in self.areas:
            btn = ctk.CTkButton(self.env_list_frame, text=nombre, fg_color="transparent", 
                               anchor="w", text_color=COLORS["text_primary"],
                               command=lambda n=nombre: self.seleccionar_entorno_ui(n))
            btn.pack(fill="x", pady=2)

    def seleccionar_entorno_ui(self, nombre_entorno):
        for widget in self.details_panel.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.details_panel, text=f"Validadores: {nombre_entorno}", 
                     font=("Segoe UI", 18, "bold")).pack(pady=10, padx=20, anchor="w")

        # Listar Validadores
        for val in self.areas[nombre_entorno]:
            val_btn = ctk.CTkButton(self.details_panel, text=f"📋 {val['nombre']}", 
                                   fg_color=COLORS["bg_input"], anchor="w",
                                   command=lambda v=val: self.gestionar_reglas_ui(nombre_entorno, v))
            val_btn.pack(fill="x", padx=20, pady=5)

        # Botón Agregar Validador
        ctk.CTkButton(self.details_panel, text="+ Agregar Validador", 
                     command=lambda: self.agregar_validador_logic(nombre_entorno)).pack(pady=20)
        
        # Botón Eliminar Entorno (Rojo)
        ctk.CTkButton(self.details_panel, text="Eliminar este Entorno", fg_color=COLORS["danger"],
                     command=lambda: self.eliminar_area_logic(nombre_entorno)).pack(pady=10)

    def agregar_entorno_ui(self):
        dialog = ctk.CTkInputDialog(text="Nombre del nuevo entorno:", title="Nuevo Entorno")
        res = dialog.get_input()
        if res and res not in self.areas:
            self.areas[res] = []
            # Aquí llamarías a tu función PUT de la API
            self.actualizar_lista_entornos()  


    def gestionar_reglas_ui(self, area, validador):
        # Limpiar panel derecho
        for widget in self.details_panel.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(self.details_panel, text=f"Reglas: {validador['nombre']}", font=("Segoe UI", 16, "bold")).pack(pady=10)

        for i, regla in enumerate(validador["reglas"]):
            ctk.CTkButton(self.details_panel, text=f"Regla {i+1}: {list(regla.values())[0]}",
                         command=lambda r=regla: self.editar_regla_logic(area, validador, r)).pack(fill="x", padx=20, pady=2)

        # Botón Analizar (El que dispara tu lógica de analizar_excel_2)
        ctk.CTkButton(self.details_panel, text="📊 ANALIZAR EXCEL", fg_color=COLORS["accent2"],
                     command=lambda: analizar_excel_2(validador)).pack(pady=20, padx=20, fill="x")
        
        ctk.CTkButton(self.details_panel, text="Volver", command=lambda: self.seleccionar_entorno_ui(area)).pack()
    # ── Página: Reportes ──────────────────────────────────────────────────────
    def _page_reports(self):
        frame = self.content
        ctk.CTkLabel(frame, text="Reportes",
                     font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=28, pady=(28, 16))

        ctk.CTkLabel(frame,
                     text="Los archivos de reporte generados por las validaciones\naparecerán aquí.",
                     font=ctk.CTkFont("Segoe UI", 13),
                     text_color=COLORS["text_muted"],
                     justify="left").pack(padx=28)

        output_dir = APP_DIR / "output"
        output_dir.mkdir(exist_ok=True)

        reports = list(output_dir.glob("*.xlsx")) + list(output_dir.glob("*.csv"))

        if not reports:
            ctk.CTkLabel(frame, text="📭  Sin reportes aún",
                         font=ctk.CTkFont("Segoe UI", 14),
                         text_color=COLORS["text_muted"]).pack(pady=40)
            return

        for rp in sorted(reports, key=lambda x: x.stat().st_mtime, reverse=True):
            row = ctk.CTkFrame(frame, fg_color=COLORS["bg_card"],
                               border_color=COLORS["border"], border_width=1, corner_radius=8)
            row.pack(fill="x", padx=24, pady=4)
            ctk.CTkLabel(row, text=f"📄 {rp.name}",
                         font=ctk.CTkFont("Consolas", 12),
                         text_color=COLORS["text_primary"]).pack(side="left", padx=14, pady=10)
            ctk.CTkButton(row, text="Abrir carpeta", width=120, height=28,
                          fg_color=COLORS["bg_input"],
                          hover_color=COLORS["border"],
                          command=lambda p=rp: os.startfile(str(p.parent))
                          ).pack(side="right", padx=10)

    # ── Página: Configuración ─────────────────────────────────────────────────
    def _page_settings(self):
        frame = self.content
        ctk.CTkLabel(frame, text="Configuración",
                     font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=28, pady=(28, 20))

        # Sección actualización
        self._settings_section(frame, "🔄  Actualizaciones")

        info = ctk.CTkFrame(frame, fg_color=COLORS["bg_card"],
                            border_color=COLORS["border"], border_width=1, corner_radius=8)
        info.pack(fill="x", padx=24, pady=(0, 12))

        ctk.CTkLabel(info, text=f"Versión instalada: v{__version__}",
                     font=ctk.CTkFont("Consolas", 12),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=16, pady=(12, 2))
        ctk.CTkLabel(info,
                     text="Las actualizaciones se descargan directamente de GitHub\n"
                          "y se aplican sin necesidad de reinstalar el programa.",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=COLORS["text_muted"]).pack(anchor="w", padx=16, pady=(0, 12))

        ctk.CTkButton(info, text="Verificar actualizaciones ahora",
                      fg_color=COLORS["accent2"],
                      hover_color=COLORS["accent2_hover"],
                      font=ctk.CTkFont("Segoe UI", 12, "bold"),
                      height=36, width=260,
                      command=self._manual_update_check).pack(anchor="w", padx=16, pady=(0, 14))

        # Sección apariencia
        self._settings_section(frame, "🎨  Apariencia")
        ap = ctk.CTkFrame(frame, fg_color=COLORS["bg_card"],
                          border_color=COLORS["border"], border_width=1, corner_radius=8)
        ap.pack(fill="x", padx=24, pady=(0, 12))
        row = ctk.CTkFrame(ap, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(row, text="Tema:", font=ctk.CTkFont("Segoe UI", 12),
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkOptionMenu(row, values=["Oscuro", "Claro", "Sistema"],
                          fg_color=COLORS["bg_input"],
                          button_color=COLORS["accent2"],
                          font=ctk.CTkFont("Segoe UI", 12),
                          command=self._change_theme).pack(side="left", padx=12)

    def _settings_section(self, parent, text: str):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=COLORS["text_muted"]).pack(anchor="w", padx=28, pady=(8, 4))

    def _change_theme(self, choice):
        if choice == "Oscuro":
            ctk.set_appearance_mode("dark")
        elif choice == "Claro":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
            
        # TRUCO: A veces CustomTkinter necesita un pequeño empujón para refrescar 
        # los colores personalizados. Forzamos un redibujado de la página:
        self._page_settings()

    # ── Callbacks de validadores ──────────────────────────────────────────────
    def _run_validator(self, file_path: str, module_name: str, label: str):
        """Lanza un validador en hilo secundario mostrando progreso."""
        dlg = ProgressDialog(self, title=f"Validando: {label}")

        def _work():
            try:
                # Importar dinámicamente el módulo de validación
                import importlib
                mod = importlib.import_module(f"validadores.{module_name}")
                dlg.update_progress(10, "Leyendo archivo...")
                result = mod.validate(file_path,
                                      progress_cb=lambda p, m: self.after(0,
                                          lambda: dlg.update_progress(p, m)))
                self.after(0, dlg.destroy)
                if result.get("ok"):
                    self.after(0, lambda: messagebox.showinfo(
                        "Validación completa",
                        f"✅ {result.get('message', 'Sin errores encontrados.')}"
                    ))
                else:
                    self.after(0, lambda: messagebox.showwarning(
                        "Validación con errores",
                        f"⚠️ {result.get('message', 'Se encontraron errores.')}"
                    ))
            except ModuleNotFoundError:
                self.after(0, dlg.destroy)
                self.after(0, lambda: messagebox.showerror(
                    "Módulo no encontrado",
                    f"El módulo 'validadores/{module_name}.py' no existe aún.\n"
                    "Agrega el módulo en la carpeta /validadores/ siguiendo la interfaz:\n\n"
                    "def validate(file_path, progress_cb=None) -> dict"
                ))
            except Exception as e:
                self.after(0, dlg.destroy)
                self.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=_work, daemon=True).start()

    def _run_validator_beneficiarios(self, path):
        self._run_validator(path, "beneficiarios", "Beneficiarios")

    def _run_validator_actividades(self, path):
        self._run_validator(path, "actividades", "Actividades")

    def _run_validator_recursos(self, path):
        self._run_validator(path, "recursos", "Recursos")

    def _run_validator_indicadores(self, path):
        self._run_validator(path, "indicadores", "Indicadores")

    # ── Auto-actualización ────────────────────────────────────────────────────
    def _on_update_check(self, result: dict):
        """Llamado cuando termina la verificación en segundo plano."""
        if result.get("available"):
            self._remote_version = result["remote_version"]
            self.after(0, self._show_update_banner)

    def _show_update_banner(self):
        self._notif_label.configure(
            text=f"🚀  Nueva versión disponible: v{self._remote_version}"
        )
        # Insertar banner entre sidebar y content
        self.notif_bar.pack(fill="x", after=self.sidebar)
        self.notif_bar.pack(fill="x", side="top")
        # Reordenar: el banner va arriba del content
        self.notif_bar.lift()

    def _show_update_dialog(self):
        if self._remote_version:
            UpdateWindow(self, self._remote_version)

    def _manual_update_check(self):
        self.btn_update_sidebar.configure(text="🔄  Verificando...", state="disabled")

        def _after(result):
            self.after(0, lambda: self.btn_update_sidebar.configure(
                text="🔄  Buscar actualización", state="normal"
            ))
            if result.get("available"):
                self._remote_version = result["remote_version"]
                self.after(0, self._show_update_dialog)
            elif "error" in result:
                self.after(0, lambda: messagebox.showwarning(
                    "Sin conexión",
                    "No se pudo verificar actualizaciones.\nRevisar conexión a internet."
                ))
            else:
                self.after(0, lambda: messagebox.showinfo(
                    "Sin actualizaciones",
                    f"✅ Estás usando la versión más reciente (v{__version__})."
                ))

        updater.check_update_async(_after)

    def _center_window(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")


# ═══════════════════════════════════════════════════════════════════════════════
def index_open():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    index_open()