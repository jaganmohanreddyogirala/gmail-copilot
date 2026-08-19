import React from 'react';
import { GitCommit, ArrowDown, Bot, CheckCircle, ShieldAlert, FileText } from 'lucide-react';

export const WorkflowDiagram: React.FC = () => {
  return (
    <div className="card-panel">
      <div className="panel-header">
        <div className="panel-title">
          <Bot size={20} color="#06b6d4" /> Target LangGraph Agent Architecture
        </div>
        <span className="badge badge-info">LangGraph StateGraph</span>
      </div>

      <div className="workflow-widget">
        <div className="diagram-step active">
          <GitCommit size={16} color="#06b6d4" />
          <span>START ➔ Fetch / Normalize Email</span>
        </div>
        <div style={{ textAlign: 'center', margin: '0.2rem 0' }}><ArrowDown size={14} color="#6b7280" /></div>

        <div className="diagram-step active">
          <FileText size={16} color="#6366f1" />
          <span>Thread Context Builder (History Retrieval)</span>
        </div>
        <div style={{ textAlign: 'center', margin: '0.2rem 0' }}><ArrowDown size={14} color="#6b7280" /></div>

        <div className="diagram-step active">
          <Bot size={16} color="#a855f7" />
          <span>Email Classifier (Intent + Priority + Risk)</span>
        </div>
        <div style={{ textAlign: 'center', margin: '0.2rem 0' }}><ArrowDown size={14} color="#6b7280" /></div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem', margin: '0.5rem 0' }}>
          <div style={{ padding: '0.5rem', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '6px', fontSize: '0.75rem', textAlign: 'center' }}>
            <span style={{ color: '#10b981', fontWeight: 600 }}>Normal Flow</span><br />
            Reply Generator
          </div>
          <div style={{ padding: '0.5rem', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '6px', fontSize: '0.75rem', textAlign: 'center' }}>
            <span style={{ color: '#f59e0b', fontWeight: 600 }}>Requires Review</span><br />
            Human Approval
          </div>
          <div style={{ padding: '0.5rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', fontSize: '0.75rem', textAlign: 'center' }}>
            <span style={{ color: '#ef4444', fontWeight: 600 }}>Ignore</span><br />
            Promotional / Spam
          </div>
        </div>

        <div style={{ textAlign: 'center', margin: '0.2rem 0' }}><ArrowDown size={14} color="#6b7280" /></div>

        <div className="diagram-step active">
          <ShieldAlert size={16} color="#10b981" />
          <span>Reply Validator (Security & Placeholder Audit)</span>
        </div>
        <div style={{ textAlign: 'center', margin: '0.2rem 0' }}><ArrowDown size={14} color="#6b7280" /></div>

        <div className="diagram-step active">
          <CheckCircle size={16} color="#10b981" />
          <span>Create Gmail Draft (users.drafts.create) ➔ END</span>
        </div>
      </div>
    </div>
  );
};
