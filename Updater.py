"""
updater.py - Con sistema de logging visible para debugging
"""

import os
import sys
import zipfile
import tempfile
import threading
import urllib.request
import subprocess
import traceback
import datetime
from pathlib import Path

# ── Configuración ────────────────────────────────────────────────────────────
GITHUB_USER   = "argg9822"
GITHUB_REPO   = "validatorsGesi"
GITHUB_BRANCH = "main"
# ─────────────────────────────────────────────────────────────────────────────

RAW_BASE    = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"
VERSION_URL = f"{RAW_BASE}/__version__.py"
ZIP_URL     = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent.resolve()
else:
    APP_DIR = Path(__file__).parent.resolve()

# ── Logger central ───────────────────────────────────────────────────────────

LOG_FILE = APP_DIR / "update_log.txt"

def _log(msg: str):
    """Escribe en consola, en archivo y en la ventana de debug si existe"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    if _debug_window and _debug_window.is_alive():
        _debug_window.append(line)


# ── Ventana de debug separada ─────────────────────────────────────────────────

_debug_window = None

class DebugWindow(threading.Thread):
    """
    Ventana Tkinter independiente que vive en su propio hilo.
    Muestra logs en tiempo real y NO se cierra con la app principal.
    """
    def __init__(self):
        super().__init__(daemon=False)
        self._queue = []
        self._lock  = threading.Lock()
        self._text_widget = None
        self._alive = True
        self.start()

    def is_alive(self):
        return self._alive

    def append(self, msg: str):
        with self._lock:
            self._queue.append(msg)

    def run(self):
        import tkinter as tk
        root = tk.Tk()
        root.title("🔧 Log de actualización - Odin")
        root.geometry("780x420")
        root.configure(bg="#1e1e1e")

        tk.Label(
            root, text="Log de actualización en tiempo real",
            bg="#1e1e1e", fg="#00d4aa", font=("Consolas", 11, "bold")
        ).pack(pady=(8, 2))

        tk.Label(
            root, text=f"Log guardado en: {LOG_FILE}",
            bg="#1e1e1e", fg="#888888", font=("Consolas", 8)
        ).pack()

        frame = tk.Frame(root, bg="#1e1e1e")
        frame.pack(fill="both", expand=True, padx=10, pady=8)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(
            frame,
            bg="#0d0d0d", fg="#e0e0e0",
            font=("Consolas", 9),
            yscrollcommand=scrollbar.set,
            wrap="word", state="disabled",
            insertbackground="white"
        )
        text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text.yview)

        text.tag_config("ERROR",   foreground="#ff5555")
        text.tag_config("OK",      foreground="#50fa7b")
        text.tag_config("WARN",    foreground="#ffb86c")
        text.tag_config("INFO",    foreground="#8be9fd")
        text.tag_config("DEFAULT", foreground="#e0e0e0")

        self._text_widget = text

        def _detect_tag(line: str) -> str:
            u = line.upper()
            if any(k in u for k in ["ERROR", "EXCEPCION", "FAILED", "FALLO", "DENEGADO", "ERRORLEVEL"]):
                return "ERROR"
            if any(k in u for k in ["OK", "COMPLETO", "EXITOSO", "LISTO", "COPIADO"]):
                return "OK"
            if "WARN" in u or "AVISO" in u:
                return "WARN"
            if any(k in u for k in ["CONECTANDO", "DESCARGANDO", "EXTRAYENDO", "COPIANDO", "REINICIANDO"]):
                return "INFO"
            return "DEFAULT"

        def _flush_queue():
            with self._lock:
                pending = self._queue[:]
                self._queue.clear()
            if pending:
                text.config(state="normal")
                for line in pending:
                    tag = _detect_tag(line)
                    text.insert("end", line + "\n", tag)
                text.see("end")
                text.config(state="disabled")
            root.after(200, _flush_queue)

        root.after(200, _flush_queue)

        def _on_close():
            self._alive = False
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", _on_close)
        root.mainloop()
        self._alive = False


def open_debug_window():
    """Abre la ventana de log. Llámala ANTES de iniciar la actualización."""
    global _debug_window
    try:
        LOG_FILE.unlink(missing_ok=True)
    except Exception:
        pass
    _debug_window = DebugWindow()
    _log("=== Sesión de actualización iniciada ===")
    _log(f"APP_DIR  : {APP_DIR}")
    _log(f"Frozen   : {getattr(sys, 'frozen', False)}")
    _log(f"Exe      : {sys.executable}")


# ── Lógica de versiones ───────────────────────────────────────────────────────

def _normalize_version(v: str) -> str:
    """Elimina prefijo 'v' o 'V' y espacios para comparación uniforme."""
    return v.strip().lstrip("vV").strip()


def _get_local_version() -> str:
    # 1. Intentar primero version.txt
    version_file = APP_DIR / "version.txt"
    if version_file.exists():
        try:
            v = version_file.read_text(encoding="utf-8").strip().replace('\r', '').replace('\n', '')
            v = _normalize_version(v)
            if v:
                _log(f"Versión local detectada: {v}")
                return v
        except Exception as e:
            _log(f"Error leyendo version.txt: {e}")

    # 2. Si no existe version.txt, buscar en __version__.py
    version_py = APP_DIR / "__version__.py"
    if version_py.exists():
        try:
            for line in version_py.read_text(encoding="utf-8").splitlines():
                if "__version__" in line and "=" in line:
                    v = _normalize_version(line.split("=")[1].strip().strip("'\""))
                    # Guardar para la próxima vez
                    version_file.write_text(v, encoding="utf-8")
                    _log(f"Versión local detectada desde __version__.py: {v}")
                    return v
        except Exception as e:
            _log(f"Error leyendo __version__.py: {e}")

    _log("WARN: No se encontró versión. Usando 0.0.0")
    return "0.0.0"


def _parse_version(text: str) -> str:
    for line in text.splitlines():
        if "__version__" in line and "=" in line:
            return _normalize_version(line.split("=")[1].strip().strip("'\""))
    return "0.0.0"


def _version_tuple(v: str):
    v = _normalize_version(v)
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0, 0, 0)


def check_for_update() -> dict:
    current = _get_local_version()
    _log(f"Versión local normalizada: {current}")
    _log(f"Consultando versión remota: {VERSION_URL}")
    try:
        req = urllib.request.Request(
            VERSION_URL,
            headers={"Cache-Control": "no-cache", "User-Agent": "ValidatorsGesi-Updater"}
        )
        # FIX: timeout más conservador + manejo de error de conexión explícito
        with urllib.request.urlopen(req, timeout=15) as resp:
            remote_text = resp.read().decode("utf-8")
        remote_ver = _parse_version(remote_text)
        _log(f"Versión remota normalizada: {remote_ver}")

        local_tuple  = _version_tuple(current)
        remote_tuple = _version_tuple(remote_ver)
        _log(f"Comparando: local={local_tuple} vs remoto={remote_tuple}")

        available = remote_tuple > local_tuple
        _log(f"Actualización disponible: {available}")
        return {
            "available":       available,
            "remote_version":  remote_ver,
            "current_version": current,
        }
    except urllib.error.URLError as e:
        _log(f"ERROR de red al consultar versión remota: {e}")
        return {"available": False, "error": str(e), "current_version": current}
    except Exception as e:
        _log(f"ERROR inesperado al consultar versión remota: {e}")
        _log(traceback.format_exc())
        return {"available": False, "error": str(e), "current_version": current}


# ── Descarga e instalación ────────────────────────────────────────────────────

def download_and_apply(remote_version: str, progress_callback=None, status_callback=None) -> bool:

    def _status(msg):
        _log(msg)
        if status_callback:
            status_callback(msg)

    def _progress(pct):
        if progress_callback:
            progress_callback(int(pct))

    try:
        _status("Conectando con GitHub...")
        _progress(5)

        tmp_dir  = Path(tempfile.mkdtemp(prefix="gesi_update_"))
        zip_path = tmp_dir / "update.zip"
        _log(f"Directorio temporal: {tmp_dir}")

        _status("Descargando actualización...")
        req = urllib.request.Request(
            ZIP_URL, headers={"User-Agent": "ValidatorsGesi-Updater"}
        )
        # FIX: timeout razonable para la descarga del ZIP
        with urllib.request.urlopen(req, timeout=120) as resp:
            total      = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            _log(f"Tamaño del ZIP: {total / 1024:.1f} KB" if total else "Tamaño desconocido")
            with open(zip_path, "wb") as f:
                while True:
                    chunk = resp.read(16384)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        _progress(5 + int(downloaded / total * 55))

        _log(f"ZIP descargado OK: {downloaded / 1024:.1f} KB")

        _status("Extrayendo archivos...")
        _progress(60)
        extract_dir = tmp_dir / "extracted"
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        subdirs = [p for p in extract_dir.iterdir() if p.is_dir()]
        _log(f"Subdirectorios extraídos: {[str(s) for s in subdirs]}")
        if not subdirs:
            raise Exception("ZIP vacío o con formato inesperado")
        source_root = subdirs[0]
        _log(f"Raíz del source: {source_root}")

        _status("Preparando script de instalación...")
        _progress(80)
        # FIX: llamada duplicada eliminada — solo se llama UNA vez
        _create_install_script(source_root, tmp_dir, remote_version)
        _log(f"Script creado en: {APP_DIR / 'finish_update.bat'}")

        _status("¡Descarga completa! Aplicando actualización...")
        _progress(100)

        import time; time.sleep(1.5)

        finalize_update()
        return True

    except urllib.error.URLError as e:
        _log(f"ERROR de red en download_and_apply: {e}")
        if status_callback:
            status_callback(f"Error de red: {e}")
        return False
    except Exception as e:
        _log(f"ERROR en download_and_apply: {e}")
        _log(traceback.format_exc())
        if status_callback:
            status_callback(f"Error: {e}")
        return False


def _create_install_script(src_path: Path, tmp_dir: Path, new_version: str):
    script_path = APP_DIR / "finish_update.bat"
    exe_name = "Odin.exe"

    app_dir_str = str(APP_DIR)
    bat_log = f'"{app_dir_str}\\update_log.txt"'

    content = f"""@echo off
chcp 65001 > nul
title Actualizando Componentes de Odin...

echo [%date% %time%] === INICIO DE ACTUALIZACIÓN DE LÓGICA === >> {bat_log}

echo [1/4] Cerrando procesos...
taskkill /IM {exe_name} /T /F >> {bat_log} 2>&1
timeout /t 3 /nobreak > nul

echo [2/4] Sincronizando archivos internos y lógica...
robocopy "{src_path}" "{app_dir_str}" /E /IS /IT /R:3 /W:2 /XF {exe_name} update_log.txt finish_update.bat /XD .git .vscode .github __pycache__ /LOG+:{bat_log} /TEE

if %ERRORLEVEL% GEQ 8 (
    echo [ERROR] Robocopy falló con código %ERRORLEVEL% >> {bat_log}
    msg * "Error crítico al copiar archivos. Revisa update_log.txt"
    exit
)

echo [3/4] Actualizando registro de versión a {new_version}...
del /f /q "{app_dir_str}\\version.txt" >> {bat_log} 2>&1
(echo {new_version})>"{app_dir_str}\\version.txt"

echo [4/4] Limpieza de temporales...
rd /s /q "{tmp_dir}" >> {bat_log} 2>&1

echo [OK] Actualización terminada exitosamente. >> {bat_log}
timeout /t 2 /nobreak > nul

start "" /D "{app_dir_str}" "{app_dir_str}\\{exe_name}"
"""
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(content)


def finalize_update():
    script = APP_DIR / "finish_update.bat"
    if not script.exists():
        _log(f"ERROR: finish_update.bat no encontrado en {APP_DIR}")
        return
    _log("Lanzando finish_update.bat y cerrando app...")
    try:
        subprocess.Popen(
            ["cmd.exe", "/c", str(script)],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            close_fds=True
        )
        os._exit(0)
    except Exception as e:
        _log(f"ERROR al lanzar script: {e}")
        _log(traceback.format_exc())


# ── API asíncrona ─────────────────────────────────────────────────────────────

def check_update_async(callback):
    threading.Thread(
        target=lambda: callback(check_for_update()),
        daemon=True
    ).start()


def apply_update_async(remote_version: str, progress_cb=None, status_cb=None, done_cb=None):
    def _run():
        ok = download_and_apply(remote_version, progress_cb, status_cb)
        if done_cb:
            done_cb(ok)
    threading.Thread(target=_run, daemon=True).start()