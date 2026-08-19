import React from 'react';
import type { ProcessedEmailResponse } from '../types/email';

interface RecentActivityProps {
  items: ProcessedEmailResponse[];
}

export const RecentActivity: React.FC<RecentActivityProps> = ({ items }) => {
  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <span>⚡</span> Recent Activity
        </h2>
      </div>

      {items.length === 0 ? (
        <div className="empty-state" style={{ padding: '2rem 1rem' }}>
          <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)' }}>No recent email activity recorded.</div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {items.slice(0, 5).map((item) => {
            const hasDraft = !!item.draft;
            const requiresApproval = item.analysis?.requires_human_approval;

            let eventTitle = 'Email Processed';
            let icon = '📩';
            let badgeStyle = 'badge-low';

            if (requiresApproval) {
              eventTitle = 'Moved to Approval Queue';
              icon = '⚠️';
              badgeStyle = 'badge-high';
            } else if (hasDraft) {
              eventTitle = item.draft?.status === 'sent' ? 'Email Direct Sent' : 'Gmail Draft Created';
              icon = '📝';
              badgeStyle = 'badge-gmail';
            }

            return (
              <div
                key={item.email.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',

                  padding: '0.65rem 0',
                  borderBottom: '1px solid var(--border-subtle)',
                  fontSize: '0.85rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', minWidth: 0 }}>
                  <span style={{ fontSize: '1rem', flexShrink: 0 }}>{icon}</span>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontWeight: 600, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {eventTitle}
                    </div>
                    <div style={{ fontSize: '0.775rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {item.email.subject}
                    </div>
                  </div>
                </div>

                <span className={`badge ${badgeStyle}`} style={{ flexShrink: 0, fontSize: '0.7rem' }}>
                  {item.analysis?.intent || 'Processed'}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
