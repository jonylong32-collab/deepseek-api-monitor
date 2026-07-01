/** 按模型用量仪表盘 (recharts) — 每个模型一行：左侧请求曲线 + 右侧 Tokens 柱状图 */
import { useMemo } from 'react';
import {
  LineChart,
  BarChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from 'recharts';
import type { UsageDashboardData } from '../types';

interface Props {
  usage: UsageDashboardData;
}

const ACCENT = '#00D4FF';
const GRID = '#2A2D3A';
const TICK = '#56586A';
const TITLE = '#E8E8F0';
const FILL = 'rgba(0, 212, 255, 0.15)';

export default function UsageChart({ usage }: Props) {
  const today = new Date();
  const currentMonth = today.getFullYear() + '-' + String(today.getMonth() + 1).padStart(2, '0');
  const daysInMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();

  // 生成当月每日的日期列表
  const dayLabels = Array.from({ length: daysInMonth }, (_, i) => String(i + 1));

  const chartDataList = useMemo(() => {
    return usage.models.map((model) => {
      const requests = dayLabels.map((d) => {
        const dateKey = `${currentMonth}-${d.padStart(2, '0')}`;
        return model.daily_requests[dateKey] || 0;
      });
      const tokens = dayLabels.map((d) => {
        const dateKey = `${currentMonth}-${d.padStart(2, '0')}`;
        return model.daily_tokens[dateKey] || 0;
      });
      return {
        model: model.model,
        totalRequests: model.total_requests,
        totalTokens: model.total_tokens,
        requests,
        tokens,
      };
    });
  }, [usage, currentMonth, dayLabels]);

  if (chartDataList.length === 0) {
    return (
      <div className="chart-placeholder">
        <p>暂无模型数据</p>
      </div>
    );
  }

  return (
    <div style={{ height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{
        fontSize: 11,
        color: TICK,
        textAlign: 'center',
        paddingBottom: 4,
        borderBottom: `1px solid ${GRID}`,
      }}>
        本月用量 API 请求 {usage.total_requests.toLocaleString()} · Tokens {usage.total_tokens.toLocaleString()}
        {usage.source && ` · ${usage.source}`}
      </div>
      {chartDataList.map((item) => {
        const chartData = dayLabels.map((day, i) => ({
          day,
          requests: item.requests[i],
          tokens: item.tokens[i],
        }));

        return (
          <div key={item.model} style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 8,
            background: '#14161F',
            borderRadius: 8,
            border: `1px solid ${GRID}`,
            padding: 8,
          }}>
            {/* 左侧：请求曲线 */}
            <div style={{ height: 80 }}>
              <div style={{ fontSize: 10, color: TITLE, fontWeight: 600, marginBottom: 2 }}>
                {item.model} — API 请求次数 {item.totalRequests.toLocaleString()}
              </div>
              <ResponsiveContainer width="100%" height={60}>
                <LineChart data={chartData} margin={{ top: 2, right: 2, bottom: 2, left: -20 }}>
                  <CartesianGrid strokeDasharray="" vertical={false} stroke={GRID} />
                  <XAxis dataKey="day" hide />
                  <YAxis hide domain={[0, 'auto']} />
                  <Line
                    type="monotone"
                    dataKey="requests"
                    stroke={ACCENT}
                    strokeWidth={1.5}
                    dot={false}
                    fill={FILL}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* 右侧：Tokens 柱状图 */}
            <div style={{ height: 80 }}>
              <div style={{ fontSize: 10, color: TITLE, fontWeight: 600, marginBottom: 2 }}>
                Tokens {item.totalTokens.toLocaleString()}
              </div>
              <ResponsiveContainer width="100%" height={60}>
                <BarChart data={chartData} margin={{ top: 2, right: 2, bottom: 2, left: -20 }}>
                  <CartesianGrid strokeDasharray="" vertical={false} stroke={GRID} />
                  <XAxis dataKey="day" hide />
                  <YAxis hide domain={[0, 'auto']} />
                  <Bar dataKey="tokens" radius={[1, 1, 0, 0]} maxBarSize={12}>
                    {chartData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.tokens > 0 ? ACCENT : 'transparent'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        );
      })}
    </div>
  );
}
