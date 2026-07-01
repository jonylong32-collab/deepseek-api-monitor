/** TypeScript 类型定义 — 对应后端 Pydantic 模型 */

export interface ModelUsage {
  model: string;
  daily_requests: Record<string, number>;
  daily_tokens: Record<string, number>;
  /** computed: sum of daily_requests values */
  total_requests: number;
  /** computed: sum of daily_tokens values */
  total_tokens: number;
}

export interface UsageDashboardData {
  models: ModelUsage[];
  source: string;
  granularity: string;
  /** computed: sum of all models' total_requests */
  total_requests: number;
  /** computed: sum of all models' total_tokens */
  total_tokens: number;
  /** true when models array is empty */
  is_empty: boolean;
}

export interface BalanceInfo {
  total_balance: number;
  granted_balance: number;
  topped_up_balance: number;
  currency: string;
}

export interface BalanceResponse {
  balance: BalanceInfo;
  daily_spend: Record<string, number>;
}

export interface UsageResponse {
  usage: UsageDashboardData;
  balance: BalanceInfo | null;
  message: string;
}

export interface ConfigResponse {
  has_api_key: boolean;
  has_web_session: boolean;
  refresh_interval: number;
  always_on_top: boolean;
}

export interface ConfigUpdateRequest {
  api_key?: string;
  refresh_interval?: number;
  always_on_top?: boolean;
}

export interface DailySpendPoint {
  date: string;
  amount: number;
}

/** 前端应用状态 */
export interface AppState {
  balance: BalanceInfo | null;
  usage: UsageDashboardData | null;
  dailySpend: DailySpendPoint[];
  config: ConfigResponse | null;
  loading: boolean;
  refreshing: boolean;
  message: string;
  error: string | null;
}
