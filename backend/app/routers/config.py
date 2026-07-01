"""
配置管理 API 路由
"""
import logging
from fastapi import APIRouter, HTTPException
from ..models import ConfigResponse, ConfigUpdateRequest
from ..config_manager import get_config

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/config", response_model=ConfigResponse)
async def get_config_endpoint():
    """获取当前配置状态。"""
    config = get_config()
    return ConfigResponse(
        has_api_key=config.has_api_key,
        has_web_session=config.has_web_session,
        refresh_interval=config.refresh_interval,
        always_on_top=config.always_on_top,
    )


@router.put("/config", response_model=ConfigResponse)
async def update_config(req: ConfigUpdateRequest):
    """更新配置。"""
    config = get_config()
    if req.api_key is not None:
        config.api_key = req.api_key
    if req.refresh_interval is not None:
        config.refresh_interval = req.refresh_interval
    if req.always_on_top is not None:
        config.always_on_top = req.always_on_top
    config.save()
    return ConfigResponse(
        has_api_key=config.has_api_key,
        has_web_session=config.has_web_session,
        refresh_interval=config.refresh_interval,
        always_on_top=config.always_on_top,
    )


@router.post("/config/web-session/clear")
async def clear_web_session():
    """清除网页登录状态。"""
    config = get_config()
    config.clear_web_session()
    return {"success": True}
