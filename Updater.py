"""
updater.py - Sistema de auto-actualización desde GitHub
Descarga y aplica actualizaciones directamente desde el repositorio
"""

import os
import sys
import json
import shutil
import zipfile
import tempfile
import threading
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from __version__ import __version__

# ── Configura aquí tu repositorio ─────────────────────────────────────────────
GITHUB_USER   = "Monhabell"
GITHUB_REPO   = "validatorsGesi"
GITHUB_BRANCH = "main"
# ──────────────────────────────────────────────────────────────────────────────

RAW_BASE    = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
API_BASE    = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}"
VERSION_URL = f"{RAW_BASE}/__version__.py"
ZIP_URL     = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"

APP_DIR = Path(__file__).parent.resolve()


def _parse_version(text: str) -> str:
    """Extrae la versión del contenido de __version__.py"""
    for line in text.splitlines():
        if "__version__" in line and "=" in line:
            return line.split("=")[1].strip().strip("'\"")
    return "0.0.0"


def _version_tuple(v: str):
    return tuple(int(x) for x in v.split("."))


def check_for_update() -> dict:
    """
    Compara la versión local con la del repositorio.
    Retorna: {'available': bool, 'remote_version': str, 'current_version': str}
    """
    try:
        req = urllib.request.Request(
            VERSION_URL,
            headers={"Cache-Control": "no-cache", "User-Agent": "ValidatorsGesi-Updater"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            remote_text = resp.read().decode("utf-8")
        remote_ver = _parse_version(remote_text)
        available  = _version_tuple(remote_ver) > _version_tuple(__version__)
        return {"available": available, "remote_version": remote_ver, "current_version": __version__}
    except Exception as e:
        return {"available": False, "remote_version": __version__, "current_version": __version__, "error": str(e)}


def download_and_apply(progress_callback=None, status_callback=None) -> bool:
    """
    Descarga el ZIP del repositorio y reemplaza los archivos Python/config.
    progress_callback(int 0-100), status_callback(str mensaje)
    Retorna True si la actualización fue exitosa.
    """
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
        _status("Descargando actualización...")
        req = urllib.request.Request(ZIP_URL, headers={"User-Agent": "ValidatorsGesi-Updater"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk = 8192
            with open(zip_path, "wb") as f:
                while True:
                    data = resp.read(chunk)
                    if not data:
                        break
                    f.write(data)
                    downloaded += len(data)
                    if total:
                        _progress(5 + int(downloaded / total * 50))

        _progress(55)
        _status("Descomprimiendo archivos...")

        # ── Extrae ────────────────────────────────────────────────────────────
        extract_dir = tmp_dir / "extracted"
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        # La carpeta raíz dentro del ZIP suele ser "repo-branch"
        roots = list(extract_dir.iterdir())
        source_root = roots[0] if roots else extract_dir

        _progress(65)
        _status("Aplicando actualización...")

        # ── Copia selectiva: .py, .json, carpeta validadores ──────────────────
        EXTENSIONS = {".py", ".json", ".txt"}
        SKIP_FILES  = {"setup.py"}          # no tocar setup

        def _copy_tree(src: Path, dst: Path):
            dst.mkdir(parents=True, exist_ok=True)
            for item in src.iterdir():
                if item.name.startswith(".") or item.name == "__pycache__":
                    continue
                target = dst / item.name
                if item.is_dir():
                    _copy_tree(item, target)
                elif item.suffix in EXTENSIONS and item.name not in SKIP_FILES:
                    shutil.copy2(item, target)

        _copy_tree(source_root, APP_DIR)

        _progress(90)
        _status("Limpiando archivos temporales...")
        shutil.rmtree(tmp_dir, ignore_errors=True)

        _progress(100)
        _status("¡Actualización completada con éxito!")
        return True

    except Exception as e:
        _status(f"Error durante la actualización: {e}")
        return False


def check_update_async(callback):
    """Verifica actualizaciones en hilo secundario y llama callback(result_dict)"""
    threading.Thread(target=lambda: callback(check_for_update()), daemon=True).start()


def apply_update_async(progress_cb=None, status_cb=None, done_cb=None):
    """Aplica la actualización en hilo secundario"""
    def _run():
        ok = download_and_apply(progress_cb, status_cb)
        if done_cb:
            done_cb(ok)
    threading.Thread(target=_run, daemon=True).start()