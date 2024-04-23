from setuptools import setup, find_packages
from __version__ import __version__

setup(
    name='nombre_del_paquete',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'colorama',
        'Pillow',
        'openpyxl',
        'pandas',
    ],
)