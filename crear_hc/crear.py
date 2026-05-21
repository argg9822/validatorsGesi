import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
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

# ── Paleta azul cobalto — coherente con Odin/index ────────────────────────────
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
    "text1":        ("#0A1628", "#EDF2FF"),
    "text2":        ("#3B5070", "#7EA8D4"),
    "text3":        ("#6B85A0", "#3D6080"),
    "border":       ("#D8E5F5", "#162035"),
    "divider":      ("#E8EFF8", "#111D2E"),
    "log_bg":       ("#F8FAFF", "#070E1A"),
    "log_fg":       ("#1B3A6B", "#4A9EE8"),
}

# Helper: extrae el valor del modo actual (índice 1 = dark, 0 = light)
def _c(key):
    import customtkinter as _ctk
    idx = 1 if _ctk.get_appearance_mode() == "Dark" else 0
    v = C[key]
    return v[idx] if isinstance(v, tuple) else v


def _divider(parent, px=0, py=4):
    ctk.CTkFrame(parent, height=1, fg_color=C["divider"],
                 corner_radius=0).pack(fill="x", padx=px, pady=py)


def _section_lbl(parent, text):
    ctk.CTkLabel(parent, text=text.upper(),
                 font=ctk.CTkFont("Consolas", 9),
                 text_color=C["text3"]).pack(anchor="w", padx=0, pady=(14, 4))
class GesiApp(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master, fg_color=C["bg"])

        # ── Estado interno ──
        self.nombres = None
        self.driver = None
        self.captcha_listo = threading.Event()
        self.confirmacion_si = threading.Event()
        self.start_time   = None

        self._build()

    def _center(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=210,
                                    fg_color=C["sidebar"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Divisor
        ctk.CTkFrame(self, width=1, fg_color=C["border"],
                     corner_radius=0).pack(side="left", fill="y")

        # Columna derecha
        right = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        self._build_sidebar()
        self._build_topbar(right)
        self._build_main(right)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = self.sidebar

        # Logo compacto
        logo = ctk.CTkFrame(sb, fg_color="transparent")
        logo.pack(fill="x", padx=16, pady=(22, 16))

        badge = ctk.CTkFrame(logo, fg_color=C["accent_soft"],
                              width=34, height=34, corner_radius=7)
        badge.pack(side="left")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="G",
                     font=ctk.CTkFont("Segoe UI", 16, "bold"),
                     text_color=C["accent"]).place(relx=0.5, rely=0.5, anchor="center")

        txt = ctk.CTkFrame(logo, fg_color="transparent")
        txt.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(txt, text="GESI",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=C["text1"]).pack(anchor="w")
        ctk.CTkLabel(txt, text="Crear HC",
                     font=ctk.CTkFont("Consolas", 9),
                     text_color=C["text3"]).pack(anchor="w")

        _divider(sb, px=12)

        # Credenciales
        form = ctk.CTkFrame(sb, fg_color="transparent")
        form.pack(fill="x", padx=14, pady=(4, 0))

        _section_lbl(form, "Credenciales")

        ctk.CTkLabel(form, text="Usuario",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=C["text2"]).pack(anchor="w")
        self.user_var = ctk.StringVar()
        ctk.CTkEntry(form, textvariable=self.user_var,
                     placeholder_text="usuario@dominio.com",
                     fg_color=C["card2"], border_color=C["border"],
                     text_color=C["text1"],
                     font=ctk.CTkFont("Segoe UI", 11), height=32
                     ).pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(form, text="Contraseña",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=C["text2"]).pack(anchor="w")
        self.pass_var = ctk.StringVar()
        ctk.CTkEntry(form, textvariable=self.pass_var,
                     placeholder_text="••••••••",
                     show="•",
                     fg_color=C["card2"], border_color=C["border"],
                     text_color=C["text1"],
                     font=ctk.CTkFont("Segoe UI", 11), height=32
                     ).pack(fill="x", pady=(2, 0))

        _divider(form, py=12)

        # Acciones de control
        _section_lbl(form, "Control")

        self.btn_captcha = ctk.CTkButton(
            form, text="✔  Confirmar Captcha",
            fg_color=C["btn2"], hover_color=C["btn2_hover"],
            text_color=C["text2"],
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            height=34, state="disabled",
            command=self.captcha_listo.set)
        self.btn_captcha.pack(fill="x", pady=(0, 6))

        self.btn_proceso_si = ctk.CTkButton(
            form, text="▶  Iniciar digitación",
            fg_color=C["btn"], hover_color=C["btn_hover"],
            text_color="white",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            height=34, state="disabled",
            command=self.confirmacion_si.set)
        self.btn_proceso_si.pack(fill="x")

        # Spacer
        ctk.CTkFrame(sb, fg_color="transparent").pack(fill="y", expand=True)

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self, parent):
        tb = ctk.CTkFrame(parent, fg_color=C["sidebar"],
                          height=48, corner_radius=0)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        ctk.CTkFrame(parent, height=1, fg_color=C["border"],
                     corner_radius=0).pack(fill="x")

        ctk.CTkLabel(tb, text="Automatización GESI",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=C["text1"]).pack(side="left", padx=20)
        ctk.CTkLabel(tb, text="  ·  Motor de digitación HC",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=C["text3"]).pack(side="left")

        # Badge estado
        self._status_badge = ctk.CTkFrame(tb, fg_color=C["accent_soft"],
                                           corner_radius=6)
        self._status_badge.pack(side="right", padx=16)
        self._status_lbl = ctk.CTkLabel(self._status_badge, text="En espera",
                                         font=ctk.CTkFont("Consolas", 9),
                                         text_color=C["accent"])
        self._status_lbl.pack(padx=10, pady=4)

    # ── Panel principal ───────────────────────────────────────────────────────
    def _build_main(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent",
                                         scrollbar_button_color=C["border"])
        scroll.pack(fill="both", expand=True, padx=20, pady=16)

        # ── Fila 1: Selector de archivo ───────────────────────────────────────
        self._file_card(scroll)

        # ── Fila 2: Progreso ──────────────────────────────────────────────────
        self._progress_card(scroll)

        # ── Fila 3: Log ───────────────────────────────────────────────────────
        self._log_card(scroll)

        # ── Fila 4: Botón iniciar ─────────────────────────────────────────────
        self.btn_action = ctk.CTkButton(
            scroll, text="▶  Inicializar motor de automatización",
            fg_color=C["btn"], hover_color=C["btn_hover"],
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            height=42, corner_radius=8,
            command=self.start_thread)
        self.btn_action.pack(fill="x", pady=(4, 8))

    # ── Tarjeta: selector de archivo ──────────────────────────────────────────
    def _file_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=C["card"],
                            border_color=C["border"], border_width=1,
                            corner_radius=8, height=46)
        card.pack(fill="x", pady=(0, 8))
        card.pack_propagate(False)

        ctk.CTkFrame(card, width=3, fg_color=C["accent"],
                     corner_radius=0).pack(side="left", fill="y")

        self.btn_file = ctk.CTkButton(
            card, text="📂  Seleccionar base de datos Excel (.xlsx)",
            fg_color="transparent", hover_color=C["card2"],
            text_color=C["text2"],
            font=ctk.CTkFont("Segoe UI", 11),
            anchor="w",
            command=self.seleccionar_archivo)
        self.btn_file.pack(side="left", fill="both", expand=True, padx=6)

    # ── Tarjeta: progreso ─────────────────────────────────────────────────────
    def _progress_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=C["card"],
                            border_color=C["border"], border_width=1,
                            corner_radius=8)
        card.pack(fill="x", pady=(0, 8))

        ctk.CTkFrame(card, height=2, fg_color=C["accent"],
                     corner_radius=0).pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=12)

        # Fila de métricas
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(fill="x", pady=(0, 8))

        self.lbl_progress = ctk.CTkLabel(row, text="Progreso: 0%",
                                          font=ctk.CTkFont("Consolas", 10, "bold"),
                                          text_color=C["text1"])
        self.lbl_progress.pack(side="left")

        self.lbl_eta = ctk.CTkLabel(row, text="ETA: --:--:--",
                                     font=ctk.CTkFont("Consolas", 10),
                                     text_color=C["text2"])
        self.lbl_eta.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(inner,
                                                fg_color=C["card2"],
                                                progress_color=C["accent"],
                                                height=6, corner_radius=3)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

    # ── Tarjeta: log ─────────────────────────────────────────────────────────
    def _log_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=C["card"],
                            border_color=C["border"], border_width=1,
                            corner_radius=8)
        card.pack(fill="x", pady=(0, 8))

        ctk.CTkFrame(card, height=2, fg_color=C["card2"],
                     corner_radius=0).pack(fill="x")

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(8, 4))
        ctk.CTkLabel(header, text="LOG DEL SISTEMA",
                     font=ctk.CTkFont("Consolas", 9),
                     text_color=C["text3"]).pack(side="left")

        self.txt_log = ctk.CTkTextbox(card,
                                       fg_color=C["log_bg"],
                                       border_width=0,
                                       font=ctk.CTkFont("Consolas", 10),
                                       text_color=C["log_fg"],
                                       corner_radius=0,
                                       height=180)
        self.txt_log.pack(fill="x", padx=0, pady=(0, 0))
        self.txt_log.configure(state="disabled")

    # ── Helpers UI ────────────────────────────────────────────────────────────
    def _set_status(self, text, color_key="accent"):
        self._status_lbl.configure(text=text, text_color=C[color_key])

    def log(self, message, is_success=False):
        t = datetime.now().strftime("%H:%M:%S")
        prefix = "✔" if is_success else "›"
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"[{t}] {prefix}  {message}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")
        self.update_idletasks()

    def update_metrics(self, current, total):
        if current == 0:
            return
        pct = current / total
        self.progress_bar.set(pct)
        self.lbl_progress.configure(text=f"Progreso: {int(pct*100)}%  ({current}/{total})")
        elapsed = time.time() - self.start_time
        eta_sec = (elapsed / current) * (total - current)
        self.lbl_eta.configure(text=f"ETA: {str(timedelta(seconds=int(eta_sec)))}")

    # ── Lógica de negocio (sin cambios) ───────────────────────────────────────
    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar Excel",
            filetypes=[("Excel", "*.xlsx;*.xls")])
        if archivo:
            try:
                wb = load_workbook(archivo)
                self.nombres = wb['Hoja1']
                self.log(f"Base cargada: {Path(archivo).name}", True)
                self.btn_file.configure(
                    text=f"✔  {Path(archivo).name}",
                    text_color=C["success"])
                self._set_status("Archivo listo", "success")
            except Exception as e:
                self.log(f"Error al cargar Excel: {e}")

    def wait_for_element(self, by, value, timeout=15):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value)))

    def start_thread(self):
        if not self.nombres:
            return messagebox.showwarning("Sistema", "Carga un archivo Excel primero.")
        if not self.user_var.get() or not self.pass_var.get():
            return messagebox.showwarning("Sistema", "Las credenciales son obligatorias.")
        threading.Thread(target=self.hc_crear, daemon=True).start()

    def hc_crear(self):
        self.btn_action.configure(state="disabled")
        self._set_status("Iniciando...", "accent")
        try:
            self.log("Iniciando motor Selenium...")
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=options)

            self.driver.get("https://gesiapps.saludcapital.gov.co/GESI_sistemas/login")
            time.sleep(2)

            try:
                self.wait_for_element(By.XPATH,
                    '/html/body/div/div[2]/button[3]', 5).click()
                time.sleep(1)
                self.wait_for_element(By.XPATH,
                    '/html/body/div/div[3]/p[2]/a', 5).click()
                time.sleep(2)
            except:
                self.log("Bypass de seguridad no requerido.")

            self.log("Inyectando credenciales...")
            self.wait_for_element(By.ID, 'usuario').send_keys(self.user_var.get())
            self.wait_for_element(By.ID, 'password').send_keys(self.pass_var.get())
            codigo = self.wait_for_element(By.ID, 'tokenAcceso').get_attribute('value')
            self.wait_for_element(By.ID, 'valorCodigoSeguridad').send_keys(codigo)

            self.log("⚠  Resuelve el Captcha y pulsa 'Confirmar Captcha'")
            self._set_status("Esperando Captcha", "accent")
            self.btn_captcha.configure(state="normal",
                                        fg_color=C["btn"],
                                        text_color="white")
            self.captcha_listo.wait()
            self.captcha_listo.clear()
            self.btn_captcha.configure(state="disabled",
                                        fg_color=C["btn2"],
                                        text_color=C["text2"])
            self.next_step()

        except Exception as e:
            self.log(f"Error crítico: {e}")
            self._set_status("Error", "danger")
            self.btn_action.configure(state="normal")

    def next_step(self):
        try:
            self.log("Navegando al módulo de Historias Clínicas...")
            self.wait_for_element(By.XPATH,
                '/html/body/section/div/div/form/div/div/div[7]/div/div/button').click()
            time.sleep(4)
            self.wait_for_element(By.XPATH,
                '/html/body/div/div/nav/div/div[4]/ul/li[7]').click()
            time.sleep(1)
            self.wait_for_element(By.XPATH,
                '/html/body/div/div/nav/div/div[4]/ul/li[7]/div/ul/li[1]/a').click()
            time.sleep(2)
            self.wait_for_element(By.XPATH,
                '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[7]/input').click()
            time.sleep(1)
            self.wait_for_element(By.XPATH,
                '/html/body/div[2]/div/div[3]/button[1]').click()

            self.log("Sistema listo. Pulsa 'Iniciar digitación' para comenzar.")
            self._set_status("Listo para iniciar", "success")
            self.btn_proceso_si.configure(state="normal")

            self.confirmacion_si.wait()
            self.confirmacion_si.clear()
            self.btn_proceso_si.configure(state="disabled")
            self._set_status("Digitando...", "accent")
            self.si_proceso()

        except Exception as e:
            self.log(f"Error de navegación: {e}")
            self._set_status("Error de navegación", "danger")

    def si_proceso(self):
        total_filas = self.nombres.max_row
        self.start_time = time.time()
        try:
            for i in range(1, total_filas + 1):
                fila = self.nombres[f'A{i}:F{i}'][0]
                ficha_val = fila[0].value
                fecha_val = fila[1].value
                formato = fecha_val.strftime('%d/%m/%Y') if fecha_val else ""
                datos = [ficha_val, formato,
                         fila[2].value, fila[3].value,
                         fila[4].value, fila[5].value]
                self.log(f"Fila {i}/{total_filas}: Ficha {ficha_val}")
                self.DatosCrearSi(datos)
                self.wait_for_element(By.XPATH,
                    '/html/body/div[2]/div/div[3]/button[1]').click()
                self.wait_for_element(By.XPATH,
                    '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[5]/input').click()
                self.wait_for_element(By.XPATH,
                    '/html/body/div[2]/div/div[3]/button[1]').click()
                self.update_metrics(i, total_filas)

            self.log("✅  Todos los registros procesados.", True)
            self._set_status("Completado", "success")
            messagebox.showinfo("Éxito", "Proceso completado correctamente.")
        except Exception as e:
            self.log(f"Error en fila {i}: {e}")
            self._set_status("Error en proceso", "danger")
        finally:
            self.btn_action.configure(state="normal")

    def DatosCrearSi(self, Datos):
        Select(self.wait_for_element(By.ID, 'Digitado')
               ).select_by_visible_text('Si')
        for field in ['Fecha_entrega_tecnologo',
                      'Fecha_actualizacion',
                      'Fecha_entrega_digitacion']:
            self.wait_for_element(By.ID, field).send_keys(Datos[1])
        self.wait_for_element(By.ID, 'Nro_actualizacion').send_keys('1')
        self.llenar(Datos)
        self.wait_for_element(By.XPATH,
            '/html/body/div/div/main/div/div/div/div[2]/form/div[12]/div/center/input').click()

    def llenar(self, Datos):
        e = self.wait_for_element(By.ID, 'Ficha_fic')
        e.clear(); e.send_keys(Datos[0])

        p = self.wait_for_element(By.ID, 'Nombre_profesional')
        p.clear(); p.send_keys(Datos[2])

        for field in ['Fecha_ingreso', 'Fecha_entrega_profesional']:
            el = self.wait_for_element(By.ID, field)
            el.clear(); el.send_keys(Datos[1])

        Select(self.wait_for_element(By.ID, 'Id_perfil')
               ).select_by_visible_text(str(Datos[5]))

        for attempt in range(10):
            try:
                esp = Select(self.wait_for_element(By.ID, 'Espacio_fic'))
                esp.select_by_visible_text('1 -Hogar')
                time.sleep(1)
                esp.select_by_visible_text(str(Datos[3]))
                time.sleep(1)
                break
            except:
                time.sleep(1)

        Select(self.wait_for_element(By.ID, 'Id_Base')
               ).select_by_visible_text(str(Datos[4]))


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.title("GESI — Intelligence Automation System")
    root.geometry("1100x820")
    root.minsize(1000, 750)
    app = GesiApp(root)
    app.pack(fill="both", expand=True)
    root.mainloop()