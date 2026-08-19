import React from 'react';
import type { DashboardStats } from '../types/email';

interface TopbarProps {
  stats: DashboardStats | null;
  activeTab: string;
  onRefresh: () => void;
  onRunBatch: () => void;
  loading: boolean;
  onToggleMobile: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  stats,
  activeTab,
  onRefresh,
  onRunBatch,
  loading,
  onToggleMobile,
}) => {
  const getTabTitle = (tab: string) => {
    switch (tab) {
      case 'home': return 'Home';
      case 'inbox': return 'Inbox';
      case 'approvals': return 'Approval Queue';
      case 'drafts': return 'Generated Drafts';
      case 'traces': return 'Execution Traces';
      case 'style': return 'Writing Style';
      case 'eval': return 'Evaluation Benchmark';
      case 'settings': return 'Settings';
      default: return 'Dashboard';
    }
  };

  const isConnected = stats?.authenticated ?? true;

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="mobile-toggle" onClick={onToggleMobile} aria-label="Toggle navigation menu">
          ☰
        </button>
        <h1 className="page-title">{getTabTitle(activeTab)}</h1>
      </div>

      <div className="topbar-right">
        <span className={`badge ${isConnected ? 'badge-gmail' : 'badge-low'}`}>
          <span style={{ fontSize: '0.65rem' }}>●</span>
          {isConnected ? 'Connected to Gmail' : 'Offline'}
        </span>

        <button className="btn-icon" onClick={onRefresh} title="Refresh data">
          🔄
        </button>

        <button className="btn btn-primary" onClick={onRunBatch} disabled={loading}>
          {loading ? 'Processing...' : 'Process Unread Inbox'}
        </button>

        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '9999px',
          background: 'var(--bg-subtle)',
          border: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',

          fontSize: '0.85rem',
          fontWeight: 600,
          color: 'var(--text-main)',
        }}>
          U
        </div>
      </div>
    </header>
  );
};
