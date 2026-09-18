import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { KnowledgeBaseView } from './components/KnowledgeBaseView';
import { TicketQueueView } from './components/TicketQueueView';
import { ScenariosView } from './components/ScenariosView';
import { AgentWorkspace } from './components/AgentWorkspace';
import { AuditFeed } from './components/AuditFeed';
import { SystemStatusModal } from './components/SystemStatusModal';
import { 
  checkBackendHealth, 
  fetchSystemInfo, 
  fetchPolicies, 
  fetchTickets, 
  fetchRequests,
  fetchAuditEvents
} from './services/api';
import { 
  HealthCheckResponse, 
  SystemInfo, 
  Policy, 
  Ticket, 
  EmployeeRequest, 
  AuditEvent,
  ActiveTab
} from './types';
import { AlertTriangle, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('workspace');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);

  const [policies, setPolicies] = useState<Policy[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [requests, setRequests] = useState<EmployeeRequest[]>([]);
  // Pure real backend audit events — no fake data in production UI
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [isDataLoading, setIsDataLoading] = useState<boolean>(true);

  const [selectedRequest, setSelectedRequest] = useState<EmployeeRequest | null>(null);
  const [isStatusModalOpen, setIsStatusModalOpen] = useState<boolean>(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);

  const loadBackendData = async () => {
    try {
      const [h, info, pols, tix, reqs, audits] = await Promise.all([
        checkBackendHealth().catch(() => null),
        fetchSystemInfo().catch(() => null),
        fetchPolicies().catch(() => ({ policies: [] })),
        fetchTickets().catch(() => ({ tickets: [] })),
        fetchRequests().catch(() => ({ requests: [] })),
        fetchAuditEvents(100).catch(() => []),
      ]);

      if (h) {
        setHealth(h);
        setIsConnected(true);
      } else {
        setIsConnected(false);
      }

      if (info) setSystemInfo(info);
      if (pols.policies) setPolicies(pols.policies);
      if (tix.tickets) setTickets(tix.tickets);
      if (reqs.requests) setRequests(reqs.requests);

      if (Array.isArray(audits) && audits.length > 0) {
        const mappedAudits: AuditEvent[] = audits.map((a: any) => ({
          id: a.id,
          timestamp: a.timestamp,
          employee: a.event_metadata?.employee_name || (a.ticket_id ? `Ticket ${a.ticket_id}` : a.actor_type || 'System'),
          request: a.event_metadata?.raw_message || a.reason || a.action,
          policyId: (a.policy_references && a.policy_references.length > 0) ? a.policy_references.join(', ') : (a.event_metadata?.policy_id || ''),
          action: (a.decision || a.action || 'AUDIT').toUpperCase().replace('POLICY_DECISION_', ''),
          summary: a.reason || a.decision || `Audit action: ${a.action}`,
          ticketId: a.ticket_id,
          actor_type: a.actor_type,
          event_metadata: a.event_metadata
        }));
        setAuditEvents(mappedAudits);
      }
    } catch (err) {
      console.warn('Backend synchronization pending or offline:', err);
      setIsConnected(false);
    } finally {
      setIsDataLoading(false);
    }
  };

  useEffect(() => {
    loadBackendData();
    const interval = setInterval(loadBackendData, 6000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectRequest = (req: EmployeeRequest) => {
    setSelectedRequest(req);
    setActiveTab('workspace');
    setIsMobileMenuOpen(false);
  };

  const handleNewRequest = () => {
    setSelectedRequest(null);
    setActiveTab('workspace');
    setIsMobileMenuOpen(false);
  };

  const handleAddAuditEvent = (event: AuditEvent) => {
    setAuditEvents((prev) => [event, ...prev]);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#070b14] text-slate-100 font-sans selection:bg-cyan-500 selection:text-black">
      {/* Top Enterprise Header */}
      <Header 
        health={health} 
        systemInfo={systemInfo} 
        isConnected={isConnected}
        onOpenStatusModal={() => setIsStatusModalOpen(true)}
        onToggleMobileMenu={() => setIsMobileMenuOpen(prev => !prev)}
        isMobileMenuOpen={isMobileMenuOpen}
      />

      {/* Offline Alert Banner if backend is not reachable */}
      {!isConnected && !isDataLoading && (
        <div className="bg-rose-950/40 border-b border-rose-500/40 px-4 py-2 text-xs text-rose-300 flex items-center justify-between">
          <div className="flex items-center gap-2 max-w-7xl mx-auto w-full">
            <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>
              AIONOS ResolveIT Backend server is unreachable at http://127.0.0.1:8000. Start backend with <code className="bg-black/40 px-1.5 py-0.5 rounded font-mono text-white">python -m uvicorn app.main:app --reload</code>.
            </span>
            <button
              onClick={loadBackendData}
              className="ml-auto text-xs text-white font-semibold underline hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Retry</span>
            </button>
          </div>
        </div>
      )}

      {/* Main Container */}
      <div className="flex-1 flex max-w-7xl w-full mx-auto p-3 sm:p-5 gap-6">
        {/* Desktop Left Sidebar */}
        <div className="hidden lg:block">
          <Sidebar
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            onNewRequest={handleNewRequest}
            policyCount={policies.length || 11}
            ticketCount={tickets.length || 10}
            requestCount={requests.length || 15}
            onOpenStatusModal={() => setIsStatusModalOpen(true)}
            isConnected={isConnected}
          />
        </div>

        {/* Mobile Slide-Over Drawer */}
        {isMobileMenuOpen && (
          <div className="fixed inset-0 z-40 lg:hidden flex">
            <div 
              className="fixed inset-0 bg-black/70 backdrop-blur-sm"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            <div className="relative z-50 w-72 max-w-[80vw] h-full bg-[#0c1222] shadow-2xl p-2 flex flex-col">
              <Sidebar
                activeTab={activeTab}
                setActiveTab={(tab) => {
                  setActiveTab(tab);
                  setIsMobileMenuOpen(false);
                }}
                onNewRequest={handleNewRequest}
                policyCount={policies.length || 11}
                ticketCount={tickets.length || 10}
                requestCount={requests.length || 15}
                onOpenStatusModal={() => {
                  setIsStatusModalOpen(true);
                  setIsMobileMenuOpen(false);
                }}
                isConnected={isConnected}
              />
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <main className="flex-1 min-w-0">
          {activeTab === 'workspace' && (
            <AgentWorkspace
              selectedRequest={selectedRequest}
              onClearSelected={() => setSelectedRequest(null)}
              policies={policies}
              tickets={tickets}
              onAddAuditEvent={handleAddAuditEvent}
              onEvaluationComplete={loadBackendData}
              onRequestNewChat={handleNewRequest}
            />
          )}

          {activeTab === 'requests' && (
            <ScenariosView
              requests={requests}
              onSelectRequest={handleSelectRequest}
            />
          )}

          {activeTab === 'tickets' && (
            <TicketQueueView
              tickets={tickets}
              isLoading={isDataLoading}
            />
          )}

          {activeTab === 'policies' && (
            <KnowledgeBaseView
              policies={policies}
              isLoading={isDataLoading}
            />
          )}

          {activeTab === 'audit' && (
            <AuditFeed
              events={auditEvents}
              isLoading={isDataLoading}
              onRefresh={loadBackendData}
            />
          )}
        </main>
      </div>

      {/* System Diagnostics & Health Modal */}
      <SystemStatusModal
        isOpen={isStatusModalOpen}
        onClose={() => setIsStatusModalOpen(false)}
        health={health}
        systemInfo={systemInfo}
        isConnected={isConnected}
        onRetryConnection={loadBackendData}
      />
    </div>
  );
};

export default App;
