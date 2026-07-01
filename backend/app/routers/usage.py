"""
用量数据 API 路由
"""
from __future__ import annotations
import logging
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from ..models import UsageDashboardData, BalanceInfo, UsageResponse
from ..usage_parser import parse_usage_export_file
from ..config_manager import get_config
from ..api_client import DeepSeekClient, DeepSeekAPIError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/usage", response_model=UsageResponse)
async def get_usage():
    """获取用量数据（优先返回缓存）。"""
    config = get_config()
    cached = config.load_usage_cache()
    if cached:
        usage = UsageDashboardData(**cached)
        return UsageResponse(usage=usage, message="本地缓存")

    # 尝试从 API 获取（如果有 Key）
    if config.has_api_key:
        try:
            client = DeepSeekClient()
            balance = client.get_balance()
        except Exception:
            balance = None

    return UsageResponse(
        usage=UsageDashboardData(),
        message="无数据",
    )


@router.post("/usage/refresh", response_model=UsageResponse)
async def refresh_usage():
    """刷新用量数据（调用 DeepSeek API 查询余额，用量需通过网页/导入）。"""
    config = get_config()
    balance = None
    msg = ""

    if config.has_api_key:
        try:
            client = DeepSeekClient()
            balance = client.get_balance()
            msg = "API 获取成功"
        except DeepSeekAPIError as e:
            msg = f"API 错误: {e.message}"
        except Exception as e:
            msg = f"异常: {e}"

    cached = config.load_usage_cache()
    if cached:
        usage = UsageDashboardData(**cached)
        if not msg:
            msg = "本地缓存"
        return UsageResponse(usage=usage, balance=balance, message=msg)

    return UsageResponse(
        usage=UsageDashboardData(),
        balance=balance,
        message=msg or "无数据",
    )


@router.post("/usage/import", response_model=UsageResponse)
async def import_usage(file: UploadFile = File(...)):
    """导入 DeepSeek 用量页导出的 CSV/ZIP 文件。"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")

    content = await file.read()
    suffix = ""
    if file.filename.lower().endswith(".csv"):
        suffix = ".csv"
        # 写临时文件给解析器
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        try:
            tmp.write(content)
            tmp.close()
            usage = parse_usage_export_file(tmp.name)
        finally:
            os.unlink(tmp.name)
    elif file.filename.lower().endswith(".zip"):
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        try:
            tmp.write(content)
            tmp.close()
            usage = parse_usage_export_file(tmp.name)
        finally:
            os.unlink(tmp.name)
    else:
        raise HTTPException(status_code=400, detail="仅支持 CSV 或 ZIP 文件")

    if usage.is_empty:
        raise HTTPException(status_code=400, detail="未找到有效数据")

    # 保存到缓存
    config = get_config()
    config.save_usage_cache(usage.model_dump())
    return UsageResponse(usage=usage, message="导入成功")


@router.get("/usage/export")
async def export_usage():
    """导出用量数据为 CSV。"""
    config = get_config()
    cached = config.load_usage_cache()
    if not cached:
        raise HTTPException(status_code=404, detail="无数据可导出")

    usage = UsageDashboardData(**cached)
    import csv, io
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["模型", "日期", "请求次数", "Tokens"])
    for m in usage.models:
        dates = set(list(m.daily_requests.keys()) + list(m.daily_tokens.keys()))
        if not dates:
            w.writerow([m.model, "总计", m.total_requests, m.total_tokens])
        else:
            for d in sorted(dates):
                w.writerow([m.model, d, m.daily_requests.get(d, 0), m.daily_tokens.get(d, 0)])

    from fastapi.responses import PlainTextResponse
    from datetime import date
    filename = f"DeepSeek用量_{date.today().isoformat()}.csv"
    return PlainTextResponse(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
