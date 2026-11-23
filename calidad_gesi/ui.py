# -*- coding: utf-8 -*-
"""calidad_gesi/ui.py — Pantalla 'Calidad del dato GESI' dentro de Odin (CustomTkinter)."""
import os, threading, subprocess, sys
from datetime import datetime, date
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from . import motor, reporte, correo

C = {
    "card": ("#FFFFFF", "#0F1A2E"), "border": ("#D8E5F5", "#162035"), "accent": ("#1B6ECC", "#4A9EE8"),
    "btn": ("#1B6ECC", "#3B8DD4"), "btn_hover": ("#1558A8", "#2A78C0"), "btn2": ("#E8F0FE", "#142236"),
    "btn2_hover": ("#D4E4FC", "#1B3050"), "text1": ("#0A1628", "#EDF2FF"), "text2": ("#3B5070", "#7EA8D4"),
    "success": ("#0F7B4F", "#2ECC8A"), "danger": ("#C0392B", "#E05555"),
}
APP_DIR = Path(__file__).parent.parent.resolve()
SALIDA = APP_DIR / 'output' / 'calidad'
DESCARGAS = APP_DIR / 'output' / 'correo_calidad'

def _abrir(p):
    try:
        if sys.platform.startswith('win'): os.startfile(str(p))
        else: subprocess.Popen(['xdg-open', str(p)])
    except Exception as e: messagebox.showerror('Error', str(e))

class CalidadUI(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.archivos, self.reportes_sds, self.ultimo_excel = [], [], None
        sc = ctk.CTkScrollableFrame(self, fg_color="transparent"); sc.pack(fill="both", expand=True)
        self._card_archivos(sc); self._card_correo(sc); self._card_opciones(sc); self._card_resultado(sc)

    # ── helpers ──
    def _card(self, parent, titulo, sub=''):
        card = ctk.CTkFrame(parent, fg_color=C["card"], border_color=C["border"], border_width=1, corner_radius=8)
        card.pack(fill="x", padx=20, pady=(14, 0))
        ctk.CTkFrame(card, height=2, fg_color=C["accent"], corner_radius=0).pack(fill="x")
        body = ctk.CTkFrame(card, fg_color="transparent"); body.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(body, text=titulo, font=ctk.CTkFont("Segoe UI", 13, "bold"), text_color=C["text1"]).pack(anchor="w")
        if sub: ctk.CTkLabel(body, text=sub, font=ctk.CTkFont("Segoe UI", 10), text_color=C["text2"],
                             justify="left", wraplength=900).pack(anchor="w", pady=(2, 8))
        return body
    def _btn(self, parent, text, cmd, primario=False, **kw):
        return ctk.CTkButton(parent, text=text, command=cmd, height=32,
                             fg_color=C["btn"] if primario else C["btn2"], hover_color=C["btn_hover"] if primario else C["btn2_hover"],
                             text_color="white" if primario else C["text1"], font=ctk.CTkFont("Segoe UI", 11, "bold" if primario else "normal"), **kw)

    # ── 1. archivos ──
    def _card_archivos(self, p):
        b = self._card(p, "1. Exportes GESI a validar (.csv)",
                       "Carga varios archivos a la vez (por ejemplo, bloques de 4 meses). Se unen, se quitan filas repetidas "
                       "y el cruce de documentos se hace contra TODOS los archivos, así un documento de un mes pasado sí cruza.")
        fila = ctk.CTkFrame(b, fg_color="transparent"); fila.pack(fill="x")
        self._btn(fila, "📂  Agregar archivos…", self._agregar).pack(side="left")
        self._btn(fila, "Quitar todos", self._limpiar).pack(side="left", padx=8)
        self.lst = ctk.CTkTextbox(b, height=90, font=ctk.CTkFont("Consolas", 10)); self.lst.pack(fill="x", pady=(8, 0))
        self._pintar_lista()
    def _agregar(self):
        fs = filedialog.askopenfilenames(title="Exportes GESI", filetypes=[("CSV GESI", "*.csv *.txt"), ("Todos", "*.*")])
        for f in fs:
            if f not in self.archivos: self.archivos.append(f)
        self._pintar_lista()
    def _limpiar(self):
        self.archivos, self.reportes_sds = [], []; self._pintar_lista()
    def _pintar_lista(self):
        self.lst.configure(state="normal"); self.lst.delete("1.0", "end")
        if not self.archivos and not self.reportes_sds: self.lst.insert("end", "  (sin archivos)")
        for f in self.archivos: self.lst.insert("end", f"  CSV   {Path(f).name}\n")
        for f in self.reportes_sds: self.lst.insert("end", f"  SDS   {Path(f).name}   ← reporte de calidad para comparar\n")
        self.lst.configure(state="disabled")

    # ── 2. correo ──
    def _card_correo(self, p):
        b = self._card(p, "2. Traer lo último del correo (Gmail)",
                       "Busca el correo más reciente con adjuntos del remitente/asunto indicados (incluye correos reenviados), "
                       "descarga los adjuntos y los agrega: los CSV de GESI se validan y los Excel de calidad de la SDS se comparan.")
        cfg = correo.cargar_config()
        fila = ctk.CTkFrame(b, fg_color="transparent"); fila.pack(fill="x")
        ctk.CTkLabel(fila, text="Remitente:", text_color=C["text2"]).pack(side="left")
        self.e_rem = ctk.CTkEntry(fila, width=230); self.e_rem.pack(side="left", padx=(4, 12))
        self.e_rem.insert(0, cfg.get('remitente', 'gesitecnico1@gmail.com'))
        ctk.CTkLabel(fila, text="Asunto contiene:", text_color=C["text2"]).pack(side="left")
        self.e_asu = ctk.CTkEntry(fila, width=140); self.e_asu.pack(side="left", padx=(4, 12))
        self.e_asu.insert(0, cfg.get('asunto', 'calidad'))
        self._btn(fila, "✉  Traer último correo", self._traer_correo, primario=True).pack(side="left")
        self._btn(fila, "⚙  Configurar cuenta", self._config_correo).pack(side="left", padx=8)
        self.lbl_correo = ctk.CTkLabel(b, text=f"Cuenta: {cfg.get('u') or 'sin configurar'}", text_color=C["text2"],
                                       font=ctk.CTkFont("Segoe UI", 10), justify="left", wraplength=900)
        self.lbl_correo.pack(anchor="w", pady=(6, 0))
    def _config_correo(self):
        w = ctk.CTkToplevel(self); w.title("Cuenta de Gmail"); w.geometry("460x300"); w.grab_set()
        cfg = correo.cargar_config()
        ctk.CTkLabel(w, text="Correo Gmail").pack(anchor="w", padx=16, pady=(14, 0))
        eu = ctk.CTkEntry(w, width=420); eu.pack(padx=16); eu.insert(0, cfg.get('u', ''))
        ctk.CTkLabel(w, text="Contraseña de aplicación (16 letras, no tu contraseña normal)").pack(anchor="w", padx=16, pady=(10, 0))
        ep = ctk.CTkEntry(w, width=420, show="•"); ep.pack(padx=16)
        ctk.CTkLabel(w, text="Google → Seguridad → Verificación en 2 pasos → Contraseñas de aplicaciones.\n"
                             "Se guarda cifrada en este equipo (Windows DPAPI).", font=ctk.CTkFont(size=10),
                     text_color=C["text2"], justify="left").pack(anchor="w", padx=16, pady=8)
        def ok():
            if not eu.get().strip() or not (ep.get().strip() or cfg.get('p')):
                messagebox.showwarning("Faltan datos", "Escribe el correo y la contraseña de aplicación."); return
            correo.guardar_config(eu.get().strip(), ep.get().strip() or cfg.get('p'), self.e_rem.get().strip(), self.e_asu.get().strip())
            self.lbl_correo.configure(text=f"Cuenta: {eu.get().strip()}"); w.destroy()
        self._btn(w, "Guardar", ok, primario=True).pack(pady=6)
    def _traer_correo(self):
        cfg = correo.cargar_config()
        if not cfg.get('u'): self._config_correo(); return
        correo.guardar_config(cfg['u'], cfg['p'], self.e_rem.get().strip(), self.e_asu.get().strip())
        self._estado("Conectando a Gmail…", 0.05)
        def work():
            try:
                r = correo.traer_ultimo_correo(DESCARGAS, self.e_rem.get().strip(), self.e_asu.get().strip(),
                                               progress=lambda p, m: self.after(0, lambda: self._estado(m, p / 100)))
                csv = [str(f) for f in r['archivos'] if correo.es_exporte_gesi(f)]
                sds = [str(f) for f in r['archivos'] if f.suffix.lower() in ('.xlsx', '.xls') and reporte.es_reporte_sds(f)]
                def fin():
                    for f in csv:
                        if f not in self.archivos: self.archivos.append(f)
                    for f in sds:
                        if f not in self.reportes_sds: self.reportes_sds.append(f)
                    self._pintar_lista()
                    fecha = r['fecha'].strftime('%Y-%m-%d %H:%M') if r['fecha'] else ''
                    self.lbl_correo.configure(text=f"Último correo: «{r['asunto']}» de {r['de']} ({fecha}) — "
                                                   f"{len(r['archivos'])} adjuntos: {len(csv)} exporte(s) GESI, {len(sds)} reporte(s) SDS.\n"
                                                   f"Guardados en {r['carpeta']}")
                    self._estado("Correo descargado. Agrega los CSV si faltan y pulsa Validar.", 1)
                self.after(0, fin)
            except Exception as e:
                self.after(0, lambda e=e: (self._estado("Error con el correo", 0), messagebox.showerror("Correo", str(e))))
        threading.Thread(target=work, daemon=True).start()

    # ── 3. opciones ──
    def _card_opciones(self, p):
        b = self._card(p, "3. Opciones")
        self.tol = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(b, text="Tolerar edad calculada solo por año (como la calcula GESI)", variable=self.tol).pack(anchor="w")
        fila = ctk.CTkFrame(b, fg_color="transparent"); fila.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(fila, text="Fecha intervención desde (AAAA-MM-DD):", text_color=C["text2"]).pack(side="left")
        self.e_desde = ctk.CTkEntry(fila, width=110); self.e_desde.pack(side="left", padx=(4, 12))
        ctk.CTkLabel(fila, text="hasta:", text_color=C["text2"]).pack(side="left")
        self.e_hasta = ctk.CTkEntry(fila, width=110); self.e_hasta.pack(side="left", padx=4)
        ctk.CTkLabel(b, text="Grupos de reglas a aplicar:", text_color=C["text2"]).pack(anchor="w", pady=(10, 0))
        self.grupos = {}
        fg = ctk.CTkFrame(b, fg_color="transparent"); fg.pack(fill="x")
        for g, t in (("SDS", "Reglas que reporta la Secretaría"), ("Instructivo", "Instructivos caja de herramientas"), ("General", "Coherencia general")):
            v = tk.BooleanVar(value=True); self.grupos[g] = v
            ctk.CTkCheckBox(fg, text=t, variable=v).pack(side="left", padx=(0, 16))
        fila2 = ctk.CTkFrame(b, fg_color="transparent"); fila2.pack(fill="x", pady=(12, 0))
        self.btn_validar = self._btn(fila2, "▶  Validar y generar Excel", self._validar, primario=True, width=220)
        self.btn_validar.pack(side="left")
        self.bar = ctk.CTkProgressBar(fila2, width=260, progress_color=C["accent"]); self.bar.set(0); self.bar.pack(side="left", padx=12)
        self.lbl_estado = ctk.CTkLabel(fila2, text="", text_color=C["text2"], font=ctk.CTkFont("Consolas", 10)); self.lbl_estado.pack(side="left")
    def _estado(self, msg, frac=None):
        self.lbl_estado.configure(text=msg[:90])
        if frac is not None: self.bar.set(max(0, min(1, frac)))

    # ── 4. resultado ──
    def _card_resultado(self, p):
        b = self._card(p, "4. Resultado")
        self.txt_res = ctk.CTkTextbox(b, height=230, font=ctk.CTkFont("Consolas", 11)); self.txt_res.pack(fill="x")
        fila = ctk.CTkFrame(b, fg_color="transparent"); fila.pack(fill="x", pady=(8, 0))
        self._btn(fila, "📊  Abrir Excel", lambda: self.ultimo_excel and _abrir(self.ultimo_excel)).pack(side="left")
        self._btn(fila, "📁  Abrir carpeta", lambda: (SALIDA.mkdir(parents=True, exist_ok=True), _abrir(SALIDA))).pack(side="left", padx=8)

    def _validar(self):
        if not self.archivos:
            messagebox.showwarning("Sin archivos", "Agrega al menos un exporte GESI (.csv) o tráelo del correo."); return
        activos = [R['id'] for R in motor.REGLAS_INFO if self.grupos.get(R['grupo'], tk.BooleanVar(value=True)).get()]
        desde, hasta = self.e_desde.get().strip(), self.e_hasta.get().strip()
        self.btn_validar.configure(state="disabled")
        prog = lambda p, m: self.after(0, lambda: self._estado(m, p / 100))
        def work():
            try:
                bl = motor.cargar_archivos(self.archivos, progress=prog)
                res = motor.analizar(bl, activos=activos, tolerante=self.tol.get(), desde=desde, hasta=hasta, progress=prog)
                comp = None
                if self.reportes_sds:
                    h = []
                    for f in self.reportes_sds: h += reporte.leer_reporte_sds(f)
                    comp = reporte.comparar_sds(h, res, bl)
                salida = SALIDA / f"calidad_GESI_{datetime.now():%Y-%m-%d_%H%M}.xlsx"
                prog(88, "Generando Excel…")
                reporte.generar_excel(res, self.archivos, salida, comp, progress=prog)
                self.after(0, lambda: self._mostrar(res, comp, salida))
            except Exception as e:
                self.after(0, lambda e=e: messagebox.showerror("Error al validar", str(e)))
            finally:
                self.after(0, lambda: self.btn_validar.configure(state="normal"))
        threading.Thread(target=work, daemon=True).start()

    def _mostrar(self, res, comp, salida):
        from collections import Counter
        D = res['detalle']; self.ultimo_excel = salida
        t = [f"Registros revisados: {res['total_registros']:,}   Errores: {len(D)}   Fichas a corregir: {len({d['idfic'] for d in D})}",
             f"Documentos de tamizajes que no cruzan con SCL/UT/NNA: {len(res['sin_cruce'])}  (hoja 'Documentos sin cruce')", "",
             "Por regla:"]
        t += [f"  {n:5d}  {k}" for k, n in Counter(d['regla'] for d in D).most_common()]
        t += ["", "Por digitador:"] + [f"  {n:5d}  {k}" for k, n in Counter(d['usuario'] for d in D).most_common(10)]
        if comp:
            t += ["", "Reporte SDS vs Odin:"] + [f"  {n:5d}  {k}" for k, n in Counter(c['odin'] for c in comp).most_common()]
        t += ["", f"Excel: {salida}"]
        self.txt_res.delete("1.0", "end"); self.txt_res.insert("end", "\n".join(t))
        self._estado("Listo ✔", 1)
