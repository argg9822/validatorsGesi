# -*- coding: utf-8 -*-
"""
calidad_gesi/motor.py — Motor de calidad del dato para exportes GESI (Odin)

- Lee uno o varios CSV exportados de GESI (UTF-16, separador `;`).
- Une varios archivos (p. ej. bloques de 4 meses) y quita filas repetidas.
- Aplica reglas: Secretaría (SDS), instructivos de la caja de herramientas y coherencia.
- El cruce de documentos de los tamizajes se hace contra TODOS los archivos cargados,
  así un documento que salió en SCL/UT/NNA de meses pasados sí cruza.
"""
import re, json, unicodedata
from datetime import date
from pathlib import Path

AQUI = Path(__file__).parent

# ───────────────────────── utilidades ─────────────────────────
def norm(s):
    s = unicodedata.normalize('NFD', str(s or ''))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').upper()
    s = s.replace('`', '').replace(';', '')
    return re.sub(r'\s+', ' ', s).strip()

def ni(s):  # normalización usada para el diccionario de instructivos
    s = norm(s)
    s = re.sub(r'^\s*\d+[\.\)]\s*', '', s)
    s = re.sub(r'[:¿?¡!"\'\.,]', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def to_date(s):
    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})', s or '')
    if not m: return None
    try: return date(int(m[1]), int(m[2]), int(m[3]))
    except ValueError: return None

def age_at(b, ref):
    a = ref.year - b.year
    if (ref.month, ref.day) < (b.month, b.day): a -= 1
    return a

def code(v):
    m = re.match(r'^(\d+)\s*-', v or '')
    return m[1] if m else None

def curso_esperado(e):
    if e <= 5: return 'PRIMERA INFANCIA'
    if e <= 11: return 'INFANCIA'
    if e <= 17: return 'ADOLESCENCIA'
    if e <= 28: return 'JUVENTUD'
    if e <= 59: return 'ADULTEZ'
    return 'VEJEZ'

MESES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
def mes_de(d):
    m = re.match(r'^(\d{4})-(\d{2})', d or '')
    return f"{MESES[int(m[2])-1]} {m[1]}" if m else ''

# ───────────────────────── lectura ─────────────────────────
def leer_texto(path):
    raw = Path(path).read_bytes()
    if raw[:2] == b'\xff\xfe': return raw.decode('utf-16-le').lstrip('﻿')
    if raw[:2] == b'\xfe\xff': return raw.decode('utf-16-be').lstrip('﻿')
    if len(raw) > 3 and raw[1] == 0 and raw[3] == 0: return raw.decode('utf-16-le')
    try: return raw.decode('utf-8').lstrip('﻿')
    except UnicodeDecodeError: return raw.decode('cp1252')

class Bloque:
    def __init__(self, entorno, modulo, seccion, headers):
        self.entorno, self.modulo, self.seccion = entorno, modulo, seccion
        self.headers = headers
        self.N = [norm(h) for h in headers]
        self.rows, self.origen = [], []   # origen[i] = archivo de la fila i

def _fix(l): return l.replace('`;Sub-Sección', '`;`Sub-Sección')

def parse_gesi(texto, archivo=''):
    bloques, mod, sec, ent, cur = [], '', '', '', None
    for l in texto.splitlines():
        if l.startswith('Entorno =>'): ent = l[10:].strip(); continue
        if l.startswith('Módulo =>'): mod = l[9:].strip(); continue
        if l.startswith('Sección =>'): sec = l[10:].strip(); continue
        if l.startswith('Sub-Sección =>'):
            l = re.sub(r'[`;]+$', '', _fix(l))
            h = [x.strip() for x in l.strip('`').split('`;`')]
            cur = Bloque(ent, mod, sec, h); bloques.append(cur); continue
        if not l.strip() or cur is None: continue
        l = _fix(l)
        l = re.sub(r'`?;$', '', l)
        r = [x.strip() for x in l.strip('`').split('`;`')]
        r += [''] * (len(cur.headers) - len(r))
        cur.rows.append(r); cur.origen.append(archivo)
    return bloques

def cargar_archivos(paths, progress=None):
    """Une varios exportes. Bloques con igual módulo+sección+encabezados se fusionan
    y se descartan filas idénticas (meses que se traslapan)."""
    unidos, vistos = {}, {}
    for k, p in enumerate(paths):
        if progress: progress(int(5 + 30 * k / max(1, len(paths))), f"Leyendo {Path(p).name}…")
        for b in parse_gesi(leer_texto(p), Path(p).name):
            key = (b.modulo, b.seccion, tuple(b.N))
            if key not in unidos:
                unidos[key] = Bloque(b.entorno, b.modulo, b.seccion, b.headers); vistos[key] = {}
            u = unidos[key]
            for r, o in zip(b.rows, b.origen):
                t = tuple(r)
                if vistos[key].get(t, k) != k: continue   # misma fila ya vino en otro archivo
                vistos[key].setdefault(t, k); u.rows.append(r); u.origen.append(o)
    return list(unidos.values())

# ───────────────────────── instructivos ─────────────────────────
try:
    _INS = json.loads((AQUI / 'instructivo.json').read_text(encoding='utf-8'))
except Exception:
    _INS = {'dicc': {}, 'oblig': {}}

def instructivo(b, col):
    m = _INS['dicc'].get(b.modulo)
    if not m: return None
    return m.get(b.seccion + '||' + ni(b.headers[col]))

# ───────────────────────── contexto global (cruces) ─────────────────────────
BASES_CRUCE = {  # bases contra las que la SDS cruza: SCL, UT, NNA
    'SCL': (re.compile(r'SESIONES COLECTIVAS'), {'PERSONAS'}),
    'UT':  (re.compile(r'UT TRABAJADORES'), {'IDENTIFICACION DE INDIVIDUOS'}),
    'NNA': (re.compile(r'NINOS NINAS Y ADOLESCENTES'), None),
}
BASES_INFO = {'Conexión nocturna': re.compile(r'CONEXION NOCTURNA'),
              'Trabajadores formales': re.compile(r'SALUD PARA TRABAJADORES'),
              'Cuidado menstrual': re.compile(r'CUIDADO MENSTRUAL')}
ES_TAMIZAJE = re.compile(r'^TAMIZAJE')
COL_DOC = re.compile(r'^(NUMERO DE DOCUMENTO|NUMERO DOCUMENTO|N° DOCUMENTO|N° DOCUMENTO:|DOCUMENTO)$')

def contexto_global(bloques):
    docs = {}                 # doc -> set(bases)
    scl_por_ficha, ut_termina = {}, {}
    for b in bloques:
        M, S = norm(b.modulo), norm(b.seccion)
        if ES_TAMIZAJE.match(M): continue
        base = None
        for nom, (rm, secs) in BASES_CRUCE.items():
            if rm.search(M) and (secs is None or S in secs): base = nom
        if base is None:
            for nom, rm in BASES_INFO.items():
                if rm.search(M): base = nom
        idf = b.N.index('ID_FIC') if 'ID_FIC' in b.N else -1
        if re.search(r'UT TRABAJADORES', M) and S == 'PLAN DE TRABAJO' and 'UTI TERMINA EL PROCESO DESARROLLADO' in b.N:
            t = b.N.index('UTI TERMINA EL PROCESO DESARROLLADO')
            for r in b.rows: ut_termina[r[idf]] = norm(r[t])
        if base is None: continue
        for i, h in enumerate(b.N):
            if not COL_DOC.match(h): continue
            for r in b.rows:
                d = r[i].strip()
                if not d: continue
                docs.setdefault(d, set()).add(base)
                if base == 'SCL':
                    scl_por_ficha.setdefault(r[idf], set()).add(d)
    return {'docs': docs, 'scl': scl_por_ficha, 'ut_termina': ut_termina}

# ───────────────────────── contexto por bloque ─────────────────────────
class Ctx: pass

def _find(N, names):
    for n in names:
        if norm(n) in N: return N.index(norm(n))
    return -1

def contexto_bloque(b, G, hoy, tolerante, excluir_fechas):
    N, c = b.N, Ctx()
    f = lambda *n: _find(N, n)
    c.fi, c.idfic, c.ficha, c.usuario = f('Fecha_intervencion'), f('Id_fic'), f('Ficha_fic'), f('Usuario')
    c.nac = f('FECHA DE NACIMIENTO')
    c.edad = next((i for i, h in enumerate(N) if h == 'EDAD' and any(re.fullmatch(r'\d+', r[i]) for r in b.rows)), -1)
    c.curso = f('CURSO DE VIDA'); c.tdoc = f('TIPO DE DOCUMENTO', 'TIPO DOCUMENTO')
    c.ndoc = f('NUMERO DE DOCUMENTO', 'NUMERO DOCUMENTO', 'N° DOCUMENTO', 'N° DOCUMENTO:', 'DOCUMENTO')
    c.nacio, c.sexo, c.genero, c.ident = f('NACIONALIDAD'), f('SEXO'), f('GENERO'), f('IDENTIDAD DE GENERO')
    c.can, c.porque, c.modal = f('CANALIZACION'), f('PORQUE NO SE CANALIZO'), f('MODALIDAD DE CANALIZACION')
    c.nom = f('NOMBRES', '1ER. NOMBRE', 'NOMBRES Y APELLIDOS')
    c.nombres = [i for i, h in enumerate(N) if re.fullmatch(r'(NOMBRES|APELLIDOS|1ER\. NOMBRE|2DO\. NOMBRE|1ER\. APELLIDO|2DO\. APELLIDO|NOMBRES Y APELLIDOS)', h)]
    c.tels = [i for i, h in enumerate(N) if h.startswith('TELEFONO')]
    excl = {norm(x) for x in excluir_fechas}
    c.fechas = [i for i, h in enumerate(N) if i != c.fi and h not in excl and not h.startswith('SUB-SECCION')
                and any(re.fullmatch(r'\d{4}-\d{2}-\d{2}', r[i]) for r in b.rows)]
    c.hoy, c.G, c.tolerante = hoy, G, tolerante
    def edad_calc(r):
        n, fi = to_date(r[c.nac]) if c.nac >= 0 else None, to_date(r[c.fi]) if c.fi >= 0 else None
        if n and fi: return age_at(n, fi)
        if c.edad >= 0 and re.fullmatch(r'\d+', r[c.edad]): return int(r[c.edad])
        return None
    def edades_alt(r):
        if not tolerante: return []
        a = []
        if c.edad >= 0 and re.fullmatch(r'\d+', r[c.edad]): a.append(int(r[c.edad]))
        n, fi = to_date(r[c.nac]) if c.nac >= 0 else None, to_date(r[c.fi]) if c.fi >= 0 else None
        if n and fi: a.append(fi.year - n.year)
        return a
    c.edad_calc, c.edades_alt = edad_calc, edades_alt
    return c

# ───────────────────────── reglas ─────────────────────────
REGLAS = []
def regla(id_, nombre, grupo):
    def deco(fn):
        REGLAS.append({'id': id_, 'nombre': nombre, 'grupo': grupo, 'run': fn}); return fn
    return deco

E_ = lambda col, msg: {'col': col, 'msg': msg}

# ---- Coherencia general ----
@regla('EDAD', 'Edad no coincide con fecha de nacimiento', 'General')
def _(c, r, b):
    if c.nac < 0 or c.edad < 0: return []
    n, f, e = to_date(r[c.nac]), to_date(r[c.fi]), r[c.edad]
    if not n or not f or not re.fullmatch(r'\d+', e): return []
    calc = age_at(n, f)
    if calc == int(e) or (c.tolerante and int(e) == f.year - n.year): return []
    return [E_(c.edad, f'Edad registrada {e}, calculada {calc} a la fecha de intervención')]

@regla('NAC', 'Fecha de nacimiento inválida', 'General')
def _(c, r, b):
    if c.nac < 0 or not r[c.nac]: return []
    n, f = to_date(r[c.nac]), to_date(r[c.fi])
    if not n: return [E_(c.nac, 'Formato de fecha inválido')]
    if f and n > f: return [E_(c.nac, 'Nacimiento posterior a la fecha de intervención')]
    if f and age_at(n, f) > 105: return [E_(c.nac, 'Edad mayor a 105 años')]
    return []

@regla('CURSO', 'Curso de vida no corresponde a la edad', 'General')
def _(c, r, b):
    if c.curso < 0 or not r[c.curso]: return []
    e = c.edad_calc(r)
    if e is None: return []
    esp, v = curso_esperado(e), norm(r[c.curso])
    if v != esp and not any(curso_esperado(a) == v for a in c.edades_alt(r)):
        return [E_(c.curso, f'Edad {e}: debería ser "{esp.lower()}"')]
    return []

@regla('DOC_EDAD', 'Tipo de documento no corresponde a la edad', 'General')
def _(c, r, b):
    if c.tdoc < 0: return []
    e, t = c.edad_calc(r), code(r[c.tdoc])
    if e is None or not t: return []
    alt = c.edades_alt(r)
    if t == '1' and e < 18 and not any(a >= 18 for a in alt): return [E_(c.tdoc, f'CC con {e} años (menor de edad)')]
    if t == '3' and (e < 7 or e > 17) and not any(7 <= a <= 17 for a in alt): return [E_(c.tdoc, f'TI con {e} años (TI es de 7 a 17)')]
    if t == '2' and e >= 7 and not any(a < 7 for a in alt): return [E_(c.tdoc, f'RC con {e} años (RC es hasta 6)')]
    if t == '7' and e < 18: return [E_(c.tdoc, f'"Adulto sin ID" con {e} años')]
    if t == '8' and e >= 18: return [E_(c.tdoc, f'"Menor sin ID" con {e} años')]
    return []

@regla('DOC_NACIONALIDAD', 'Tipo de documento vs nacionalidad', 'General')
def _(c, r, b):
    if c.tdoc < 0 or c.nacio < 0: return []
    t, n = code(r[c.tdoc]), norm(r[c.nacio])
    if not t or not n: return []
    nombre = r[c.tdoc].split('-', 1)[-1].strip()
    if t in ('1', '2', '3') and n != 'COL': return [E_(c.nacio, f'Documento colombiano ({nombre}) con nacionalidad {n}')]
    if t in ('4', '10', '11', '12', '13', '14') and n == 'COL': return [E_(c.nacio, f'Documento de extranjero ({nombre}) con nacionalidad COL')]
    return []

@regla('DOC_NUM', 'Número de documento con formato inválido', 'General')
def _(c, r, b):
    if c.ndoc < 0 or not r[c.ndoc]: return []
    v, t = r[c.ndoc], code(r[c.tdoc]) if c.tdoc >= 0 else None
    if t in ('7', '8'): return []
    if t in ('1', '2', '3', '4', '11', '13', '14'):
        if not v.isdigit(): return [E_(c.ndoc, 'Contiene letras, espacios o símbolos')]
        if t == '1' and not (4 <= len(v) <= 10): return [E_(c.ndoc, f'CC con {len(v)} dígitos')]
        if t in ('2', '3') and not (10 <= len(v) <= 11): return [E_(c.ndoc, f"{'TI' if t=='3' else 'RC'} con {len(v)} dígitos")]
    if re.fullmatch(r'(\d)\1+', v): return [E_(c.ndoc, 'Número repetido/ficticio')]
    return []

@regla('DOC_VACIO', 'Persona sin tipo o número de documento', 'General')
def _(c, r, b):
    if c.tdoc < 0 or c.ndoc < 0: return []
    if not ((c.nom >= 0 and r[c.nom]) or r[c.ndoc] or r[c.tdoc]): return []
    out = []
    if not r[c.tdoc]: out.append(E_(c.tdoc, 'Tipo de documento vacío'))
    if not r[c.ndoc] and code(r[c.tdoc]) not in ('7', '8'): out.append(E_(c.ndoc, 'Número de documento vacío'))
    return out

@regla('SEXO_GENERO', 'Sexo / género / identidad incoherentes', 'General')
def _(c, r, b):
    out = []
    if c.sexo < 0: return out
    s = code(r[c.sexo])
    if c.genero >= 0:
        g = code(r[c.genero])
        if (s, g) in (('1', '2'), ('2', '1')):
            out.append(E_(c.genero, f'Sexo "{r[c.sexo]}" con género "{r[c.genero]}" (si es persona trans debe marcarse Transgénero)'))
        e = c.edad_calc(r)
        if g == '4' and e is not None and e >= 18: out.append(E_(c.genero, f'Género "No aplica" en persona de {e} años'))
        if c.ident >= 0:
            i = norm(r[c.ident])
            if (g == '1' and i == 'FEMENINO') or (g == '2' and i == 'MASCULINO'):
                out.append(E_(c.ident, f'Género "{r[c.genero]}" con identidad "{r[c.ident]}"'))
            if g == '3' and i in ('FEMENINO', 'MASCULINO'):
                out.append(E_(c.ident, f'Género Transgénero con identidad "{r[c.ident]}"'))
    return out

@regla('CANALIZACION', 'Canalización incompleta o contradictoria', 'General')
def _(c, r, b):
    if c.can < 0: return []
    v, out = norm(r[c.can]), []
    if not v: return [E_(c.can, 'Canalización vacía')]
    if v == 'SI':
        if c.modal >= 0 and not r[c.modal]: out.append(E_(c.modal, 'Canalización "Si" sin modalidad'))
        if c.porque >= 0 and r[c.porque]: out.append(E_(c.porque, 'Canalización "Si" pero tiene motivo de no canalización'))
    if v == 'NO':
        if c.porque >= 0 and not r[c.porque]: out.append(E_(c.porque, 'Canalización "No" sin motivo'))
        if c.modal >= 0 and r[c.modal]: out.append(E_(c.modal, 'Canalización "No" pero tiene modalidad'))
    return out

@regla('NOMBRES', 'Nombres/apellidos con caracteres inválidos', 'General')
def _(c, r, b):
    out = []
    for i in c.nombres:
        v = r[i]
        if not v: continue
        if re.search(r'[0-9@#$%&*_=+!?¿¡()\[\]{}<>/\\|"]', v): out.append(E_(i, 'Contiene números o símbolos'))
        elif re.fullmatch(r'[A-Za-zÑñ]', v.strip()): out.append(E_(i, 'Solo una letra'))
    return out

@regla('TELEFONO', 'Teléfono con formato inválido', 'General')
def _(c, r, b):
    out = []
    for i in c.tels:
        v = re.sub(r'\s', '', r[i])
        if not v: continue
        if not v.isdigit(): out.append(E_(i, 'Contiene caracteres no numéricos'))
        elif len(v) == 10 and not (v.startswith('3') or v.startswith('60')): out.append(E_(i, 'Celular debe iniciar por 3 o fijo por 60'))
        elif len(v) not in (7, 10): out.append(E_(i, f'Tiene {len(v)} dígitos'))
        elif re.fullmatch(r'(\d)\1+', v): out.append(E_(i, 'Número ficticio'))
    return out

@regla('FECHAS', 'Fechas antes de la intervención o posteriores a hoy', 'General')
def _(c, r, b):
    out, hoy = [], c.hoy.isoformat()
    fi = r[c.fi][:10] if c.fi >= 0 else ''
    if fi and fi > hoy: out.append(E_(c.fi, f'Fecha de intervención {fi} es posterior a hoy'))
    for i in c.fechas:
        v = r[i].strip()
        if not v: continue
        if not re.match(r'^\d{4}-\d{2}-\d{2}', v):
            if re.search(r'\d', v): out.append(E_(i, 'Formato de fecha inválido'))
            continue
        d = v[:10]
        if d > hoy: out.append(E_(i, f'Fecha {d} es posterior a hoy'))
        elif fi and d < fi: out.append(E_(i, f'Fecha {d} es anterior a la fecha de intervención ({fi})'))
    return out

# ---- Reglas que reporta la Secretaría (SDS) ----
@regla('SDS_CRUCE', 'Documento del tamizaje no cruza con SCL / UT / NNA', 'SDS')
def _(c, r, b):
    M, S, G = norm(b.modulo), norm(b.seccion), c.G
    if ES_TAMIZAJE.match(M):
        if c.ndoc < 0: return []
        d = r[c.ndoc].strip()
        if not d or (c.tdoc >= 0 and code(r[c.tdoc]) in ('7', '8')): return []
        bases = G['docs'].get(d, set())
        if not bases & {'SCL', 'UT', 'NNA'}:
            extra = f" (sí aparece en: {', '.join(sorted(bases))})" if bases else ''
            return [E_(c.ndoc, 'No cruza con SCL, UT ni NNA en ninguno de los archivos cargados' + extra)]
    if 'SESIONES COLECTIVAS' in M and S == 'TAMIZAJES':
        i = _find(b.N, ['NUMERO DE DOCUMENTO'])
        d = r[i].strip() if i >= 0 else ''
        if d and d not in G['scl'].get(r[c.idfic], set()):
            return [E_(i, 'No cruza con la cédula registrada en la pestaña PERSONAS de la misma ficha')]
    return []

@regla('SDS_FINDRISC_MENOR', 'FINDRISC aplicado a menor de edad', 'SDS')
def _(c, r, b):
    if 'FINDRISC' not in norm(b.modulo) or c.tdoc < 0: return []
    return [E_(c.tdoc, 'FINDRISC no se puede aplicar a menores de edad')] if code(r[c.tdoc]) in ('2', '3', '8') else []

@regla('SDS_ERC_SUBSECCION', 'ERC ASMA EPOC: datos en subsección que no corresponde a la edad', 'SDS')
def _(c, r, b):
    if 'ASMA EPOC' not in norm(b.modulo): return []
    e = c.edad_calc(r)
    if e is None: return []
    subs = [i for i, h in enumerate(b.N) if h.startswith('SUB-SECCION')]
    out = []
    for k, ini in enumerate(subs):
        h = b.N[ini]
        rango = (0, 17) if '0 A 17' in h else (18, 39) if '18 A 39' in h else (40, 200) if 'MAYOR 4' in h else None
        if not rango or rango[0] <= e <= rango[1]: continue
        fin = subs[k + 1] if k + 1 < len(subs) else len(b.N)
        for i in range(ini + 1, fin):
            if r[i].strip():
                sub = re.sub(r'Sub-Sección =>\s*', '', b.headers[ini])
                out.append(E_(i, f'Persona de {e} años con datos en "{sub}"')); break
    return out

@regla('SDS_PORCENTAJE', 'Porcentaje sin signo %', 'SDS')
def _(c, r, b):
    return [E_(i, 'Falta el signo %') for i, h in enumerate(b.N)
            if re.search(r'PORCENTAJE|^% ', h) and re.fullmatch(r'\d+([.,]\d+)?', r[i].strip())]

@regla('SDS_UT_OBLIGATORIOS', 'UT individuos: variables obligatorias vacías', 'SDS')
def _(c, r, b):
    if 'UT TRABAJADORES' not in norm(b.modulo) or norm(b.seccion) != 'IDENTIFICACION DE INDIVIDUOS': return []
    out = [E_(i, 'Variable vacía (si no aplica debe marcarse "No aplica"/"Ninguno")') for i, h in enumerate(b.N)
           if re.match(r'(ETAPA DE GESTACION|TAMIZAJE APLICADO|¿QUE HACE CON LA ROPA)', h) and not r[i].strip()]
    if 'DECALOGO CUMPLIMIENTO' in b.N:
        dc = b.N.index('DECALOGO CUMPLIMIENTO')
        if not r[dc].strip() and c.G['ut_termina'].get(r[c.idfic]) == 'SI':
            out.append(E_(dc, 'La UT terminó el proceso: debe diligenciar Decálogo cumplimiento'))
    return out

@regla('SDS_GESTACION', 'Etapa de gestación incoherente con el sexo', 'SDS')
def _(c, r, b):
    if 'ETAPA DE GESTACION' not in b.N or 'UT TRABAJADORES' in norm(b.modulo): return []
    i = b.N.index('ETAPA DE GESTACION'); v = r[i]
    if v and c.sexo >= 0 and code(r[c.sexo]) == '1' and 'NO APLICA' not in norm(v):
        return [E_(i, f'Hombre con etapa de gestación "{v}"')]
    return []

@regla('SDS_DISCAPACIDAD', 'Población discapacidad vs categoría de discapacidad', 'SDS')
def _(c, r, b):
    p = _find(b.N, ['POBLACION DIFERENCIAL Y DE INCLUSION'])
    k = next((i for i, h in enumerate(b.N) if re.fullmatch(r'CATEGORIA(S)? (DE LA )?DISCAPACIDAD', h)), -1)
    if p < 0 or k < 0: return []
    es, cat = 'DISCAPACIDAD' in norm(r[p]), norm(r[k])
    na = not cat or cat == 'NO APLICA'
    if es and na: return [E_(k, 'Población "Discapacidad" pero categoría de discapacidad "No aplica"')]
    if not es and not na: return [E_(p, f'Tiene categoría "{r[k]}" pero la población no es Discapacidad')]
    return []

@regla('SDS_ESTUDIA', 'NNA: estudia vs institución educativa', 'SDS')
def _(c, r, b):
    e, i = _find(b.N, ['¿ACTUALMENTE ESTUDIA?']), _find(b.N, ['INSTITUCION O JARDIN DONDE ACTUALMENTE ESTUDIA'])
    if e < 0 or i < 0: return []
    v = norm(r[e])
    if v == 'NO' and r[i].strip(): return [E_(i, 'No está estudiando pero tiene institución registrada')]
    if v == 'SI' and not r[i].strip(): return [E_(i, 'Estudia pero no tiene institución registrada')]
    return []

@regla('SDS_SEGUIMIENTOS', 'Fechas de seguimiento fuera de orden', 'SDS')
def _(c, r, b):
    out, seq = [], ['PRIMER SEGUIMIENTO', 'SEGUNDO SEGUIMIENTO', 'TERCER SEGUIMIENTO', 'MONITOREO SEGUIMIENTO']
    for i, h in enumerate(b.N):
        if h != 'PRIMER SEGUIMIENTO': continue
        prev, pn, k = None, '', 0
        for j in range(i, len(b.N)):
            if k >= 4: break
            if b.N[j] != seq[k]: continue
            v = r[j][:10]
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}', v):
                if prev and v < prev: out.append(E_(j, f'{b.headers[j]} ({v}) es anterior a {pn} ({prev})'))
                prev, pn = v, b.headers[j].lower()
            k += 1
    return out

def _num(v):
    try: return float(str(v).replace(',', '.'))
    except ValueError: return None

@regla('SDS_ANTROPOMETRIA', 'Peso, talla o IMC fuera de rango', 'SDS')
def _(c, r, b):
    out = []
    P = next((i for i, h in enumerate(b.N) if h in ('PESO', 'PESO (KG)', 'NUTRICIONAL - PESO')), -1)
    T = next((i for i, h in enumerate(b.N) if h in ('TALLA', 'TALLA_CM', 'TALLA (CM)', 'NUTRICIONAL - TALLA')), -1)
    I = next((i for i, h in enumerate(b.N) if h.startswith('IMC')), -1)
    p = _num(r[P]) if P >= 0 and r[P] else None
    t = _num(r[T]) if T >= 0 and r[T] else None
    if p is not None and not (2 <= p <= 250):
        out.append(E_(P, f'Peso {r[P]}: parece sin punto decimal o en gramos (debe ir en kg)' if p > 1000 else f'Peso {r[P]} kg fuera de rango'))
    if t is not None and not (40 <= t <= 220):
        out.append(E_(T, f'Talla {r[T]}: parece registrada en metros, debe ir en cm' if t < 3 else f'Talla {r[T]} cm fuera de rango'))
    if I >= 0 and p and t and t >= 40:
        imc = _num(r[I]) if r[I] else None
        calc = p / (t / 100) ** 2
        if imc is not None and abs(imc - calc) > 0.6: out.append(E_(I, f'IMC {r[I]} no corresponde a peso/talla (debería ser {calc:.1f})'))
    return out

@regla('SDS_EDAD_FORMAL', 'Trabajador formal con edad atípica (menor de 18 o mayor de 70)', 'SDS')
def _(c, r, b):
    if 'SALUD PARA TRABAJADORES' not in norm(b.modulo): return []
    e = c.edad_calc(r)
    if e is None: return []
    col = c.edad if c.edad >= 0 else c.nac
    if e < 18: return [E_(col, f'Trabajador formal de {e} años (menor de edad)')]
    if e > 70: return [E_(col, f'Revisar edad: {e} años en empresa formal')]
    return []

@regla('SDS_MENSTRUAL', 'Cuidado menstrual: respuestas que dependen de "¿Actualmente menstrúas?"', 'SDS')
def _(c, r, b):
    if 'CUIDADO MENSTRUAL' not in norm(b.modulo): return []
    a = next((i for i, h in enumerate(b.N) if 'ACTUALMENTE MENSTRUAS' in h), -1)
    if a < 0 or norm(r[a]) != 'NO': return []
    for i in range(a + 1, len(b.N)):
        if b.N[i].startswith('SUB-SECCION => 6'): break
        if b.N[i].startswith('SUB-SECCION'): continue
        if r[i].strip(): return [E_(i, 'Respondió "No menstrúa" pero tiene respuestas dependientes diligenciadas')]
    return []

@regla('INSTR_OBLIG', 'Variable obligatoria según instructivo sin dato', 'Instructivo')
def _(c, r, b):
    L = _INS['oblig'].get(ni(b.seccion))
    if not L: return []
    out, vistos = [], set()
    for i, h in enumerate(b.headers):
        k = ni(h)
        if k not in L or k in vistos: continue
        vistos.add(k)
        if not r[i].strip(): out.append(E_(i, 'Sin dato: el instructivo la define como OBLIGATORIA'))
    return out

REGLAS_INFO = [{'id': R['id'], 'nombre': R['nombre'], 'grupo': R['grupo']} for R in REGLAS] + \
              [{'id': 'DUPLICADO', 'nombre': 'Documento repetido en la misma ficha', 'grupo': 'General'}]

def _duplicados(c, b):
    res, seen = {}, {}
    if c.ndoc < 0: return res
    for k, r in enumerate(b.rows):
        d = r[c.ndoc]
        if not d: continue
        key = (r[c.idfic], d)
        if key in seen: res[k] = [E_(c.ndoc, f'Documento repetido en la misma ficha (fila {seen[key]+1})')]
        else: seen[key] = k
    return res

# ───────────────────────── análisis ─────────────────────────
EXCLUIR_FECHAS = ['FECHA DE NACIMIENTO', 'FECHA ULTIMA CARACTERIZACION']

def analizar(bloques, activos=None, tolerante=True, desde='', hasta='', hoy=None,
             excluir_fechas=EXCLUIR_FECHAS, progress=None):
    hoy = hoy or date.today()
    G = contexto_global(bloques)
    reglas = [R for R in REGLAS if activos is None or R['id'] in activos]
    detalle, por_bloque = [], []
    for n, b in enumerate(bloques):
        if progress: progress(40 + int(45 * n / max(1, len(bloques))), f'Validando {b.seccion[:40]}…')
        c = contexto_bloque(b, G, hoy, tolerante, excluir_fechas)
        dups = _duplicados(c, b) if (activos is None or 'DUPLICADO' in activos) else {}
        filas = []
        for k, r in enumerate(b.rows):
            fi = r[c.fi][:10] if c.fi >= 0 else ''
            if (desde and fi and fi < desde) or (hasta and fi and fi > hasta): continue
            errs = []
            for R in reglas:
                for e in R['run'](c, r, b): errs.append({**e, 'regla': R['nombre'], 'grupo': R['grupo']})
            for e in dups.get(k, []): errs.append({**e, 'regla': 'Documento repetido en la misma ficha', 'grupo': 'General'})
            if not errs: continue
            filas.append((k, errs))
            for e in errs:
                ins = instructivo(b, e['col'])
                detalle.append({
                    'mes': mes_de(fi), 'modulo': b.modulo, 'seccion': b.seccion,
                    'idfic': r[c.idfic] if c.idfic >= 0 else '', 'ficha': r[c.ficha] if c.ficha >= 0 else '',
                    'fecha': fi, 'usuario': r[c.usuario] if c.usuario >= 0 else '',
                    'doc': r[c.ndoc] if c.ndoc >= 0 else '', 'columna': b.headers[e['col']],
                    'valor': r[e['col']], 'error': e['msg'], 'regla': e['regla'], 'grupo': e['grupo'],
                    'instructivo': f"[{ins['o']}] {ins['t']}" if ins else '', 'archivo': b.origen[k]})
        por_bloque.append((b, c, filas))
    sin_cruce = documentos_sin_cruce(bloques, G)
    return {'detalle': detalle, 'bloques': por_bloque, 'sin_cruce': sin_cruce, 'G': G,
            'total_registros': sum(len(b.rows) for b in bloques)}

def documentos_sin_cruce(bloques, G):
    """Documentos de tamizajes (y de Tamizajes de SCL) que no aparecen en SCL, UT ni NNA
    en NINGUNO de los archivos cargados."""
    out = []
    for b in bloques:
        M = norm(b.modulo)
        if not ES_TAMIZAJE.match(M): continue
        f = lambda *n: _find(b.N, n)
        nd = f('NUMERO DE DOCUMENTO', 'NUMERO DOCUMENTO', 'N° DOCUMENTO', 'N° DOCUMENTO:', 'DOCUMENTO')
        td, fi, fic, idf, us = f('TIPO DE DOCUMENTO', 'TIPO DOCUMENTO'), f('Fecha_intervencion'), f('Ficha_fic'), f('Id_fic'), f('Usuario')
        n1, n2, a1, a2 = f('1ER. NOMBRE', 'NOMBRES'), f('2DO. NOMBRE'), f('1ER. APELLIDO', 'APELLIDOS'), f('2DO. APELLIDO')
        if nd < 0: continue
        for k, r in enumerate(b.rows):
            d = r[nd].strip()
            if not d or (td >= 0 and code(r[td]) in ('7', '8')): continue
            bases = G['docs'].get(d, set())
            if bases & {'SCL', 'UT', 'NNA'}: continue
            nombre = ' '.join(r[i] for i in (n1, n2, a1, a2) if i >= 0 and r[i]).strip()
            out.append({'documento': d, 'tipo': r[td] if td >= 0 else '', 'nombre': nombre,
                        'tamizaje': b.modulo, 'ficha': r[fic] if fic >= 0 else '', 'idfic': r[idf] if idf >= 0 else '',
                        'fecha': r[fi][:10] if fi >= 0 else '', 'usuario': r[us] if us >= 0 else '',
                        'otras_bases': ', '.join(sorted(bases)) or '—', 'archivo': b.origen[k]})
    return out
