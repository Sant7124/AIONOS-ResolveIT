export type PolicyCategory = 
  | 'Authentication'
  | 'Network & Remote Access'
  | 'Hardware'
  | 'Software & Applications'
  | 'Peripherals & Printing'
  | 'Email & Collaboration'
  | 'Network & Facilities'
  | 'Enterprise Systems & Finance'
  | 'Information Security'
  | 'Equipment & Facilities'
  | 'Asset Lifecycle & Governance';

export interface PolicyMetadata {
  max_failed_attempts?: number;
  self_service_url?: string;
  requires_approval?: boolean;
  credential_validity_days?: number;
  requires_manager_approval_for_contractors?: boolean;
  access_request_form?: string;
  min_service_years?: number;
  early_replacement_condition?: string;
  lead_time_weeks?: number;
  governed_by_asset_policy?: boolean;
  catalog_url?: string;
  security_review_sla_days_min?: number;
  security_review_sla_days_max?: number;
  first_step?: string;
  ticket_mandatory_field?: string;
  default_quota_gb?: number;
  max_quota_gb?: number;
  validity_hours?: number;
  generation_method?: string;
  requires_ticket?: boolean;
  security_email?: string;
  priority?: string;
  standard_refresh_years?: number;
  interacts_with?: string;
  [key: string]: any;
}

export interface Policy {
  id: string;
  title: string;
  category: PolicyCategory | string;
  summary: string;
  content: string;
  prerequisites: string[];
  approvals_required: string[];
  resolution_type: string;
  sla: string;
  metadata: PolicyMetadata;
}

export interface EmployeeRequest {
  request_id: string;
  employee: string;
  email: string;
  date_opened: string;
  request: string;
  initial_action_taken: string;
  expected_policy_id?: string | null;
  cross_reference_policy_id?: string | null;
  category?: string;
  expected_outcome?: string;
  analysis?: string;
}

export interface Ticket {
  ticket_id: string;
  employee: string;
  issue_summary: string;
  status: string;
  is_active: boolean;
  policy_id: string;
  resolution_note: string;
  precedent_value: string;
  priority?: string;
  assigned_team?: string;
  created_at?: string;
  updated_at?: string;
  description?: string;
}

export interface SystemInfo {
  product_name: string;
  version: string;
  environment: string;
  simulation_base_date: string;
  simulation_window: string;
  active_llm_provider: string;
  counts: {
    policies: number;
    tickets: number;
    employee_requests: number;
  };
  status: string;
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
  simulation_base_date: string;
  active_provider: string;
}

export interface AuditEvent {
  id: string;
  timestamp: string;
  employee: string;
  request: string;
  policyId?: string;
  action: 'RESOLVE' | 'CLARIFY' | 'ESCALATE' | 'REJECT' | 'TICKET' | 'UPDATE_TICKET' | string;
  summary: string;
  ticketId?: string;
  actor_type?: string;
  event_metadata?: Record<string, any>;
}

export interface SourceCitation {
  policy_id: string;
  title: string;
  statement: string;
}

export interface TicketDetails {
  ticket_id: string;
  status: string;
  priority: string;
  assigned_team?: string;
  issue_summary?: string;
}

export interface EscalationDetails {
  required: boolean;
  reason?: string;
  team?: string;
  nextStep?: string;
  source?: string;
}

export interface StructuredAgentResponse {
  understood: string;
  policy: string;
  policyId?: string;
  decision: string;
  nextStep: string;
  ticket: TicketDetails | null;
  sources: SourceCitation[];
  escalation: EscalationDetails | null;
  isLinkedExistingTicket?: boolean;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'agent';
  timestamp: string;
  rawText: string;
  employeeName?: string;
  employeeEmail?: string;
  structured?: StructuredAgentResponse;
  followUpQuestions?: string[];
  actionType?: string;
  outcome?: string;
  status?: string;
  isError?: boolean;
}

export type ActiveTab = 'workspace' | 'requests' | 'tickets' | 'policies' | 'audit';

export type TicketFilterTab = 'ALL' | 'ACTIVE' | 'RESOLVED' | 'REJECTED' | 'CLOSED';

export interface ApiError {
  message: string;
  status?: number;
  canRetry?: boolean;
}

export interface AgentStatus {
  operational: boolean;
  status: string;
  ai_provider_connected: boolean;
  ai_provider_name: string;
  knowledge_base_loaded: boolean;
  knowledge_base_policy_count: number;
  database_connected: boolean;
  active_tickets_count: number;
  simulation_date: string;
  details: Record<string, any>;
}

