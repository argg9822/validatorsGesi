"""
updater.py - Sistema de auto-actualización desde GitHub
Optimizado para ValidatorsGesi (Odin.exe)
"""

import os
import sys
import zipfile
import tempfile
import threading
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

# Intentamos importar la versión local. Si falla, asumimos 0.0.0
try:
    from __version__ import __version__
except ImportError:
    __version__ = "0.0.0"

# ── Configuración de tu repositorio ─────────────────────────────────────────────
GITHUB_USER   = "argg9822"
GITHUB_REPO   = "validatorsGesi"
GITHUB_BRANCH = "main"
# ──────────────────────────────────────────────────────────────────────────────

RAW_BASE    = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
VERSION_URL = f"{RAW_BASE}/__version__.py"
ZIP_URL     = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"

# Directorio donde está instalado el programa (Odin.exe)
APP_DIR = Path(__file__).parent.resolve()

def _parse_version(text: str) -> str:
    """Extrae la versión del contenido de __version__.py remoto"""
    for line in text.splitlines():
        if "__version__" in line and "=" in line:
            return line.split("=")[1].strip().strip("'\"")
    return "0.0.0"

def _version_tuple(v: str):
    try:
        return tuple(int(x) for x in v.split("."))
    except:
        return (0, 0, 0)

def check_for_update() -> dict:
    """Compara versión local vs remota"""
    try:
        req = urllib.request.Request(
            VERSION_URL,
            headers={"Cache-Control": "no-cache", "User-Agent": "ValidatorsGesi-Updater"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            remote_text = resp.read().decode("utf-8")
        remote_ver = _parse_version(remote_text)
        
        # Lógica de comparación
        available = _version_tuple(remote_ver) > _version_tuple(__version__)
        
        return {
            "available": available, 
            "remote_version": remote_ver, 
            "current_version": __version__
        }
    except Exception as e:
        return {"available": False, "error": str(e)}

def download_and_apply(progress_callback=None, status_callback=None) -> bool:
    """Descarga y prepara la actualización"""
    def _status(msg):
        if status_callback: status_callback(msg)

    def _progress(pct):
        if progress_callback: progress_callback(int(pct))

    try:
        _status("Conectando con GitHub...")
        _progress(10)

        tmp_dir = Path(tempfile.mkdtemp(prefix="gesi_update_"))
        zip_path = tmp_dir / "update.zip"

        # Descarga del ZIP
        req = urllib.request.Request(ZIP_URL, headers={"User-Agent": "ValidatorsGesi-Updater"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(zip_path, "wb") as f:
                while True:
                    data = resp.read(8192)
                    if not data: break
                    f.write(data)
                    downloaded += len(data)
                    if total:
                        _progress(10 + int(downloaded / total * 60))

        _status("Extrayendo archivos...")
        extract_dir = tmp_dir / "extracted"
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        # Localizar la carpeta raíz real dentro del ZIP (GitHub añade '-main' al nombre)
        try:
            source_root = next(extract_dir.iterdir())
        except StopIteration:
            raise Exception("ZIP de actualización vacío")

        _status("Preparando script de instalación...")
        _create_install_script(source_root, APP_DIR)

        _status("¡Listo para reiniciar!")
        _progress(100)
        return True

    except Exception as e:
        _status(f"Error: {e}")
        return False

def _create_install_script(src_path: Path, dest_path: Path):
    """Crea un archivo .bat robusto que usa Robocopy para mover archivos"""
    script_path = dest_path / "finish_update.bat"
    
    # Determinar comando de reinicio (Odin.exe o Odin.py)
    if getattr(sys, 'frozen', False):
        restart_cmd = f"start \"\" \"{dest_path}\\Odin.exe\""
    else:
        restart_cmd = "start python Odin.py"

    # Robocopy /MOVE limpia los archivos del temporal automáticamente al terminar
    content = f"""@echo off
title Actualizando Odin...
echo ===========================================
echo   ESPERANDO A QUE EL PROGRAMA SE CIERRE...
echo ===========================================
timeout /t 5 > nul

echo Aplicando archivos nuevos...
robocopy "{src_path}" "{dest_path}" /E /IS /IT /MOVE /R:3 /W:2 /V

echo Limpiando residuos...
if exist "{src_path.parent}" rd /s /q "{src_path.parent}"

echo Reiniciando aplicacion...
{restart_cmd}
del "%~f0"
"""
    # Guardamos con encoding cp1252 para compatibilidad total con CMD Windows
    with open(script_path, "w", encoding="cp1252") as f:
        f.write(content)

def finalize_update():
    """Lanza el script .bat de forma independiente y cierra el programa actual"""
    script = APP_DIR / "finish_update.bat"
    if script.exists():
        try:
            # Popen asegura que el .bat viva aunque Odin.exe se cierre
            subprocess.Popen([str(script)], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            os._exit(0) # Salida forzosa inmediata
        except Exception as e:
            print(f"Error al lanzar el script: {e}")

# Funciones Asíncronas para la Interfaz (CustomTkinter)
def check_update_async(callback):
    threading.Thread(target=lambda: callback(check_for_update()), daemon=True).start()

def apply_update_async(progress_cb=None, status_cb=None, done_cb=None):
    def _run():
        ok = download_and_apply(progress_cb, status_cb)
        if done_cb: done_cb(ok)
    threading.Thread(target=_run, daemon=True).start()