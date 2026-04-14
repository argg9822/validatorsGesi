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
import subprocess
from pathlib import Path

# ── Configuración ────────────────────────────────────────────────────────────
GITHUB_USER   = "argg9822"
GITHUB_REPO   = "validatorsGesi"
GITHUB_BRANCH = "main"
# ─────────────────────────────────────────────────────────────────────────────

RAW_BASE    = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
VERSION_URL = f"{RAW_BASE}/__version__.py"
ZIP_URL     = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"

APP_DIR = Path(__file__).parent.resolve()


def _get_local_version() -> str:
    """
    Lee la versión SIEMPRE desde version.txt en disco.
    Esto funciona correctamente aunque el .exe esté congelado por PyInstaller.
    """
    version_file = APP_DIR / "version.txt"
    if version_file.exists():
        v = version_file.read_text(encoding="utf-8").strip()
        if v:
            return v
    # Fallback: leer __version__.py desde disco (no desde el módulo importado)
    version_py = APP_DIR / "__version__.py"
    if version_py.exists():
        for line in version_py.read_text(encoding="utf-8").splitlines():
            if "__version__" in line and "=" in line:
                return line.split("=")[1].strip().strip("'\"")
    return "0.0.0"


def _parse_version(text: str) -> str:
    """Extrae la versión del contenido de __version__.py remoto"""
    for line in text.splitlines():
        if "__version__" in line and "=" in line:
            return line.split("=")[1].strip().strip("'\"")
    return "0.0.0"


def _version_tuple(v: str):
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0, 0, 0)


def check_for_update() -> dict:
    """Compara versión local (version.txt) vs remota (GitHub)"""
    current = _get_local_version()
    try:
        req = urllib.request.Request(
            VERSION_URL,
            headers={"Cache-Control": "no-cache", "User-Agent": "ValidatorsGesi-Updater"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            remote_text = resp.read().decode("utf-8")
        remote_ver = _parse_version(remote_text)

        available = _version_tuple(remote_ver) > _version_tuple(current)

        return {
            "available": available,
            "remote_version": remote_ver,
            "current_version": current
        }
    except Exception as e:
        return {"available": False, "error": str(e), "current_version": current}


def download_and_apply(progress_callback=None, status_callback=None) -> bool:
    """Descarga el ZIP y prepara el script de instalación"""

    def _status(msg):
        if status_callback:
            status_callback(msg)

    def _progress(pct):
        if progress_callback:
            progress_callback(int(pct))

    try:
        _status("Conectando con GitHub...")
        _progress(5)

        tmp_dir = Path(tempfile.mkdtemp(prefix="gesi_update_"))
        zip_path = tmp_dir / "update.zip"

        # ── Descarga ──────────────────────────────────────────────────────────
        req = urllib.request.Request(
            ZIP_URL, headers={"User-Agent": "ValidatorsGesi-Updater"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(zip_path, "wb") as f:
                while True:
                    chunk = resp.read(16384)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        _progress(5 + int(downloaded / total * 55))

        _status("Extrayendo archivos...")
        _progress(60)

        extract_dir = tmp_dir / "extracted"
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        # GitHub descomprime en una subcarpeta tipo "repo-main"
        subdirs = [p for p in extract_dir.iterdir() if p.is_dir()]
        if not subdirs:
            raise Exception("ZIP de actualización vacío o con formato inesperado")
        source_root = subdirs[0]

        _status("Preparando instalación...")
        _progress(80)

        _create_install_script(source_root, tmp_dir)

        _status("¡Descarga completa! Reiniciando para aplicar...")
        _progress(100)
        return True

    except Exception as e:
        _status(f"Error durante la descarga: {e}")
        return False


def _create_install_script(src_path: Path, tmp_dir: Path):
    """
    Crea finish_update.bat en APP_DIR.
    
    Estrategia:
      1. Espera a que Odin.exe se cierre (taskkill + timeout)
      2. Copia archivos nuevos con Robocopy (sin /MOVE para no perder fuente si falla)
      3. Actualiza version.txt con la nueva versión
      4. Limpia el temporal
      5. Reinicia Odin.exe
    """
    script_path = APP_DIR / "finish_update.bat"

    # Nueva versión extraída desde el source
    new_version = "desconocida"
    ver_file = src_path / "version.txt"
    if ver_file.exists():
        new_version = ver_file.read_text(encoding="utf-8").strip()
    else:
        ver_py = src_path / "__version__.py"
        if ver_py.exists():
            for line in ver_py.read_text(encoding="utf-8").splitlines():
                if "__version__" in line and "=" in line:
                    new_version = line.split("=")[1].strip().strip("'\"")
                    break

    exe_name = "Odin.exe"
    if getattr(sys, "frozen", False):
        restart_cmd = f'start "" "{APP_DIR}\\{exe_name}"'
    else:
        restart_cmd = f'start "" python "{APP_DIR}\\Odin.py"'

    content = f"""@echo off
chcp 65001 > nul
title Actualizando Odin...

echo ============================================
echo   Esperando cierre del programa...
echo ============================================

:: Intenta cerrar Odin.exe si sigue abierto
taskkill /IM {exe_name} /F > nul 2>&1
timeout /t 3 /nobreak > nul

:: Espera adicional para liberar bloqueos de archivo
:wait_loop
tasklist /FI "IMAGENAME eq {exe_name}" 2>nul | find /I "{exe_name}" > nul
if not errorlevel 1 (
    timeout /t 2 /nobreak > nul
    goto wait_loop
)

echo Copiando archivos nuevos...
robocopy "{src_path}" "{APP_DIR}" /E /IS /IT /R:5 /W:3
if errorlevel 8 (
    echo ERROR: Robocopy fallo con codigo de error grave.
    pause
    goto cleanup
)

echo Actualizando version...
echo {new_version}> "{APP_DIR}\\version.txt"

:cleanup
echo Limpiando archivos temporales...
rd /s /q "{tmp_dir}" > nul 2>&1

echo Reiniciando aplicacion...
{restart_cmd}

del "%~f0"
"""
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(content)


def finalize_update():
    """Lanza el .bat de actualización y cierra el programa"""
    script = APP_DIR / "finish_update.bat"
    if not script.exists():
        print("Error: finish_update.bat no encontrado")
        return

    try:
        subprocess.Popen(
            ["cmd.exe", "/c", str(script)],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            close_fds=True
        )
        os._exit(0)
    except Exception as e:
        print(f"Error al lanzar el script de actualización: {e}")


# ── API asíncrona para CustomTkinter ─────────────────────────────────────────

def check_update_async(callback):
    threading.Thread(
        target=lambda: callback(check_for_update()),
        daemon=True
    ).start()


def apply_update_async(progress_cb=None, status_cb=None, done_cb=None):
    def _run():
        ok = download_and_apply(progress_cb, status_cb)
        if done_cb:
            done_cb(ok)
    threading.Thread(target=_run, daemon=True).start()