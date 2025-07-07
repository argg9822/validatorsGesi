import os
import sys
import shutil
import zipfile
import threading
import importlib
import requests
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import customtkinter as ctk
import index
from index import index_open

# Configuración de constantes
VERSION_FILE = "version.txt"
APP_NAME = "Odin"
VERSION = "0.0.0.3"
AUTHORS = "Gabriel Monhabell - Aramis Garcia"
COPYRIGHT = f"© 2024 {AUTHORS}"
GITHUB_REPO = "argg9822/validatorsGesi"
TRANSPARENT_COLOR = '#00c7fc'

class AppUpdater:
    @staticmethod
    def obtener_ultima_version():
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()["tag_name"]
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener la última versión: {e}")
            return None

    @staticmethod
    def leer_version_actual():
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                return f.read().strip()
        return None

    @staticmethod
    def guardar_version_actual(version):
        with open(VERSION_FILE, "w") as f:
            f.write(version)

    @staticmethod
    def descargar_cambios(version):
        url = f"https://api.github.com/repos/{GITHUB_REPO}/zipball/{version}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open("cambios.zip", "wb") as f:
                    f.write(response.content)
                return True
        except requests.exceptions.RequestException as e:
            print(f"Error al descargar cambios: {e}")
        return False

    @staticmethod
    def aplicar_cambios():
        zip_path = "cambios.zip"
        current_dir = os.path.dirname(os.path.abspath(zip_path))
        
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            temp_dir = os.path.join(current_dir, "temp_extract")
            zip_ref.extractall(temp_dir)

        extracted_folders = [f for f in os.listdir(temp_dir) 
                           if os.path.isdir(os.path.join(temp_dir, f))]
        
        if not extracted_folders:
            print("Error: No se encontraron carpetas en el ZIP")
            return False

        root_folder = os.path.join(temp_dir, extracted_folders[0])
        required_items = {
            'crc_princ': False,
            'crear_hc': False,
            'img': False,
            'index.py': False
        }

        for root, dirs, files in os.walk(root_folder):
            for item in required_items:
                if not required_items[item]:
                    if item in dirs or item in files:
                        source = os.path.join(root, item)
                        destination = os.path.join(current_dir, item)
                        
                        # Eliminar destino existente
                        if os.path.exists(destination):
                            if os.path.isdir(destination):
                                shutil.rmtree(destination)
                            else:
                                os.remove(destination)
                        
                        # Mover el nuevo elemento
                        shutil.move(source, destination)
                        print(f"{'Carpeta' if item in dirs else 'Archivo'} {item} reemplazado")
                        required_items[item] = True

            # Salir si todos los elementos fueron encontrados
            if all(required_items.values()):
                break

        # Eliminar carpeta temporal
        shutil.rmtree(temp_dir)
        
        # Verificar si faltó algún elemento
        missing_items = [k for k, v in required_items.items() if not v]
        if missing_items:
            AppUI.mostrar_error_actualizacion(missing_items)
            return False
        
        os.remove(zip_path)
        return True

class AppUI:
    @staticmethod
    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')

    @staticmethod
    def mostrar_error_actualizacion(missing_items):
        ventana_error = ctk.CTkToplevel()
        ventana_error.title("Error de Actualización")
        ventana_error.geometry("400x200")
        AppUI.center_window(ventana_error, 400, 200)

        label = ctk.CTkLabel(
            ventana_error, 
            text="No se encontraron los siguientes elementos:",
            font=("Arial", 14)
        )
        label.pack(pady=10)

        for item in missing_items:
            item_label = ctk.CTkLabel(ventana_error, text=f"- {item}")
            item_label.pack()

        cerrar_button = ctk.CTkButton(
            ventana_error, 
            text="Cerrar", 
            command=ventana_error.destroy
        )
        cerrar_button.pack(pady=20)

    @staticmethod
    def crear_ventana_actualizacion(version_actual, ultima_version):
        ventana = tk.Tk()
        ventana.title(f"Actualizar {APP_NAME}")
        ventana.geometry("350x180")
        ventana.configure(bg="#f0f0f0")
        AppUI.center_window(ventana, 350, 180)
        AppUI.set_window_icon(ventana)

        tk.Label(
            ventana, 
            text="Hay una actualización disponible.",
            font=("Arial", 12), 
            bg="#f0f0f0"
        ).pack(pady=5)

        tk.Label(
            ventana, 
            text=f"Versión actual: {version_actual}\nÚltima versión: {ultima_version}",
            font=("Arial", 10), 
            bg="#f0f0f0"
        ).pack()

        tk.Label(
            ventana, 
            text="¿Desea instalarla ahora?",
            font=("Arial", 11), 
            bg="#f0f0f0"
        ).pack(pady=5)

        frame_botones = tk.Frame(ventana, bg="#f0f0f0")
        frame_botones.pack(pady=10)

        tk.Button(
            frame_botones, 
            text="Sí", 
            command=lambda: AppUI.iniciar_actualizacion(ventana, ultima_version),
            font=("Arial", 10), 
            width=15
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            frame_botones, 
            text="No", 
            command=ventana.destroy,
            font=("Arial", 10), 
            width=15
        ).pack(side=tk.LEFT, padx=10)

        return ventana

    @staticmethod
    def iniciar_actualizacion(parent_window, ultima_version):
        parent_window.destroy()
        
        ventana = tk.Tk()
        ventana.title(f"Actualizando {APP_NAME}")
        ventana.geometry("300x120")
        AppUI.center_window(ventana, 300, 120)

        tk.Label(
            ventana, 
            text=f"Actualizando {APP_NAME}\nPor favor espere",
            font=("Arial", 12)
        ).pack(pady=10)

        progress_bar = ctk.CTkProgressBar(
            ventana, 
            orientation="horizontal",
            mode="indeterminate", 
            width=250
        )
        progress_bar.pack(pady=10)
        progress_bar.start()

        def proceso_actualizacion():
            if AppUpdater.descargar_cambios(ultima_version) and AppUpdater.aplicar_cambios():
                AppUpdater.guardar_version_actual(ultima_version)
                try:
                    importlib.reload(index)
                    from index import index_open
                    messagebox.showinfo("Éxito", "Aplicación actualizada correctamente.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al recargar módulos: {e}")
            
            progress_bar.stop()
            ventana.after(0, ventana.destroy)
            AppManager.reiniciar_aplicacion()

        threading.Thread(target=proceso_actualizacion, daemon=True).start()
        ventana.mainloop()

    @staticmethod
    def set_window_icon(window):
        icon_paths = [
            os.path.join(os.path.dirname(sys.executable), "img", "logo.ico"),
            os.path.join(os.path.dirname(__file__), "img", "logo.ico")
        ]
        
        for path in icon_paths:
            if os.path.exists(path):
                try:
                    window.wm_iconbitmap(path)
                    break
                except Exception:
                    continue

    @staticmethod
    def crear_splash_screen():
        splash = tk.Tk()
        splash.title("Iniciando...")
        splash.overrideredirect(True)
        splash.attributes('-transparentcolor', TRANSPARENT_COLOR)
        splash.configure(bg=TRANSPARENT_COLOR)

        width, height = 500, 500
        AppUI.center_window(splash, width, height)

        canvas = tk.Canvas(
            splash, 
            width=width, 
            height=height, 
            bg=TRANSPARENT_COLOR, 
            highlightthickness=0
        )
        canvas.pack()

        # Cargar imagen de splash
        img_paths = [
            os.path.join(os.path.dirname(sys.executable), "img", "intro.png"),
            os.path.join(os.path.dirname(__file__), "img", "intro.png"),
            "img/intro.png"
        ]
        
        logo_image = None
        for path in img_paths:
            if os.path.exists(path):
                try:
                    logo_image = Image.open(path).convert("RGBA")
                    break
                except Exception as e:
                    print(f"Error al cargar imagen {path}: {e}")

        if logo_image:
            logo_photo = ImageTk.PhotoImage(logo_image)
            canvas.image = logo_photo  # Mantener referencia
            canvas.create_image(width//2, height//2, image=logo_photo)

        # Información de la aplicación
        info_text = f"{APP_NAME} v.{VERSION} {COPYRIGHT}"
        canvas.create_text(
            width//2, 
            height-15, 
            text=info_text, 
            fill='white', 
            font=('Helvetica', 8)
        )

        # Barra de progreso
        progress_width = 400
        progress_height = 2
        progress_x = (width - progress_width) // 2
        progress_y = height - 40
        progress_bar = canvas.create_rectangle(
            progress_x, progress_y,
            progress_x + progress_width, progress_y + progress_height,
            fill='red', outline='red'
        )

        def update_progress(percentage):
            canvas.coords(
                progress_bar,
                progress_x, progress_y,
                progress_x + (progress_width * percentage), progress_y + progress_height
            )
            canvas.update_idletasks()

        def run_progress():
            for i in range(101):
                splash.after(i * 30, lambda p=i/100: update_progress(p))
            splash.after(3000, lambda: AppManager.abrir_ventana_principal(splash))

        run_progress()
        return splash

class AppManager:
    @staticmethod
    def verificar_actualizaciones():
        version_actual = AppUpdater.leer_version_actual()
        ultima_version = AppUpdater.obtener_ultima_version()
        
        if ultima_version and version_actual != ultima_version:
            ventana = AppUI.crear_ventana_actualizacion(version_actual, ultima_version)
            ventana.mainloop()
        else:
            print("La aplicación ya está actualizada")

    @staticmethod
    def abrir_ventana_principal(splash_root):
        splash_root.destroy()
        index_open()

    @staticmethod
    def reiniciar_aplicacion():
        python = sys.executable
        os.execl(python, python, *sys.argv)

    @staticmethod
    def main():
        try:
            AppManager.verificar_actualizaciones()
            splash = AppUI.crear_splash_screen()
            splash.mainloop()
        except Exception as e:
            with open("error_log.txt", "w") as f:
                f.write(f"Error: {str(e)}\n")
                import traceback
                f.write(traceback.format_exc())
            messagebox.showerror("Error", f"Ocurrió un error inesperado:\n{str(e)}")

if __name__ == "__main__":
    AppManager.main()