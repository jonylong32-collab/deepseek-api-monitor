"""
数据模型模块 — Pydantic 模型
移植自原项目 usage_data.py
"""
from __future__ import annotations
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, computed_field


class ModelUsage(BaseModel):
    """单个模型的用量汇总。"""
    model: str
    daily_requests: Dict[str, int] = Field(default_factory=dict)
    daily_tokens: Dict[str, int] = Field(default_factory=dict)

    @computed_field
    @property
    def total_requests(self) -> int:
        return sum(self.daily_requests.values())

    @computed_field
    @property
    def total_tokens(self) -> int:
        return sum(self.daily_tokens.values())


class UsageDashboardData(BaseModel):
    """界面显示所需的完整用量数据。"""
    models: List[ModelUsage] = Field(default_factory=list)
    source: str = ""
    granularity: str = "daily"

    @computed_field
    @property
    def total_requests(self) -> int:
        return sum(m.total_requests for m in self.models)

    @computed_field
    @property
    def total_tokens(self) -> int:
        return sum(m.total_tokens for m in self.models)

    @computed_field
    @property
    def is_empty(self) -> bool:
        return not self.models


class BalanceInfo(BaseModel):
    """余额信息。"""
    total_balance: float = 0.0
    granted_balance: float = 0.0
    topped_up_balance: float = 0.0
    currency: str = "CNY"


class BalanceResponse(BaseModel):
    """余额查询响应。"""
    balance: BalanceInfo
    daily_spend: Dict[str, float] = Field(default_factory=dict)


class UsageResponse(BaseModel):
    """用量数据响应。"""
    usage: UsageDashboardData
    balance: Optional[BalanceInfo] = None
    message: str = ""


class ConfigResponse(BaseModel):
    """配置响应。"""
    has_api_key: bool = False
    has_web_session: bool = False
    refresh_interval: int = 300
    always_on_top: bool = False
    window_size: tuple = (980, 650)


class ConfigUpdateRequest(BaseModel):
    """配置更新请求。"""
    api_key: Optional[str] = None
    refresh_interval: Optional[int] = None
    always_on_top: Optional[bool] = None
