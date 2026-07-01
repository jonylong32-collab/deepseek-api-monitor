"""
DeepSeek API 客户端模块
移植自原项目 api_client.py
封装与 DeepSeek 开放平台的 HTTP 通信
"""
from __future__ import annotations
import time
import logging
from typing import Dict, Optional

import requests

from .config_manager import get_config
from .models import BalanceInfo

logger = logging.getLogger(__name__)

BASE_URL = "https://api.deepseek.com"
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2


class DeepSeekAPIError(Exception):
    """API 调用异常，包含对用户友好的中文消息。"""
    def __init__(self, message: str, detail: str = ""):
        self.message = message
        self.detail = detail
        super().__init__(message)


class DeepSeekClient:
    """DeepSeek API 客户端。"""

    def __init__(self, api_key: Optional[str] = None):
        if api_key is None:
            api_key = get_config().api_key
        self._api_key = api_key
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def check_connection(self) -> bool:
        try:
            resp = self._request("GET", "/user/balance")
            data = resp.json()
            return data.get("is_available", False)
        except DeepSeekAPIError:
            raise
        except Exception as e:
            raise DeepSeekAPIError("连接失败，请检查网络", str(e))

    def get_balance(self) -> BalanceInfo:
        resp = self._request("GET", "/user/balance")
        data = resp.json()
        if not data.get("is_available"):
            raise DeepSeekAPIError("账户余额不可用，请检查账户状态")
        infos = data.get("balance_infos", [])
        if not infos:
            raise DeepSeekAPIError("未获取到余额信息")
        info = infos[0]
        result = BalanceInfo(
            total_balance=float(info.get("total_balance", 0)),
            granted_balance=float(info.get("granted_balance", 0)),
            topped_up_balance=float(info.get("topped_up_balance", 0)),
            currency=info.get("currency", "CNY"),
        )
        config = get_config()
        config.record_balance(result.total_balance)
        return result

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{BASE_URL}{path}"
        kwargs.setdefault("timeout", TIMEOUT)
        for attempt in range(MAX_RETRIES):
            try:
                resp = self._session.request(method, url, **kwargs)
                if resp.status_code == 200:
                    return resp
                if resp.status_code == 401:
                    raise DeepSeekAPIError("API Key 无效，请重新设置")
                if resp.status_code == 403:
                    raise DeepSeekAPIError("API Key 权限不足")
                if resp.status_code == 429:
                    if attempt < MAX_RETRIES - 1:
                        retry_after = int(resp.headers.get("Retry-After", RETRY_DELAY * (attempt + 1)))
                        time.sleep(retry_after)
                        continue
                    raise DeepSeekAPIError("请求过于频繁，请稍后重试")
                if resp.status_code >= 500:
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY * (attempt + 1))
                        continue
                    raise DeepSeekAPIError("DeepSeek 服务器异常，请稍后重试")
                raise DeepSeekAPIError(f"请求失败（{resp.status_code}），请稍后重试")
            except requests.ConnectionError:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                raise DeepSeekAPIError("无法连接 DeepSeek 服务器，请检查网络")
            except requests.Timeout:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                raise DeepSeekAPIError("请求超时，请检查网络连接")
        raise DeepSeekAPIError("请求失败次数过多，请稍后重试")
