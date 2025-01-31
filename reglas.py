from tkinter import messagebox
import customtkinter as ctk  # Asegúrate de usar el mismo módulo

def crear_regla(tipo_regla, validador, area, guardar_areas, gestionar_validador):
    nueva_regla = None
    
    if tipo_regla == "longitud":
                
        columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar por longitud (por ejemplo, Cedula):")
        columna_result = columna.get_input()

        # Verificar si no se ingresó nada
        if not columna_result:
            return
        
        condicion2 = ctk.CTkInputDialog(title="Longitud", text="Ingrese la longitud máxima (ejemplo: 10):")
        columna_result2 = condicion2.get_input()

        if not columna_result2:
            return
        
        nueva_regla = {"columna": columna_result, "tipo": "longitud", "condicion": f"<= {columna_result2}"}
        
    elif tipo_regla == "numerico":
        
        columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar numerico (por ejemplo, Telefono):")
        columna_result = columna.get_input()
        if not columna_result:
            return
        
        condicion2 = ctk.CTkInputDialog(title="Numerico", text="Ingrese la condición (ejemplo: 'mayor  5'):")
        condicion2_result = condicion2.get_input()
        if not condicion2_result:
            return
        nueva_regla = {"columna": columna_result, "tipo": "numerico", "condicion": condicion2_result}
    
    elif tipo_regla == "patron":
        columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar para que no tenga caracteres especiales (por ejemplo, Nombres):")
        columna_result = columna.get_input()
        if not columna_result:
            return
        
        patron = ctk.CTkInputDialog(title="Expresión Regular", text="Ingrese el patrón regex (ejemplo: \\d{3}-\\d{2}-\\d{4}):")
        patron_result = patron.get_input()
        if not patron_result:
            return
        
        nueva_regla = {"columna": columna_result, "tipo": "patron", "patron": patron_result}
    
    elif tipo_regla == "unico":
        columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar para qvalores unicos (por ejemplo, Nombres):")
        columna_result = columna.get_input()
        if not columna_result:
            return
        nueva_regla = {"columna": columna_result, "tipo": "unico"}
    
    elif tipo_regla == "dependiente_positivo":
        columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar  (por ejemplo, Telefono):")
        columna_result = columna.get_input()
        if not columna_result:
            return
        
        columna_dependiente = ctk.CTkInputDialog(title="Columna Dependiente", text="¿De qué columna depende esta regla? (por ejemplo, A):")
        columna_dependiente_result = columna_dependiente.get_input()
        
        if not columna_dependiente_result:
            return
        
        valor_dependiente = ctk.CTkInputDialog(title="Valor Dependiente", text="¿Qué valor debe tener la columna dependiente? (ejemplo: 50):")
        valor_dependiente_result = valor_dependiente.get_input()
        if not valor_dependiente_result:
            return
        
        valor_dependiente = float(valor_dependiente_result) if valor_dependiente_result.replace('.', '', 1).isdigit() else valor_dependiente
        
        valor_esperado = ctk.CTkInputDialog(title="Valor Esperado", text="¿Qué valor debe tener la columna a validar si la columna dependiente tiene este valor? (ejemplo: 51):")
        valor_esperado_result = valor_esperado.get_input()
        if not valor_esperado_result:
            return
        
        nueva_regla = {
            "columna": columna_result, 
            "tipo": "dependiente positivo", 
            "columna_dependiente": columna_dependiente_result, 
            "valor_dependiente": valor_dependiente, 
            "valor_esperado": valor_esperado_result
        }
        
    elif tipo_regla == "dependiente_error":
        columna = ctk.CTkInputDialog(title="Agregar Regla", text="Ingrese la columna a validar numerico (por ejemplo, Telefono):")
        columna_result = columna.get_input()
        if not columna_result:
            return
        
        columna_dependiente = ctk.CTkInputDialog(title="Columna Dependiente", text="¿De qué columna depende esta regla? (por ejemplo, A):")
        columna_dependiente_result = columna_dependiente.get_input()
        if not columna_dependiente_result:
            return
        
        valor_dependiente = ctk.CTkInputDialog(title="Valor Dependiente", text="¿Qué valor debe tener la columna dependiente? (ejemplo: VEN):")
        valor_dependiente_result = valor_dependiente.get_input()
        if not valor_dependiente_result:
            return
        
        valor_dependiente_result = float(valor_dependiente_result) if valor_dependiente_result.replace('.', '', 1).isdigit() else valor_dependiente_result
        
        valor_esperado = ctk.CTkInputDialog(title="Valor Esperado", text="¿Qué valor debe tener la columna a validar si la columna dependiente tiene este valor? (ejemplo: NO APLICA):")
        valor_esperado_result = valor_esperado.get_input()

        if not valor_esperado_result:
            return
        
        nueva_regla = {
            "columna": columna_result, 
            "tipo": "dependiente_error", 
            "columna_dependiente": columna_dependiente_result, 
            "valor_dependiente": valor_dependiente_result, 
            "valor_esperado": valor_esperado_result
        }
        
        
    elif tipo_regla == "no_vacio":
        columnas = ctk.CTkInputDialog(
            title="No Vacío", 
            text="Ingrese las columnas que no pueden estar vacías, separadas por comas (ejemplo: A, B, C):"
        )
        columnas_resultado = columnas.get_input()

        if not columnas_resultado:
            return
        
        columna = "Ficha_fic"
        columnas_resultado = [col.strip() for col in columnas_resultado.split(",") if col.strip()]
        nueva_regla = {"columna": columna, "tipo": "no_vacio", "columnas": columnas_resultado}

    
    elif tipo_regla == "dependiente longitud":
        columna = ctk.CTkInputDialog(
            title="Agregar Regla", 
            text="Ingrese la columna a validar (por ejemplo, DOCUMENTO):"
        )
        columna_resultado = columna.get_input()
        if not columna_resultado:
            return
        
        columna_dependiente = ctk.CTkInputDialog(
            title="Columna Dependiente", 
            text="¿De qué columna depende esta regla? (por ejemplo, TIPO DOCUMENTO):"
        )
        columna_dependiente_resultado = columna_dependiente.get_input()
        if not columna_dependiente_resultado:
            return

        valor_dependiente = ctk.CTkInputDialog(
            title="Valor Dependiente", 
            text="¿Qué valor debe tener la columna dependiente? (ejemplo: 3- TI):"
        )
        valor_dependiente_resultado = valor_dependiente.get_input()
        if not valor_dependiente_resultado:
            return

        valor_esperado = ctk.CTkInputDialog(
            title="Valor Esperado", 
            text="¿Qué cantidad de dígitos debe tener la columna a validar (por ejemplo: 10)?"
        )
        valor_esperado_resultado = valor_esperado.get_input()
        if not valor_esperado_resultado:
            return

        nueva_regla = {
            "columna": columna_resultado,
            "tipo": "dependiente longitud",
            "columna_dependiente": columna_dependiente_resultado,
            "valor_dependiente": valor_dependiente_resultado,
            "valor_esperado": f"<= {valor_esperado_resultado}"
        }

    elif tipo_regla == "dependiente edad positivo":
        columna = ctk.CTkInputDialog(
            title="Agregar Regla", 
            text="Ingrese la columna a validar (por ejemplo, ESTADO CIVIL):"
        )
        columna_resultado = columna.get_input()
        if not columna_resultado:
            return
        
        columna_dependiente = ctk.CTkInputDialog(
            title="Columna Dependiente", 
            text="¿De qué columna depende esta regla? (por ejemplo, FECHA DE NACIMIENTO):"
        )
        columna_dependiente_resultado = columna_dependiente.get_input()
        if not columna_dependiente_resultado:
            return

        valor_dependiente = ctk.CTkInputDialog(
            title="Valor Dependiente", 
            text="Indique la edad o rango de edades separados por coma (por ejemplo: 7,17):"
        )
        valor_dependiente_resultado = valor_dependiente.get_input()
        if not valor_dependiente_resultado:
            return

        valor_esperado = ctk.CTkInputDialog(
            title="Valor Esperado", 
            text="Valor esperado según la edad:"
        )
        valor_esperado_resultado = valor_esperado.get_input()
        if not valor_esperado_resultado:
            return

        Columna_para_fecha = ctk.CTkInputDialog(
            title="Agregar Regla", 
            text="Ingrese la columna sobre la cual se calculará la edad (por ejemplo, Fecha_intervencion):"
        )
        Columna_para_fecha_resultado = Columna_para_fecha.get_input()
        if not Columna_para_fecha_resultado:
            return
        
        nacionalidad = ctk.CTkInputDialog(
            title="Agregar Regla", 
            text="Ingrese la nacionalidad (por ejemplo, Col):"
        )
        
        nacionalidad_resultado = nacionalidad.get_input()
        if not nacionalidad_resultado:
            return
            

        nueva_regla = {
            "columna": columna_resultado,
            "nacionalidad": nacionalidad_resultado,
            "tipo": "dependiente edad positivo",
            "Fecha_int": Columna_para_fecha_resultado,
            "columna_dependiente": columna_dependiente_resultado,
            "valor_dependiente": valor_dependiente_resultado,
            "valor_esperado": valor_esperado_resultado
        }

        
    elif tipo_regla == "dependiente edad error":
        columna = ctk.CTkInputDialog(
            title="Agregar Regla", 
            text="Ingrese la columna a validar (por ejemplo, ESTADO CIVIL):"
        )
        columna_resultado = columna.get_input()
        if not columna_resultado:
            return
        
        columna_dependiente = ctk.CTkInputDialog(
            title="Columna Dependiente", 
            text="¿De qué columna depende esta regla? (por ejemplo, FECHA DE NACIMIENTO):"
        )
        columna_dependiente_resultado = columna_dependiente.get_input()
        if not columna_dependiente_resultado:
            return

        valor_dependiente = ctk.CTkInputDialog(
            title="Valor Dependiente", 
            text="Indique la edad o rango de edades separados por coma (por ejemplo: 7,17):"
        )
        valor_dependiente_resultado = valor_dependiente.get_input()
        if not valor_dependiente_resultado:
            return

        valor_esperado = ctk.CTkInputDialog(
            title="Valor Esperado", 
            text="Ingrese el valor que es error:"
        )
        valor_esperado_resultado = valor_esperado.get_input()
        if not valor_esperado_resultado:
            return

        Columna_para_fecha = ctk.CTkInputDialog(
            title="Agregar Regla", 
            text="Ingrese la columna sobre la cual se calculará la edad (por ejemplo, Fecha_intervencion):"
        )
        Columna_para_fecha_resultado = Columna_para_fecha.get_input()
        if not Columna_para_fecha_resultado:
            return
        
        nacionalidad = ctk.CTkInputDialog(
            title="Agregar Regla", 
            text="Ingrese la nacionalidad (por ejemplo, colombia):"
        )
        
        nacionalidad_resultado = nacionalidad.get_input()
        if not nacionalidad_resultado:
            return
        

        nueva_regla = {
            "columna": columna_resultado,
            "tipo": "dependiente edad error",
            "nacionalidad": nacionalidad_resultado,
            "Fecha_int": Columna_para_fecha_resultado,
            "columna_dependiente": columna_dependiente_resultado,
            "valor_dependiente": valor_dependiente_resultado,
            "valor_esperado": valor_esperado_resultado
        }

    else:
        messagebox.showerror("Error", "Tipo de regla no reconocido.")
        return

    validador["reglas"].append(nueva_regla)
    guardar_areas()
    gestionar_validador(area, validador)
