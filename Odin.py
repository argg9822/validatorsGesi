import os
import requests
import zipfile
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import shutil
import tkinter as tk
import customtkinter as ctk
import threading

try:

    VERSION_FILE = "version.txt"  # Archivo para guardar la versión actual

    def open_main_window(splash_root):
        splash_root.destroy()  # Cierra la pantalla de inicio
        # Ruta al ejecutable `index.exe`
        script_path = os.path.join(os.path.dirname(sys.executable), "index.exe")
        
        # Ejecuta el ejecutable de forma independiente
        os.system(f'"{script_path}"')

    def center_window(window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def obtener_ultima_version():
        try:
            url = "https://api.github.com/repos/argg9822/validatorsGesi/releases/latest"
            response = requests.get(url, timeout=5)  # Agrega un timeout de 5 segundos
            response.raise_for_status()  # Lanza una excepción si la respuesta tiene un código de error HTTP
            return response.json()["tag_name"]
        except requests.exceptions.Timeout:
            print("La solicitud ha agotado el tiempo de espera.")
        

    def leer_version_actual():
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                return f.read().strip()
        return None

    def guardar_version_actual(version):
        with open(VERSION_FILE, "w") as f:
            f.write(version)
            
    def descargar_cambios(version):
        url = f"https://api.github.com/repos/argg9822/validatorsGesi/zipball/{version}"
        response = requests.get(url)
        if response.status_code == 200:
            with open("cambios.zip", "wb") as f:
                f.write(response.content)
            return True
        return False

    def aplicar_cambios():
        zip_path = "cambios.zip"
        current_dir = os.path.dirname(os.path.abspath(zip_path))
        
        # Extraer el ZIP en una carpeta temporal
        temp_dir = os.path.join(current_dir, "temp_extract")
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        except Exception as e:
            print(f"Error al extraer el ZIP: {e}")
            return

        # Función para mover archivos o carpetas
        def mover_y_reemplazar(origen, destino):
            try:
                if os.path.exists(destino):
                    if os.path.isdir(destino):
                        shutil.rmtree(destino)
                    else:
                        os.remove(destino)
                shutil.move(origen, destino)
                print(f"Reemplazado: {origen} -> {destino}")
            except Exception as e:
                print(f"Error al reemplazar {origen}: {e}")

        # Variables de búsqueda
        elementos = {
            'index.py': None,
            'index.exe': None,
            'areas.json': None,
            'validadores': None,
            'crear_hc': None,
            'img': None,
        }

        # Buscar elementos en la carpeta temporal
        for root, dirs, files in os.walk(temp_dir):
            for file_name in files:
                if file_name in elementos:
                    elementos[file_name] = os.path.join(root, file_name)
            for dir_name in dirs:
                if dir_name in elementos:
                    elementos[dir_name] = os.path.join(root, dir_name)

        # Mover y reemplazar elementos encontrados
        for elemento, ruta_origen in elementos.items():
            if ruta_origen:
                destino = os.path.join(current_dir, elemento)
                mover_y_reemplazar(ruta_origen, destino)

        # Eliminar la carpeta temporal
        try:
            shutil.rmtree(temp_dir)
            print(f"Carpeta temporal eliminada: {temp_dir}")
        except Exception as e:
            print(f"Error al eliminar la carpeta temporal: {e}")
        
    def actualizar_aplicacion():
        version_actual = leer_version_actual()
        ultima_version = obtener_ultima_version()
        
        if ultima_version:
            if version_actual != ultima_version:
                # Crea una ventana para mostrar la opción de actualizar
                ventana_actualizacion = tk.Tk()
                ventana_actualizacion.title("Actualizar validador")
                ventana_actualizacion.geometry("300x150")  # Establece el tamaño de la ventana
                ventana_actualizacion.configure(bg="#f0f0f0")  # Establece el color de fondo

                # Centra la ventana en la pantalla
                pantalla_ancho = ventana_actualizacion.winfo_screenwidth()
                pantalla_alto = ventana_actualizacion.winfo_screenheight()
                x = (pantalla_ancho / 2) - (300 / 2)
                y = (pantalla_alto / 2) - (150 / 2)
                ventana_actualizacion.geometry(f"300x150+{int(x)}+{int(y)}")

                # Agrega el logo de la aplicación
                ventana_actualizacion.wm_iconbitmap(os.path.join(os.path.dirname(sys.executable), "img", "logo.ico"))

                # Crea un label para mostrar el mensaje de actualización
                label_actualizacion = tk.Label(ventana_actualizacion, text="Hay una actualización disponible.", font=("Arial", 12), bg="#f0f0f0")
                label_actualizacion.pack(pady=5)

                # Crea un label para mostrar la versión actual y la última versión
                label_versiones = tk.Label(ventana_actualizacion, text=f"Versión actual: {version_actual}\nÚltima versión: {ultima_version}", font=("Arial", 10), bg="#f0f0f0")
                label_versiones.pack()
                
                label_actualizacion = tk.Label(ventana_actualizacion, text="Desea instalarla ahora?", font=("Arial", 11), bg="#f0f0f0")
                label_actualizacion.pack(pady=5)
                
                # Crea un frame para contener los botones
                frame_botones = tk.Frame(ventana_actualizacion, bg="#f0f0f0")
                frame_botones.pack(pady=10)

                # Crea un botón para actualizar la aplicación
                boton_actualizar = tk.Button(frame_botones, text="Si", command=lambda: actualizar_aplicacion_sí(ventana_actualizacion, ultima_version),  font=("Arial", 10), width=15)
                boton_actualizar.pack(side=tk.LEFT, padx=10)

                # Crea un botón para no actualizar la aplicación
                boton_no_actualizar = tk.Button(frame_botones, text="No", command=ventana_actualizacion.destroy, font=("Arial", 10), width=15)
                boton_no_actualizar.pack(side=tk.LEFT, padx=10)

                # Muestra la ventana de actualización
                ventana_actualizacion.mainloop()
            else:
                print("La aplicación ya está actualizada")
        else:
            print("No se encontró la versión actual")

    def actualizar_aplicacion_sí(ventana_actualizacion, ultima_version):
        # Descarga y aplica los cambios
        ventana_actualizacion.destroy()
        # Crear una nueva ventana para mostrar el progreso
        vie_actualizaion = tk.Tk()
        vie_actualizaion.title("Actualizar validador")
        vie_actualizaion.geometry("280x100")
        

        # Centra la ventana en la pantalla
        pantalla_ancho = vie_actualizaion.winfo_screenwidth()
        pantalla_alto = vie_actualizaion.winfo_screenheight()
        x = (pantalla_ancho / 2) - (280 / 2)
        y = (pantalla_alto / 2) - (100 / 2)
        vie_actualizaion.geometry(f"280x100+{int(x)}+{int(y)}")

        # Configura la etiqueta y la barra de progreso
        label_actualizacion = tk.Label(vie_actualizaion, text="Actualizando app Odin \n Por favor espere", font=("Arial", 12), bg="#f0f0f0")
        label_actualizacion.pack(pady=5)

        progress_bar = ctk.CTkProgressBar(vie_actualizaion, orientation="horizontal", mode="indeterminate", width=300)
        progress_bar.pack(pady=20 ,padx = 25)
        progress_bar.start()

        
        def proceso_actualizacion():
            
            if descargar_cambios(ultima_version):
                aplicar_cambios()
                guardar_version_actual(ultima_version)
                print("App actualizada con éxito")
                
                # Detiene la barra de progreso y cierra la ventana
                # Detiene la barra de progreso
                progress_bar.stop()

                # Cierra la ventana en el hilo principal
                vie_actualizaion.after(0, vie_actualizaion.destroy)
                
                return
            else:
                
                print("Error al descargar los cambios")
            
        hilo_actualizacion = threading.Thread(target=proceso_actualizacion)
        hilo_actualizacion.start()
        
        vie_actualizaion.mainloop()
        

    def main():
        actualizar_aplicacion()  # Llama a la función de actualización

        # Configuración de la pantalla de inicio
        splash_root = tk.Tk()
        splash_root.title("Pantalla de inicio")

        # Define el tamaño de la ventana de inicio
        window_width = 900
        window_height = 500
        # Centra la ventana en la pantalla
        center_window(splash_root, window_width, window_height)
        splash_root.overrideredirect(True)  # Elimina la barra de título
        # Configura la ventana para ser completamente transparente
        transparent_color = '#00c7fc'
        splash_root.attributes('-transparentcolor', transparent_color)  # Establece el color azul como transparente
        splash_root.configure(bg=transparent_color)  # Configura el color de fondo como azul (esto se hará transparente)

        # Crear un canvas para colocar el contenido
        canvas = tk.Canvas(splash_root, width=window_width, height=window_height, bg=transparent_color, highlightthickness=0)
        canvas.pack()

        # Cargar y mostrar el logo
        logo_path = os.path.join(os.path.dirname(sys.executable), "img", "intro.png")
        logo_image = Image.open(logo_path).convert("RGBA")  # Asegúrate de que el logo tenga fondo transparente
        logo_photo = ImageTk.PhotoImage(logo_image)

        # Mantén una referencia a la imagen
        canvas.image = logo_photo

        # Coloca la imagen en el centro del canvas
        canvas.create_image(window_width // 2, window_height // 2, image=logo_photo)

        # Mostrar información de la aplicación
        info_text = "Odin v-1.0\n© 2024 Gabriel Monhabell - Aramis Garcia"
        offset_x = 100  # Ajusta este valor para mover el texto más a la izquierda o derecha
        canvas.create_text((window_width // 2.2) - offset_x, window_height - 140, text=info_text, fill='white', font=('Helvetica', 14))  # Ajusta la posición y el estilo

        # Crear una barra de progreso
        progress_width = 607  # Ancho de la barra de progreso
        progress_height = 5  # Altura de la barra de progreso
        progress_x = ((window_width - progress_width) // 2) -49
        
        progress_y = window_height - 80
        progress_bar = canvas.create_rectangle(progress_x, progress_y, progress_x + progress_width, progress_y + progress_height, fill='white', outline='white')

        # Función para actualizar la barra de progreso
        def update_progress_bar(percentage):
            canvas.coords(progress_bar, progress_x, progress_y, progress_x + (progress_width * percentage), progress_y + progress_height)
            canvas.update_idletasks()

        # Actualizar la barra de progreso gradualmente
        def run_progress():
            for i in range(101):
                splash_root.after(i * 80, lambda p=i/100: update_progress_bar(p))  # Actualiza cada 80ms
            splash_root.after(8100, lambda: open_main_window(splash_root))  # Espera 8 segundos antes de abrir la ventana principal

        run_progress()

        # Iniciar la ventana de inicio
        splash_root.mainloop()

    if __name__ == "__main__":
        main()

except Exception as e:
    import traceback
    with open("error_log.txt", "w") as f:
        f.write(str(e))
        f.write(traceback.format_exc())