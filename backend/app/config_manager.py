"""
配置管理模块
移植自原项目 config.py
- API Key 加密存储 (Fernet)
- 余额历史记录 (90天)
- 用量数据缓存
- 窗口配置记忆
"""
from __future__ import annotations
import os
import json
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, Optional
from cryptography.fernet import Fernet

DEFAULT_REFRESH_INTERVAL = 300
DATA_DIR_NAME = "deepseek-monitor"


class ConfigManager:
    """应用配置管理器 — 单例模式。"""

    DEFAULTS = {
        "api_key": "",
        "refresh_interval": DEFAULT_REFRESH_INTERVAL,
        "always_on_top": False,
    }

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir:
            self._data_dir = Path(data_dir)
        else:
            appdata = os.environ.get("APPDATA", "")
            self._data_dir = Path(appdata) / DATA_DIR_NAME

        self._config_path = self._data_dir / "config.json"
        self._history_path = self._data_dir / "balance_history.json"
        self._usage_cache_path = self._data_dir / "usage_cache.json"
        self._key_path = self._data_dir / ".keyfile"
        self._web_session_dir = self._data_dir / "web-session"
        self._web_downloads_dir = self._data_dir / "web-downloads"
        self._data = dict(self.DEFAULTS)
        self._init()

    def _init(self):
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._web_session_dir.mkdir(parents=True, exist_ok=True)
        self._web_downloads_dir.mkdir(parents=True, exist_ok=True)
        if not self._key_path.exists():
            self._key_path.write_bytes(Fernet.generate_key())
        self.load()

    def _get_fernet(self) -> Fernet:
        return Fernet(self._key_path.read_bytes())

    # ── 属性 ────────────────────────────────────────

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    @property
    def web_session_dir(self) -> Path:
        return self._web_session_dir

    @property
    def web_downloads_dir(self) -> Path:
        return self._web_downloads_dir

    @property
    def has_web_session(self) -> bool:
        try:
            return any(p.is_file() for p in self._web_session_dir.rglob("*"))
        except OSError:
            return False

    def clear_web_session(self):
        import shutil
        if self._web_session_dir.exists():
            shutil.rmtree(self._web_session_dir, ignore_errors=True)
        self._web_session_dir.mkdir(parents=True, exist_ok=True)

    # ── API Key ─────────────────────────────────────

    @property
    def api_key(self) -> str:
        encrypted = self._data.get("api_key", "")
        if not encrypted:
            return ""
        try:
            return self._get_fernet().decrypt(encrypted.encode()).decode()
        except Exception:
            return ""

    @api_key.setter
    def api_key(self, plain_text: str):
        if plain_text:
            self._data["api_key"] = self._get_fernet().encrypt(
                plain_text.encode()
            ).decode()
        else:
            self._data["api_key"] = ""

    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key)

    @property
    def refresh_interval(self) -> int:
        return self._data.get("refresh_interval", DEFAULT_REFRESH_INTERVAL)

    @refresh_interval.setter
    def refresh_interval(self, seconds: int):
        self._data["refresh_interval"] = max(30, min(seconds, 3600))

    @property
    def always_on_top(self) -> bool:
        return self._data.get("always_on_top", False)

    @always_on_top.setter
    def always_on_top(self, value: bool):
        self._data["always_on_top"] = value

    # ── 余额历史记录 ────────────────────────────────

    def load_balance_history(self) -> Dict[str, float]:
        if self._history_path.exists():
            try:
                return json.loads(self._history_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_balance_history(self, history: Dict[str, float]):
        self._history_path.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def record_balance(self, balance: float):
        today = date.today().isoformat()
        history = self.load_balance_history()
        history[today] = balance
        cutoff = (date.today() - timedelta(days=90)).isoformat()
        history = {k: v for k, v in history.items() if k >= cutoff}
        self.save_balance_history(history)

    def get_daily_spend(self) -> Dict[str, float]:
        history = self.load_balance_history()
        if len(history) < 2:
            return {}
        dates = sorted(history.keys())
        spend = {}
        for i in range(1, len(dates)):
            day = dates[i]
            prev = history[dates[i - 1]]
            curr = history[day]
            spent = prev - curr
            spend[day] = round(max(spent, 0.0), 4)
        return spend

    # ── 用量数据缓存 ────────────────────────────────

    def load_usage_cache(self) -> Dict:
        if self._usage_cache_path.exists():
            try:
                return json.loads(self._usage_cache_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_usage_cache(self, data: Dict):
        self._usage_cache_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # ── 持久化 ──────────────────────────────────────

    def load(self):
        if self._config_path.exists():
            try:
                saved = json.loads(self._config_path.read_text(encoding="utf-8"))
                for k in self.DEFAULTS:
                    if k in saved:
                        self._data[k] = saved[k]
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        self._config_path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def as_dict(self) -> dict:
        return {
            "has_api_key": self.has_api_key,
            "has_web_session": self.has_web_session,
            "refresh_interval": self.refresh_interval,
            "always_on_top": self.always_on_top,
        }


# ── 全局单例 ────────────────────────────────────────

_config_instance: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance
