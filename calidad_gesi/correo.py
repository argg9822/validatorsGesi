# -*- coding: utf-8 -*-
"""
calidad_gesi/correo.py — Trae el último correo de calidad desde Gmail (IMAP) y guarda sus adjuntos.

Requiere una "contraseña de aplicación" de Google (no la contraseña normal):
  Cuenta de Google → Seguridad → Verificación en 2 pasos → Contraseñas de aplicaciones.
Las credenciales se guardan cifradas con Windows DPAPI (igual que credentials_store.py).
"""
import email, imaplib, json, re, zipfile
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from pathlib import Path

_CFG = Path(__file__).parent.parent.resolve() / '.gmail_calidad'
EXT_UTILES = ('.xlsx', '.xls', '.csv', '.txt', '.zip')

# ───────── credenciales cifradas ─────────
def _enc(b):
    try:
        import win32crypt; return win32crypt.CryptProtectData(b, 'OdinGmail', None, None, None, 0)
    except ImportError: return b
def _dec(b):
    try:
        import win32crypt; return win32crypt.CryptUnprotectData(b, None, None, None, 0)[1]
    except ImportError: return b

def guardar_config(correo, clave_app, remitente='gesitecnico1@gmail.com', asunto='calidad'):
    _CFG.write_bytes(_enc(json.dumps({'u': correo, 'p': clave_app.replace(' ', ''),
                                      'remitente': remitente, 'asunto': asunto}).encode('utf-8')))

def cargar_config():
    if not _CFG.exists(): return {}
    try: return json.loads(_dec(_CFG.read_bytes()).decode('utf-8'))
    except Exception: return {}

# ───────── utilidades ─────────
def _txt(h):
    try: return str(make_header(decode_header(h or '')))
    except Exception: return h or ''

def _limpio(nombre):
    return re.sub(r'[\\/:*?"<>|]', '_', nombre).strip() or 'adjunto'

def _guardar_partes(msg, carpeta, guardados):
    """Recorre el mensaje (incluye correos reenviados adjuntos .eml) y guarda los adjuntos útiles."""
    for part in msg.walk():
        if part.get_content_type() == 'message/rfc822':
            continue  # walk() ya desciende a su contenido
        nombre = part.get_filename()
        if not nombre: continue
        nombre = _limpio(_txt(nombre))
        if not nombre.lower().endswith(EXT_UTILES): continue
        data = part.get_payload(decode=True)
        if not data: continue
        destino, i = carpeta / nombre, 2
        while destino.exists():
            destino = carpeta / f"{Path(nombre).stem} ({i}){Path(nombre).suffix}"; i += 1
        destino.write_bytes(data)
        if destino.suffix.lower() == '.zip':
            try:
                with zipfile.ZipFile(destino) as z:
                    for n in z.namelist():
                        if n.lower().endswith(EXT_UTILES[:-1]):
                            z.extract(n, carpeta); guardados.append(carpeta / n)
            except zipfile.BadZipFile: pass
        else:
            guardados.append(destino)

def traer_ultimo_correo(carpeta_base, remitente=None, asunto=None, progress=None):
    """Busca el correo MÁS RECIENTE con adjuntos que cumpla remitente/asunto y guarda los adjuntos.
    Retorna {'asunto','de','fecha','archivos':[Path], 'carpeta': Path}."""
    cfg = cargar_config()
    if not cfg.get('u') or not cfg.get('p'):
        raise RuntimeError('Configura primero tu correo y la contraseña de aplicación de Google.')
    remitente = remitente if remitente is not None else cfg.get('remitente', '')
    asunto = asunto if asunto is not None else cfg.get('asunto', '')
    if progress: progress(5, 'Conectando a Gmail…')
    M = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    try:
        M.login(cfg['u'], cfg['p'])
        # Carpeta "Todos" (\All) para incluir correos archivados; si no se encuentra, Recibidos
        todos = None
        typ, carpetas = M.list()
        for linea in carpetas or []:
            l = linea.decode('utf-8', 'ignore')
            if '\\All' in l:
                todos = l.split(' "/" ')[-1].strip(); break
        if not todos or M.select(todos, readonly=True)[0] != 'OK':
            M.select('INBOX', readonly=True)
        consulta = 'has:attachment'
        if remitente: consulta += f' from:{remitente}'
        if asunto: consulta += f' subject:({asunto})'
        if progress: progress(15, f'Buscando: {consulta}')
        typ, data = M.uid('search', None, 'X-GM-RAW', f'"{consulta}"')
        uids = data[0].split() if typ == 'OK' and data and data[0] else []
        if not uids:
            raise RuntimeError(f'No encontré correos con: {consulta}')
        uid = uids[-1]                                   # el más reciente
        if progress: progress(30, 'Descargando el correo…')
        typ, msgdata = M.uid('fetch', uid, '(RFC822)')
        msg = email.message_from_bytes(msgdata[0][1])
    finally:
        try: M.logout()
        except Exception: pass
    fecha = parsedate_to_datetime(msg['Date']) if msg['Date'] else None
    carpeta = Path(carpeta_base) / (fecha.strftime('%Y-%m-%d_%H%M') if fecha else 'correo')
    carpeta.mkdir(parents=True, exist_ok=True)
    guardados = []
    _guardar_partes(msg, carpeta, guardados)
    if progress: progress(40, f'{len(guardados)} adjunto(s) guardados')
    return {'asunto': _txt(msg['Subject']), 'de': _txt(msg['From']), 'fecha': fecha,
            'archivos': guardados, 'carpeta': carpeta}

def es_exporte_gesi(path):
    """True si el archivo es un CSV exportado de GESI (empieza con 'Entorno =>')."""
    try:
        raw = Path(path).read_bytes()[:400]
        for enc in ('utf-16', 'utf-8', 'cp1252'):
            try:
                if 'Entorno =>' in raw.decode(enc, errors='ignore')[:200]: return True
            except Exception: pass
    except Exception: pass
    return False
