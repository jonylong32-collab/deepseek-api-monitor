/** 仪表盘主页面 — 用量仪表盘 + 消费柱状图 */
import type { BalanceInfo, UsageDashboardData, DailySpendPoint } from '../types';
import SpendChart from '../components/SpendChart';
import UsageChart from '../components/UsageChart';
import MetricCard from '../components/MetricCard';
import './Dashboard.css';

interface Props {
  balance: BalanceInfo | null;
  usage: UsageDashboardData | null;
  dailySpend: DailySpendPoint[];
  message: string;
  error: string | null;
}

export default function Dashboard({
  balance,
  usage,
  dailySpend,
  message,
  error,
}: Props) {
  const hasData = usage && !usage.is_empty;

  return (
    <div className="dashboard">
      {/* 顶部概览卡片 */}
      <div className="summary-row">
        <MetricCard
          title="账户余额"
          value={balance ? `¥${balance.total_balance.toFixed(2)}` : '—'}
          subtitle={balance ? `${balance.currency}` : '请设置 API Key'}
          accent
        />
        <MetricCard
          title="本月 API 请求"
          value={hasData ? usage!.total_requests.toLocaleString() : '—'}
          subtitle={hasData ? `${usage!.models.length} 个模型` : '无数据'}
        />
        <MetricCard
          title="本月 Tokens"
          value={hasData ? usage!.total_tokens.toLocaleString() : '—'}
          subtitle={hasData ? `来自 ${usage!.models.length} 个模型` : '无数据'}
        />
      </div>

      {/* 图表区域 */}
      <div className="charts-row">
        <div className="chart-card chart-card-wide">
          <div className="chart-header">
            <h3>按模型用量仪表盘</h3>
            {message && <span className="chart-source">{message}</span>}
          </div>
          <div className="chart-body">
            {hasData ? (
              <UsageChart usage={usage!} />
            ) : (
              <div className="chart-placeholder">
                <div className="placeholder-icon">📊</div>
                <p>暂无用量数据</p>
                <p className="placeholder-hint">点击底部「刷新」或「导入」加载数据</p>
              </div>
            )}
          </div>
        </div>

        <div className="chart-card chart-card-narrow">
          <div className="chart-header">
            <h3>每日消费趋势</h3>
          </div>
          <div className="chart-body">
            {balance ? (
              <SpendChart dailySpend={dailySpend} balance={balance} />
            ) : (
              <div className="chart-placeholder">
                <div className="placeholder-icon">💰</div>
                <p>请设置 API Key 后刷新</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="error-bar">
          <span>⚠</span>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
