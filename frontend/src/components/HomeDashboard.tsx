import React from 'react';
import { MetricsOverview } from './MetricsOverview';
import { AgentStatusCompact } from './AgentStatusCompact';
import { ApprovalQueue } from './ApprovalQueue';
import { EmailList } from './EmailList';
import { RecentActivity } from './RecentActivity';
import { DemoScenariosBar } from './DemoScenariosBar';
import type { DashboardStats, ProcessedEmailResponse, DraftReply } from '../types/email';

interface HomeDashboardProps {
  stats: DashboardStats | null;
  emails: ProcessedEmailResponse[];
  loading: boolean;
  onApproveDraft: (draft: DraftReply) => void;
  onSelectEmail: (item: ProcessedEmailResponse) => void;
  onNavigateTab: (tab: string) => void;
  onRunScenario: (scenarioId: string) => void;
}

export const HomeDashboard: React.FC<HomeDashboardProps> = ({
  stats,
  emails,
  loading,
  onApproveDraft,
  onSelectEmail,
  onNavigateTab,
  onRunScenario,
}) => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Home Welcome Header */}
      <div>
        <h1 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-main)', letterSpacing: '-0.01em' }}>
          {getGreeting()}
        </h1>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
          Your inbox is under control.
        </p>
      </div>

      {/* Recruiter Demo Mode Scenarios Bar */}
      <DemoScenariosBar onSelectScenario={onRunScenario} loading={loading} />

      {/* 4 Compact Metric Cards */}
      <MetricsOverview stats={stats} />

      {/* Compact Horizontal Agent Status Bar */}
      <AgentStatusCompact isProcessing={loading} />

      {/* Home Content Grid */}
      <div className="dashboard-grid">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <ApprovalQueue
            items={emails}
            onApprove={onApproveDraft}
            onSelect={onSelectEmail}
            onViewAll={() => onNavigateTab('approvals')}
          />
          <EmailList emails={emails} onSelect={onSelectEmail} loading={loading} />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <RecentActivity items={emails} />
        </div>
      </div>
    </div>
  );
};
