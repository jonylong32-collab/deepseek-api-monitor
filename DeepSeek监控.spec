# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置 — DeepSeek API 用量监控
打包命令: pyinstaller DeepSeek监控.spec
"""
a = Analysis(
    ['backend/run.py'],
    pathex=['backend'],
    binaries=[],
    datas=[
        # 前端静态文件
        ('backend/app/static', 'app/static'),
        # 应用图标
        ('icon.ico', '.'),
    ],
    hiddenimports=[
        # FastAPI / uvicorn 全家桶
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.middleware',
        'uvicorn.middleware.asgi',
        'uvicorn.middleware.wsgi',
        # Pydantic
        'pydantic',
        'pydantic.computed_field',
        'pydantic.deprecated',
        'pydantic.json',
        # Starlette
        'starlette',
        'starlette.applications',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.routing',
        'starlette.staticfiles',
        'starlette.responses',
        # FastAPI
        'fastapi',
        # cryptography
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        # requests
        'requests',
        # pywebview
        'webview',
        'webview.platforms',
        'webview.platforms.edgechromium',
        'bottle',
        # pystray
        'pystray',
        # Pillow
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',   # 不再需要
        'matplotlib',
        'test',
        'unittest',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DeepSeek监控',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # 隐藏控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
