"""
余额相关 API 路由
"""
import logging
from fastapi import APIRouter, HTTPException
from ..models import BalanceInfo, BalanceResponse
from ..api_client import DeepSeekClient, DeepSeekAPIError
from ..config_manager import get_config

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/balance", response_model=BalanceResponse)
async def get_balance():
    """获取账户余额及每日消费趋势。"""
    config = get_config()
    if not config.has_api_key:
        raise HTTPException(status_code=400, detail="请先设置 API Key")

    try:
        client = DeepSeekClient()
        balance = client.get_balance()
        daily_spend = config.get_daily_spend()
        return BalanceResponse(
            balance=balance,
            daily_spend=daily_spend,
        )
    except DeepSeekAPIError as e:
        raise HTTPException(status_code=502, detail=e.message)
    except Exception as e:
        logger.exception("余额查询失败")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance/simple")
async def get_balance_simple():
    """仅返回余额数值（轻量接口）。"""
    config = get_config()
    if not config.has_api_key:
        return {"total_balance": None}

    try:
        client = DeepSeekClient()
        balance = client.get_balance()
        return {"total_balance": balance.total_balance, "currency": balance.currency}
    except Exception as e:
        logger.warning(f"简单余额查询失败: {e}")
        return {"total_balance": None}
