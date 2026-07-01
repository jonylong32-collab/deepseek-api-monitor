"""
用量数据解析模块
移植自原项目 usage_data.py
- CSV/ZIP 文件解析
- 多语言字段映射
- 明细记录按模型+日期分组汇总
"""
from __future__ import annotations
import csv
import io
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .models import ModelUsage, UsageDashboardData

DATE_FIELDS = ("date", "day", "created_at", "created", "timestamp", "time",
               "日期", "统计日期", "请求日期")
MODEL_FIELDS = ("model", "model_name", "model_id", "模型", "模型名称", "Model")
REQUEST_FIELDS = ("request_count", "requests", "api_requests", "n_requests",
                  "count", "API 请求次数", "请求次数", "请求数")
TOKEN_TOTAL_FIELDS = ("total_tokens", "tokens", "token_count", "Token",
                      "Tokens", "总 Tokens", "总Token数")
PROMPT_TOKEN_FIELDS = ("prompt_tokens", "input_tokens", "输入 Tokens", "输入Token数")
COMPLETION_TOKEN_FIELDS = ("completion_tokens", "output_tokens", "输出 Tokens", "输出Token数")
CACHED_TOKEN_FIELDS = ("cached_tokens", "cache_tokens", "缓存 Tokens", "缓存Token数")
REASONING_TOKEN_FIELDS = ("reasoning_tokens", "reasoning_output_tokens", "推理 Tokens", "推理Token数")


def normalize_usage_records(records: Iterable[Dict[str, Any]], source: str = "") -> UsageDashboardData:
    """把明细记录整理成按模型分组的统计数据。"""
    grouped: Dict[str, Dict[str, Dict[str, int]]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        model = _first_text(record, MODEL_FIELDS)
        day = _normalize_date(_first_value(record, DATE_FIELDS))
        if not model or not day:
            continue
        req_cnt = _first_int(record, REQUEST_FIELDS, default=0)
        tok_cnt = _extract_token_count(record)
        if req_cnt == 0 and tok_cnt == 0:
            continue
        bucket = grouped.setdefault(model, {"requests": {}, "tokens": {}})
        bucket["requests"][day] = bucket["requests"].get(day, 0) + req_cnt
        bucket["tokens"][day] = bucket["tokens"].get(day, 0) + tok_cnt

    models = [
        ModelUsage(
            model=model,
            daily_requests=values["requests"],
            daily_tokens=values["tokens"],
        )
        for model, values in grouped.items()
    ]
    models.sort(key=lambda m: (-m.total_tokens, -m.total_requests, m.model))
    return UsageDashboardData(models=models, source=source)


def parse_usage_csv_text(text: str, source: str = "CSV") -> UsageDashboardData:
    text = text.lstrip("\ufeff")
    reader = csv.DictReader(io.StringIO(text))
    return normalize_usage_records(reader, source=source)


def parse_usage_export_file(file_path: str | Path) -> UsageDashboardData:
    path = Path(file_path)
    records: List[Dict[str, Any]] = []
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if not name.lower().endswith(".csv"):
                    continue
                text = _decode_bytes(archive.read(name))
                reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")))
                records.extend(reader)
        return normalize_usage_records(records, source=f"导入：{path.name}")
    text = _decode_bytes(path.read_bytes())
    return parse_usage_csv_text(text, source=f"导入：{path.name}")


def extract_usage_records(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("data", "usage", "items", "records", "result"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = extract_usage_records(value)
            if nested:
                return nested
    return []


def _decode_bytes(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _first_text(record: Dict, fields: Iterable[str]) -> str:
    val = _first_value(record, fields)
    return str(val).strip() if val else ""


def _first_int(record: Dict, fields: Iterable[str], default: int = 0) -> int:
    val = _first_value(record, fields)
    return _to_int(val) if val is not None else default


def _first_value(record: Dict, fields: Iterable[str]) -> Optional[Any]:
    for field in fields:
        if field in record and record[field] not in (None, ""):
            return record[field]
    usage = record.get("usage")
    if isinstance(usage, dict):
        for field in fields:
            if field in usage and usage[field] not in (None, ""):
                return usage[field]
    return None


def _extract_token_count(record: Dict) -> int:
    total = _first_value(record, TOKEN_TOTAL_FIELDS)
    if total is not None:
        return _to_int(total)
    groups = (PROMPT_TOKEN_FIELDS, COMPLETION_TOKEN_FIELDS,
              CACHED_TOKEN_FIELDS, REASONING_TOKEN_FIELDS)
    return sum(_first_int(record, f, default=0) for f in groups)


def _normalize_date(value: Any) -> str:
    if value is None:
        return ""
    from datetime import datetime, date as dt_date
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, dt_date):
        return value.isoformat()
    text = str(value).strip()
    if not text:
        return ""
    if text.isdigit() and len(text) >= 10:
        try:
            return datetime.fromtimestamp(int(text[:10])).date().isoformat()
        except (OSError, ValueError):
            return ""
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    for fmt in ("%Y/%m/%d", "%Y.%m.%d", "%Y年%m月%d日"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def _to_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().replace(",", "").replace("，", "")
    if not text:
        return 0
    try:
        return int(float(text))
    except ValueError:
        return 0
