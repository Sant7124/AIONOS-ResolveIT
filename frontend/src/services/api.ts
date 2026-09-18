import { 
  HealthCheckResponse, 
  SystemInfo, 
  Policy, 
  Ticket, 
  EmployeeRequest,
  SourceCitation,
  TicketDetails
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';
const DEFAULT_TIMEOUT_MS = 15000;

class ApiClientError extends Error {
  status?: number;
  isNetworkError: boolean;

  constructor(message: string, status?: number, isNetworkError: boolean = false) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.isNetworkError = isNetworkError;
  }
}

async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    return response;
  } catch (err: any) {
    if (err.name === 'AbortError') {
      throw new ApiClientError(`Request timed out after ${timeoutMs / 1000}s. Please retry.`, 408);
    }
    throw new ApiClientError(
      'Unable to reach AIONOS ResolveIT backend. Please ensure the backend server is running.',
      0,
      true
    );
  } finally {
    clearTimeout(timer);
  }
}

export async function checkBackendHealth(): Promise<HealthCheckResponse> {
  const res = await fetchWithTimeout(`${API_BASE}/health`, {}, 5000);
  if (!res.ok) {
    throw new ApiClientError(`Health check failed with status: ${res.status}`, res.status);
  }
  return res.json();
}

export async function fetchSystemInfo(): Promise<SystemInfo> {
  const res = await fetchWithTimeout(`${API_BASE}/api/info`);
  if (!res.ok) {
    throw new ApiClientError(`Failed to fetch system info: ${res.status}`, res.status);
  }
  return res.json();
}

export async function fetchPolicies(): Promise<{ policies: Policy[] }> {
  const res = await fetchWithTimeout(`${API_BASE}/api/policies`);
  if (!res.ok) {
    throw new ApiClientError(`Failed to fetch policies: ${res.status}`, res.status);
  }
  return res.json();
}

export async function fetchTickets(activeOnly?: boolean): Promise<{ tickets: Ticket[] }> {
  const query = activeOnly ? '?active_only=true' : '';
  const res = await fetchWithTimeout(`${API_BASE}/api/tickets${query}`);
  if (!res.ok) {
    throw new ApiClientError(`Failed to fetch tickets: ${res.status}`, res.status);
  }
  return res.json();
}

export async function fetchRequests(): Promise<{ requests: EmployeeRequest[] }> {
  const res = await fetchWithTimeout(`${API_BASE}/api/requests`);
  if (!res.ok) {
    throw new ApiClientError(`Failed to fetch requests: ${res.status}`, res.status);
  }
  return res.json();
}

export interface AgentChatPayload {
  message: string;
  employee_name?: string;
  employee_email?: string;
  conversation_id?: string;
  context?: Record<string, any>;
}

export interface AgentChatApiResponse {
  conversation_id: string;
  intent: string;
  category: string;
  action: 'resolve' | 'ask' | 'ticket' | 'update_ticket' | 'escalate' | 'reject' | string;
  status: string;
  message: string;
  follow_up_questions: string[];
  ticket_id: string | null;
  ticket_details: TicketDetails | null;
  escalation_team: string | null;
  sources: SourceCitation[];
  audit_event_id: string;
}

export async function sendAgentChat(payload: AgentChatPayload): Promise<AgentChatApiResponse> {
  const res = await fetchWithTimeout(`${API_BASE}/api/agent/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    let errorDetail = `Status ${res.status}`;
    try {
      const errJson = await res.json();
      if (errJson.detail) errorDetail = errJson.detail;
    } catch {
      // ignore
    }
    throw new ApiClientError(`Agent request failed: ${errorDetail}`, res.status);
  }
  return res.json();
}

export async function fetchAuditEvents(limit = 100): Promise<any[]> {
  const res = await fetchWithTimeout(`${API_BASE}/api/audit?limit=${limit}`);
  if (!res.ok) {
    throw new ApiClientError(`Failed to fetch audit events: ${res.status}`, res.status);
  }
  return res.json();
}

export async function fetchAuditEventsForRequest(requestId: string): Promise<any[]> {
  const res = await fetchWithTimeout(`${API_BASE}/api/audit/${encodeURIComponent(requestId)}`);
  if (!res.ok) {
    throw new ApiClientError(`Failed to fetch audit events for request ${requestId}: ${res.status}`, res.status);
  }
  return res.json();
}

export async function fetchAgentStatus(): Promise<any> {
  const res = await fetchWithTimeout(`${API_BASE}/api/agent/status`, {}, 5000);
  if (!res.ok) {
    throw new ApiClientError(`Failed to fetch agent status: ${res.status}`, res.status);
  }
  return res.json();
}

export async function fetchRequestById(id: string): Promise<EmployeeRequest> {
  const res = await fetchWithTimeout(`${API_BASE}/api/requests/${encodeURIComponent(id)}`);
  if (!res.ok) {
    throw new ApiClientError(`Failed to fetch request ${id}: ${res.status}`, res.status);
  }
  return res.json();
}

export async function fetchTicketById(id: string): Promise<Ticket> {
  const res = await fetchWithTimeout(`${API_BASE}/api/tickets/${encodeURIComponent(id)}`);
  if (!res.ok) {
    throw new ApiClientError(`Failed to fetch ticket ${id}: ${res.status}`, res.status);
  }
  return res.json();
}

export async function createTicket(payload: any): Promise<Ticket> {
  const res = await fetchWithTimeout(`${API_BASE}/api/tickets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new ApiClientError(`Failed to create ticket: ${res.status}`, res.status);
  }
  return res.json();
}

export async function updateTicket(id: string, payload: any): Promise<Ticket> {
  const res = await fetchWithTimeout(`${API_BASE}/api/tickets/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new ApiClientError(`Failed to update ticket ${id}: ${res.status}`, res.status);
  }
  return res.json();
}

