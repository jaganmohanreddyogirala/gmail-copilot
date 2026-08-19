import { useState, useEffect } from 'react';
import type { ExecutionTrace } from '../types/email';
import { api } from '../api/client';

export function ExecutionTraceView() {
  const [traces, setTraces] = useState<ExecutionTrace[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<ExecutionTrace | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadTraces = async () => {
    setLoading(true);
    try {
      const data = await api.getExecutionTraces(30);
      setTraces(data);
      if (data.length > 0 && !selectedTrace) {
        setSelectedTrace(data[0]);
      }
    } catch (err) {
      console.warn('Execution trace load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTraces();
  }, []);

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case 'DRAFT_CREATED':
        return <span className="badge badge-gmail">Draft Created</span>;
      case 'NEEDS_HUMAN_APPROVAL':
        return <span className="badge badge-warning">Needs Approval</span>;
      case 'IGNORED':
        return <span className="badge badge-low">Ignored / FYI</span>;
      default:
        return <span className="badge badge-low">{decision}</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">
              <span>⚡</span> Execution Traces & Agent Observability
            </h2>
            <p className="card-subtitle">Detailed step-by-step LangGraph node trajectory logs</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={loadTraces}>
            Refresh Traces
          </button>
        </div>

        {loading ? (
          <div className="empty-state">
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Loading agent execution traces...</div>
          </div>
        ) : traces.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-main)' }}>No execution traces found</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              Process emails to generate agent trajectory traces.
            </div>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '1.5rem' }}>
            {/* Trace List Column */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '600px', overflowY: 'auto' }}>
              {traces.map((trace) => {
                const isSelected = selectedTrace?.id === trace.id;
                return (
                  <div
                    key={trace.id}
                    onClick={() => setSelectedTrace(trace)}
                    style={{
                      background: isSelected ? 'var(--accent-subtle)' : 'var(--bg-subtle)',
                      border: isSelected ? '1px solid var(--accent-primary)' : '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '0.85rem 1rem',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)' }}>
                        Email {trace.email_id.substring(0, 10)}...
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
                        Intent: <strong>{trace.intent || 'N/A'}</strong> | {trace.processing_time_ms} ms
                      </div>
                    </div>
                    {getDecisionBadge(trace.decision)}
                  </div>
                );
              })}
            </div>

            {/* Detailed Trace Inspection Panel */}
            {selectedTrace ? (
              <div className="card" style={{ background: 'var(--bg-subtle)', border: '1px solid var(--border-color)' }}>
                <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>TRACE DETAILS</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
                    {selectedTrace.id}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                    Model: <strong>{selectedTrace.model_used}</strong> | Confidence: <strong>{((selectedTrace.confidence ?? 0.85) * 100).toFixed(0)}%</strong> | Duration: <strong>{selectedTrace.processing_time_ms} ms</strong>
                  </div>
                </div>

                {/* Step-by-Step Node Trajectory Timeline */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                  {[
                    { node: 'thread_builder', label: 'Fetch & Thread History' },
                    { node: 'mcp_context', label: 'MCP External Tools (GitHub/Calendar)' },
                    { node: 'classify', label: 'Classifier & Safety Gate' },
                    { node: 'style_memory', label: 'Style Memory RAG' },
                    { node: 'generate_reply', label: 'Generate Draft Reply' },
                    { node: 'validate_reply', label: 'Reply Validator' },
                    { node: 'human_approval', label: 'Human Approval Router' },
                  ].map((step, idx) => {
                    const latencies = selectedTrace.agent_state?.node_latencies || {};
                    const dur = latencies[step.node] !== undefined ? `${latencies[step.node]} ms` : 'Completed';

                    return (
                      <div
                        key={step.node}
                        style={{
                          background: 'var(--bg-surface)',
                          border: '1px solid var(--border-color)',
                          borderRadius: '4px',
                          padding: '0.6rem 0.85rem',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          fontSize: '0.825rem',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ color: 'var(--success-color)', fontWeight: 700 }}>✓</span>
                          <span style={{ fontWeight: 500, color: 'var(--text-main)' }}>{idx + 1}. {step.label}</span>
                        </div>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontFamily: 'JetBrains Mono, monospace' }}>
                          {dur}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Select a trace from the list to inspect execution state.</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
