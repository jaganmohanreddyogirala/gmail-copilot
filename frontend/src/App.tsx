import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Topbar } from './components/Topbar';
import { HomeDashboard } from './components/HomeDashboard';
import { EmailList } from './components/EmailList';
import { EmailWorkspaceView } from './components/EmailWorkspaceView';
import { ApprovalQueue } from './components/ApprovalQueue';
import { DraftsView } from './components/DraftsView';
import { ExecutionTraceView } from './components/ExecutionTraceView';
import { UserStyleManager } from './components/UserStyleManager';
import { EvaluationDashboard } from './components/EvaluationDashboard';
import { IntegrationsView } from './components/IntegrationsView';
import { SettingsView } from './components/SettingsView';
import { EmailDetailModal } from './components/EmailDetailModal';
import type { DashboardStats, ProcessedEmailResponse, DraftReply } from './types/email';
import { api } from './api/client';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('home');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [emails, setEmails] = useState<ProcessedEmailResponse[]>([]);
  const [selectedItem, setSelectedItem] = useState<ProcessedEmailResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [mobileOpen, setMobileOpen] = useState<boolean>(false);

  const loadData = async () => {
    try {
      const statsData = await api.getDashboardStats();
      setStats(statsData);
    } catch (err) {
      console.warn('Dashboard stats load error:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunBatch = async () => {
    setLoading(true);
    try {
      const res = await api.processBatchUnread(5);
      setEmails(res.results);
      await loadData();
    } catch (err: any) {
      alert(`Processing error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRunDemoScenario = async (scenarioId: string) => {
    setLoading(true);
    try {
      const result = await api.runDemoScenario(scenarioId);
      setEmails((prev) => [result, ...prev.filter((e) => e.email.id !== result.email.id)]);
      setSelectedItem(result);
      await loadData();
    } catch (err: any) {
      alert(`Demo scenario execution error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveDraft = async (draft: DraftReply) => {
    try {
      await api.createGmailDraft(draft);
      alert(`Gmail draft successfully created & saved to Gmail for ${draft.recipient}!`);
      setEmails((prev) =>
        prev.map((item) => {
          if (item.email.id === draft.email_id && item.draft) {
            return { ...item, draft: { ...item.draft, status: 'created' } };
          }
          return item;
        })
      );
      await loadData();
    } catch (err: any) {
      alert(`Draft approval error: ${err.response?.data?.detail || err.message}`);
    }
  };

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        pendingApprovalsCount={stats?.pending_approvals_count ?? 0}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />

      {/* Main Wrapper */}
      <div className="main-wrapper">
        <Topbar
          stats={stats}
          activeTab={activeTab}
          onRefresh={loadData}
          onRunBatch={handleRunBatch}
          loading={loading}
          onToggleMobile={() => setMobileOpen(!mobileOpen)}
        />

        <main className="main-content">
          {activeTab === 'home' && (
            <HomeDashboard
              stats={stats}
              emails={emails}
              loading={loading}
              onApproveDraft={handleApproveDraft}
              onSelectEmail={setSelectedItem}
              onNavigateTab={setActiveTab}
              onRunScenario={handleRunDemoScenario}
            />
          )}

          {activeTab === 'inbox' && (
            <EmailList emails={emails} onSelect={setSelectedItem} loading={loading} />
          )}

          {activeTab === 'workspace' && (
            <EmailWorkspaceView emails={emails} onApproveDraft={handleApproveDraft} />
          )}

          {activeTab === 'approvals' && (
            <ApprovalQueue items={emails} onApprove={handleApproveDraft} onSelect={setSelectedItem} />
          )}

          {activeTab === 'drafts' && (
            <DraftsView items={emails} onSelect={setSelectedItem} />
          )}

          {activeTab === 'traces' && <ExecutionTraceView />}

          {activeTab === 'style' && <UserStyleManager />}

          {activeTab === 'eval' && <EvaluationDashboard />}

          {activeTab === 'integrations' && <IntegrationsView stats={stats} />}

          {activeTab === 'settings' && <SettingsView stats={stats} />}
        </main>
      </div>

      {/* Email Detail Inspection Modal */}
      <EmailDetailModal item={selectedItem} onClose={() => setSelectedItem(null)} />
    </div>
  );
}

export default App;
