import threading
import time
from pathlib import Path
from datetime import datetime
from openpyxl import load_workbook

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import customtkinter as ctk
from tkinter import filedialog, messagebox

# ── Paleta azul cobalto — coherente con crear.py ──────────────────────────────
C = {
    "bg":           ("#F4F7FB", "#0B1220"),
    "sidebar":      ("#FFFFFF", "#080F1C"),
    "card":         ("#FFFFFF", "#0F1A2E"),
    "card2":        ("#F0F5FF", "#111D30"),
    "accent":       ("#1B6ECC", "#4A9EE8"),
    "accent_soft":  ("#EBF3FF", "#0D2040"),
    "btn":          ("#1B6ECC", "#3B8DD4"),
    "btn_hover":    ("#1558A8", "#2A78C0"),
    "btn2":         ("#E8F0FE", "#142236"),
    "btn2_hover":   ("#D4E4FC", "#1B3050"),
    "success":      ("#0F7B4F", "#2ECC8A"),
    "danger":       ("#C0392B", "#E05555"),
    "danger_hover": ("#A03020", "#C04040"),
    "text1":        ("#0A1628", "#EDF2FF"),
    "text2":        ("#3B5070", "#7EA8D4"),
    "text3":        ("#6B85A0", "#3D6080"),
    "border":       ("#D8E5F5", "#162035"),
    "divider":      ("#E8EFF8", "#111D2E"),
    "log_bg":       ("#F8FAFF", "#070E1A"),
    "log_fg":       ("#1B3A6B", "#4A9EE8"),
}


def _divider(parent, px=0, py=4):
    ctk.CTkFrame(parent, height=1, fg_color=C["divider"],
                 corner_radius=0).pack(fill="x", padx=px, pady=py)


class OPENUI(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master, fg_color=C["bg"])

        self.nombres = None
        self.fichas  = []
        self.driver  = None
        self.captcha_listo    = threading.Event()
        self.confirmacion_si  = threading.Event()
        self.stop_event       = threading.Event()
        self._tiempo_inicio   = None
        self._tick_activo     = False
        self._eta_segundos    = None

        self.entorno_var = ctk.StringVar(value="")
        self.entorno_xpath = {
            "Laboral": {
                "entorno":   "/html/body/div[1]/div/nav/div/div[4]/ul/li[6]/a",
                "base":      "/html/body/div[1]/div/nav/div/div[4]/ul/li[6]/div/ul/form[6]/li/a",
                "seccion_1": "controlBotonSeccion322",
                "seccion_2": "controlBotonSeccion323",
            },
            "Educativo": {
                "entorno":   "/html/body/div[1]/div/nav/div/div[4]/ul/li[5]/a",
                "base":      "/html/body/div[1]/div/nav/div/div[4]/ul/li[5]/div/ul/form[6]/li/a",
                "seccion_1": "controlBotonSeccion287",
                "seccion_2": "controlBotonSeccion288",
            },
            "Comunitario": {
                "entorno":   "/html/body/div[1]/div/nav/div/div[4]/ul/li[4]/a",
                "base":      "/html/body/div[1]/div/nav/div/div[4]/ul/li[4]/div/ul/form[5]/li/a",
                "seccion_1": "controlBotonSeccion318",
                "seccion_2": "controlBotonSeccion319",
            },
            "Institucional": {
                "entorno":   "/html/body/div/div/nav/div/div[4]/ul/li[3]/a",
                "base":      "/html/body/div/div/nav/div/div[4]/ul/li[3]/div/ul/form[10]/li/a",
                "seccion_1": "controlBotonSeccion314",
                "seccion_2": "controlBotonSeccion315",
            },
        }
        self.solo_calidad_var     = ctk.BooleanVar(value=False)
        self.solo_comprobador_var = ctk.BooleanVar(value=False)

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        self._build_topbar()
        ctk.CTkFrame(self, height=1, fg_color=C["border"],
                     corner_radius=0).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        body.pack(fill="both", expand=True)

        left = ctk.CTkFrame(body, fg_color=C["sidebar"],
                            width=160, corner_radius=0)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkFrame(body, width=1, fg_color=C["border"],
                     corner_radius=0).pack(side="left", fill="y")

        right = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        self._build_left_panel(left)
        self._build_main_panel(right)

    # ── Topbar: logo + credenciales + captcha + status ────────────────────────
    def _build_topbar(self):
        tb = ctk.CTkFrame(self, fg_color=C["sidebar"],
                          height=52, corner_radius=0)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # Badge + título
        badge = ctk.CTkFrame(tb, fg_color=C["accent_soft"],
                              width=34, height=34, corner_radius=7)
        badge.pack(side="left", padx=(14, 0))
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="G",
                     font=ctk.CTkFont("Segoe UI", 16, "bold"),
                     text_color=C["accent"]).place(relx=0.5, rely=0.5, anchor="center")

        ttl = ctk.CTkFrame(tb, fg_color="transparent")
        ttl.pack(side="left", padx=(8, 0))
        ctk.CTkLabel(ttl, text="GesiForm",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=C["text1"]).pack(anchor="w")
        ctk.CTkLabel(ttl, text="Validación de sesiones",
                     font=ctk.CTkFont("Consolas", 8),
                     text_color=C["text3"]).pack(anchor="w")

        ctk.CTkFrame(tb, width=1, fg_color=C["border"],
                     corner_radius=0).pack(side="left", fill="y", padx=14, pady=10)

        # Usuario
        u = ctk.CTkFrame(tb, fg_color="transparent")
        u.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(u, text="Usuario",
                     font=ctk.CTkFont("Segoe UI", 9),
                     text_color=C["text3"]).pack(anchor="w")
        self.user_var = ctk.StringVar()
        ctk.CTkEntry(u, textvariable=self.user_var,
                     placeholder_text="usuario@dominio.com",
                     fg_color=C["card2"], border_color=C["border"],
                     text_color=C["text1"],
                     font=ctk.CTkFont("Segoe UI", 11),
                     width=180, height=28).pack()

        # Contraseña
        p = ctk.CTkFrame(tb, fg_color="transparent")
        p.pack(side="left", padx=(0, 0))
        ctk.CTkLabel(p, text="Contraseña",
                     font=ctk.CTkFont("Segoe UI", 9),
                     text_color=C["text3"]).pack(anchor="w")
        self.pass_var = ctk.StringVar()
        ctk.CTkEntry(p, textvariable=self.pass_var,
                     placeholder_text="••••••••", show="•",
                     fg_color=C["card2"], border_color=C["border"],
                     text_color=C["text1"],
                     font=ctk.CTkFont("Segoe UI", 11),
                     width=150, height=28).pack()

        ctk.CTkFrame(tb, width=1, fg_color=C["border"],
                     corner_radius=0).pack(side="left", fill="y", padx=14, pady=10)

        # Captcha
        cap = ctk.CTkFrame(tb, fg_color="transparent")
        cap.pack(side="left")
        ctk.CTkLabel(cap, text="Captcha",
                     font=ctk.CTkFont("Segoe UI", 9),
                     text_color=C["text3"]).pack(anchor="w")
        self.btn_captcha = ctk.CTkButton(
            cap, text="✔  Confirmar",
            fg_color=C["btn2"], hover_color=C["btn2_hover"],
            text_color=C["text2"],
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            width=130, height=28, state="disabled",
            command=lambda: self.captcha_listo.set())
        self.btn_captcha.pack()

        # Badge de estado
        self._status_badge = ctk.CTkFrame(tb, fg_color=C["accent_soft"],
                                           corner_radius=6)
        self._status_badge.pack(side="right", padx=16)
        self._status_lbl = ctk.CTkLabel(
            self._status_badge, text="En espera",
            font=ctk.CTkFont("Consolas", 9),
            text_color=C["accent"])
        self._status_lbl.pack(padx=10, pady=4)

    # ── Panel izquierdo: entorno + opciones ───────────────────────────────────
    def _build_left_panel(self, parent):
        ctk.CTkLabel(parent, text="ENTORNO",
                     font=ctk.CTkFont("Consolas", 9),
                     text_color=C["text3"]).pack(anchor="w", padx=12, pady=(16, 6))

        ENTORNOS = [
            ("🏭  Laboral",       "Laboral"),
            ("🎓  Educativo",     "Educativo"),
            ("🏘️  Comunitario",   "Comunitario"),
            ("🏥  Institucional", "Institucional"),
        ]
        self._entorno_btns = {}
        for label, valor in ENTORNOS:
            btn = ctk.CTkButton(
                parent, text=label,
                height=30, anchor="w",
                fg_color=C["btn2"], hover_color=C["btn2_hover"],
                text_color=C["text2"],
                font=ctk.CTkFont("Segoe UI", 10),
                command=lambda v=valor: self._seleccionar_entorno(v))
            btn.pack(fill="x", padx=8, pady=2)
            self._entorno_btns[valor] = btn

        _divider(parent, px=8, py=8)

        ctk.CTkLabel(parent, text="OPCIONES",
                     font=ctk.CTkFont("Consolas", 9),
                     text_color=C["text3"]).pack(anchor="w", padx=12, pady=(0, 6))

        self.chk_calidad = ctk.CTkCheckBox(
            parent, text="Solo calidad",
            variable=self.solo_calidad_var,
            fg_color=C["btn"], hover_color=C["btn_hover"],
            text_color=C["text2"],
            font=ctk.CTkFont("Segoe UI", 10),
            command=self._on_opcion_calidad)
        self.chk_calidad.pack(anchor="w", padx=12, pady=(0, 6))

        self.chk_comprobador = ctk.CTkCheckBox(
            parent, text="Solo comprobador",
            variable=self.solo_comprobador_var,
            fg_color=C["btn"], hover_color=C["btn_hover"],
            text_color=C["text2"],
            font=ctk.CTkFont("Segoe UI", 10),
            command=self._on_opcion_comprobador)
        self.chk_comprobador.pack(anchor="w", padx=12)

    # ── Panel principal: archivo + progreso + log + acciones ──────────────────
    def _build_main_panel(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                         scrollbar_button_color=C["border"])
        scroll.pack(fill="both", expand=True, padx=16, pady=12)

        # Selector de archivo
        file_card = ctk.CTkFrame(scroll, fg_color=C["card"],
                                  border_color=C["border"], border_width=1,
                                  corner_radius=8, height=42)
        file_card.pack(fill="x", pady=(0, 8))
        file_card.pack_propagate(False)
        ctk.CTkFrame(file_card, width=3, fg_color=C["accent"],
                     corner_radius=0).pack(side="left", fill="y")
        self.btn_file = ctk.CTkButton(
            file_card,
            text="📂  Seleccionar archivo de Excel",
            fg_color="transparent", hover_color=C["card2"],
            text_color=C["text2"],
            font=ctk.CTkFont("Segoe UI", 11), anchor="w",
            command=self.seleccionar_archivo)
        self.btn_file.pack(side="left", fill="both", expand=True, padx=6)

        # Progreso
        prog_card = ctk.CTkFrame(scroll, fg_color=C["card"],
                                  border_color=C["border"], border_width=1,
                                  corner_radius=8)
        prog_card.pack(fill="x", pady=(0, 8))
        ctk.CTkFrame(prog_card, height=2, fg_color=C["accent"],
                     corner_radius=0).pack(fill="x")
        inner = ctk.CTkFrame(prog_card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=8)

        hdr = ctk.CTkFrame(inner, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 4))
        self._lbl_progreso = ctk.CTkLabel(
            hdr, text="",
            font=ctk.CTkFont("Consolas", 10, "bold"),
            text_color=C["text1"])
        self._lbl_progreso.pack(side="left")
        self._lbl_tiempo = ctk.CTkLabel(
            hdr, text="",
            font=ctk.CTkFont("Consolas", 10),
            text_color=C["text2"])
        self._lbl_tiempo.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(
            inner, fg_color=C["card2"], progress_color=C["accent"],
            height=6, corner_radius=3)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

        # Log
        log_card = ctk.CTkFrame(scroll, fg_color=C["card"],
                                 border_color=C["border"], border_width=1,
                                 corner_radius=8)
        log_card.pack(fill="x", pady=(0, 8))
        ctk.CTkFrame(log_card, height=2, fg_color=C["card2"],
                     corner_radius=0).pack(fill="x")
        ctk.CTkLabel(log_card, text="LOG DEL SISTEMA",
                     font=ctk.CTkFont("Consolas", 9),
                     text_color=C["text3"]).pack(anchor="w", padx=14, pady=(6, 2))
        self.txt_log = ctk.CTkTextbox(
            log_card, fg_color=C["log_bg"], border_width=0,
            font=ctk.CTkFont("Consolas", 10),
            text_color=C["log_fg"], corner_radius=0, height=220)
        self.txt_log.pack(fill="x")
        self.txt_log.configure(state="disabled")

        # Botones de acción
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", pady=(4, 4))

        self.btn_action = ctk.CTkButton(
            btn_row, text="▶  Iniciar validación",
            fg_color=C["btn"], hover_color=C["btn_hover"],
            text_color="white",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            height=36, corner_radius=8,
            command=self.start_thread)
        self.btn_action.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_stop = ctk.CTkButton(
            btn_row, text="⏹  Detener",
            fg_color=C["danger"], hover_color=C["danger_hover"],
            text_color="white",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            height=36, corner_radius=8, state="disabled",
            command=self.detener_validacion)
        self.btn_stop.pack(side="left", ipadx=12)

    # ── Helpers de estado ─────────────────────────────────────────────────────
    def _seleccionar_entorno(self, valor: str):
        if self.entorno_var.get() == valor:
            self.entorno_var.set("")
            self._entorno_btns[valor].configure(
                fg_color=C["btn2"], text_color=C["text2"])
            return
        for _, btn in self._entorno_btns.items():
            btn.configure(fg_color=C["btn2"], text_color=C["text2"])
        self.entorno_var.set(valor)
        self._entorno_btns[valor].configure(fg_color=C["btn"], text_color="white")

    def _on_opcion_calidad(self):
        if self.solo_calidad_var.get():
            self.solo_comprobador_var.set(False)

    def _on_opcion_comprobador(self):
        if self.solo_comprobador_var.get():
            self.solo_calidad_var.set(False)

    # ── Lógica — sin cambios ──────────────────────────────────────────────────
    def log(self, message):
        t = datetime.now().strftime("%H:%M:%S")
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"[{t}] {message}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")
        self.update_idletasks()

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de Excel",
            filetypes=[("Archivos de Excel", "*.xlsx;*.xls")])
        if archivo:
            try:
                wb = load_workbook(archivo)
                self.nombres = wb['Hoja1']
                self.log(f"Archivo cargado: {Path(archivo).name}")
                self.btn_file.configure(text=f"✅ {Path(archivo).name}")
                self.fichas = [
                    str(r[0]).strip()
                    for r in self.nombres.iter_rows(
                        min_col=1, max_col=1, values_only=True)
                    if r[0] is not None and str(r[0]).strip()
                ]
                messagebox.showinfo("Carga exitosa",
                                    f"Se cargaron {len(self.fichas)} fichas")
            except Exception as e:
                self.log(f"Error cargando Excel: {e}")

    def wait_for_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value)))

    def start_thread(self):
        if not self.nombres:
            return messagebox.showwarning("Falta Info", "Carga el Excel primero.")
        self.stop_event.clear()
        self._eta_segundos  = None
        self._tiempo_inicio = datetime.now()
        self._tick_activo   = True
        self._lbl_tiempo.configure(text="⏱  00:00    TIEMPO RESTANTE: --:--")
        self._lbl_progreso.configure(text="")
        self.progress_bar.set(0)
        self.btn_action.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self._tick()
        threading.Thread(target=self.ingresoAplicativo, daemon=True).start()

    def detener_validacion(self):
        self.log("⏹ Deteniendo... se completará la ficha en curso y luego se generará el reporte.")
        self.stop_event.set()
        self.btn_stop.configure(state="disabled")

    def _reset_botones(self):
        self._tick_activo = False
        self.btn_action.configure(state="normal")
        self.btn_stop.configure(state="disabled")

    @staticmethod
    def _fmt_tiempo(seg: int) -> str:
        h = seg // 3600
        m = (seg % 3600) // 60
        s = seg % 60
        return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

    def _tick(self):
        if not self._tick_activo or not self._tiempo_inicio:
            return
        elapsed = int((datetime.now() - self._tiempo_inicio).total_seconds())
        eta_part = (f"    TIEMPO RESTANTE: ~{self._fmt_tiempo(self._eta_segundos)}"
                    if self._eta_segundos is not None else "    TIEMPO RESTANTE: calculando...")
        self._lbl_tiempo.configure(
            text=f"⏱  {self._fmt_tiempo(elapsed)}{eta_part}")
        self.after(1000, self._tick)

    def actualizar_progreso(self, actual: int, total: int):
        pct = actual / total if total else 0
        texto = f"Fichas validadas: {actual} / {total}  ({round(pct * 100)}%)"
        if actual > 0 and self._tiempo_inicio:
            elapsed = (datetime.now() - self._tiempo_inicio).total_seconds()
            self._eta_segundos = int(elapsed / actual * (total - actual))
        self.after(0, lambda: (
            self.progress_bar.set(pct),
            self._lbl_progreso.configure(text=texto),
        ))

    def ingresoAplicativo(self):
        try:
            self.log("Abriendo Chrome...")
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options)

            self.driver.get("https://gesiapps.saludcapital.gov.co/GESI_sistemas/login")
            time.sleep(2)

            try:
                self.wait_for_element(By.XPATH,
                    '/html/body/div/div[2]/button[3]').click()
                time.sleep(1)
                self.wait_for_element(By.XPATH,
                    '/html/body/div/div[3]/p[2]/a').click()
                time.sleep(3)
            except:
                self.log("Omitiendo bypass de seguridad inicial.")

            self.log("Enviando credenciales de usuario...")
            self.wait_for_element(By.ID, 'usuario').send_keys(self.user_var.get())
            self.wait_for_element(By.ID, 'password').send_keys(self.pass_var.get())

            codigo = self.wait_for_element(
                By.ID, 'tokenAcceso').get_attribute('value')
            self.wait_for_element(
                By.ID, 'valorCodigoSeguridad').send_keys(codigo)

            self.log("⚠️ POR FAVOR, RESUELVE EL CAPTCHA Y PRESIONA 'Confirmar Captcha'.")
            self.btn_captcha.configure(state="normal",
                                        fg_color=C["btn"], text_color="white")
            self.captcha_listo.wait()
            self.captcha_listo.clear()
            self.btn_captcha.configure(state="disabled",
                                        fg_color=C["btn2"], text_color=C["text2"])
            self.next_step()

        except Exception as e:
            self.log(f"Error: {e}")
            self.after(0, self._reset_botones)

    def next_step(self):
        self.wait_for_element(By.XPATH,
            '/html/body/section/div/div/form/div/div/div[7]/div/div/button').click()
        try:
            from liveValidator.main import ejecutarValidacion
            ejecutarValidacion(self)
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al abrir ventana: {e}")
        finally:
            self.after(0, self._reset_botones)


def main(master=None):
    if master is None:
        root = ctk.CTk()
        root.title("GESI - Validador sesiones")
        root.geometry("1000x750")
        app = OPENUI(root)
        app.pack(fill="both", expand=True)
        root.mainloop()
    else:
        app = OPENUI(master)
        return app

if __name__ == "__main__":
    main()
