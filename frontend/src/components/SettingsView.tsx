import React, { useState } from 'react';
import type { DashboardStats } from '../types/email';

interface SettingsViewProps {
  stats: DashboardStats | null;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ stats }) => {
  const [autoSend, setAutoSend] = useState<boolean>(true);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '800px', margin: '0 auto' }}>
      {/* Gmail Connection Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <span>📧</span> Gmail Connection Status
            </h2>
            <p className="card-subtitle">Google OAuth 2.0 PKCE authentication credentials</p>
          </div>
          <span className="badge badge-gmail">
            <span style={{ fontSize: '0.65rem' }}>●</span> {stats?.authenticated ? 'Connected' : 'Active'}
          </span>

        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
            <span style={{ color: 'var(--text-secondary)' }}>OAuth Scopes</span>
            <span style={{ fontWeight: 500 }}>readonly, compose, modify</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Token Status</span>
            <span style={{ fontWeight: 500, color: 'var(--success-color)' }}>Auto-Refreshed & Valid</span>
          </div>
        </div>
      </div>

      {/* Agent Preferences Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <span>⚙️</span> Agent Preferences
            </h2>
            <p className="card-subtitle">Configure automated email actions</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem 0' }}>
          <div>
            <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)' }}>Auto-Send Low Risk Replies</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
              Directly send replies via Gmail API for verified low-risk emails (`AUTO_SEND_LOW_RISK_REPLIES=true`)
            </div>
          </div>
          <input
            type="checkbox"
            checked={autoSend}
            onChange={(e) => setAutoSend(e.target.checked)}
            style={{ width: '18px', height: '18px', cursor: 'pointer' }}
          />
        </div>
      </div>

      {/* Security & Secrets Card */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <span>🛡️</span> Security & Secrets Overview
            </h2>
            <p className="card-subtitle">Secrets are stored securely in environment variables</p>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
            <span style={{ color: 'var(--text-secondary)' }}>API Secret Key</span>
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '0.8rem' }}>copilot-prod-secret-***</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border-subtle)' }}>
            <span style={{ color: 'var(--text-secondary)' }}>OpenAI API Key</span>
            <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '0.8rem' }}>sk-proj-***</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.6rem 0' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Rate Limiting</span>
            <span className="badge badge-accent">Active (Sliding Window)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
