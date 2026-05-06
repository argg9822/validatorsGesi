import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from openpyxl import load_workbook

# Selenium e integraciones
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import customtkinter as ctk
from tkinter import filedialog, messagebox

# ─────────────────────────────────────────────
#  PALETA REFINADA — Midnight & Crimson Elite
# ─────────────────────────────────────────────
COLORS = {
    "bg_void":      "#101214",   # Gris azulado casi negro (Elegante)
    "bg_panel":     "#16191C",   # Panel lateral
    "bg_card":      "#1C2126",   # Tarjetas
    "bg_input":     "#0D0F11",   # Fondo de inputs
    "border_glow":  "#E74C3C",   # Rojo vibrante
    "accent":       "#C0392B",   # Rojo base
    "accent_dim":   "#4A1212",   # Rojo sombra
    "text_main":    "#ECEFF1",   # Blanco suave
    "text_dim":     "#78909C",   # Gris azulado
    "progress_bg":  "#263238",   # Fondo barra
    "success":      "#2ECC71",   # Verde éxito
    "gold":         "#BF9B30"    # Dorado premium
}

class GesiApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)

        self.title("GESI — Intelligence Automation System")
        self.geometry("1100x820")
        self.minsize(1000, 750)
        self.configure(fg_color=COLORS["bg_void"])

        # Asegurar que la ventana esté al frente
        self.after(100, self.lift)
        self.focus_force()

        # ── Estado interno ──
        self.nombres = None
        self.driver = None
        self.captcha_listo = threading.Event()
        self.confirmacion_si = threading.Event()
        
        # Métricas de tiempo
        self.start_time = None

        # Layout principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_panel()

    # ─────────────────────────────────────────
    #  CONSTRUCCIÓN DE UI
    # ─────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color=COLORS["bg_panel"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Header Premium
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", pady=(40, 20), padx=20)
        
        ctk.CTkLabel(header, text="GESI", font=ctk.CTkFont("Georgia", 38, "bold"), text_color=COLORS["border_glow"]).pack()
        ctk.CTkLabel(header, text="SYSTEM ENGINE v2.5", font=ctk.CTkFont("Consolas", 10, "bold"), text_color=COLORS["gold"]).pack()

        ctk.CTkFrame(self.sidebar, height=2, fg_color=COLORS["accent_dim"]).pack(fill="x", padx=40, pady=15)

        # Formulario de Credenciales
        form = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=25)

        self._section_title(form, "CREDENTIALS")
        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()
        
        self.entry_user = self._make_entry(form, self.user_var, "Username / Email")
        self.entry_pass = self._make_entry(form, self.pass_var, "Password", show="●")

        ctk.CTkFrame(form, height=1, fg_color="#2D3436").pack(fill="x", pady=25)

        self._section_title(form, "CONTROL ACTIONS")
        self.btn_captcha = self._make_side_btn(form, "✦ CONFIRM CAPTCHA", "#1A3A5C", self.captcha_listo.set)
        self.btn_proceso_si = self._make_side_btn(form, "✦ START DIGITIZING", COLORS["accent_dim"], self.confirmacion_si.set)

        # Footer Sidebar
        footer_side = ctk.CTkLabel(self.sidebar, text="SECRETARÍA DE SALUD\nBOGOTÁ D.C.", 
                                  font=ctk.CTkFont("Consolas", 9), text_color=COLORS["text_dim"])
        footer_side.pack(side="bottom", pady=20)

    def _build_main_panel(self):
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew", padx=35, pady=35)
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(2, weight=1)

        # 1. Selección de Archivo
        top_card = ctk.CTkFrame(self.main, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color="#2D3436")
        top_card.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        self.btn_file = ctk.CTkButton(top_card, text="◈  SELECT EXCEL DATABASE (.xlsx)", fg_color="transparent", border_width=1, 
                                     border_color=COLORS["text_dim"], text_color=COLORS["text_main"], hover_color="#2D3436",
                                     height=50, font=ctk.CTkFont("Consolas", 12), command=self.seleccionar_archivo)
        self.btn_file.pack(padx=20, pady=20, fill="x")

        # 2. Monitor de Progreso e Inteligencia de Tiempo
        prog_frame = ctk.CTkFrame(self.main, fg_color=COLORS["bg_card"], corner_radius=12, border_width=1, border_color="#2D3436")
        prog_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        inner_prog = ctk.CTkFrame(prog_frame, fg_color="transparent")
        inner_prog.pack(fill="x", padx=25, pady=25)

        time_info = ctk.CTkFrame(inner_prog, fg_color="transparent")
        time_info.pack(fill="x", pady=(0, 12))
        
        self.lbl_progress = ctk.CTkLabel(time_info, text="Progress: 0%", font=ctk.CTkFont("Consolas", 12, "bold"), text_color=COLORS["text_main"])
        self.lbl_progress.pack(side="left")
        
        self.lbl_eta = ctk.CTkLabel(time_info, text="ETA: --:--:--", font=ctk.CTkFont("Consolas", 12, "bold"), text_color=COLORS["border_glow"])
        self.lbl_eta.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(inner_prog, fg_color=COLORS["progress_bg"], progress_color=COLORS["border_glow"], height=12)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x")

        # 3. Consola de Log
        self.txt_log = ctk.CTkTextbox(self.main, fg_color=COLORS["bg_input"], border_width=1, border_color="#2D3436",
                                     font=ctk.CTkFont("Consolas", 12), text_color=COLORS["text_dim"], corner_radius=8)
        self.txt_log.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        self.txt_log.configure(state="disabled")

        # 4. Botón de Acción Principal
        self.btn_action = ctk.CTkButton(self.main, text="⬡  INITIALIZE AUTOMATION ENGINE", fg_color=COLORS["accent"],
                                       hover_color=COLORS["border_glow"], height=65, font=ctk.CTkFont("Georgia", 18, "bold"),
                                       command=self.start_thread)
        self.btn_action.grid(row=3, column=0, sticky="ew")

    # ─────────────────────────────────────────
    #  HELPERS UI
    # ─────────────────────────────────────────
    def _section_title(self, parent, txt):
        ctk.CTkLabel(parent, text=txt, font=ctk.CTkFont("Consolas", 10, "bold"), text_color=COLORS["gold"]).pack(anchor="w", pady=(10, 5))

    def _make_entry(self, parent, var, placeholder, show=None):
        e = ctk.CTkEntry(parent, textvariable=var, placeholder_text=placeholder, height=42, fg_color=COLORS["bg_input"], 
                         border_color="#2D3436", text_color=COLORS["text_main"], show=show)
        e.pack(fill="x", pady=5)
        return e

    def _make_side_btn(self, parent, txt, color, cmd):
        btn = ctk.CTkButton(parent, text=txt, fg_color=color, hover_color=COLORS["accent"], height=42, 
                           state="disabled", font=ctk.CTkFont("Consolas", 11, "bold"), command=cmd)
        btn.pack(fill="x", pady=8)
        return btn

    def log(self, message, is_success=False):
        t = datetime.now().strftime("%H:%M:%S")
        prefix = "✔" if is_success else "›"
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"[{t}] {prefix} {message}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")
        self.update_idletasks()

    def update_metrics(self, current, total):
        if current == 0: return
        percent = current / total
        self.progress_bar.set(percent)
        self.lbl_progress.configure(text=f"Progress: {int(percent*100)}% ({current}/{total})")
        
        # Lógica de Tiempo Restante (ETA)
        elapsed = time.time() - self.start_time
        avg_per_row = elapsed / current
        remaining_rows = total - current
        eta_seconds = remaining_rows * avg_per_row
        
        eta_str = str(timedelta(seconds=int(eta_seconds)))
        self.lbl_eta.configure(text=f"ETA: {eta_str}")

    # ─────────────────────────────────────────
    #  LÓGICA DE NEGOCIO (FULL)
    # ─────────────────────────────────────────
    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(title="Seleccionar Excel", filetypes=[("Excel", "*.xlsx;*.xls")])
        if archivo:
            try:
                wb = load_workbook(archivo)
                self.nombres = wb['Hoja1']
                self.log(f"Database loaded: {Path(archivo).name}", True)
                self.btn_file.configure(text=f"✔  {Path(archivo).name}", text_color=COLORS["success"], border_color=COLORS["success"])
            except Exception as e:
                self.log(f"Excel Load Error: {e}")

    def wait_for_element(self, by, value, timeout=15):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))

    def start_thread(self):
        if not self.nombres:
            return messagebox.showwarning("System", "Please load an Excel file first.")
        if not self.user_var.get() or not self.pass_var.get():
            return messagebox.showwarning("System", "Credentials are required.")
        threading.Thread(target=self.hc_crear, daemon=True).start()

    def hc_crear(self):
        self.btn_action.configure(state="disabled")
        try:
            self.log("Launching Selenium Web Engine...")
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            # Evitar detección de bot básica
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            self.driver.get("https://gesiapps.saludcapital.gov.co/GESI_sistemas/login")
            time.sleep(2)

            # Bypass de seguridad (si aparece)
            try:
                self.wait_for_element(By.XPATH, '/html/body/div/div[2]/button[3]', 5).click()
                time.sleep(1)
                self.wait_for_element(By.XPATH, '/html/body/div/div[3]/p[2]/a', 5).click()
                time.sleep(2)
            except:
                self.log("Security bypass not required.")

            self.log("Injecting credentials...")
            self.wait_for_element(By.ID, 'usuario').send_keys(self.user_var.get())
            self.wait_for_element(By.ID, 'password').send_keys(self.pass_var.get())

            codigo = self.wait_for_element(By.ID, 'tokenAcceso').get_attribute('value')
            self.wait_for_element(By.ID, 'valorCodigoSeguridad').send_keys(codigo)

            self.log("⚠️ ACTION REQUIRED: Solve Captcha and press 'Confirm Captcha'", False)
            self.btn_captcha.configure(state="normal", fg_color="#1F6FEB")

            self.captcha_listo.wait()
            self.captcha_listo.clear()
            self.btn_captcha.configure(state="disabled", fg_color="#1A3A5C")

            self.next_step()

        except Exception as e:
            self.log(f"Critical Error: {e}")
            self.btn_action.configure(state="normal")

    def next_step(self):
        try:
            self.log("Navigating to Clinical Records module...")
            self.wait_for_element(By.XPATH, '/html/body/section/div/div/form/div/div/div[7]/div/div/button').click()
            time.sleep(4)
            self.wait_for_element(By.XPATH, '/html/body/div/div/nav/div/div[4]/ul/li[7]').click()
            time.sleep(1)
            self.wait_for_element(By.XPATH, '/html/body/div/div/nav/div/div[4]/ul/li[7]/div/ul/li[1]/a').click()
            time.sleep(2)
            self.wait_for_element(By.XPATH, '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[7]/input').click()
            time.sleep(1)
            self.wait_for_element(By.XPATH, '/html/body/div[2]/div/div[3]/button[1]').click()

            self.log("System ready. Press 'START DIGITIZING' to begin loop.")
            self.btn_proceso_si.configure(state="normal", fg_color=COLORS["accent"])

            self.confirmacion_si.wait()
            self.confirmacion_si.clear()
            self.btn_proceso_si.configure(state="disabled", fg_color=COLORS["accent_dim"])

            self.si_proceso()
        except Exception as e:
            self.log(f"Navigation Error: {e}")

    def si_proceso(self):
        total_filas = self.nombres.max_row
        self.start_time = time.time()
        
        try:
            for i in range(1, total_filas + 1):
                fila = self.nombres[f'A{i}:F{i}'][0]
                
                # Extracción de datos
                ficha_val = fila[0].value
                fecha_val = fila[1].value
                formato = fecha_val.strftime('%d/%m/%Y') if fecha_val else ""
                
                # Datos: [0:Ficha, 1:Fecha, 2:Profesional, 3:Espacio, 4:Base, 5:Perfil]
                datos = [ficha_val, formato, fila[2].value, fila[3].value, fila[4].value, fila[5].value]
                
                self.log(f"Processing row {i}/{total_filas}: Ficha {ficha_val}")
                
                self.DatosCrearSi(datos)

                # Clicks de confirmación post-llenado
                self.wait_for_element(By.XPATH, '/html/body/div[2]/div/div[3]/button[1]').click()
                self.wait_for_element(By.XPATH, '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[5]/input').click()
                self.wait_for_element(By.XPATH, '/html/body/div[2]/div/div[3]/button[1]').click()
                
                # Actualizar progreso y tiempo
                self.update_metrics(i, total_filas)

            self.log("✅ ALL RECORDS PROCESSED SUCCESSFULLY", True)
            messagebox.showinfo("Success", "Process completed.")
        except Exception as e:
            self.log(f"Loop Error at row {i}: {e}")
        finally:
            self.btn_action.configure(state="normal")

    def DatosCrearSi(self, Datos):
        # Selector "Digitado: SI"
        Select(self.wait_for_element(By.ID, 'Digitado')).select_by_visible_text('Si')
        
        # Fechas automáticas
        fecha_fields = ['Fecha_entrega_tecnologo', 'Fecha_actualizacion', 'Fecha_entrega_digitacion']
        for field in fecha_fields:
            self.wait_for_element(By.ID, field).send_keys(Datos[1])
        
        self.wait_for_element(By.ID, 'Nro_actualizacion').send_keys('1')

        self.llenar(Datos)
        # Click en Guardar/Siguiente
        self.wait_for_element(By.XPATH, '/html/body/div/div/main/div/div/div/div[2]/form/div[12]/div/center/input').click()

    def llenar(self, Datos):
        # Campo Ficha
        element_ficha = self.wait_for_element(By.ID, 'Ficha_fic')
        element_ficha.clear()
        element_ficha.send_keys(Datos[0])

        # Nombre Profesional
        profesional = self.wait_for_element(By.ID, 'Nombre_profesional')
        profesional.clear()
        profesional.send_keys(Datos[2])

        # Fechas de ingreso
        fecha_fields = ['Fecha_ingreso', 'Fecha_entrega_profesional']
        for field in fecha_fields:
            element = self.wait_for_element(By.ID, field)
            element.clear()
            element.send_keys(Datos[1])

        # Perfil
        Select(self.wait_for_element(By.ID, 'Id_perfil')).select_by_visible_text(str(Datos[5]))

        # Espacio Ficha con re-intento (Lógica original)
        for attempt in range(10):
            try:
                espacio = Select(self.wait_for_element(By.ID, 'Espacio_fic'))
                espacio.select_by_visible_text('1 -Hogar')
                time.sleep(1)
                espacio.select_by_visible_text(str(Datos[3]))
                time.sleep(1)
                break
            except:
                time.sleep(1)

        # Id Base
        Select(self.wait_for_element(By.ID, 'Id_Base')).select_by_visible_text(str(Datos[4]))

if __name__ == "__main__":
    # Configuración de apariencia inicial
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    root.withdraw() # Ocultamos la raíz innecesaria
    app = GesiApp(root)
    root.mainloop()