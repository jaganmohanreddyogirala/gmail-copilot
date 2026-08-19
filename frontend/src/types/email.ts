export type EmailCategory = 'Work' | 'Urgent' | 'Support / Bug' | 'Notification / CI-CD' | 'Newsletter / Promo' | 'Personal';
export type EmailPriority = 'P0 - Critical' | 'P1 - High' | 'P2 - Medium' | 'P3 - Low';
export type RiskLevel = 'Low' | 'Medium' | 'High - Requires Human Review';
export type EmailIntent = 'Technical Query' | 'Action Required / Task Request' | 'Informational / FYI' | 'Decision Needed' | 'Security Alert / Credential Exposure Risk' | 'Promotional / Marketing';

export interface EmailMessage {
  id: string;
  thread_id: string;
  sender: string;
  recipient?: string;
  subject: string;
  body: string;
  snippet?: string;
  date?: string;
  is_unread: boolean;
  labels: string[];
}

export interface EmailThread {
  thread_id: string;
  messages: EmailMessage[];
}

export interface AnalysisResult {
  email_id: string;
  category: EmailCategory;
  priority: EmailPriority;
  intent: EmailIntent;
  risk_level: RiskLevel;
  risk_reasoning?: string;
  requires_reply: boolean;
  requires_human_approval: boolean;
  reasoning: string;
  key_action_items: string[];
}

export interface DraftReply {
  email_id: string;
  thread_id: string;
  recipient: string;
  subject: string;
  body: string;
  reasoning?: string;
  draft_id?: string;
  status: 'created' | 'pending_approval' | 'approved' | 'sent';

}

export interface MCPContext {
  calendar_events: string[];
  github_context: string[];
  tool_notes?: string;
}

export interface ProcessedEmailResponse {
  email: EmailMessage;
  thread_context?: EmailThread;
  analysis?: AnalysisResult;
  draft?: DraftReply;
  mcp_context?: MCPContext;
}

export interface DashboardStats {
  authenticated: boolean;
  unread_count: number;
  pending_approvals_count: number;
  processed_today: number;
  risk_breakdown: {
    high: number;
    medium: number;
    low: number;
  };
  system_status: string;
}

export interface ExecutionTrace {
  id: string;
  email_id: string;
  thread_id: string;
  intent?: string;
  priority?: string;
  risk?: string;
  decision: string;
  confidence?: number;
  agent_state: Record<string, any>;
  model_used: string;
  processing_time_ms: number;
  draft_created: boolean;
  human_approved?: boolean | null;
  validation_result: string;
  created_at?: string;
}

export interface UserStyleMemory {
  tone: string;
  greeting_template: string;
  signoff_template: string;
  custom_rules: string[];
}

export interface EvalMetrics {
  id: string;
  intent_accuracy: number;
  risk_accuracy: number;
  priority_accuracy: number;
  validation_accuracy: number;
  approval_precision: number;
  false_positive_rate: number;
  high_risk_precision?: number;
  high_risk_recall?: number;
  high_risk_f1?: number;
  high_risk_false_negatives?: number;
  avg_latency_ms: number;
  total_samples: number;
  metrics_json?: Record<string, any>;
  created_at?: string;
}


