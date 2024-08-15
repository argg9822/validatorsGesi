import cx_Freeze
from cx_Freeze import setup, Executable
import os


# Incluye las carpetas img y validadores
include_files = [
    ("img", "img"),
    ("validadores", "validadores"),
    ("index.py", "index.py"),
    ("__version__.py", "__version__.py")  # Asegúrate de incluir __version__.py
]

executables = [cx_Freeze.Executable("splash.py", base=None)]

cx_Freeze.setup(
    name="Gesi App",
    version="1.0",
    description="Gesi App",
    executables=executables,
    options={"build_exe": {
        "include_files": include_files,
        "packages": ["tkinter", "PIL", "requests", "json", "zipfile", "subprocess", "sys", "openpyxl", "pandas", "re", "shutil", "datetime"],
        "includes": ["validadores", "img", "colorama", "__version__", "tkinter.filedialog", "tkinter.messagebox", "tkinter.simpledialog", "openpyxl.styles", "openpyxl.utils"],
        "excludes": ["tkinter.ttk", "tkinter.tix"]  # Optional, but recommended to avoid unnecessary dependencies
    }},
)