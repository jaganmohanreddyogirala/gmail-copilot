import React from 'react';
import type { ProcessedEmailResponse } from '../types/email';

interface EmailDetailModalProps {
  item: ProcessedEmailResponse | null;
  onClose: () => void;
}

export const EmailDetailModal: React.FC<EmailDetailModalProps> = ({ item, onClose }) => {
  if (!item) return null;

  const { email, analysis, draft, mcp_context } = item;

  const riskLevel = analysis?.risk_level || 'Low';
  const riskBadge = riskLevel.toLowerCase().includes('high')
    ? 'badge-high'
    : riskLevel.toLowerCase().includes('medium')
    ? 'badge-warning'
    : 'badge-low';

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>EMAIL DETAIL & ANALYSIS</div>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              {email.subject}
            </h2>
          </div>
          <button className="btn-icon" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-body">
          {/* Metadata Bar */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center', background: 'var(--bg-subtle)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>From: {email.sender}</span>
            <span className="badge badge-accent">{analysis?.intent || 'FYI'}</span>
            <span className={`badge ${riskBadge}`}>{riskLevel.split(' - ')[0]}</span>
            <span className="badge badge-low">{analysis?.priority || 'P2'}</span>
          </div>

          {/* Email Body */}
          <div className="card" style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.775rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              MESSAGE BODY
            </div>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-main)', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
              {email.body}
            </div>
          </div>

          {/* Agent Analysis Reasoning */}
          {analysis && (
            <div className="card" style={{ border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.775rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                AGENT CLASSIFICATION REASONING
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-main)' }}>
                {analysis.reasoning}
              </div>
            </div>
          )}

          {/* MCP Tools Context */}
          {mcp_context && (mcp_context.calendar_events?.length > 0 || mcp_context.github_context?.length > 0) && (
            <div className="card" style={{ border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.775rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                MCP CONTEXT LOOKUP
              </div>
              {mcp_context.calendar_events?.map((ev, i) => (
                <div key={i} style={{ fontSize: '0.8rem', color: 'var(--text-main)' }}>📅 {ev}</div>
              ))}
              {mcp_context.github_context?.map((gh, i) => (
                <div key={i} style={{ fontSize: '0.8rem', color: 'var(--text-main)' }}>🐙 {gh}</div>
              ))}
            </div>
          )}

          {/* Generated Reply Draft */}
          {draft && (
            <div className="card" style={{ border: '1px solid var(--accent-primary)', background: 'var(--accent-subtle)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-primary)' }}>GENERATED REPLY DRAFT</span>
                <span className="badge badge-gmail">{draft.status}</span>
              </div>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-main)', whiteSpace: 'pre-wrap', fontFamily: 'JetBrains Mono, monospace' }}>
                {draft.body}
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
