import React, { useState } from 'react';
import type { ProcessedEmailResponse } from '../types/email';

interface EmailListProps {
  emails: ProcessedEmailResponse[];
  onSelect: (email: ProcessedEmailResponse) => void;
  loading?: boolean;
}

export const EmailList: React.FC<EmailListProps> = ({ emails, onSelect, loading }) => {
  const [filter, setFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filterTabs = [
    { id: 'all', label: 'All' },
    { id: 'unread', label: 'Unread' },
    { id: 'high_risk', label: 'High Risk' },
    { id: 'action', label: 'Action Required' },
    { id: 'decision', label: 'Decision Needed' },
    { id: 'fyi', label: 'FYI' },
  ];

  const filteredEmails = emails.filter((item) => {
    // Search query filter
    const matchesSearch =
      searchQuery.trim() === '' ||
      item.email.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.email.sender.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.email.body.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    if (filter === 'all') return true;
    if (filter === 'unread') return item.email.is_unread;
    if (filter === 'high_risk') return item.analysis?.risk_level?.toLowerCase().includes('high');
    if (filter === 'action') return item.analysis?.intent?.toLowerCase().includes('action');
    if (filter === 'decision') return item.analysis?.intent?.toLowerCase().includes('decision');
    if (filter === 'fyi') return item.analysis?.intent?.toLowerCase().includes('fyi') || item.analysis?.intent?.toLowerCase().includes('informational');

    return true;
  });

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">
            <span>📥</span> Processed Inbox ({filteredEmails.length})
          </h2>
          <p className="card-subtitle">Real-time parsed & classified email messages</p>
        </div>
      </div>

      {/* Filter Tabs & Search Bar */}
      <div className="filter-bar">
        <div className="filter-tabs">
          {filterTabs.map((t) => (
            <button
              key={t.id}
              className={`filter-tab ${filter === t.id ? 'active' : ''}`}
              onClick={() => setFilter(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="search-input-box">
          <span>🔍</span>
          <input
            type="text"
            placeholder="Search emails"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button
              style={{ border: 'none', background: 'transparent', cursor: 'pointer', color: 'var(--text-muted)' }}
              onClick={() => setSearchQuery('')}
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Email List Data Table */}
      {loading ? (
        <div className="empty-state">
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Processing unread emails...</div>
        </div>
      ) : filteredEmails.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-main)' }}>No emails found</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            {searchQuery ? 'Try adjusting your search criteria.' : 'Process unread emails to populate your inbox.'}
          </div>
        </div>
      ) : (
        <div className="data-table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Sender</th>
                <th>Subject & Snippet</th>
                <th>Priority</th>
                <th>Intent</th>
                <th>Risk</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredEmails.map((item) => {
                const priority = item.analysis?.priority || 'P2 - Medium';
                const intent = item.analysis?.intent || 'FYI';
                const risk = item.analysis?.risk_level || 'Low';

                const riskBadge = risk.toLowerCase().includes('high')
                  ? 'badge-high'
                  : risk.toLowerCase().includes('medium')
                  ? 'badge-warning'
                  : 'badge-low';

                const priorityBadge = priority.includes('P0')
                  ? 'badge-high'
                  : priority.includes('P1')
                  ? 'badge-warning'
                  : 'badge-low';

                return (
                  <tr key={item.email.id} onClick={() => onSelect(item)}>
                    <td style={{ fontWeight: 600, whiteSpace: 'nowrap', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {item.email.sender}
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>{item.email.subject}</div>
                      <div style={{ fontSize: '0.775rem', color: 'var(--text-secondary)', marginTop: '0.15rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '380px' }}>
                        {item.email.snippet || item.email.body.substring(0, 90)}
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${priorityBadge}`}>{priority.split(' - ')[0]}</span>
                    </td>
                    <td>
                      <span className="badge badge-accent">{intent}</span>
                    </td>
                    <td>
                      <span className={`badge ${riskBadge}`}>{risk.split(' - ')[0]}</span>
                    </td>
                    <td>
                      <span className={`badge ${item.draft ? (item.draft.status === 'sent' ? 'badge-gmail' : 'badge-gmail') : 'badge-low'}`}>
                        {item.draft ? (item.draft.status === 'sent' ? 'Sent' : 'Draft Created') : 'Processed'}
                      </span>
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
