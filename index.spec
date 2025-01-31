# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['index.py'],
    pathex=[],
    binaries=[],
    datas=[('img', 'img'), ('areas.json', '.'), ('bases.json', '.'), ('crear_hc', 'crear_hc'), ('validadores', 'validadores'), ('version.txt', '.'), ('index.py', '.'), ('analizar_exel.py', '.'), ('reglas.py', '.'), ('error_log.txt', '.'), ('__version__.py', '.')],
    hiddenimports=['pkg_resources', 'pkg_resources.py2_warn', 'pkg_resources.extern'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='index',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
