import React from 'react';
import type { DashboardStats } from '../types/email';

interface IntegrationsViewProps {
  stats: DashboardStats | null;
}

export const IntegrationsView: React.FC<IntegrationsViewProps> = ({ stats }) => {
  const isGmailConnected = stats?.authenticated ?? true;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '900px', margin: '0 auto' }}>
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <span>🔌</span> Connected Tools & MCP Integrations
            </h2>
            <p className="card-subtitle">Manage OAuth credentials and external tool API connections</p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem', marginTop: '0.5rem' }}>
          {/* Gmail Card */}
          <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-main)' }}>📧 Gmail API</div>
              <span className={`badge ${isGmailConnected ? 'badge-gmail' : 'badge-low'}`}>
                {isGmailConnected ? 'Connected' : 'Offline'}
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Reads incoming inbox threads and creates drafts via Google OAuth 2.0 PKCE.
            </p>
            <button className="btn btn-secondary btn-sm" style={{ width: '100%' }}>
              {isGmailConnected ? 'Re-authenticate OAuth' : 'Connect Gmail Account'}
            </button>
          </div>

          {/* Google Calendar Card */}
          <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-main)' }}>📅 Google Calendar</div>
              <span className="badge badge-accent">MCP Active</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Checks schedule availability and retrieves meeting context for scheduling emails.
            </p>
            <button className="btn btn-secondary btn-sm" style={{ width: '100%' }}>
              Configure Calendar MCP
            </button>
          </div>

          {/* GitHub API Card */}
          <div style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-main)' }}>🐙 GitHub REST API</div>
              <span className="badge badge-accent">MCP Active</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Queries PR statuses, issue tracking, and repository updates for technical queries.
            </p>
            <button className="btn btn-secondary btn-sm" style={{ width: '100%' }}>
              Configure GitHub Token
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
