import React from 'react';

interface AgentStatusCompactProps {
  isProcessing?: boolean;
  activeStep?: string;
}

export const AgentStatusCompact: React.FC<AgentStatusCompactProps> = ({
  isProcessing = false,
  activeStep,
}) => {
  const steps = [
    { id: 'fetch', label: 'Fetch' },
    { id: 'context', label: 'Context' },
    { id: 'classify', label: 'Classify' },
    { id: 'generate', label: 'Generate' },
    { id: 'validate', label: 'Validate' },
    { id: 'draft', label: 'Draft' },
  ];

  return (
    <div className="agent-status-bar">
      <div className="status-indicator">
        <span className="status-dot" style={{ background: isProcessing ? 'var(--accent-primary)' : 'var(--success-color)' }} />
        <span>{isProcessing ? 'Agent processing email...' : 'Agent operational'}</span>
      </div>

      <div className="status-steps">
        {steps.map((s, idx) => {
          const isActive = isProcessing && activeStep === s.id;
          return (
            <React.Fragment key={s.id}>
              <span className={`step-pill ${isActive ? 'active' : ''}`}>
                {s.label}
              </span>
              {idx < steps.length - 1 && <span className="step-arrow">→</span>}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
