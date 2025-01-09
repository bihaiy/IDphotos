# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# 基本文件列表
added_files = [
    # 配置文件
    ('api_config.json', '.'),
    ('paper_sizes.json', '.'),
    ('photo_sizes.json', '.'),
    ('layout_styles.json', '.'),
    
    # 确保包含config目录下的所有Python文件
    ('config/*.py', 'config'),
    
    # OpenCV数据
    ('venv/Lib/site-packages/cv2/data/haarcascade_*.xml', 'cv2/data'),
    
    # hivision模型和数据文件
    ('hivision/creator/weights/*.onnx', 'hivision/creator/weights'),
    ('hivision/creator/retinaface/weights/*.onnx', 'hivision/creator/retinaface/weights'),
    ('hivision/plugin/beauty/lut/*.png', 'hivision/plugin/beauty/lut'),
]

# 收集所有Python文件
for root, dirs, files in os.walk('hivision'):
    for file in files:
        if file.endswith('.py'):
            source = os.path.join(root, file)
            target = os.path.dirname(source)
            added_files.append((source, target))

a = Analysis(
    ['main.py'],
    pathex=[SPECPATH],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.colorchooser',
        'numpy',
        'cv2',
        'requests',
        'json',
        'base64',
        'tempfile',
        'onnxruntime',
        'onnxruntime.capi.session',
        'onnxruntime.capi._pybind_state',
        'onnxruntime.capi.onnxruntime_pybind11_state',
        'hivision',
        'hivision.creator',
        'hivision.plugin',
        'hivision.plugin.beauty',
        'config',  # 添加config模块
        'config.default_sizes',  # 添加default_sizes模块
        'win32print',  # 添加打印相关模块
        'win32ui',
        'win32gui',
        'win32con',
        'win32api',
    ],
    hookspath=[],
    hooksconfig={
        'onnxruntime': {
            'include_dlls': True,
            'include_data_files': True,
        }
    },
    runtime_hooks=['hooks/runtime_hook.py'],
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
    name='证件照制作系统',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
) 