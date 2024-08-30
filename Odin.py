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


VERSION_FILE = "version.txt"  # Archivo para guardar la versión actual

def open_main_window(splash_root):
    splash_root.destroy()  # Cierra la pantalla de inicio
    os.system(f'pythonw {os.path.abspath("index.py")}')  # Ejecuta index.py sin mostrar la consola

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
    current_dir = os.path.dirname(os.path.abspath(zip_path))
    
    # Extraer el ZIP en una carpeta temporal
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        temp_dir = os.path.join(current_dir, "temp_extract")
        zip_ref.extractall(temp_dir)

    # Variables para almacenar rutas encontradas
    index_found = False
    validadores_found = False
    img_found = False

    # Buscar los archivos y carpetas dentro de las carpetas extraídas
    for root, dirs, files in os.walk(temp_dir):
        # Buscar y reemplazar index.py
        if not index_found and 'index.py' in files:
            index_py_path = os.path.join(root, 'index.py')
            destination_path = os.path.join(current_dir, 'index.py')
            shutil.move(index_py_path, destination_path)
            print(f"Archivo {index_py_path} reemplazado en {destination_path}")
            index_found = True
            
        if not index_found and 'funciones.py' in files:
            index_py_path = os.path.join(root, 'funciones.py')
            destination_path = os.path.join(current_dir, 'funciones.py')
            shutil.move(index_py_path, destination_path)
            print(f"Archivo {index_py_path} reemplazado en {destination_path}")
            index_found = True
            
        if not index_found and 'bases.json' in files:
            index_py_path = os.path.join(root, 'bases.json')
            destination_path = os.path.join(current_dir, 'bases.json')
            shutil.move(index_py_path, destination_path)
            print(f"Archivo {index_py_path} reemplazado en {destination_path}")
            index_found = True

        # Buscar y reemplazar la carpeta validadores
        if not validadores_found and 'validadores' in dirs:
            validadores_path = os.path.join(root, 'validadores')
            destination_path = os.path.join(current_dir, 'validadores')

            # Si la carpeta ya existe, eliminarla antes de reemplazarla
            if os.path.exists(destination_path):
                shutil.rmtree(destination_path)

            # Mover la carpeta validadores al destino
            shutil.move(validadores_path, destination_path)
            print(f"Carpeta {validadores_path} reemplazada en {destination_path}")
            validadores_found = True
            
        # Buscar y reemplazar la carpeta validadores
        if not validadores_found and 'crear_hc' in dirs:
            validadores_path = os.path.join(root, 'crear_hc')
            destination_path = os.path.join(current_dir, 'crear_hc')

            # Si la carpeta ya existe, eliminarla antes de reemplazarla
            if os.path.exists(destination_path):
                shutil.rmtree(destination_path)

            # Mover la carpeta validadores al destino
            shutil.move(validadores_path, destination_path)
            print(f"Carpeta {validadores_path} reemplazada en {destination_path}")
            validadores_found = True
            
        # Buscar y reemplazar la carpeta img
        if not img_found and 'img' in dirs:
            img_path = os.path.join(root, 'img')
            destination_path = os.path.join(current_dir, 'img')

            # Si la carpeta ya existe, eliminarla antes de reemplazarla
            if os.path.exists(destination_path):
                shutil.rmtree(destination_path)

            # Mover la carpeta img al destino
            shutil.move(img_path, destination_path)
            print(f"Carpeta {img_path} reemplazada en {destination_path}")
            img_found = True

        # Detener la búsqueda si ya se encontraron index.py, validadores, y img
        if index_found and validadores_found and img_found:
            break

    # Eliminar la carpeta temporal
    shutil.rmtree(temp_dir)
    
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
    
    
    print("Actualiz en proceso")
    
    if descargar_cambios(ultima_version):
        # crear ventana mostrando actualizacinon

        aplicar_cambios()
        guardar_version_actual(ultima_version)
        
        
        print("App actualizada con exito")
    else:
        print("Error al descargar los cambios")
        

    
    
   
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
