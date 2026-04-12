# ValidatorsGesi — Guía completa

## 🚀 Instalación rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/Monhabell/validatorsGesi.git
cd validatorsGesi

# 2. Instalar dependencias
pip install customtkinter pandas openpyxl

# 3. Ejecutar
python index.py
```

---

## 🔄 Sistema de Auto-Actualización

El programa se actualiza **solo**, directamente desde GitHub, sin reinstalar.

### ¿Cómo funciona?
1. Al abrir la app, verifica silenciosamente la versión en `__version__.py` del repositorio.
2. Si hay una versión más nueva, aparece un **banner azul** en la parte superior.
3. Haz clic en **"Ver →"** para abrir el diálogo de actualización.
4. Pulsa **"Actualizar ahora"** — el programa descarga el ZIP del repo, extrae y reemplaza los archivos `.py` y `.json`.
5. Reinicia la app para usar la nueva versión.

### ¿Cómo publicar una actualización?
1. Modifica el código y sube los cambios a GitHub.
2. Incrementa la versión en `__version__.py`:
   ```python
   __version__ = '1.2.0'   # de 1.1.0 a 1.2.0
   ```
3. Haz `git push`. ¡Listo! Los usuarios verán la actualización al abrir la app.

---

## 📂 Estructura del proyecto

```
validatorsGesi/
├── index.py            # Interfaz principal (CustomTkinter)
├── updater.py          # Motor de auto-actualización desde GitHub
├── __version__.py      # Versión actual — ESTE ARCHIVO controla las actualizaciones
├── validadores/
│   ├── __init__.py
│   ├── beneficiarios.py   # Validador de beneficiarios (ejemplo completo)
│   ├── actividades.py     # Tu validador de actividades
│   ├── recursos.py        # Tu validador de recursos
│   └── indicadores.py     # Tu validador de indicadores
└── output/             # Reportes generados (creado automáticamente)
```

---

## ➕ Agregar un nuevo validador

Crea un archivo en `validadores/mi_modulo.py` con esta interfaz:

```python
def validate(file_path: str, progress_cb=None) -> dict:
    """
    file_path   : ruta al archivo Excel
    progress_cb : función(pct: int, mensaje: str) — opcional
    Retorna     : {"ok": bool, "message": str, "errors": list, "output_file": str|None}
    """
    # Tu lógica aquí
    errors = []
    # ...
    return {
        "ok":          len(errors) == 0,
        "message":     "Sin errores" if not errors else f"{len(errors)} errores encontrados",
        "errors":      errors,
        "output_file": None
    }
```

Luego en `index.py`, agrega la tarjeta en `_page_validators()`:

```python
("Mi Nuevo Validador",
 "Descripción del validador.",
 "🔍", self._run_validator_mi_modulo),
```

Y el callback:

```python
def _run_validator_mi_modulo(self, path):
    self._run_validator(path, "mi_modulo", "Mi Módulo")
```

---

## 🛠️ Dependencias

| Librería       | Uso                        |
|----------------|----------------------------|
| customtkinter  | Interfaz gráfica moderna   |
| pandas         | Lectura de archivos Excel  |
| openpyxl       | Escritura de reportes xlsx |

Instalar todo: `pip install customtkinter pandas openpyxl`

---

## 📋 Versiones

| Versión | Cambios |
|---------|---------|
| 1.1.0   | Nuevo diseño UI, auto-actualización desde GitHub, arquitectura modular |
| 1.0.1   | Versión original |
