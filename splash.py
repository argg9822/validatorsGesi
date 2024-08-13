import tkinter as tk
from PIL import Image, ImageTk  # Necesitarás Pillow para manejar imágenes PNG
import subprocess
import sys
import os
from PIL import Image, ImageTk

def open_main_window():
    splash_root.destroy()  # Cierra la pantalla de inicio
    os.system(f'python {os.path.abspath("index.py")}')  # Ejecuta index.py

def center_window(window, width, height):
    # Obtén el tamaño de la pantalla
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calcula la posición centrada
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Establece la geometría de la ventana
    window.geometry(f'{width}x{height}+{x}+{y}')

# Configuración de la pantalla de inicio
splash_root = tk.Tk()
splash_root.title("Splash Screen")

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
logo_path = "img/intro.png"  # Asegúrate de especificar la ruta correcta
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
progress_x = (window_width - progress_width) -196  # Centrar la barra de progreso horizontalmente
progress_y = window_height - 80  # Ajusta la posición vertical de la barra de progreso

# Agregar un canvas para la barra de progreso
progress_canvas = tk.Canvas(splash_root, width=window_width, height=progress_height, bg=transparent_color, highlightthickness=0)
progress_canvas.place(x=0, y=window_height - progress_height - 60)  # Ajusta la posición de la barra de progreso

# Dibuja la barra de progreso
progress_canvas.create_rectangle(progress_x, 0, progress_x + progress_width, progress_height, fill='grey', outline='white')  # Fondo de la barra de progreso
progress_bar = progress_canvas.create_rectangle(progress_x, 0, progress_x, progress_height, fill='white', outline='white')  # Barra de progreso

# Función para actualizar la barra de progreso
def update_progress_bar():
    current_width = progress_canvas.coords(progress_bar)[2] - progress_canvas.coords(progress_bar)[0]
    new_width = current_width + 20  # Ajusta la velocidad de llenado
    if new_width >= progress_width:
        new_width = progress_width
        splash_root.after(100, open_main_window)  # Llama a open_main_window después de 100 ms
    progress_canvas.coords(progress_bar, progress_x, 0, progress_x + new_width, progress_height)
    if new_width < progress_width:
        splash_root.after(100, update_progress_bar)  # Llama a la función de nuevo después de 100 ms

# Inicia la actualización de la barra de progreso
splash_root.after(500, update_progress_bar)  # Comienza la actualización de la barra de progreso después de 500 ms

splash_root.mainloop()