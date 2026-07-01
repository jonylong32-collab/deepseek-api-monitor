/** 指标卡片组件 */
interface Props {
  title: string;
  value: string;
  subtitle?: string;
  accent?: boolean;
}

export default function MetricCard({ title, value, subtitle, accent }: Props) {
  return (
    <div className={`metric-card ${accent ? 'accent' : ''}`}>
      <span className="metric-title">{title}</span>
      <span className={`metric-value ${accent ? 'accent-value' : ''}`}>
        {value}
      </span>
      {subtitle && <span className="metric-subtitle">{subtitle}</span>}
    </div>
  );
}
