import React from 'react';
import { Mail, Shield, RefreshCw, ExternalLink, CheckCircle, AlertTriangle } from 'lucide-react';
import type { DashboardStats } from '../types/email';

interface NavbarProps {
  stats: DashboardStats | null;
  onRefresh: () => void;
  onRunBatch: () => void;
  loading: boolean;
  activeTab: 'inbox' | 'traces' | 'style' | 'eval';
  setActiveTab: (tab: 'inbox' | 'traces' | 'style' | 'eval') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ stats, onRefresh, onRunBatch, loading, activeTab, setActiveTab }) => {
  const authenticated = stats?.authenticated ?? false;

  return (
    <header className="navbar" style={{ flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
        <div className="brand">
          <div className="brand-icon">
            <Mail size={22} color="#ffffff" />
          </div>
          <div>
            <h1 className="brand-title">Gmail Copilot</h1>
            <p style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Production-Grade AI Engineering Agent & LangGraph Observability</p>
          </div>
        </div>

        <div className="nav-actions">
          {authenticated ? (
            <span className="badge badge-success">
              <CheckCircle size={14} /> Gmail Authenticated
            </span>
          ) : (
            <span className="badge badge-warning">
              <AlertTriangle size={14} /> Auth Required
            </span>
          )}

          <button className="btn btn-secondary" onClick={onRefresh} disabled={loading}>
            <RefreshCw size={16} className={loading ? 'spin' : ''} /> Refresh
          </button>

          {!authenticated ? (
            <a
              href="http://localhost:8000/auth/login"
              target="_blank"
              rel="noreferrer"
              className="btn btn-primary"
            >
              <ExternalLink size={16} /> Authenticate Gmail
            </a>
          ) : (
            <button className="btn btn-primary" onClick={onRunBatch} disabled={loading}>
              <Shield size={16} /> Process Unread Inbox
            </button>
          )}
        </div>
      </div>

      {/* Recruiter-Level Navigation Tabs */}
      <div style={{ display: 'flex', gap: '0.75rem', borderTop: '1px solid var(--color-border)', paddingTop: '0.75rem', width: '100%' }}>
        <button
          onClick={() => setActiveTab('inbox')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            background: activeTab === 'inbox' ? 'var(--color-primary)' : 'transparent',
            color: activeTab === 'inbox' ? '#ffffff' : 'var(--color-text-secondary)',
            border: 'none',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: '0.85rem',
          }}
        >
          Inbox & Approvals
        </button>

        <button
          onClick={() => setActiveTab('traces')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            background: activeTab === 'traces' ? 'var(--color-primary)' : 'transparent',
            color: activeTab === 'traces' ? '#ffffff' : 'var(--color-text-secondary)',
            border: 'none',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: '0.85rem',
          }}
        >
          Execution Traces
        </button>

        <button
          onClick={() => setActiveTab('style')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            background: activeTab === 'style' ? 'var(--color-primary)' : 'transparent',
            color: activeTab === 'style' ? '#ffffff' : 'var(--color-text-secondary)',
            border: 'none',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: '0.85rem',
          }}
        >
          Style Memory RAG
        </button>

        <button
          onClick={() => setActiveTab('eval')}
          style={{
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            background: activeTab === 'eval' ? 'var(--color-primary)' : 'transparent',
            color: activeTab === 'eval' ? '#ffffff' : 'var(--color-text-secondary)',
            border: 'none',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: '0.85rem',
          }}
        >
          Evaluation Benchmark (100 Emails)
        </button>
      </div>
    </header>
  );
};

