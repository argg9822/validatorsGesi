# credentials_store.py
# Guarda y carga credenciales GesiForm usando Windows DPAPI (pywin32).
# El cifrado está atado al usuario y máquina Windows — nadie más puede descifrar el archivo.

import json
from pathlib import Path

_CREDS_FILE = Path(__file__).parent.resolve() / ".gesi_creds"


def _encrypt(data: bytes) -> bytes:
    import win32crypt
    return win32crypt.CryptProtectData(data, "GesiForm", None, None, None, 0)


def _decrypt(data: bytes) -> bytes:
    import win32crypt
    _, plaintext = win32crypt.CryptUnprotectData(data, None, None, None, 0)
    return plaintext


def guardar_credenciales(usuario: str, contrasena: str) -> None:
    raw = json.dumps({"u": usuario, "p": contrasena}).encode("utf-8")
    _CREDS_FILE.write_bytes(_encrypt(raw))


def cargar_credenciales() -> tuple[str, str]:
    if not _CREDS_FILE.exists():
        return "", ""
    try:
        data = _decrypt(_CREDS_FILE.read_bytes())
        obj = json.loads(data.decode("utf-8"))
        return obj.get("u", ""), obj.get("p", "")
    except Exception:
        return "", ""


def credenciales_guardadas() -> bool:
    return _CREDS_FILE.exists()
