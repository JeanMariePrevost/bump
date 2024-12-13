# -*- mode: python ; coding: utf-8 -*-


added_files = [
    # ("config", "config"),
    ("assets", "assets"),
    ("metadata.json", "."),
    ("src/frontend/content", "src/frontend/content"),
]


a = Analysis(
    ["src/app.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=["plyer.platforms.win.notification"],
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
    name="bump",
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
    icon="assets/icon_32px.ico",
)


exe_debug = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="bump_debug_mode",
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon_32px.ico",
)
coll = COLLECT(
    exe,
    exe_debug,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="app",
)


import os
import shutil

# Post-Processing: Move certain folders outside of pyinstaller's "_internal" directory
dist_dir = os.path.join(os.getcwd(), "dist", "app")  # Default PyInstaller "root" location
folders_to_move_to_app_root = ["assets", "config"]

for folder in folders_to_move_to_app_root:
    src = os.path.join(dist_dir, "_internal", folder)  # Default PyInstaller directory for "datas"
    dest = os.path.join(dist_dir, folder)
    if os.path.exists(src):
        print(f"My custom post-processing: Moving {src} to {dest}")
        shutil.move(src, dest)
