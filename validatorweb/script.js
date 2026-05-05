// ============================
// STATE
// ============================
let selectedEntorno = null;
let selectedFormatId = null;
let loadedFiles = [];
let allIssues = [];
let allResults = [];
let currentFilter = 'all';
let editingFormatId = null;

// Builtin formats loaded from rules.json at startup
let BUILTIN_FORMATS = [];
let LISTAS = {};

// ============================
// CONSTANTS
// ============================
const ENTORNO_CODES = { laboral: '2', educativo: '3', comunitario: '4', institucional: '6' };
const ENTORNO_NAMES = { laboral: 'Laboral', educativo: 'Educativo', comunitario: 'Comunitario', institucional: 'Institucional' };
const ENTORNO_ICONS = { laboral: '🏭', educativo: '🎓', comunitario: '🏘️', institucional: '🏥' };
const ALL_ENTORNOS = ['laboral', 'educativo', 'comunitario', 'institucional'];

// ============================
// LOAD rules.json
// ============================
async function loadRulesJSON() {
    try {
        const res = await fetch('rules.json');
        if (!res.ok) throw new Error('rules.json no encontrado');
        const data = await res.json();

        LISTAS = data._listas || {};

        BUILTIN_FORMATS = (data.formats || []).map(fmt => {
            const resolved = resolveRuleValues(fmt.rules);
            return { ...fmt, builtin: true, rules: resolved };
        });
    } catch (err) {
        console.error('Error cargando rules.json:', err);
        BUILTIN_FORMATS = [];
    }
}

// Resolve $LIST references inside rule values
function resolveRuleValues(rules) {
    const out = {};
    for (const [campo, rule] of Object.entries(rules)) {
        const r = { ...rule };
        if (typeof r.valores === 'string' && r.valores.startsWith('$')) {
            const key = r.valores.slice(1);
            r.valores = LISTAS[key] || [];
        }
        if (r.dependencia) {
            r.dependencia = { ...r.dependencia };
            // normalize: ensure .valores is always an array (multi-value dependency)
            if (r.dependencia.valor && !r.dependencia.valores) {
                r.dependencia.valores = [r.dependencia.valor];
            }
        }
        out[campo] = r;
    }
    return out;
}

// ============================
// FORMAT REGISTRY
// ============================
function loadUserFormats() {
    try { return JSON.parse(localStorage.getItem('mb_user_formats') || '[]'); } catch { return []; }
}
function saveUserFormats(formats) {
    localStorage.setItem('mb_user_formats', JSON.stringify(formats));
}
// Builtin overrides (edits to builtin formats)
function loadBuiltinOverrides() {
    try { return JSON.parse(localStorage.getItem('mb_builtin_overrides') || '{}'); } catch { return {}; }
}
function saveBuiltinOverrides(overrides) {
    localStorage.setItem('mb_builtin_overrides', JSON.stringify(overrides));
}

function getAllFormats() {
    const overrides = loadBuiltinOverrides();
    const builtins = BUILTIN_FORMATS.map(f => {
        if (overrides[f.id]) return { ...f, ...overrides[f.id], builtin: true, id: f.id };
        return f;
    });
    return [...builtins, ...loadUserFormats()];
}

function getFormatsForEntorno(entorno) {
    return getAllFormats().filter(f => f.entornos.includes(entorno));
}
function getFormatById(id) {
    return getAllFormats().find(f => f.id === id) || null;
}

// ============================
// UI — STEP 1: ENTORNO
// ============================
function selectEntorno(btn) {
    document.querySelectorAll('.entorno-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    selectedEntorno = btn.dataset.entorno;
    selectedFormatId = null;

    document.getElementById('step1').classList.add('done');
    document.getElementById('step2').classList.add('active');
    document.getElementById('panel-formato').classList.remove('section-hidden');
    document.getElementById('panel-files').classList.add('section-hidden');
    document.getElementById('results-section').style.display = 'none';

    renderFormatoGrid();
    document.getElementById('formato-panel-title').textContent =
        `Paso 2 — Seleccione el formato para entorno ${ENTORNO_NAMES[selectedEntorno]}`;
}

function renderFormatoGrid() {
    const grid = document.getElementById('formato-grid');
    const formats = getFormatsForEntorno(selectedEntorno);
    if (formats.length === 0) {
        grid.innerHTML = `<div class="empty-state"><span class="empty-icon">📋</span>No hay formatos para este entorno.<br>Cree uno nuevo con el botón de abajo.</div>`;
        return;
    }
    grid.innerHTML = formats.map(f => `
    <button class="formato-btn ${f.id === selectedFormatId ? 'selected' : ''}" data-fmt="${f.id}" onclick="selectFormato(this)">
      <div class="fmt-code">${f.code}</div>
      <div class="fmt-name">${f.nombre}</div>
      <div class="fmt-desc">${f.desc || ''}</div>
      <div class="fmt-entornos">${f.entornos.map(e => ENTORNO_ICONS[e]).join(' ')}</div>
      ${!f.builtin ? '<div class="fmt-custom-badge">Personalizado</div>' : '<div class="fmt-builtin-badge">Builtin</div>'}
    </button>
  `).join('');
}

function selectFormato(btn) {
    document.querySelectorAll('.formato-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    selectedFormatId = btn.dataset.fmt;

    const fmt = getFormatById(selectedFormatId);
    document.getElementById('step2').classList.add('done');
    document.getElementById('step3').classList.add('active');
    document.getElementById('panel-files').classList.remove('section-hidden');
    document.getElementById('files-panel-title').textContent =
        `Paso 3 — Cargue los archivos del formato ${fmt.nombre}`;
    document.getElementById('selected-badge').textContent =
        `Entorno: ${ENTORNO_NAMES[selectedEntorno]} · Formato: ${fmt.nombre} (${fmt.code})`;
    document.getElementById('btn-validate').disabled = loadedFiles.length === 0;
}

// ============================
// UI — FILE HANDLING
// ============================
function handleFiles(files) {
    for (const f of files) {
        const ext = f.name.split('.').pop().toLowerCase();
        if (!['xlsx', 'csv'].includes(ext)) {
            alert(`El archivo ${f.name} no es válido. Use .xlsx o .csv`);
            continue;
        }
        if (loadedFiles.some(x => x.name === f.name)) continue;
        loadedFiles.push(f);
    }
    renderFileList();
}

function renderFileList() {
    const list = document.getElementById('file-list');
    list.innerHTML = '';
    for (const f of loadedFiles) {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
      <span class="file-icon">📄</span>
      <span class="file-name">${f.name}</span>
      <span class="file-size">${(f.size / 1024).toFixed(1)} KB</span>
      <button class="file-remove" onclick="removeFile('${f.name}')">✕</button>`;
        list.appendChild(item);
    }
    document.getElementById('btn-validate').disabled = loadedFiles.length === 0 || !selectedFormatId;
}

function removeFile(name) {
    loadedFiles = loadedFiles.filter(f => f.name !== name);
    renderFileList();
}

// Drag & drop
document.addEventListener('DOMContentLoaded', () => {
    const dropArea = document.getElementById('drop-area');
    if (dropArea) {
        dropArea.addEventListener('dragover', e => { e.preventDefault(); dropArea.classList.add('drag'); });
        dropArea.addEventListener('dragleave', () => dropArea.classList.remove('drag'));
        dropArea.addEventListener('drop', e => {
            e.preventDefault(); dropArea.classList.remove('drag');
            handleFiles(e.dataTransfer.files);
        });
    }
});

// ============================
// FILE READERS
// ============================
function readExcelFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array' });
                const firstSheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[firstSheetName];
                const jsonData = XLSX.utils.sheet_to_json(worksheet, { range: 1, defval: '' });
                const headers = jsonData.length > 0 ? Object.keys(jsonData[0]) : [];
                resolve({ headers, rows: jsonData });
            } catch (err) { reject(err); }
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
}

function readCSVFile(file) {
    return new Promise((res, rej) => {
        const reader = new FileReader();
        reader.onload = e => {
            const ab = e.target.result;
            const decoder = new TextDecoder('windows-1252');
            const text = decoder.decode(ab);
            const lines = text.split('\n').filter(l => l.trim());
            if (lines.length < 2) return res({ headers: [], rows: [] });
            const headers = lines[0].split(';').map(h => h.trim());
            const rows = [];
            for (let i = 1; i < lines.length; i++) {
                const vals = lines[i].split(';');
                const row = {};
                headers.forEach((h, j) => row[h] = (vals[j] || '').trim());
                rows.push(row);
            }
            res({ headers, rows });
        };
        reader.onerror = rej;
        reader.readAsArrayBuffer(file);
    });
}

// ============================
// VALIDATION ENGINE
// ============================
function normalizeCode(val) {
    if (val == null || val === '') return '';
    return String(val).split('-')[0].trim().split(' ')[0].trim();
}

function isBlank(val) {
    return val == null || String(val).trim() === '' || String(val).trim().toLowerCase() === 'nan';
}

function excelDateToJSDate(serial) {
    if (serial instanceof Date) return serial;
    if (isNaN(serial) || serial === '') return serial;
    const date = new Date(Math.round((serial - 25569) * 86400 * 1000));
    date.setMinutes(date.getMinutes() + date.getTimezoneOffset());
    return date;
}

/**
 * Check if a dependencia condition is met.
 * Supports:
 *   - dependencia.valores: string[]  — field is required when ref matches ANY of these values
 *   - dependencia.valor: string      — legacy single-value (normalized to valores array at load time)
 */
function checkDependencia(dep, row, columnasPresentes) {
    if (!dep || !columnasPresentes.includes(dep.campo)) return false;
    const refVal = normalizeCode(row[dep.campo]);
    const expectedValues = dep.valores || (dep.valor ? [dep.valor] : []);
    return expectedValues.map(v => normalizeCode(v)).includes(refVal);
}

function validateRecord(row, rowIdx, fileName, entorno, rules) {
    const issues = [];
    const columnasPresentes = Object.keys(row);
    const ahora = new Date();
    const HOY_LIMITE = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate(), 23, 59, 59, 999).getTime();

    for (const [campo, rule] of Object.entries(rules)) {
        if (!columnasPresentes.includes(campo)) continue;

        const val = row[campo];
        const normVal = normalizeCode(val);
        const desc = rule.desc || campo;

        let isObligatorio = rule.obligatorio && rule.obligatorio.includes(entorno);

        // Excepción condicional (exceptoSi)
        if (isObligatorio && rule.exceptoSi) {
            const { campo: refCampo, valor: refValor } = rule.exceptoSi;
            if (columnasPresentes.includes(refCampo)) {
                if (normalizeCode(row[refCampo]) === normalizeCode(refValor)) isObligatorio = false;
            }
        }

        // Dependencia cruzada (uno o varios valores)
        if (rule.dependencia) {
            const dep = rule.dependencia;
            const condMet = checkDependencia(dep, row, columnasPresentes);
            if (condMet && isBlank(val)) {
                issues.push({ severity: 'error', campo, valor: val, fila: rowIdx, archivo: fileName, mensaje: dep.mensaje || `${desc} es obligatorio según la dependencia configurada.` });
                continue;
            }
        }

        // Obligatoriedad
        if (isObligatorio && isBlank(val)) {
            issues.push({ severity: 'error', campo, valor: val, fila: rowIdx, archivo: fileName, mensaje: `${desc} es obligatorio para este registro.` });
            continue;
        }

        // Validaciones de contenido
        if (!isBlank(val)) {
            // Fechas
            if (rule.tipo && rule.tipo.toString().includes('fecha')) {
                const fechaObjeto = excelDateToJSDate(val);
                const fechaMs = fechaObjeto instanceof Date ? fechaObjeto.getTime() : new Date(fechaObjeto).getTime();
                if (isNaN(fechaMs)) {
                    issues.push({ severity: 'error', campo, valor: val, fila: rowIdx, archivo: fileName, mensaje: `${desc} no es una fecha válida.` });
                } else {
                    if (rule.maxHoy && fechaMs > HOY_LIMITE) {
                        const fechaLegible = fechaObjeto instanceof Date ? fechaObjeto.toLocaleDateString('es-CO') : val;
                        issues.push({ severity: 'error', campo, valor: val, fila: rowIdx, archivo: fileName, mensaje: `${desc} (${fechaLegible}) no puede ser una fecha futura.` });
                    }
                    if (rule.comparar) {
                        const { campoRef, operacion, mensaje } = rule.comparar;
                        const valRef = row[campoRef];
                        if (!isBlank(valRef)) {
                            const fechaRefObj = excelDateToJSDate(valRef);
                            const fechaRefMs = fechaRefObj instanceof Date ? fechaRefObj.getTime() : new Date(fechaRefObj).getTime();
                            if (!isNaN(fechaRefMs)) {
                                const inconsistente =
                                    (operacion === '>=' && fechaMs < fechaRefMs) ||
                                    (operacion === '<=' && fechaMs > fechaRefMs) ||
                                    (operacion === '>' && fechaMs <= fechaRefMs) ||
                                    (operacion === '<' && fechaMs >= fechaRefMs);
                                if (inconsistente) issues.push({ severity: 'error', campo, valor: val, fila: rowIdx, archivo: fileName, mensaje });
                            }
                        }
                    }
                }
            }

            // Excepciones por entorno
            if (rule.excepcionPorEntorno && rule.excepcionPorEntorno[entorno]) {
                const exc = rule.excepcionPorEntorno[entorno];
                if (exc.prohibido && normVal === normalizeCode(exc.prohibido)) {
                    issues.push({ severity: 'error', campo, valor: val, fila: rowIdx, archivo: fileName, mensaje: exc.mensaje || `El valor "${val}" no es válido aquí.` });
                }
            }

            // Lista de valores
            if (rule.valores && !rule.valores.map(v => normalizeCode(v)).includes(normVal)) {
                issues.push({ severity: 'error', campo, valor: val, fila: rowIdx, archivo: fileName, mensaje: `${desc} incorrecto. Se esperaba: ${rule.valores.join(', ')}` });
            }

            // Numérico y rango
            if (rule.tipo === 'numero' || rule.tipo === 'rango') {
                const num = Number(val);
                if (isNaN(num)) {
                    issues.push({ severity: 'error', campo, valor: val, fila: rowIdx, archivo: fileName, mensaje: `${desc} debe ser un número` });
                } else if (rule.tipo === 'rango' && (num < rule.min || num > rule.max)) {
                    issues.push({ severity: 'error', campo, valor: val, fila: rowIdx, archivo: fileName, mensaje: `${desc} debe estar entre ${rule.min} y ${rule.max}` });
                }
            }

            // Texto no vacío
            if (rule.tipo === 'texto_nonempty' && String(val).trim().length === 0) {
                issues.push({ severity: 'error', campo, valor: val, fila: rowIdx, archivo: fileName, mensaje: `${desc} no puede estar vacío.` });
            }
        }
    }

    return issues;
}

// ============================
// MAIN VALIDATION
// ============================
async function runValidation() {
    if (!selectedEntorno || !selectedFormatId || loadedFiles.length === 0) return;

    const fmt = getFormatById(selectedFormatId);
    if (!fmt) return alert('Formato no encontrado');

    const btn = document.getElementById('btn-validate');
    btn.disabled = true;
    btn.classList.add('loading');
    document.getElementById('btn-icon').innerHTML = '<div class="spinner"></div>';
    document.getElementById('btn-text').textContent = 'PROCESANDO...';

    allIssues = [];
    allResults = [];

    for (const file of loadedFiles) {
        try {
            const ext = file.name.split('.').pop().toLowerCase();
            const { headers, rows } = ext === 'csv' ? await readCSVFile(file) : await readExcelFile(file);
            let fileIssues = 0;

            if (rows.length === 0) {
                allIssues.push({ severity: 'error', campo: 'Archivo', valor: file.name, mensaje: 'Archivo vacío o sin datos desde la fila 2', fila: 0, archivo: file.name });
                continue;
            }

            for (let i = 0; i < rows.length; i++) {
                const realRowIdx = i + 3;
                const rowIssues = validateRecord(rows[i], realRowIdx, file.name, selectedEntorno, fmt.rules);
                allIssues.push(...rowIssues);
                fileIssues += rowIssues.length;
            }

            allResults.push({ name: file.name, records: rows.length, issues: fileIssues, headers });
        } catch (err) {
            allIssues.push({ severity: 'error', campo: 'Archivo', valor: file.name, mensaje: `Error al procesar: ${err.message}`, fila: 0, archivo: file.name });
        }
    }

    renderResults();

    btn.disabled = false;
    btn.classList.remove('loading');
    document.getElementById('btn-icon').textContent = '▶';
    document.getElementById('btn-text').textContent = 'VALIDAR ARCHIVOS';
}

// ============================
// RESULTS RENDERING
// ============================
function renderResults() {
    const fmt = getFormatById(selectedFormatId);
    const totalRecords = allResults.reduce((s, r) => s + r.records, 0);
    const errors = allIssues.filter(i => i.severity === 'error').length;
    const warnings = allIssues.filter(i => i.severity === 'warning').length;
    const infos = allIssues.filter(i => i.severity === 'info').length;

    const maxDeduct = totalRecords * 10;
    const deductions = errors * 2 + warnings * 0.5;
    const score = totalRecords > 0 ? Math.max(0, Math.round(100 - (deductions / Math.max(maxDeduct, deductions + 1)) * 100)) : 0;

    document.getElementById('stat-records').textContent = totalRecords.toLocaleString('es');
    document.getElementById('stat-errors').textContent = errors.toLocaleString('es');
    document.getElementById('stat-warnings').textContent = warnings.toLocaleString('es');

    const sn = document.getElementById('score-num');
    sn.textContent = score + '%';
    sn.className = 'score-num ' + (score >= 80 ? 'score-good' : score >= 60 ? 'score-med' : 'score-bad');
    document.getElementById('score-pct').textContent = score + '%';

    const bar = document.getElementById('quality-bar');
    bar.style.width = score + '%';
    bar.style.background = score >= 80 ? 'var(--ok)' : score >= 60 ? 'var(--warn)' : 'var(--err)';

    document.getElementById('results-subtitle').textContent =
        `Entorno ${ENTORNO_NAMES[selectedEntorno]} · Formato ${fmt.nombre} — ${allResults.length} archivo(s) — ${totalRecords} registros — ${errors + warnings + infos} incidencias`;

    document.getElementById('results-section').style.display = 'block';
    document.getElementById('step3').classList.add('done');
    document.getElementById('step4').classList.add('active');

    renderIssues('all');
}

function renderIssues(filter) {
    currentFilter = filter;
    const body = document.getElementById('issues-body');
    const filtered = filter === 'all' ? allIssues : allIssues.filter(i => i.severity === filter);

    if (filtered.length === 0) {
        body.innerHTML = `<div class="empty-state"><span class="empty-icon">${filter === 'error' ? '✅' : '🎉'}</span>${filter === 'all' ? 'Sin incidencias encontradas. ¡Excelente calidad del dato!' : 'Sin incidencias de este tipo.'}</div>`;
        return;
    }

    const byFile = {};
    for (const issue of filtered) {
        if (!byFile[issue.archivo]) byFile[issue.archivo] = [];
        byFile[issue.archivo].push(issue);
    }

    let html = '';
    for (const [fname, issues] of Object.entries(byFile)) {
        const errC = issues.filter(i => i.severity === 'error').length;
        const warnC = issues.filter(i => i.severity === 'warning').length;
        html += `<div class="file-section">
      <div class="file-section-header" onclick="toggleSection(this)">
        <span style="font-size:16px;">📄</span>
        <span class="fsec-name">${fname}</span>
        <span class="tag ${errC > 0 ? 'tag-err' : warnC > 0 ? 'tag-warn' : 'tag-ok'}">${issues.length} incidencias</span>
        <span style="font-size:12px; color:var(--text3);">${errC} err / ${warnC} adv</span>
        <span class="chevron open">▾</span>
      </div>
      <div class="file-section-body">
        <div class="issues-container">
        <table class="issues-table">
          <thead><tr><th>TIPO</th><th>FILA</th><th>CAMPO</th><th>VALOR</th><th>DESCRIPCIÓN</th></tr></thead>
          <tbody>`;
        for (const issue of issues) {
            const tagClass = issue.severity === 'error' ? 'tag-err' : issue.severity === 'warning' ? 'tag-warn' : 'tag-info';
            const tagLabel = issue.severity === 'error' ? '❌ ERROR' : issue.severity === 'warning' ? '⚠️ ADVERTENCIA' : 'ℹ️ INFO';
            html += `<tr>
        <td><span class="tag ${tagClass}">${tagLabel}</span></td>
        <td><span class="row-ref">#${issue.fila}</span></td>
        <td style="font-family:'Space Mono',monospace;font-size:11px; max-width:180px; word-break:break-word;">${escHtml(issue.campo)}</td>
        <td style="font-family:'Space Mono',monospace;font-size:11px; color:var(--text3);">${escHtml(issue.valor)}</td>
        <td style="font-size:12px;">${escHtml(issue.mensaje)}</td>
      </tr>`;
        }
        html += `</tbody></table></div></div></div>`;
    }
    body.innerHTML = html;
}

function escHtml(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function toggleSection(header) {
    const body = header.nextElementSibling;
    const chevron = header.querySelector('.chevron');
    if (body.style.display === 'none') { body.style.display = ''; chevron.classList.add('open'); }
    else { body.style.display = 'none'; chevron.classList.remove('open'); }
}

function filterIssues(type, btn) {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderIssues(type);
}

function exportCSV() {
    if (allIssues.length === 0) return;
    const header = 'Archivo;Fila;Tipo;Campo;Valor;Descripción\n';
    const rows = allIssues.map(i =>
        `"${i.archivo}";"${i.fila}";"${i.severity}";"${i.campo}";"${String(i.valor).replace(/"/g, '""')}";"${i.mensaje.replace(/"/g, '""')}"`
    ).join('\n');
    const blob = new Blob(['\uFEFF' + header + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `errores_${selectedFormatId}_${selectedEntorno}_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
}

function resetApp() {
    selectedEntorno = null;
    selectedFormatId = null;
    loadedFiles = [];
    allIssues = [];
    allResults = [];
    document.querySelectorAll('.entorno-btn').forEach(b => b.classList.remove('selected'));
    document.getElementById('panel-formato').classList.add('section-hidden');
    document.getElementById('panel-files').classList.add('section-hidden');
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('file-list').innerHTML = '';
    document.getElementById('btn-validate').disabled = true;
    ['step1', 'step2', 'step3', 'step4'].forEach(id => {
        document.getElementById(id).classList.remove('active', 'done');
    });
    document.getElementById('step1').classList.add('active');
}

// ============================
// FORMAT MANAGER MODAL
// ============================
function openFormatManager() {
    document.getElementById('modal-overlay').classList.remove('hidden');
    editingFormatId = null;
    renderFmtList();
    showEditorEmpty();
}

function closeFormatManager() {
    document.getElementById('modal-overlay').classList.add('hidden');
    if (selectedEntorno) renderFormatoGrid();
}

function closeFormatManagerIfBg(e) {
    if (e.target === document.getElementById('modal-overlay')) closeFormatManager();
}

function renderFmtList() {
    const container = document.getElementById('fmt-list');
    const all = getAllFormats();
    container.innerHTML = all.map(f => `
    <div class="fmt-list-item ${f.id === editingFormatId ? 'active' : ''}" onclick="editFormat('${f.id}')">
      <div class="fli-code">${f.code}</div>
      <div class="fli-info">
        <div class="fli-name">${f.nombre}</div>
        <div class="fli-entornos">${f.entornos.map(e => ENTORNO_ICONS[e]).join('')} · ${Object.keys(f.rules).length} campos</div>
      </div>
      ${f.builtin ? '<div class="fli-builtin" title="Formato base (editable)">⚙</div>' : '<div class="fli-custom">✦</div>'}
    </div>
  `).join('');
}

function showEditorEmpty() {
    document.getElementById('fmt-editor-empty').style.display = '';
    document.getElementById('fmt-editor-form').style.display = 'none';
}

function startNewFormat() {
    editingFormatId = null;
    document.getElementById('fmt-editor-empty').style.display = 'none';
    document.getElementById('fmt-editor-form').style.display = '';
    document.getElementById('btn-delete-fmt').style.display = 'none';
    document.getElementById('btn-reset-builtin').style.display = 'none';
    document.getElementById('fmt-builtin-notice').style.display = 'none';

    document.getElementById('fmt-name').value = '';
    document.getElementById('fmt-code').value = '';
    document.getElementById('fmt-desc').value = '';
    document.querySelectorAll('#fmt-entornos input[type=checkbox]').forEach(cb => cb.checked = false);
    document.getElementById('rules-container').innerHTML = '';
}

function editFormat(id) {
    const fmt = getFormatById(id);
    if (!fmt) return;
    editingFormatId = id;

    document.getElementById('fmt-editor-empty').style.display = 'none';
    document.getElementById('fmt-editor-form').style.display = '';

    const isBuiltin = fmt.builtin;
    const overrides = loadBuiltinOverrides();
    const hasOverride = isBuiltin && !!overrides[id];

    // For all formats (builtin and custom), show delete only for custom
    document.getElementById('btn-delete-fmt').style.display = isBuiltin ? 'none' : '';

    // Show reset button for builtins that have been modified
    const resetBtn = document.getElementById('btn-reset-builtin');
    resetBtn.style.display = (isBuiltin && hasOverride) ? '' : 'none';

    // Show builtin notice
    const notice = document.getElementById('fmt-builtin-notice');
    notice.style.display = isBuiltin ? 'flex' : 'none';

    document.getElementById('fmt-name').value = fmt.nombre;
    document.getElementById('fmt-code').value = fmt.code;
    document.getElementById('fmt-desc').value = fmt.desc || '';

    // All entorno checkboxes enabled for all formats
    document.querySelectorAll('#fmt-entornos input[type=checkbox]').forEach(cb => {
        cb.checked = fmt.entornos.includes(cb.value);
        cb.disabled = false;
    });

    // Render rules — all editable
    const container = document.getElementById('rules-container');
    container.innerHTML = '';
    for (const [campo, rule] of Object.entries(fmt.rules)) {
        addRuleRow(campo, rule, false);
    }

    renderFmtList();
}

// ============================
// RULE ROWS
// ============================
function addRuleRow(campoDefault = '', ruleDefault = null, readonly = false) {
    const tpl = document.getElementById('rule-row-tpl');
    const clone = tpl.content.cloneNode(true);
    const row = clone.querySelector('.rule-row');
    row.dataset.ruleId = Date.now() + Math.random();

    const campoInput = row.querySelector('.rule-campo');
    const tipoSelect = row.querySelector('.rule-tipo');
    const descInput = row.querySelector('.rule-desc');
    const minInput = row.querySelector('.rule-min');
    const maxInput = row.querySelector('.rule-max');
    const valoresInput = row.querySelector('.rule-valores');

    // Dependencia fields
    const depCampoInput = row.querySelector('.rule-dep-campo');
    const depValoresInput = row.querySelector('.rule-dep-valores');
    const depMsgInput = row.querySelector('.rule-dep-msg');

    campoInput.value = campoDefault;
    descInput.value = ruleDefault?.desc || '';

    if (ruleDefault) {
        const tipo = ruleDefault.tipo || 'texto';
        tipoSelect.value = tipo;

        if (tipo === 'rango') {
            row.querySelector('.rule-extra-rango').style.display = 'flex';
            minInput.value = ruleDefault.min ?? '';
            maxInput.value = ruleDefault.max ?? '';
        }
        if (tipo === 'codigo') {
            row.querySelector('.rule-extra-valores').style.display = 'flex';
            valoresInput.value = (ruleDefault.valores || []).join('|');
        }

        // Obligatorio checks
        row.querySelectorAll('.rule-obligatorio input').forEach(cb => {
            cb.checked = ruleDefault.obligatorio && ruleDefault.obligatorio.includes(cb.value);
        });

        // Dependencia
        if (ruleDefault.dependencia) {
            row.querySelector('.rule-extra-dep').style.display = 'flex';
            row.querySelector('.rule-dep-toggle').classList.add('active');
            depCampoInput.value = ruleDefault.dependencia.campo || '';
            // Support both .valores (array) and legacy .valor (string)
            const depVals = ruleDefault.dependencia.valores || (ruleDefault.dependencia.valor ? [ruleDefault.dependencia.valor] : []);
            depValoresInput.value = depVals.join('|');
            depMsgInput.value = ruleDefault.dependencia.mensaje || '';
        }
    }

    if (readonly) {
        row.querySelectorAll('input, select, button.btn-icon-danger').forEach(el => {
            if (el.tagName === 'BUTTON') el.style.display = 'none';
            else el.disabled = true;
        });
        row.style.opacity = '0.7';
    }

    document.getElementById('rules-container').appendChild(clone);
}

function onRuleTipoChange(select) {
    const row = select.closest('.rule-row');
    const tipo = select.value;
    row.querySelector('.rule-extra-rango').style.display = tipo === 'rango' ? 'flex' : 'none';
    row.querySelector('.rule-extra-valores').style.display = tipo === 'codigo' ? 'flex' : 'none';
}

function toggleDepSection(btn) {
    const row = btn.closest('.rule-row');
    const depSection = row.querySelector('.rule-extra-dep');
    const isOpen = depSection.style.display === 'flex';
    depSection.style.display = isOpen ? 'none' : 'flex';
    btn.classList.toggle('active', !isOpen);
}

function removeRuleRow(btn) {
    btn.closest('.rule-row').remove();
}

// ============================
// SAVE / DELETE FORMAT
// ============================
function saveFormat() {
    const nombre = document.getElementById('fmt-name').value.trim();
    const code = document.getElementById('fmt-code').value.trim().toUpperCase();
    const desc = document.getElementById('fmt-desc').value.trim();
    const entornos = [...document.querySelectorAll('#fmt-entornos input:checked')].map(cb => cb.value);

    if (!nombre) return alert('El nombre del formato es obligatorio.');
    if (entornos.length === 0) return alert('Seleccione al menos un entorno.');

    // Collect rules
    const rules = {};
    document.querySelectorAll('#rules-container .rule-row').forEach(row => {
        const campo = row.querySelector('.rule-campo').value.trim();
        if (!campo) return;
        const tipo = row.querySelector('.rule-tipo').value;
        const desc = row.querySelector('.rule-desc').value.trim();
        const obligatorio = [...row.querySelectorAll('.rule-obligatorio input:checked')].map(cb => cb.value);
        const rule = { tipo, desc };
        if (obligatorio.length > 0) rule.obligatorio = obligatorio;

        if (tipo === 'rango') {
            rule.min = Number(row.querySelector('.rule-min').value) || 0;
            rule.max = Number(row.querySelector('.rule-max').value) || 999;
        }
        if (tipo === 'codigo') {
            const valStr = row.querySelector('.rule-valores').value.trim();
            rule.valores = valStr ? valStr.split('|').map(v => v.trim()).filter(Boolean) : [];
        }

        // Dependencia
        const depSection = row.querySelector('.rule-extra-dep');
        if (depSection && depSection.style.display === 'flex') {
            const depCampo = row.querySelector('.rule-dep-campo').value.trim();
            const depValores = row.querySelector('.rule-dep-valores').value.trim();
            const depMsg = row.querySelector('.rule-dep-msg').value.trim();
            if (depCampo && depValores) {
                rule.dependencia = {
                    campo: depCampo,
                    valores: depValores.split('|').map(v => v.trim()).filter(Boolean),
                    mensaje: depMsg
                };
            }
        }

        rules[campo] = rule;
    });

    const isBuiltin = BUILTIN_FORMATS.some(f => f.id === editingFormatId);

    if (isBuiltin) {
        // Save as override for builtin
        const overrides = loadBuiltinOverrides();
        overrides[editingFormatId] = { nombre, code: code || editingFormatId.toUpperCase(), desc, entornos, rules };
        saveBuiltinOverrides(overrides);
    } else {
        const userFormats = loadUserFormats();
        if (editingFormatId) {
            const idx = userFormats.findIndex(f => f.id === editingFormatId);
            if (idx >= 0) userFormats[idx] = { ...userFormats[idx], nombre, code: code || userFormats[idx].code, desc, entornos, rules };
        } else {
            const id = 'uf_' + Date.now();
            userFormats.push({ id, nombre, code: code || nombre.substring(0, 4).toUpperCase(), desc, builtin: false, entornos, rules });
            editingFormatId = id;
        }
        saveUserFormats(userFormats);
    }

    renderFmtList();
    // Refresh reset button visibility
    editFormat(editingFormatId);
    alert(`✅ Formato "${nombre}" guardado correctamente.`);
}

function deleteFormat() {
    if (!editingFormatId) return;
    if (!confirm('¿Eliminar este formato? Esta acción no se puede deshacer.')) return;
    const userFormats = loadUserFormats().filter(f => f.id !== editingFormatId);
    saveUserFormats(userFormats);
    editingFormatId = null;
    renderFmtList();
    showEditorEmpty();
}

function resetBuiltinFormat() {
    if (!editingFormatId) return;
    if (!confirm('¿Restaurar este formato a sus valores originales? Se perderán los cambios guardados.')) return;
    const overrides = loadBuiltinOverrides();
    delete overrides[editingFormatId];
    saveBuiltinOverrides(overrides);
    editFormat(editingFormatId);
    alert('✅ Formato restaurado a los valores originales.');
}

// ============================
// INIT
// ============================
(async () => {
    await loadRulesJSON();
    // Re-render any initial state if needed
})();