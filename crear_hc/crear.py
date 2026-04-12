import threading
import time
from pathlib import Path
from datetime import datetime
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

# --- Configuración de Estilo ---
COLORS = {
    "bg_dark":      "#0D1117",
    "bg_card":      "#161B22",
    "bg_input":     "#010409",
    "accent":       "#238636",
    "accent_hover": "#2EA043",
    "text_main":    "#E6EDF3",
    "text_dim":     "#8B949E",
    "border":       "#30363D",
    "blue_btn":     "#1F6FEB",
    "red_btn":      "#DA3633"
}

class GesiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GESI - Automatización de Historias Clínicas")
        self.geometry("1000x750")
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Variables de estado originales
        self.nombres = None
        self.driver = None
        self.captcha_listo = threading.Event()
        self.confirmacion_si = threading.Event()

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_panel()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=320, fg_color=COLORS["bg_card"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="🔑 PANEL DE CONTROL", 
                     font=ctk.CTkFont("Segoe UI", 18, "bold")).pack(pady=(30, 20))

        # Inputs de Login
        self.user_var = ctk.StringVar()
        self.pass_var = ctk.StringVar()
        
        ctk.CTkLabel(self.sidebar, text="Usuario GESI", text_color=COLORS["text_dim"]).pack(anchor="w", padx=25)
        self.entry_user = ctk.CTkEntry(self.sidebar, textvariable=self.user_var, height=35, fg_color=COLORS["bg_input"])
        self.entry_user.pack(fill="x", padx=25, pady=(0, 10))

        ctk.CTkLabel(self.sidebar, text="Contraseña", text_color=COLORS["text_dim"]).pack(anchor="w", padx=25)
        self.entry_pass = ctk.CTkEntry(self.sidebar, textvariable=self.pass_var, show="*", height=35, fg_color=COLORS["bg_input"])
        self.entry_pass.pack(fill="x", padx=25, pady=(0, 20))

        # Divisor
        ctk.CTkFrame(self.sidebar, height=2, fg_color=COLORS["border"]).pack(fill="x", padx=20, pady=10)

        # Botón para Captcha (Reemplaza al dialog anterior)
        self.btn_captcha = ctk.CTkButton(self.sidebar, text="Confirmar Captcha ✅", 
                                        fg_color=COLORS["blue_btn"], state="disabled",
                                        command=lambda: self.captcha_listo.set())
        self.btn_captcha.pack(fill="x", padx=25, pady=15)

        # Botones de Proceso (SI/NO)
        self.btn_proceso_si = ctk.CTkButton(self.sidebar, text="Incluir Digitado (SÍ)", 
                                           fg_color=COLORS["accent"], state="disabled",
                                           command=lambda: self.confirmacion_si.set())
        self.btn_proceso_si.pack(fill="x", padx=25, pady=5)

    def _build_main_panel(self):
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)

        # Selector de Archivo
        self.btn_file = ctk.CTkButton(self.main_view, text="📂 Seleccionar Archivo de Excel", 
                                     fg_color=COLORS["bg_card"], height=45, 
                                     command=self.seleccionar_archivo)
        self.btn_file.pack(fill="x", pady=(0, 10))

        # Monitor de Procesos (Log)
        self.txt_log = ctk.CTkTextbox(self.main_view, fg_color="#010409", border_width=1,
                                     font=ctk.CTkFont("Consolas", 12), text_color="#76e1fe")
        self.txt_log.pack(fill="both", expand=True, pady=10)
        self.txt_log.configure(state="disabled")

        # Botón Principal
        self.btn_action = ctk.CTkButton(self.main_view, text="🚀 INICIAR AUTOMATIZACIÓN", 
                                       fg_color=COLORS["accent"], height=55,
                                       font=ctk.CTkFont("Segoe UI", 16, "bold"),
                                       command=self.start_thread)
        self.btn_action.pack(fill="x")

    def log(self, message):
        t = datetime.now().strftime("%H:%M:%S")
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"[{t}] {message}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")
        self.update_idletasks()

    # --- LÓGICA ORIGINAL RESTAURADA ---

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(title="Seleccionar archivo de Excel", filetypes=[("Archivos de Excel", "*.xlsx;*.xls")])
        if archivo:
            try:
                wb = load_workbook(archivo)
                self.nombres = wb['Hoja1']
                self.log(f"Archivo cargado: {Path(archivo).name}")
                self.btn_file.configure(text=f"✅ {Path(archivo).name}")
            except Exception as e:
                self.log(f"Error cargando Excel: {e}")

    def wait_for_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))

    def start_thread(self):
        if not self.nombres:
            return messagebox.showwarning("Falta Info", "Carga el Excel primero.")
        threading.Thread(target=self.hc_crear, daemon=True).start()

    def hc_crear(self):
        self.btn_action.configure(state="disabled")
        try:
            self.log("Abriendo Chrome...")
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            self.driver.get("https://gesiapps.saludcapital.gov.co/GESI_sistemas/login")
            time.sleep(2)

            try:
                self.wait_for_element(By.XPATH, '/html/body/div/div[2]/button[3]').click()
                time.sleep(1)
                self.wait_for_element(By.XPATH, '/html/body/div/div[3]/p[2]/a').click()
                time.sleep(3)
            except:
                self.log("Omitiendo bypass de seguridad inicial.")

            # Login con los datos del sidebar
            self.log("Enviando credenciales de usuario...")
            self.wait_for_element(By.ID, 'usuario').send_keys(self.user_var.get())
            self.wait_for_element(By.ID, 'password').send_keys(self.pass_var.get())
            
            codigo = self.wait_for_element(By.ID, 'tokenAcceso').get_attribute('value')
            self.wait_for_element(By.ID, 'valorCodigoSeguridad').send_keys(codigo)
            
            self.log("⚠️ POR FAVOR, RESUELVE EL CAPTCHA Y PRESIONA 'Confirmar Captcha' EN EL PANEL.")
            self.btn_captcha.configure(state="normal")
            
            # Espera al evento del botón
            self.captcha_listo.wait()
            self.captcha_listo.clear()
            self.btn_captcha.configure(state="disabled")
            
            self.next_step()
            
        except Exception as e:
            self.log(f"Error: {e}")
            self.btn_action.configure(state="normal")

    def next_step(self):
        self.log("Navegando al módulo de Historias Clínicas...")
        self.wait_for_element(By.XPATH, '/html/body/section/div/div/form/div/div/div[7]/div/div/button').click()
        time.sleep(4)
        self.wait_for_element(By.XPATH, '/html/body/div/div/nav/div/div[4]/ul/li[7]').click()
        time.sleep(1)
        self.wait_for_element(By.XPATH, '/html/body/div/div/nav/div/div[4]/ul/li[7]/div/ul/li[1]/a').click()
        time.sleep(2)
        self.wait_for_element(By.XPATH, '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[7]/input').click()
        time.sleep(1)
        self.wait_for_element(By.XPATH, '/html/body/div[2]/div/div[3]/button[1]').click()
        
        self.log("Esperando confirmación de inicio de proceso...")
        self.btn_proceso_si.configure(state="normal")
        
        # Espera al evento del botón SI
        self.confirmacion_si.wait()
        self.confirmacion_si.clear()
        self.btn_proceso_si.configure(state="disabled")
        
        self.si_proceso()

    def si_proceso(self):
        total_filas = self.nombres.max_row
        try:
            for i in range(1, total_filas + 1):
                fila = self.nombres[f'A{i}:F{i}'][0]
                ficha_val = fila[0].value
                fecha_val = fila[1].value
                formato = fecha_val.strftime('%d/%m/%Y')
                
                datos = [ficha_val, formato, fila[2].value, fila[3].value, fila[4].value, fila[5].value]
                self.log(f"Ingresando ficha: {ficha_val}")
                
                self.DatosCrearSi(datos) 
                
                self.wait_for_element(By.XPATH, '/html/body/div[2]/div/div[3]/button[1]').click()
                self.wait_for_element(By.XPATH, '/html/body/div/div/main/div/div/div/div[1]/div/div/table/tbody/tr/td[5]/input').click()
                self.wait_for_element(By.XPATH, '/html/body/div[2]/div/div[3]/button[1]').click()
            
            self.log("✅ PROCESO COMPLETADO CORRECTAMENTE.")
            messagebox.showinfo("Éxito", "Proceso completado.")
        except Exception as e:
            self.log(f"Error en bucle: {e}")
        finally:
            self.btn_action.configure(state="normal")

    def DatosCrearSi(self, Datos):
        Select(self.wait_for_element(By.ID, 'Digitado')).select_by_visible_text('Si')
        fecha_fields = ['Fecha_entrega_tecnologo', 'Fecha_actualizacion', 'Fecha_entrega_digitacion']
        for field in fecha_fields:
            self.wait_for_element(By.ID, field).send_keys(Datos[1])
        self.wait_for_element(By.ID, 'Nro_actualizacion').send_keys('1')
        
        self.llenar(Datos)
        self.wait_for_element(By.XPATH, '/html/body/div/div/main/div/div/div/div[2]/form/div[12]/div/center/input').click()

    def llenar(self, Datos):
        element_ficha = self.wait_for_element(By.ID, 'Ficha_fic')
        element_ficha.clear()
        element_ficha.send_keys(Datos[0])
        
        profesional = self.wait_for_element(By.ID, 'Nombre_profesional')
        profesional.clear()
        profesional.send_keys(Datos[2])
        
        fecha_fields = ['Fecha_ingreso', 'Fecha_entrega_profesional']
        for field in fecha_fields:
            element = self.wait_for_element(By.ID, field)
            element.clear()
            element.send_keys(Datos[1])
        
        Select(self.wait_for_element(By.ID, 'Id_perfil')).select_by_visible_text(Datos[5])
        
        for attempt in range(10):
            try:
                espacio = Select(self.wait_for_element(By.ID, 'Espacio_fic'))
                espacio.select_by_visible_text('1 -Hogar')
                time.sleep(1)
                espacio.select_by_visible_text(Datos[3])
                time.sleep(1)
                break
            except:
                time.sleep(1)
        
        Select(self.wait_for_element(By.ID, 'Id_Base')).select_by_visible_text(Datos[4])

if __name__ == "__main__":
    app = GesiApp()
    app.mainloop()