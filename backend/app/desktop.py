"""
桌面启动器模块
整合 FastAPI 后端 + 系统托盘 + 浏览器/pywebview
"""
from __future__ import annotations
import os
import sys
import time
import json
import logging
import threading
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

logger = logging.getLogger("desktop")

# ── 托盘图标 ─────────────────────────────────────────

COLOR_ACCENT = "#00D4FF"
COLOR_ACCENT_PRESS = "#00A8CC"
COLOR_TEXT_PRIMARY = "#E8E8F0"


def _create_tray_image() -> "PIL.Image.Image":
    from PIL import Image, ImageDraw
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (4, 4, 60, 60), radius=14,
        fill=COLOR_ACCENT, outline=COLOR_ACCENT_PRESS, width=2,
    )
    cx, cy = size // 2, size // 2
    r = 16
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=COLOR_TEXT_PRIMARY)
    draw.rectangle([cx, cy - r, cx + r // 2, cy + r], fill=COLOR_ACCENT)
    return img


# ── WebView2 检测 ────────────────────────────────────

def _webview2_available() -> bool:
    """检测 Microsoft Edge WebView2 是否可用。"""
    try:
        import webview.platforms.edgechromium  # noqa
        return True
    except Exception:
        return False


# ── 桌面应用 ─────────────────────────────────────────

class DesktopApp:
    """桌面应用主控：启动服务 → 打开界面 → 系统托盘。"""

    PORT = 5678
    HOST = "127.0.0.1"
    TITLE = "DeepSeek 用量监控"
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 750

    def __init__(self):
        self.server: Optional["uvicorn.Server"] = None
        self.server_thread: Optional[threading.Thread] = None
        self.window: Optional["webview.Window"] = None
        self.tray_icon: Optional["pystray.Icon"] = None
        self._ready = threading.Event()
        self._shutdown = False

    # ── 服务器 ────────────────────────────────────────

    def start_server(self):
        """在后台线程启动 FastAPI 服务器。"""
        import uvicorn
        from app.main import app

        config = uvicorn.Config(
            app,
            host=self.HOST,
            port=self.PORT,
            log_level="info",
            access_log=False,
            log_config={
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "simple": {
                        "format": "%(asctime)s [%(levelname)s] %(message)s",
                        "datefmt": "%H:%M:%S",
                    },
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "simple",
                        "stream": "ext://sys.stdout",
                    },
                },
                "loggers": {
                    "uvicorn": {
                        "handlers": ["console"],
                        "level": "INFO",
                        "propagate": False,
                    },
                    "uvicorn.error": {
                        "handlers": ["console"],
                        "level": "INFO",
                        "propagate": False,
                    },
                    "uvicorn.access": {
                        "handlers": ["console"],
                        "level": "WARNING",
                        "propagate": False,
                    },
                },
            },
        )
        self.server = uvicorn.Server(config)
        self.server_thread = threading.Thread(
            target=self.server.run, daemon=True, name="uvicorn"
        )
        self.server_thread.start()
        self._wait_for_server()
        logger.info("后端服务已启动: http://%s:%s", self.HOST, self.PORT)

    def _wait_for_server(self, timeout: float = 10.0):
        url = f"http://{self.HOST}:{self.PORT}/api/health"
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                resp = urllib.request.urlopen(url, timeout=1)
                if resp.status == 200:
                    self._ready.set()
                    return
            except (urllib.error.URLError, ConnectionError, OSError):
                time.sleep(0.2)
        logger.warning("服务器启动超时")

    # ── 界面 ──────────────────────────────────────────

    def open_ui(self):
        """打开用户界面：优先原生窗口，否则回退到浏览器。"""
        # 尝试 pywebview 原生窗口
        if _webview2_available():
            logger.info("WebView2 可用，尝试原生窗口")
            try:
                self._open_webview_window()
                return
            except Exception as e:
                logger.warning("原生窗口创建失败: %s", e)
        else:
            logger.info("WebView2 不可用，直接使用浏览器")

        # 回退到浏览器
        self._fallback_to_browser()

    def _open_webview_window(self):
        """创建 pywebview 原生窗口（阻塞直到窗口关闭）。"""
        import webview

        def on_closing():
            logger.info("窗口关闭，准备退出")
            self.shutdown()

        self.window = webview.create_window(
            self.TITLE,
            f"http://{self.HOST}:{self.PORT}",
            width=self.WINDOW_WIDTH,
            height=self.WINDOW_HEIGHT,
            resizable=True,
            fullscreen=False,
            easy_drag=False,
            confirm_close=False,
        )
        logger.info("启动 GUI 事件循环...")
        webview.start()
        logger.info("GUI 事件循环结束")

    def _fallback_to_browser(self):
        """回退：用默认浏览器打开。"""
        import webbrowser
        url = f"http://{self.HOST}:{self.PORT}"
        logger.info("用浏览器打开: %s", url)
        webbrowser.open(url)
        # 保持服务器运行直到退出信号
        logger.info("应用在后台运行中，使用系统托盘管理")
        try:
            while not self._shutdown:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    # ── 系统托盘 ──────────────────────────────────────

    def setup_tray(self):
        """设置系统托盘（后台线程运行）。"""
        import pystray
        from pystray import MenuItem as Item

        icon_img = _create_tray_image()

        def on_show(icon, item):
            self._show_window()

        def on_refresh(icon, item):
            self._trigger_refresh()

        def on_quit(icon, item):
            logger.info("托盘退出")
            self.shutdown()
            if self.tray_icon:
                self.tray_icon.stop()
            os._exit(0)

        menu = pystray.Menu(
            Item("显示窗口", on_show, default=True),
            Item("立即刷新", on_refresh),
            pystray.Menu.SEPARATOR,
            Item("退出", on_quit),
        )

        self.tray_icon = pystray.Icon(
            "ds_monitor", icon_img, self.TITLE, menu=menu,
        )
        self.tray_icon.run()

    def _show_window(self):
        if self.window:
            try:
                self.window.show()
                self.window.on_top = True
                time.sleep(0.1)
                self.window.on_top = False
            except Exception:
                pass

    def _trigger_refresh(self):
        if self.window:
            try:
                self.window.load_url(f"http://{self.HOST}:{self.PORT}")
            except Exception:
                pass

    # ── 生命周期 ──────────────────────────────────────

    def run(self):
        """启动桌面应用。"""
        logger.info("桌面应用启动...")
        self.start_server()

        # 系统托盘（后台线程）
        tray_thread = threading.Thread(target=self.setup_tray, daemon=True)
        tray_thread.start()

        # 打开界面（阻塞）
        self.open_ui()

        self.shutdown()

    def shutdown(self):
        if self._shutdown:
            return
        self._shutdown = True
        logger.info("正在关闭...")
        if self.server:
            self.server.should_exit = True
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
