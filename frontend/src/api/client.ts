/** API 客户端 — 封装与后端的全部通信 */
import type {
  BalanceResponse,
  UsageResponse,
  ConfigResponse,
  ConfigUpdateRequest,
} from '../types';

const BASE = '';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(detail.detail || `请求失败 (${res.status})`);
  }
  return res.json();
}

export const api = {
  // ── 余额 ──
  getBalance(): Promise<BalanceResponse> {
    return request('/api/balance');
  },

  getBalanceSimple(): Promise<{ total_balance: number | null }> {
    return request('/api/balance/simple');
  },

  // ── 用量 ──
  getUsage(): Promise<UsageResponse> {
    return request('/api/usage');
  },

  refreshUsage(): Promise<UsageResponse> {
    return request('/api/usage/refresh', { method: 'POST' });
  },

  async importUsage(file: File): Promise<UsageResponse> {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${BASE}/api/usage/import`, { method: 'POST', body: form });
    if (!res.ok) {
      const detail = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(detail.detail || '导入失败');
    }
    return res.json();
  },

  exportUsage(): Promise<Blob> {
    return fetch(`${BASE}/api/usage/export`).then((r) => {
      if (!r.ok) throw new Error('导出失败');
      return r.blob();
    });
  },

  // ── 配置 ──
  getConfig(): Promise<ConfigResponse> {
    return request('/api/config');
  },

  updateConfig(data: ConfigUpdateRequest): Promise<ConfigResponse> {
    return request('/api/config', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  clearWebSession(): Promise<{ success: boolean }> {
    return request('/api/config/web-session/clear', { method: 'POST' });
  },
};
