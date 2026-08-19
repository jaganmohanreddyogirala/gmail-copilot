import React from 'react';
import type { DashboardStats } from '../types/email';

interface MetricsOverviewProps {
  stats: DashboardStats | null;
}

export const MetricsOverview: React.FC<MetricsOverviewProps> = ({ stats }) => {
  const unreadCount = stats?.unread_count ?? 0;
  const pendingApprovalsCount = stats?.pending_approvals_count ?? 0;
  const processedToday = stats?.processed_today ?? 0;

  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-info">
          <span className="metric-label">Unread Emails</span>
          <span className="metric-value">{unreadCount}</span>
        </div>
        <div className="metric-icon-box">📥</div>
      </div>

      <div className="metric-card">
        <div className="metric-info">
          <span className="metric-label">Pending Approvals</span>
          <span className="metric-value" style={{ color: pendingApprovalsCount > 0 ? 'var(--warning-color)' : 'var(--text-main)' }}>
            {pendingApprovalsCount}
          </span>
        </div>
        <div className="metric-icon-box">⚠️</div>
      </div>

      <div className="metric-card">
        <div className="metric-info">
          <span className="metric-label">Drafts Today</span>
          <span className="metric-value">{processedToday}</span>
        </div>
        <div className="metric-icon-box">📝</div>
      </div>

      <div className="metric-card">
        <div className="metric-info">
          <span className="metric-label">System Status</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '1rem', fontWeight: 600, marginTop: '0.35rem', color: 'var(--success-color)' }}>
            <span style={{ fontSize: '0.65rem' }}>●</span> Active
          </span>
        </div>
        <div className="metric-icon-box">⚡</div>
      </div>
    </div>
  );
};
