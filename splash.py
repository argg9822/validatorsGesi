import os
import requests
import zipfile
import tkinter as tk
from PIL import Image, ImageTk
import sys
import shutil

VERSION_FILE = "version.txt"  # Archivo para guardar la versión actual

def open_main_window(splash_root):
    splash_root.destroy()  # Cierra la pantalla de inicio
    os.system(f'python {os.path.abspath("index.py")}')  # Ejecuta index.py

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def obtener_ultima_version():
    url = "https://api.github.com/repos/argg9822/validatorsGesi/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["tag_name"]
    return None

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
    target_dir = os.path.dirname(zip_path)  # Obtener el directorio donde está el archivo ZIP

    # Eliminar archivos y carpetas existentes en el directorio de destino
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            shutil.rmtree(os.path.join(root, name))

    # Extraer el contenido del ZIP al directorio de destino
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        # Obtener la lista de todos los archivos en el ZIP
        all_files = zip_ref.namelist()

        # Encontrar la carpeta dentro del ZIP
        folder_name = [name for name in all_files if name.endswith('/')][0]

        # Filtrar solo los archivos dentro de la carpeta
        files_to_extract = [f for f in all_files if f.startswith(folder_name)]

        # Extraer solo los archivos que están dentro de la carpeta
        for file in files_to_extract:
            zip_ref.extract(file, target_dir)


    


def actualizar_aplicacion():
    version_actual = leer_version_actual()
    ultima_version = obtener_ultima_version()
    
    if ultima_version:
        if version_actual != ultima_version:
            print("Actualización disponible. Descargando cambios...")
            if descargar_cambios(ultima_version):
                aplicar_cambios()
                guardar_version_actual(ultima_version)
                print("La aplicación ha sido actualizada con éxito")
            else:
                print("Error al descargar los cambios")
        else:
            print("La aplicación ya está actualizada")
    else:
        print("No se encontró la versión actual")

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
    info_text = "Gesi-app v-1.0\n© 2024 Gabriel Monhabell - Aramis Garcia"
    offset_x = 100  # Ajusta este valor para mover el texto más a la izquierda o derecha
    canvas.create_text((window_width // 2.2) - offset_x, window_height - 140, text=info_text, fill='white', font=('Helvetica', 14))  # Ajusta la posición y el estilo

    # Crear una barra de progreso
    progress_width = 607  # Ancho de la barra de progreso
    progress_height = 5  # Altura de la barra de progreso
    progress_x = (window_width - progress_width) // 2
    progress_y = window_height - 100
    progress_bar = canvas.create_rectangle(progress_x, progress_y, progress_x + progress_width, progress_y + progress_height, fill='blue', outline='blue')

    # Actualizar la barra de progreso
    def update_progress_bar():
        canvas.itemconfig(progress_bar, fill='green')
        canvas.update_idletasks()
        splash_root.after(1000, lambda: open_main_window(splash_root))  # Pasa splash_root como argumento

    update_progress_bar()

    # Iniciar la ventana de inicio
    splash_root.mainloop()

if __name__ == "__main__":
    main()
