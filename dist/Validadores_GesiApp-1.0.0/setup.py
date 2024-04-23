from setuptools import setup, find_packages
import os

# Función para obtener todos los archivos de una carpeta y sus subcarpetas
def get_files(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files

setup(
    name='Validadores_GesiApp',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'colorama',
        'Pillow',
        'openpyxl',
        'pandas',
        'requests',
    ],
    
    # Incluye las carpetas img y validadores y sus archivos en el paquete
    data_files=[
        ('img', get_files('img')),
        ('validadores', get_files('validadores')),
        ('index.exe')
    ]
)
