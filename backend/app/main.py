"""
DeepSeek API 用量监控平台 — FastAPI 后端入口
同时支持标准服务模式和 PyInstaller 嵌入式模式
"""
import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers import balance, usage, config as config_router

logger = logging.getLogger("backend")

# ── 静态文件路径（支持 PyInstaller 打包） ──────────────

def _static_dir() -> Path:
    """返回静态文件目录（开发 / PyInstaller 打包均支持）。"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，文件在 sys._MEIPASS/app/static 下
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    # 优先查找 app/static（PyInstaller 打包布局）
    for candidate in (base / "app" / "static", base / "static"):
        if candidate.is_dir():
            return candidate
    return base / "static"


_static_path = _static_dir()
logger.info("静态文件目录: %s", _static_path)


# ── FastAPI 应用 ─────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("DeepSeek 用量监控后端启动...")
    yield
    logger.info("后端已关闭")


app = FastAPI(
    title="DeepSeek API 用量监控",
    description="DeepSeek API 用量监控平台后端服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — 本地桌面应用需要允许来自 webview 的请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由
app.include_router(balance.router, prefix="/api", tags=["余额"])
app.include_router(usage.router, prefix="/api", tags=["用量"])
app.include_router(config_router.router, prefix="/api", tags=["配置"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


# 静态文件服务（SPA 模式：未匹配的路径全部返回 index.html）
if _static_path.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_static_path / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA 回退：所有非 API 路由都返回 index.html。"""
        file_path = _static_path / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        index = _static_path / "index.html"
        if index.is_file():
            return FileResponse(str(index))
        return {"error": "not found"}
