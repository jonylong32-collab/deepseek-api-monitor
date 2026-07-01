"""
DeepSeek API 用量监控 — 桌面应用入口
单例检测 + 启动桌面应用
所有日志同时写入文件（方便调试闪退问题）
"""
from __future__ import annotations
import os
import sys
import time
import ctypes
import logging
import tempfile
from ctypes import wintypes

# ── 日志配置：同时输出到控制台和文件 ─────────────────

_APP_DIR = os.path.dirname(os.path.abspath(__file__))
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

# 日志文件路径（方便调试闪退）
_LOG_DIR = os.path.join(tempfile.gettempdir(), "deepseek-monitor-logs")
os.makedirs(_LOG_DIR, exist_ok=True)
_LOG_FILE = os.path.join(_LOG_DIR, "startup.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

# 增加文件日志处理器，方便调试闪退
_file_handler = logging.FileHandler(_LOG_FILE, mode="w", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
))
logging.getLogger().addHandler(_file_handler)

logger.info("日志文件: %s", _LOG_FILE)
logger.info("DeepSeek API 用量监控启动...")

SINGLETON_MUTEX_NAME = "DeepSeekMonitor-Web-Mutex"


def _show_message_box(message: str, title: str = "DeepSeek 用量监控", icon: int = 0x40):
    """弹出 Windows 消息框。"""
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, icon)
    except Exception:
        pass


def is_already_running() -> bool:
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.argtypes = [
            wintypes.LPCVOID, wintypes.BOOL, wintypes.LPCWSTR,
        ]
        kernel32.CreateMutexW.restype = wintypes.HANDLE

        kernel32.CreateMutexW(None, False, SINGLETON_MUTEX_NAME)
        ctypes.get_last_error()
        err = ctypes.get_last_error()
        if err == 183:
            return True
        if not kernel32.CreateMutexW(None, False, SINGLETON_MUTEX_NAME):
            logger.warning("CreateMutexW 失败，回退到文件锁")
            raise Exception("CreateMutexW failed")
        return False
    except Exception:
        lockfile = os.path.join(
            tempfile.gettempdir(), ".deepseek_monitor_web.lock"
        )
        try:
            fd = os.open(lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(fd)
            return False
        except FileExistsError:
            return True


def main():
    # 单例检测
    if is_already_running():
        logger.warning("检测到已有实例在运行")
        _show_message_box(
            "DeepSeek 用量监控已经在运行中。\n请检查系统托盘图标。",
            "重复启动", 0x40
        )
        sys.exit(0)

    # 启动桌面应用
    try:
        from app.desktop import DesktopApp
        desktop = DesktopApp()
        desktop.run()
    except KeyboardInterrupt:
        logger.info("用户中断")
    except Exception as e:
        logger.exception("启动失败")
        _show_message_box(
            f"启动失败:\n{e}\n\n日志文件: {_LOG_FILE}",
            "错误", 0x10
        )
        sys.exit(1)

    logger.info("应用已退出")


if __name__ == "__main__":
    main()
