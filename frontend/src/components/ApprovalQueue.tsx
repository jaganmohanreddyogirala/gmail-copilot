import React from 'react';
import type { ProcessedEmailResponse, DraftReply } from '../types/email';

interface ApprovalQueueProps {
  items: ProcessedEmailResponse[];
  onApprove?: (draft: DraftReply) => void;
  onSelect?: (item: ProcessedEmailResponse) => void;
  onViewAll?: () => void;
}

export const ApprovalQueue: React.FC<ApprovalQueueProps> = ({
  items,
  onApprove,
  onSelect,
  onViewAll,
}) => {
  // Filter items requiring human approval
  const pendingApprovals = items.filter(
    (item) => item.analysis?.requires_human_approval && item.draft && item.draft.status !== 'approved' && item.draft.status !== 'created'
  );

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            <span>⚠️</span> Approval Queue
          </h2>
          <p className="card-subtitle">Emails flagged for security or high-risk human review</p>
        </div>
        {onViewAll && pendingApprovals.length > 0 && (
          <button className="btn btn-secondary btn-sm" onClick={onViewAll}>
            View all ({pendingApprovals.length})
          </button>
        )}
      </div>

      {pendingApprovals.length === 0 ? (
        <div className="empty-state" style={{ padding: '2rem 1rem' }}>
          <div className="empty-icon">✓</div>
          <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-main)' }}>No pending approvals</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            All processed emails passed safety checks cleanly.
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {pendingApprovals.map((item) => {
            const riskLevel = item.analysis?.risk_level || 'Medium';
            const riskBadgeClass = riskLevel.toLowerCase().includes('high')
              ? 'badge-high'
              : riskLevel.toLowerCase().includes('medium')
              ? 'badge-warning'
              : 'badge-low';

            return (
              <div
                key={item.email.id}
                style={{
                  background: 'var(--bg-subtle)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '1rem 1.1rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '1rem',
                  cursor: onSelect ? 'pointer' : 'default',
                  transition: 'background 0.15s ease',
                }}
                onClick={() => onSelect && onSelect(item)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', minWidth: 0 }}>
                  <span style={{ fontSize: '1.1rem', flexShrink: 0 }}>⚠️</span>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {item.email.subject}
                    </div>
                    <div style={{ fontSize: '0.775rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
                      {item.email.sender}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexShrink: 0 }}>
                  <span className={`badge ${riskBadgeClass}`}>{riskLevel}</span>
                  {item.draft && onApprove && (
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onApprove(item.draft!);
                      }}
                    >
                      Approve & Save
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
