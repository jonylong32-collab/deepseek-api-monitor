/** 设置弹窗 */
import { useState } from 'react';
import type { ConfigResponse } from '../types';
import './SettingsDialog.css';

interface Props {
  config: ConfigResponse | null;
  onSave: (data: Record<string, any>) => Promise<void>;
  onClose: () => void;
}

export default function SettingsDialog({ config, onSave, onClose }: Props) {
  const [apiKey, setApiKey] = useState('');
  const [interval, setInterval] = useState(config?.refresh_interval ?? 300);
  const [alwaysOnTop, setAlwaysOnTop] = useState(config?.always_on_top ?? false);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      const data: Record<string, any> = {};
      if (apiKey) data.api_key = apiKey;
      data.refresh_interval = interval;
      data.always_on_top = alwaysOnTop;
      await onSave(data);
      onClose();
    } catch (e) {
      // error handled by parent
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="dialog-overlay" onClick={onClose}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <h2 className="dialog-title">设置</h2>

        <div className="dialog-body">
          {/* API Key */}
          <div className="field">
            <label className="field-label">DeepSeek API Key</label>
            <input
              className="field-input"
              type="password"
              placeholder="sk-xxxxxxxxxxxxxxxx"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
            />
            <span className="field-hint">
              {config?.has_api_key ? '已配置' : '未配置'} ·
              用于查询余额，加密本地存储
            </span>
          </div>

          {/* 刷新间隔 */}
          <div className="field">
            <label className="field-label">自动刷新间隔（秒）</label>
            <input
              className="field-input"
              type="number"
              min={30}
              max={3600}
              value={interval}
              onChange={(e) => setInterval(Number(e.target.value))}
            />
            <span className="field-hint">范围 30–3600 秒（{Math.round(interval / 60)} 分钟）</span>
          </div>

          {/* 置顶 */}
          <div className="field field-row">
            <label className="field-label">窗口置顶</label>
            <label className="toggle">
              <input
                type="checkbox"
                checked={alwaysOnTop}
                onChange={(e) => setAlwaysOnTop(e.target.checked)}
              />
              <span className="toggle-slider" />
            </label>
          </div>
        </div>

        <div className="dialog-footer">
          <button className="btn btn-secondary" onClick={onClose}>取消</button>
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  );
}
