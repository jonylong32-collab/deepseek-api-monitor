# 验证后端可导入
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

# 测试关键模块导入
from app.models import ModelUsage, UsageDashboardData, BalanceInfo
from app.config_manager import ConfigManager, get_config
from app.usage_parser import normalize_usage_records, parse_usage_csv_text
from app.api_client import DeepSeekClient
print("OK: 所有后端模块导入成功")

# 测试模型
mu = ModelUsage(model="deepseek-chat", daily_requests={"2026-07-01": 10}, daily_tokens={"2026-07-01": 500})
ud = UsageDashboardData(models=[mu])
assert ud.total_requests == 10
assert ud.total_tokens == 500
print("OK: 数据模型验证通过")

# 测试 config
from tempfile import mkdtemp
tmpdir = mkdtemp()
cfg = ConfigManager(data_dir=tmpdir)
assert cfg.has_api_key == False
cfg.api_key = "sk-test"
assert cfg.has_api_key == True
cfg.save()
cfg2 = ConfigManager(data_dir=tmpdir)
assert cfg2.has_api_key == True
print("OK: 配置管理验证通过 (Fernet加密)")

# 测试 CSV 解析
csv_text = "模型,日期,请求次数,Tokens\ndeepseek-chat,2026-07-01,100,5000\ndeepseek-r1,2026-07-01,50,3000"
result = parse_usage_csv_text(csv_text)
assert not result.is_empty
assert len(result.models) == 2
assert result.total_requests == 150
assert result.total_tokens == 8000
print("OK: CSV 解析验证通过")

# 测试 API 客户端创建
client = DeepSeekClient(api_key="sk-test-key")
print("OK: API 客户端创建成功")

import shutil
shutil.rmtree(tmpdir, ignore_errors=True)
print("ALL PASS: 后端全部验证通过")
