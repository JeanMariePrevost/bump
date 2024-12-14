# -*- mode: python ; coding: utf-8 -*-

import os


def collect_hiddenimports(src_folder):
    """
    Walk through the src folder and collect all Python modules and submodules
    as fully qualified import strings for hidden imports.
    """
    hiddenimports = []
    for root, _, files in os.walk(src_folder):
        # Get the relative path from the root of the src folder
        rel_path = os.path.relpath(root, src_folder)
        package = rel_path.replace(os.sep, ".").strip(".")  # Convert to Python package/module format

        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_name = file[:-3]  # Remove ".py"
                if package:
                    hiddenimports.append(f"{package}.{module_name}")
                else:
                    hiddenimports.append(module_name)  # Top-level module

    return hiddenimports


# Dynamically determine the root directory of the spec file and "src" folder
src_folder = os.path.join(os.getcwd(), "src")  # Append "src" to the spec file location
if not os.path.exists(src_folder):
    raise FileNotFoundError(f"Source folder not found: {src_folder}")
dynamic_hidden_imports = collect_hiddenimports(src_folder)


hardcoded_hidden_imports = ["plyer.platforms.win.notification"]
all_hidden_imports = dynamic_hidden_imports + hardcoded_hidden_imports


# DEBUG: Print the hidden imports
print("Hidden imports:")
for imp in all_hidden_imports:
    print(imp)

added_files = [
    # ("config", "config"),
    ("assets", "assets"),
    ("metadata.json", "."),
    ("src/frontend/content", "src/frontend/content"),
    ("extra_pyinstaller_datas/playwright/driver/package/.local-browsers", "playwright/driver/package/.local-browsers"),
]


a = Analysis(
    ["src/app.py"],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=all_hidden_imports,
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
