import React from 'react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  pendingApprovalsCount?: number;
  mobileOpen: boolean;
  setMobileOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  pendingApprovalsCount = 0,
  mobileOpen,
  setMobileOpen,
}) => {
  const navItems = [
    { id: 'home', label: 'Dashboard', icon: '🏠' },
    { id: 'inbox', label: 'Inbox', icon: '📥' },
    { id: 'workspace', label: 'Email Workspace', icon: '💻' },
    { id: 'approvals', label: 'Approval Queue', icon: '⚠️', badge: pendingApprovalsCount },
    { id: 'drafts', label: 'Drafts', icon: '📝' },
    { id: 'traces', label: 'Agent Traces', icon: '⚡' },
    { id: 'style', label: 'Style Memory', icon: '🎨' },
    { id: 'eval', label: 'Evaluations', icon: '📊' },
    { id: 'integrations', label: 'Integrations', icon: '🔌' },
  ];

  const handleNavClick = (tabId: string) => {
    setActiveTab(tabId);
    setMobileOpen(false);
  };

  return (
    <>
      {mobileOpen && <div className="drawer-overlay" onClick={() => setMobileOpen(false)} />}
      <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
        <div>
          <div className="sidebar-header">
            <div className="sidebar-logo">✉️</div>
            <span className="sidebar-title">Gmail Copilot</span>
          </div>

          <nav className="sidebar-nav">
            {navItems.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
                  onClick={() => handleNavClick(item.id)}
                >
                  <span style={{ fontSize: '1rem' }}>{item.icon}</span>
                  <span>{item.label}</span>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span className="nav-item-badge">{item.badge}</span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="sidebar-footer">
          <button
            className={`sidebar-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => handleNavClick('settings')}
          >
            <span style={{ fontSize: '1rem' }}>⚙️</span>
            <span>Settings</span>
          </button>
          <div style={{ padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            v2.0.0 • Connected
          </div>
        </div>
      </aside>
    </>
  );
};
