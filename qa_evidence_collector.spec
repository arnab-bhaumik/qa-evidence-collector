# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

added_files = [
    ('src/qa_evidence_collector/resources/icons/*.svg', 'qa_evidence_collector/resources/icons'),
]

a = Analysis(
    ['src/qa_evidence_collector/main.py'],
    pathex=['src'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PySide6.QtXml',
        'PySide6.QtSvg',
        'PySide6.QtSvgWidgets',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'PIL.Image',
        'PIL.ImageFilter',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'docx',
        'docx.oxml',
        'docx.shared',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QAEvidenceCollector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
