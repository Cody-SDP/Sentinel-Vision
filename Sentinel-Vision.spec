# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(SPECPATH).resolve()
ICON_PATH = BASE_DIR / 'assets' / 'Sentinel-Vision-new.ico'
MODELS_PATH = BASE_DIR / 'models'

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        (str(MODELS_PATH), 'models'),
        (str(ICON_PATH), 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'datasets',
        'runs',
    ],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Sentinel-Vision',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/Sentinel-Vision-new.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Sentinel-Vision',
)
