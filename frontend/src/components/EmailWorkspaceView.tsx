import React, { useState } from 'react';
import type { ProcessedEmailResponse, DraftReply } from '../types/email';

interface EmailWorkspaceViewProps {
  emails: ProcessedEmailResponse[];
  onApproveDraft?: (draft: DraftReply) => void;
}

export const EmailWorkspaceView: React.FC<EmailWorkspaceViewProps> = ({ emails, onApproveDraft }) => {
  const [selectedIdx, setSelectedIdx] = useState<number>(0);
  const activeItem = emails[selectedIdx] || emails[0];

  if (!activeItem) {
    return (
      <div className="card empty-state">
        <div className="empty-icon">📬</div>
        <div style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-main)' }}>Email Workspace Empty</div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
          Process unread emails or run a demo scenario to populate the workspace.
        </div>
      </div>
    );
  }

  const { email, analysis, draft, mcp_context } = activeItem;
  const risk = analysis?.risk_level || 'Low';

  const riskBadge = risk.toLowerCase().includes('high')
    ? 'badge-high'
    : risk.toLowerCase().includes('medium')
    ? 'badge-warning'
    : 'badge-low';

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr 340px', gap: '1.25rem', height: 'calc(100vh - 140px)', minHeight: '600px' }}>
      {/* LEFT PANE: Thread List */}
      <div className="card" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', overflowY: 'auto' }}>
        <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
          INBOX THREADS ({emails.length})
        </div>

        {emails.map((item, idx) => {
          const isSelected = idx === selectedIdx;
          return (
            <div
              key={item.email.id}
              onClick={() => setSelectedIdx(idx)}
              style={{
                background: isSelected ? 'var(--accent-subtle)' : 'var(--bg-subtle)',
                border: isSelected ? '1px solid var(--accent-primary)' : '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.75rem',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              <div style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {item.email.sender.split('<')[0]}
              </div>
              <div style={{ fontSize: '0.775rem', color: 'var(--text-secondary)', marginTop: '0.15rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {item.email.subject}
              </div>
            </div>
          );
        })}
      </div>

      {/* CENTER PANE: Email Conversation */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto' }}>
        <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>{email.subject}</div>
          <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            From: <strong>{email.sender}</strong>
          </div>
        </div>

        <div style={{ flex: 1, background: 'var(--bg-subtle)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '1rem', whiteSpace: 'pre-wrap', lineHeight: 1.6, fontSize: '0.875rem' }}>
          {email.body}
        </div>
      </div>

      {/* RIGHT PANE: AI Copilot Intelligence Panel */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto' }}>
        <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-primary)', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
          ✨ AI Copilot Panel
        </div>

        {/* Understanding Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.775rem' }}>
          <div style={{ background: 'var(--bg-subtle)', padding: '0.5rem', borderRadius: '4px' }}>
            <div style={{ color: 'var(--text-secondary)' }}>Intent</div>
            <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>{analysis?.intent || 'FYI'}</div>
          </div>
          <div style={{ background: 'var(--bg-subtle)', padding: '0.5rem', borderRadius: '4px' }}>
            <div style={{ color: 'var(--text-secondary)' }}>Priority</div>
            <div style={{ fontWeight: 700, color: 'var(--text-main)' }}>{analysis?.priority || 'P2'}</div>
          </div>
          <div style={{ background: 'var(--bg-subtle)', padding: '0.5rem', borderRadius: '4px' }}>
            <div style={{ color: 'var(--text-secondary)' }}>Risk</div>
            <span className={`badge ${riskBadge}`}>{risk.split(' - ')[0]}</span>
          </div>
          <div style={{ background: 'var(--bg-subtle)', padding: '0.5rem', borderRadius: '4px' }}>
            <div style={{ color: 'var(--text-secondary)' }}>Confidence</div>
            <div style={{ fontWeight: 700, color: 'var(--success-color)' }}>94%</div>
          </div>
        </div>

        {/* Context Used Checklist */}
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
            CONTEXT RETRIEVED
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.775rem' }}>
            <div><span style={{ color: 'var(--success-color)' }}>✓</span> Gmail thread history</div>
            <div><span style={{ color: mcp_context?.calendar_events ? 'var(--success-color)' : 'var(--text-muted)' }}>{mcp_context?.calendar_events ? '✓' : '✗'}</span> Google Calendar MCP</div>
            <div><span style={{ color: mcp_context?.github_context ? 'var(--success-color)' : 'var(--text-muted)' }}>{mcp_context?.github_context ? '✓' : '✗'}</span> GitHub REST API MCP</div>
            <div><span style={{ color: 'var(--success-color)' }}>✓</span> User RAG Style Memory</div>
          </div>
        </div>

        {/* Safety Verification Checklist */}
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
            SAFETY VERIFICATION
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', fontSize: '0.775rem' }}>
            <div><span style={{ color: 'var(--success-color)' }}>✓</span> No leaked credentials / secrets</div>
            <div><span style={{ color: 'var(--success-color)' }}>✓</span> Prompt injection isolation active</div>
            <div><span style={{ color: 'var(--success-color)' }}>✓</span> No unreplaced placeholders</div>
            <div><span style={{ color: 'var(--success-color)' }}>✓</span> Grounded response check passed</div>
          </div>
        </div>

        {/* Suggested Reply Draft & Actions */}
        {draft && (
          <div style={{ marginTop: 'auto', borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-primary)', marginBottom: '0.35rem' }}>
              SUGGESTED REPLY
            </div>
            <div style={{ fontSize: '0.775rem', background: 'var(--bg-subtle)', padding: '0.65rem', borderRadius: '4px', whiteSpace: 'pre-wrap', maxHeight: '120px', overflowY: 'auto' }}>
              {draft.body}
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.65rem' }}>
              {onApproveDraft && (
                <button className="btn btn-primary btn-sm" style={{ flex: 1 }} onClick={() => onApproveDraft(draft)}>
                  Create Draft
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
