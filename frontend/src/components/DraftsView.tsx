import React from 'react';
import type { ProcessedEmailResponse } from '../types/email';

interface DraftsViewProps {
  items: ProcessedEmailResponse[];
  onSelect: (item: ProcessedEmailResponse) => void;
}

export const DraftsView: React.FC<DraftsViewProps> = ({ items, onSelect }) => {
  const draftItems = items.filter((item) => !!item.draft);

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            <span>📝</span> Generated Drafts ({draftItems.length})
          </h2>
          <p className="card-subtitle">AI-generated response drafts prepared for Gmail</p>
        </div>
      </div>

      {draftItems.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">✍️</div>
          <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-main)' }}>No drafts created yet</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Process unread emails requiring replies to generate automated drafts.
          </div>
        </div>
      ) : (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Subject</th>
                <th>Recipient</th>
                <th>Risk Level</th>
                <th>Draft Status</th>
                <th>Generated Reply Preview</th>
              </tr>
            </thead>
            <tbody>
              {draftItems.map((item) => {
                const draft = item.draft!;
                const risk = item.analysis?.risk_level || 'Low';

                const riskBadge = risk.toLowerCase().includes('high')
                  ? 'badge-high'
                  : risk.toLowerCase().includes('medium')
                  ? 'badge-warning'
                  : 'badge-low';

                const statusBadge =
                  draft.status === 'sent'
                    ? 'badge-gmail'
                    : draft.status === 'created'
                    ? 'badge-gmail'
                    : 'badge-warning';

                return (
                  <tr key={item.email.id} onClick={() => onSelect(item)}>
                    <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                      {draft.subject || item.email.subject}
                    </td>
                    <td style={{ color: 'var(--text-secondary)' }}>{draft.recipient}</td>
                    <td>
                      <span className={`badge ${riskBadge}`}>{risk.split(' - ')[0]}</span>
                    </td>
                    <td>
                      <span className={`badge ${statusBadge}`}>
                        {draft.status === 'sent' ? 'Sent' : draft.status === 'created' ? 'Saved to Gmail' : 'Pending Review'}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {draft.body}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
