import { useEffect, useCallback } from 'react';
import { useAppState } from './hooks/useAppState';
import { api } from './api/client';
import Dashboard from './pages/Dashboard';
import SettingsDialog from './components/SettingsDialog';
import Toast from './components/Toast';
import './App.css';

function App() {
  const { state, init, refresh, importFile, saveConfig, startAutoRefresh } = useAppState();
  const [showSettings, setShowSettings] = React.useState(false);
  const [toast, setToast] = React.useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  useEffect(() => {
    init().then((cfg) => {
      if (cfg) startAutoRefresh(cfg.refresh_interval);
    });
  }, [init, startAutoRefresh]);

  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  }, []);

  const handleExport = useCallback(async () => {
    try {
      const blob = await api.exportUsage();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `DeepSeek用量_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('导出成功', 'success');
    } catch (e: any) {
      showToast(e.message, 'error');
    }
  }, [showToast]);

  const handleImport = useCallback(async () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv,.zip';
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;
      try {
        await importFile(file);
        showToast('导入成功', 'success');
      } catch (e: any) {
        showToast(e.message, 'error');
      }
    };
    input.click();
  }, [importFile, showToast]);

  const handleSaveSettings = useCallback(async (data: Record<string, any>) => {
    await saveConfig(data);
    showToast('设置已保存', 'success');
  }, [saveConfig, showToast]);

  if (state.loading) {
    return (
      <div className="app-loading">
        <div className="loading-spinner" />
        <span>加载中...</span>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <div className="logo-dot">
            <div className="logo-inner" />
          </div>
          <h1 className="app-title">DeepSeek 用量监控</h1>
        </div>
        <div className="header-right">
          <span className="pill-badge time-pill">
            {new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
          </span>
          <span className={`pill-badge status-pill ${state.error ? 'status-error' : ''}`}>
            {state.error ? '错误' : '运行中'}
          </span>
        </div>
      </header>

      <main className="app-main">
        <Dashboard
          balance={state.balance}
          usage={state.usage}
          dailySpend={state.dailySpend}
          message={state.message}
          error={state.error}
        />
      </main>

      <footer className="app-footer">
        <div className="footer-metrics" id="metrics">
          {state.balance && (
            <span className="metric-badge neon-pulse">
              余额 ¥{state.balance.total_balance.toFixed(2)}
            </span>
          )}
          {state.usage && !state.usage.is_empty && (
            <>
              <span className="metric-badge">
                请求 {state.usage.total_requests.toLocaleString()}
              </span>
              <span className="metric-badge">
                Tokens {state.usage.total_tokens.toLocaleString()}
              </span>
              <span className="metric-badge">
                模型 {state.usage.models.length}
              </span>
            </>
          )}
        </div>
        <div className="footer-actions">
          <button className="btn btn-primary" onClick={refresh} disabled={state.refreshing}>
            {state.refreshing ? '⟳' : '刷新'}
          </button>
          <button className="btn btn-secondary" onClick={() => setShowSettings(true)}>
            设置
          </button>
          <button className="btn btn-secondary" onClick={handleImport}>
            导入
          </button>
          <button className="btn btn-secondary" onClick={handleExport}>
            导出
          </button>
        </div>
      </footer>

      {showSettings && (
        <SettingsDialog
          config={state.config}
          onSave={handleSaveSettings}
          onClose={() => setShowSettings(false)}
        />
      )}

      {toast && <Toast message={toast.message} type={toast.type} />}
    </div>
  );
}

import React from 'react';
export default App;
