import axios from 'axios';
import type { DashboardStats, EmailMessage, ProcessedEmailResponse, DraftReply, ExecutionTrace, UserStyleMemory, EvalMetrics } from '../types/email';

const API_BASE_URL = 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-API-Key': 'copilot-prod-secret-key-2026',
  },
});

export const api = {
  checkAuthStatus: async (): Promise<{ authenticated: boolean; message: string }> => {
    const res = await client.get(`/auth/status`);
    return res.data;
  },

  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await client.get(`/dashboard/stats`);
    return res.data;
  },

  fetchUnreadEmails: async (limit = 10): Promise<EmailMessage[]> => {
    const res = await client.get(`/emails/unread?limit=${limit}`);
    return res.data;
  },

  processSingleEmail: async (email: EmailMessage): Promise<ProcessedEmailResponse> => {
    const res = await client.post(`/emails/process`, email);
    return res.data;
  },

  processBatchUnread: async (limit = 5): Promise<{
    status: string;
    total_unread_processed: number;
    drafts_created_in_gmail: number;
    drafts_pending_human_approval: number;
    results: ProcessedEmailResponse[];
  }> => {
    const res = await client.post(`/emails/process-unread?limit=${limit}`);
    return res.data;
  },

  createGmailDraft: async (draft: DraftReply): Promise<any> => {
    const res = await client.post(`/emails/draft`, draft);
    return res.data;
  },

  getExecutionTraces: async (limit = 20): Promise<ExecutionTrace[]> => {
    const res = await client.get(`/dashboard/traces?limit=${limit}`);
    return res.data;
  },

  getUserStyle: async (): Promise<UserStyleMemory> => {
    const res = await client.get(`/api/user-style`);
    return res.data;
  },

  updateUserStyle: async (style: UserStyleMemory): Promise<any> => {
    const res = await client.post(`/api/user-style`, style);
    return res.data;
  },

  getLatestEval: async (): Promise<EvalMetrics> => {
    const res = await client.get(`/api/eval/latest`);
    return res.data;
  },

  triggerEvalRun: async (limit = 100): Promise<{ status: string; metrics: EvalMetrics }> => {
    const res = await client.post(`/api/eval/run?limit=${limit}`);
    return res.data;
  },

  getDemoScenarios: async (): Promise<any[]> => {
    const res = await client.get(`/api/demo/scenarios`);
    return res.data;
  },

  runDemoScenario: async (scenarioId: string): Promise<ProcessedEmailResponse> => {
    const res = await client.post(`/api/demo/scenario/${scenarioId}`);
    return res.data;
  },
};


