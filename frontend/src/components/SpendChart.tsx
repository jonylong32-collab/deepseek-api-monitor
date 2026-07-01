/** 每日消费柱状图 (recharts) */
import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from 'recharts';
import type { BalanceInfo, DailySpendPoint } from '../types';

interface Props {
  dailySpend: DailySpendPoint[];
  balance: BalanceInfo;
}

const CHART_COLORS = {
  today: '#7B61FF',
  normal: '#00D4FF',
  grid: '#2A2D3A',
  tick: '#56586A',
  label: '#8D8F9F',
};

export default function SpendChart({ dailySpend, balance }: Props) {
  const today = new Date().toISOString().slice(0, 10);
  const currentMonth = today.slice(0, 7);

  const monthData = useMemo(() => {
    return dailySpend
      .filter((d) => d.date.startsWith(currentMonth))
      .map((d) => ({
        day: String(parseInt(d.date.split('-')[2])),
        amount: d.amount,
        isToday: d.date === today,
      }));
  }, [dailySpend, currentMonth, today]);

  const totalSpend = useMemo(
    () => monthData.reduce((s, d) => s + d.amount, 0),
    [monthData]
  );

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload?.length) {
      return (
        <div style={{
          background: '#1E2030',
          border: '1px solid #3D4055',
          borderRadius: 6,
          padding: '8px 12px',
          fontSize: 12,
          color: '#E8E8F0',
        }}>
          <div>{payload[0].payload.isToday ? '今日' : `${currentMonth}-${payload[0].payload.day}`}</div>
          <div style={{ color: '#00D4FF', fontWeight: 700 }}>
            ¥{payload[0].value.toFixed(4)}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{
        fontSize: 11,
        color: '#56586A',
        marginBottom: 8,
        textAlign: 'center',
      }}>
        本月消费 ¥{totalSpend.toFixed(2)} · 当前余额 ¥{balance.total_balance.toFixed(2)}
      </div>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={monthData} margin={{ top: 4, right: 4, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="" vertical={false} stroke={CHART_COLORS.grid} />
          <XAxis
            dataKey="day"
            tick={{ fill: CHART_COLORS.tick, fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: CHART_COLORS.tick, fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => v >= 100 ? `¥${v.toFixed(0)}` : `¥${v.toFixed(1)}`}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(42,45,58,0.5)' }} />
          <Bar dataKey="amount" radius={[3, 3, 0, 0]} maxBarSize={24}>
            {monthData.map((entry, idx) => (
              <Cell
                key={idx}
                fill={entry.isToday ? CHART_COLORS.today : CHART_COLORS.normal}
                fillOpacity={entry.amount > 0 ? 1 : 0.3}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
