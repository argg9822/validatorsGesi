import customtkinter as ctk

def mostrar_modal(tipo_regla_var, callback):
    """
    Crea una ventana modal para seleccionar el tipo de regla.

    Args:
        tipo_regla_var (ctk.StringVar): Variable para almacenar el tipo de regla seleccionado.
        callback (function): Función que se ejecutará al confirmar el tipo de regla.
    """
    # Crear una ventana modal
    modal = ctk.CTkToplevel()
    modal.title("Seleccionar Tipo de Regla")
    modal.geometry("300x200")
    modal.grab_set()  # Bloquea la ventana principal hasta que se cierre esta

    ctk.CTkLabel(modal, text="Seleccione el tipo de regla:").pack(pady=10)
    tipo_regla_menu = ctk.CTkOptionMenu(
        modal,
        values=[
            "longitud", "numerico", "patron", "unico",
            "dependiente_positivo", "dependiente_error", "no_vacio",
            "dependiente longitud", "dependiente edad positivo", 
            "dependiente edad error", "fechas menor/mayor que", 
            "dependiente_Vacio", "coincidencia_textos"
        ],
        variable=tipo_regla_var
    )
    tipo_regla_menu.pack(pady=10)

    def confirmar_tipo_regla():
        callback(tipo_regla_var.get())  # Ejecuta el callback con el tipo de regla seleccionado
        modal.destroy()  # Cierra la ventana modal

    # Botón para confirmar la selección
    confirmar_btn = ctk.CTkButton(modal, text="Confirmar", command=confirmar_tipo_regla)
    confirmar_btn.pack(pady=20)
    modal.protocol("WM_DELETE_WINDOW", modal.destroy)  # Permite cerrar la ventana con la 'X'
