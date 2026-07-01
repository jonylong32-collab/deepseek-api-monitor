/** 应用状态 Hook */
import { useState, useCallback, useRef } from 'react';
import type { AppState, DailySpendPoint } from '../types';
import { api } from '../api/client';

const initialState: AppState = {
  balance: null,
  usage: null,
  dailySpend: [],
  config: null,
  loading: true,
  refreshing: false,
  message: '',
  error: null,
};

export function useAppState() {
  const [state, setState] = useState<AppState>(initialState);
  const intervalRef = useRef<number | null>(null);

  /** 初始化：加载配置、缓存数据和余额 */
  const init = useCallback(async () => {
    try {
      const config = await api.getConfig();
      const usageResp = await api.getUsage().catch(() => null);

      // 如果有 API Key，同时拉取余额
      let balance = null;
      let dailySpend: DailySpendPoint[] = [];
      if (config.has_api_key) {
        try {
          const balanceResp = await api.getBalance();
          balance = balanceResp.balance;
          dailySpend = balanceResp.daily_spend
            ? Object.entries(balanceResp.daily_spend).map(([date, amount]) => ({ date, amount }))
            : [];
        } catch (e) {
          // 余额拉取失败不影响启动
        }
      }

      setState((prev) => ({
        ...prev,
        config,
        balance,
        dailySpend,
        usage: usageResp?.usage ?? null,
        message: usageResp?.message ?? '',
        loading: false,
      }));
      return config;
    } catch (e: any) {
      setState((prev) => ({ ...prev, loading: false, error: e.message }));
      return null;
    }
  }, []);

  /** 刷新余额 + 用量 */
  const refresh = useCallback(async () => {
    setState((prev) => ({ ...prev, refreshing: true, error: null }));
    try {
      const [balanceResp, usageResp] = await Promise.all([
        api.getBalance().catch(() => null),
        api.refreshUsage().catch(() => null),
      ]);

      const dailySpend: DailySpendPoint[] = balanceResp?.daily_spend
        ? Object.entries(balanceResp.daily_spend).map(([date, amount]) => ({
            date,
            amount,
          }))
        : [];

      setState((prev) => ({
        ...prev,
        balance: balanceResp?.balance ?? prev.balance,
        dailySpend,
        usage: usageResp?.usage ?? prev.usage,
        message: usageResp?.message ?? '',
        refreshing: false,
        error: null,
      }));
    } catch (e: any) {
      setState((prev) => ({ ...prev, refreshing: false, error: e.message }));
    }
  }, []);

  /** 导入文件 */
  const importFile = useCallback(async (file: File) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const resp = await api.importUsage(file);
      setState((prev) => ({
        ...prev,
        usage: resp.usage,
        loading: false,
        message: resp.message,
      }));
      return resp;
    } catch (e: any) {
      setState((prev) => ({ ...prev, loading: false, error: e.message }));
      throw e;
    }
  }, []);

  /** 保存配置 */
  const saveConfig = useCallback(async (data: Record<string, any>) => {
    const config = await api.updateConfig(data);
    setState((prev) => ({ ...prev, config }));
    return config;
  }, []);

  /** 设置自动刷新 */
  const startAutoRefresh = useCallback(
    (intervalSeconds: number) => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      intervalRef.current = window.setInterval(() => {
        refresh();
      }, intervalSeconds * 1000);
    },
    [refresh]
  );

  const stopAutoRefresh = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  return {
    state,
    init,
    refresh,
    importFile,
    saveConfig,
    startAutoRefresh,
    stopAutoRefresh,
  };
}
