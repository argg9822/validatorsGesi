# -*- coding: utf-8 -*-
"""calidad_gesi/reporte.py — Genera el Excel de calidad (errores en rojo) y compara con el reporte SDS."""
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
from .motor import norm

ROJO = PatternFill('solid', fgColor='FFFF0000')
AMAR = PatternFill('solid', fgColor='FFFFF2CC')
VERDE = PatternFill('solid', fgColor='FFE2EFDA')
HEAD = PatternFill('solid', fgColor='FF1F3864')
F_BLANCA = Font(bold=True, color='FFFFFFFF')
F_ROJA = Font(bold=True, color='FFC00000')

def _encabezado(ws, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(1, c); cell.fill = HEAD; cell.font = F_BLANCA
        cell.alignment = Alignment(wrap_text=True, vertical='center')
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = f"A1:{get_column_letter(ncols)}1"

def _nombre_hoja(nombre, usados):
    base = re.sub(r'[\\/\?\*\[\]:]', ' ', nombre or 'Sección')
    base = re.sub(r'\s+', ' ', base).strip()[:28] or 'Sección'
    k, i = base, 2
    while k.upper() in usados: k = f"{base[:26]} {i}"; i += 1
    usados.add(k.upper()); return k

# ───────────────────── reporte SDS (correo) ─────────────────────
def leer_reporte_sds(path):
    """Lee el Excel 'calidad laboral - NORTE …' de la Secretaría. Devuelve lista de hallazgos."""
    out = []
    try: wb = load_workbook(path, read_only=True, data_only=True)
    except Exception: return out
    for ws in wb.worksheets:
        hdr, idx = None, {}
        for row in ws.iter_rows(values_only=True):
            vals = [str(v).strip() if v is not None else '' for v in row]
            if hdr is None:
                N = [norm(v) for v in vals]
                if 'FICHA' in N and any('HALLAZGO' in x for x in N):
                    hdr = N
                    for i, h in enumerate(N):
                        for k, pat in (('anio', 'ANO'), ('mes', 'MES'), ('formulario', 'FORMULARIO'), ('seccion', 'SECCION'),
                                       ('ficha', 'FICHA'), ('variable', 'VARIABLE'), ('doc', 'DOCUMENTO'),
                                       ('hallazgo', 'HALLAZGO'), ('estado', 'ESTADO'), ('motivo', 'MOTIVO'), ('obs', 'OBSERVACION')):
                            if k not in idx and h.startswith(pat): idx[k] = i
                continue
            g = lambda k: vals[idx[k]] if k in idx and idx[k] < len(vals) else ''
            ficha = re.sub(r'\D', '', g('ficha'))
            if not ficha: continue
            out.append({'anio': g('anio'), 'mes': g('mes'), 'formulario': g('formulario'), 'seccion': g('seccion'),
                        'ficha': ficha, 'variable': g('variable'), 'doc': g('doc'), 'hallazgo': g('hallazgo'),
                        'estado': g('estado'), 'motivo': g('motivo'), 'archivo': Path(path).name})
    return out

def es_reporte_sds(path):
    return bool(leer_reporte_sds(path))

def comparar_sds(hallazgos, res, bloques):
    """Para cada hallazgo SDS: ¿la ficha está en los archivos cargados? ¿Odin detecta algo en esa ficha?"""
    fichas_cargadas = set()
    for b in bloques:
        if 'FICHA_FIC' in b.N:
            i = b.N.index('FICHA_FIC'); fichas_cargadas.update(r[i] for r in b.rows)
    por_ficha = {}
    for d in res['detalle']: por_ficha.setdefault(d['ficha'], []).append(d)
    out = []
    for h in hallazgos:
        errs = por_ficha.get(h['ficha'], [])
        var = norm(h['variable'])
        misma = [e for e in errs if var and (var in norm(e['columna']) or norm(e['columna']) in var)]
        if h['ficha'] not in fichas_cargadas: est = 'Ficha no está en los archivos cargados'
        elif misma: est = 'Detectado (misma variable)'
        elif errs: est = 'Odin detecta otros errores en la ficha'
        else: est = 'NO detectado por Odin'
        out.append({**h, 'odin': est, 'odin_errores': ' | '.join(f"{e['columna']}: {e['error']}" for e in (misma or errs)[:4])})
    return out

# ───────────────────── Excel principal ─────────────────────
def generar_excel(res, archivos, salida, comparacion=None, progress=None):
    D = res['detalle']
    wb = Workbook()
    wr = wb.active; wr.title = 'Resumen'
    wr.append(['Revisión de calidad GESI — Odin']); wr['A1'].font = Font(bold=True, size=14)
    wr.append(['Archivo(s)', ', '.join(Path(a).name for a in archivos)])
    wr.append(['Generado', datetime.now().strftime('%Y-%m-%d %H:%M')])
    wr.append(['Registros revisados', res['total_registros']])
    wr.append(['Errores', len(D)])
    wr.append(['Fichas a corregir', len({d['idfic'] for d in D})])
    wr.append(['Documentos de tamizajes sin cruce (SCL/UT/NNA)', len(res['sin_cruce'])]); wr.append([])
    def bloque(t, pares):
        r = wr.max_row + 1; wr.append([t, 'Errores'])
        for c in (1, 2): wr.cell(r, c).fill = HEAD; wr.cell(r, c).font = F_BLANCA
        for k, v in pares: wr.append([k, v])
        wr.append([])
    bloque('Por regla', Counter(d['regla'] for d in D).most_common())
    bloque('Por usuario (digitador)', Counter(d['usuario'] for d in D).most_common())
    bloque('Por sección', Counter(d['seccion'] for d in D).most_common())
    bloque('Por mes de intervención', Counter(d['mes'] for d in D).most_common())
    if comparacion:
        bloque('Hallazgos SDS vs Odin', Counter(c['odin'] for c in comparacion).most_common())
    wr.column_dimensions['A'].width = 60; wr.column_dimensions['B'].width = 40

    # Detalle
    if progress: progress(90, 'Escribiendo detalle…')
    cols = [('Mes', 'mes', 14), ('Módulo', 'modulo', 34), ('Sección', 'seccion', 30), ('Id_fic', 'idfic', 11),
            ('Ficha_fic', 'ficha', 14), ('Fecha_intervencion', 'fecha', 13), ('Usuario', 'usuario', 13),
            ('Documento', 'doc', 14), ('Columna con error', 'columna', 30), ('Valor registrado', 'valor', 26),
            ('Error', 'error', 50), ('Regla', 'regla', 32), ('Origen de la regla', 'grupo', 12),
            ('Qué dice el instructivo', 'instructivo', 70), ('Archivo', 'archivo', 28)]
    wd = wb.create_sheet('Detalle errores')
    wd.append([c[0] for c in cols])
    for d in D:
        wd.append([d[c[1]] for c in cols]); r = wd.max_row
        for k in (5, 10):
            wd.cell(r, k).fill = ROJO; wd.cell(r, k).font = F_BLANCA
        wd.cell(r, 14).alignment = Alignment(wrap_text=True, vertical='top')
    for i, c in enumerate(cols, 1): wd.column_dimensions[get_column_letter(i)].width = c[2]
    _encabezado(wd, len(cols))

    # Documentos sin cruce
    ws = wb.create_sheet('Documentos sin cruce')
    sc = [('Documento', 'documento', 14), ('Tipo documento', 'tipo', 26), ('Nombre', 'nombre', 30), ('Tamizaje', 'tamizaje', 40),
          ('Ficha_fic', 'ficha', 14), ('Id_fic', 'idfic', 11), ('Fecha_intervencion', 'fecha', 13), ('Usuario', 'usuario', 13),
          ('Aparece en otras bases', 'otras_bases', 26), ('Archivo', 'archivo', 28)]
    ws.append([c[0] for c in sc])
    for d in res['sin_cruce']:
        ws.append([d[c[1]] for c in sc]); r = ws.max_row
        ws.cell(r, 1).fill = ROJO; ws.cell(r, 1).font = F_BLANCA
        ws.cell(r, 5).fill = ROJO; ws.cell(r, 5).font = F_BLANCA
    for i, c in enumerate(sc, 1): ws.column_dimensions[get_column_letter(i)].width = c[2]
    _encabezado(ws, len(sc))
    ws.cell(ws.max_row + 2, 1, f"Se buscó cada documento en SCL (Personas), UT (Identificación de individuos) y NNA "
                              f"de TODOS los archivos cargados ({len(archivos)}).").font = Font(italic=True, color='FF667085')

    # Comparación SDS
    if comparacion:
        wc = wb.create_sheet('Comparación SDS')
        cc = [('Mes', 'mes', 12), ('Formulario', 'formulario', 26), ('Sección', 'seccion', 26), ('Ficha', 'ficha', 14),
              ('Variable (SDS)', 'variable', 30), ('Hallazgo (SDS)', 'hallazgo', 36), ('Estado (SDS)', 'estado', 14),
              ('Resultado Odin', 'odin', 32), ('Lo que encuentra Odin en la ficha', 'odin_errores', 70), ('Archivo SDS', 'archivo', 30)]
        wc.append([c[0] for c in cc])
        for d in comparacion:
            wc.append([d[c[1]] for c in cc]); r = wc.max_row
            fill = VERDE if d['odin'].startswith('Detectado') else AMAR if d['odin'].startswith('Odin') else ROJO
            wc.cell(r, 8).fill = fill
            if fill is ROJO: wc.cell(r, 8).font = F_BLANCA
        for i, c in enumerate(cc, 1): wc.column_dimensions[get_column_letter(i)].width = c[2]
        _encabezado(wc, len(cc))

    # Una hoja por sección con la fila original
    usados = {s.title.upper() for s in wb.worksheets}
    for b, c, filas in res['bloques']:
        if not filas: continue
        ws = wb.create_sheet(_nombre_hoja(b.seccion, usados))
        idx = [i for i, h in enumerate(b.headers) if not h.startswith('Sub-Sección')]
        ws.append(['ERRORES ENCONTRADOS', 'MÓDULO', 'ARCHIVO'] + [b.headers[i] for i in idx])
        for k, errs in filas:
            r = b.rows[k]
            ws.append([' | '.join(f"{b.headers[e['col']]}: {e['msg']}" for e in errs), b.modulo, b.origen[k]] + [r[i] for i in idx])
            n = ws.max_row
            ws.cell(n, 1).font = F_ROJA; ws.cell(n, 1).alignment = Alignment(wrap_text=True, vertical='top')
            marcar = {e['col'] for e in errs} | ({c.ficha} if c.ficha >= 0 else set())
            for col in marcar:
                if col in idx:
                    cell = ws.cell(n, idx.index(col) + 4); cell.fill = ROJO; cell.font = F_BLANCA
        ws.column_dimensions['A'].width = 60; ws.column_dimensions['B'].width = 22; ws.column_dimensions['C'].width = 20
        for j in range(4, len(idx) + 4): ws.column_dimensions[get_column_letter(j)].width = 16
        _encabezado(ws, len(idx) + 3); ws.freeze_panes = 'B2'

    Path(salida).parent.mkdir(parents=True, exist_ok=True)
    wb.save(salida)
    return salida
