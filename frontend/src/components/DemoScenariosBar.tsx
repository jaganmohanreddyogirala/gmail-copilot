import React from 'react';

interface DemoScenariosBarProps {
  onSelectScenario: (scenarioId: string) => void;
  loading: boolean;
}

export const DemoScenariosBar: React.FC<DemoScenariosBarProps> = ({ onSelectScenario, loading }) => {
  const scenarios = [
    { id: 'scenario_1', label: '1. Interview Scheduling', icon: '📅' },
    { id: 'scenario_2', label: '2. GitHub PR Update', icon: '🐙' },
    { id: 'scenario_3', label: '3. Credential Leak (High Risk)', icon: '🔑' },
    { id: 'scenario_4', label: '4. Prompt Injection Defense', icon: '🛡️' },
    { id: 'scenario_5', label: '5. Unverified Financial Info', icon: '❓' },
  ];

  return (
    <div style={{ background: 'var(--accent-subtle)', border: '1px solid var(--accent-primary)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1.25rem', marginBottom: '1.25rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-primary)' }}>
          <span>🚀 RECRUITER DEMO MODE</span>
          <span className="badge badge-accent">No OAuth Credentials Required</span>
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Select a scenario to execute through LangGraph agent:</span>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
        {scenarios.map((sc) => (
          <button
            key={sc.id}
            className="btn btn-secondary btn-sm"
            onClick={() => onSelectScenario(sc.id)}
            disabled={loading}
            style={{ background: 'var(--bg-surface)' }}
          >
            <span>{sc.icon}</span>
            <span>{sc.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
