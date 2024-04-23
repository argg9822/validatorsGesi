from setuptools import setup, find_packages
import os
from __version__ import __version__ as version_actual_actual  # Importa la versión actual desde __version__.py

# Función para obtener todos los archivos de una carpeta y sus subcarpetas
def get_files(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

setup(
    name='Validadores_GesiApp',
    version=version_actual_actual,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'colorama',
        'Pillow',
        'openpyxl',
        'pandas',
        'requests',
        'gitpython',
        
    ],
    
    # Incluye las carpetas img y validadores y sus archivos en el paquete
    data_files=[
        ('img', get_files('img')),
        ('validadores', get_files('validadores')),
        ('index.exe'),
        ('__version__.py'),
    ]
)
