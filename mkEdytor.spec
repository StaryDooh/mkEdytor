# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mkEdytor.py'],
    pathex=[],
    binaries=[],
    datas=[('ikona.ico', '.'), ('lewo.png', '.'), ('srodek.png', '.'), ('prawo.png', '.'), ('justuj.png', '.'), ('l_punktowana.png', '.'), ('l_numerowana.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mkEdytor',
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
    version='wersja.txt',
    icon=['ikona.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mkEdytor',
)
