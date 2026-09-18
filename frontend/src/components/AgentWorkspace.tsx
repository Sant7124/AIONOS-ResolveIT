import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  User, 
  Sparkles, 
  AlertTriangle, 
  CheckCircle2, 
  ShieldAlert, 
  BookOpen, 
  Layers, 
  RefreshCw,
  HelpCircle,
  CornerDownRight,
  Shield,
  Bot,
  ExternalLink,
  ChevronRight,
  Clock,
  ArrowRight,
  Check,
  AlertCircle
} from 'lucide-react';
import { 
  EmployeeRequest, 
  Policy, 
  Ticket, 
  ChatMessage, 
  StructuredAgentResponse 
} from '../types';
import { sendAgentChat, AgentChatApiResponse } from '../services/api';

interface AgentWorkspaceProps {
  selectedRequest: EmployeeRequest | null;
  onClearSelected: () => void;
  policies: Policy[];
  tickets: Ticket[];
  onAddAuditEvent: (event: any) => void;
  onEvaluationComplete?: () => void;
  onRequestNewChat?: () => void;
}

export const AgentWorkspace: React.FC<AgentWorkspaceProps> = ({
  selectedRequest,
  onClearSelected,
  policies: _policies,
  tickets: _tickets,
  onAddAuditEvent,
  onEvaluationComplete,
}) => {
  const [employeeName, setEmployeeName] = useState<string>(
    selectedRequest ? selectedRequest.employee : 'Aditi Sharma'
  );
  const [employeeEmail, setEmployeeEmail] = useState<string>(
    selectedRequest ? selectedRequest.email : 'aditi.sharma@veridian-corp.example'
  );

  const [inputPrompt, setInputPrompt] = useState<string>('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [evalStep, setEvalStep] = useState<string>('');
  const [followUpResponse, setFollowUpResponse] = useState<string>('');
  const [activeContext, setActiveContext] = useState<StructuredAgentResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Initial messages stream
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-msg',
      role: 'agent',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      rawText: 'Hello! I am AIONOS ResolveIT, your AI-powered internal IT service and resolution agent. I resolve routine IT requests, enforce company policies (KB-01 to KB-10 and Asset Management), check active ticket history, and route escalations. How can I assist you today?',
    }
  ]);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  // Sync if selectedRequest changes from outside (e.g. Scenarios tab)
  useEffect(() => {
    if (selectedRequest) {
      setEmployeeName(selectedRequest.employee);
      setEmployeeEmail(selectedRequest.email);
      setInputPrompt(selectedRequest.request);
      setConversationId(null);
      setErrorMessage(null);
    }
  }, [selectedRequest]);

  // Suggested quick action pills
  const quickActions = [
    { label: 'VPN not working', prompt: 'My VPN stopped working this morning, says credentials expired.' },
    { label: 'Reset my locked account', prompt: 'I entered my password incorrectly 6 times and now my account is locked.' },
    { label: 'Install software', prompt: 'I need to install Figma and an unapproved third-party code generator on my workstation.' },
    { label: 'Report phishing', prompt: 'I think I got a phishing email asking for my login — forwarding it to a few teammates to check.' },
    { label: 'Laptop issue', prompt: 'My laptop won’t turn on at all, it’s completely dead, had it about 3.5 years now.' },
    { label: 'Printer problem', prompt: 'Office printer PRN-BLD2-FL3 is jammed and not printing my queue jobs.' },
  ];

  // Quick clarification suggestions for ambiguous cases
  const clarificationPresets = [
    'Laptop screen flickers intermittently, device is 2 years old, powers on.',
    'Account locked after 6 failed login attempts on Windows domain.',
    'Requesting admin access to Finance reporting server for month-end reconciliation.',
  ];

  const handleSendMessage = async (overrideText?: string) => {
    const textToSend = (overrideText || inputPrompt).trim();
    if (!textToSend || isProcessing) return;

    setErrorMessage(null);

    // Append User Message
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      rawText: textToSend,
      employeeName,
      employeeEmail,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputPrompt('');
    setIsProcessing(true);

    // Realistic evaluation steps for feedback
    setEvalStep('Detecting intent & extracting parameters...');
    const stepTimer1 = setTimeout(() => setEvalStep('Retrieving grounded policies (KB-01–KB-10)...'), 400);
    const stepTimer2 = setTimeout(() => setEvalStep('Checking active ticket queue for duplicates...'), 800);
    const stepTimer3 = setTimeout(() => setEvalStep('Executing deterministic rules engine...'), 1200);

    try {
      const response: AgentChatApiResponse = await sendAgentChat({
        message: textToSend,
        employee_name: employeeName,
        employee_email: employeeEmail,
        conversation_id: conversationId || undefined,
      });

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Structure the response for visual display
      const outcome = response.action.toUpperCase();
      const primaryPolicy = response.sources.length > 0 ? response.sources[0] : null;
      const isEscalation = response.action === 'escalate' || !!response.escalation_team;
      const isLinkedTicket = response.action === 'update_ticket';

      const structured: StructuredAgentResponse = {
        understood: `${response.intent.replace(/_/g, ' ').toUpperCase()} (${response.category})`,
        policy: primaryPolicy ? `${primaryPolicy.policy_id} — ${primaryPolicy.title}` : 'Veridian Corporate Policy',
        policyId: primaryPolicy ? primaryPolicy.policy_id : undefined,
        decision: response.status || outcome,
        nextStep: response.message,
        ticket: response.ticket_details,
        sources: response.sources,
        escalation: isEscalation ? {
          required: true,
          team: response.escalation_team || 'IT Security / Operations',
          reason: response.status || 'Policy mandate requires specialist escalation or emergency containment.',
          nextStep: response.message,
          source: primaryPolicy ? primaryPolicy.policy_id : 'Corporate Governance'
        } : null,
        isLinkedExistingTicket: isLinkedTicket
      };

      setActiveContext(structured);

      const agentMsg: ChatMessage = {
        id: `agent-${Date.now()}`,
        role: 'agent',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        rawText: response.message,
        structured,
        followUpQuestions: response.follow_up_questions || [],
        actionType: response.action,
        outcome,
        status: response.status,
      };

      setMessages((prev) => [...prev, agentMsg]);
      setFollowUpResponse('');

      // Add to global audit event feed
      onAddAuditEvent({
        id: response.audit_event_id,
        timestamp: new Date().toISOString(),
        employee: employeeName,
        request: textToSend,
        policyId: primaryPolicy ? primaryPolicy.policy_id : undefined,
        action: outcome,
        summary: response.message.substring(0, 110) + '...',
        ticketId: response.ticket_id || undefined,
      });

      if (onEvaluationComplete) {
        onEvaluationComplete();
      }
    } catch (err: any) {
      console.error('Agent chat error:', err);
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      setErrorMessage(err.message || 'An error occurred while contacting the AIONOS ResolveIT service.');
      
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'agent',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        rawText: 'Service Connection Error: Unable to complete policy evaluation. Please verify backend service availability.',
        isError: true,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsProcessing(false);
      setEvalStep('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const resetSession = () => {
    onClearSelected();
    setConversationId(null);
    setActiveContext(null);
    setInputPrompt('');
    setErrorMessage(null);
    setMessages([
      {
        id: `welcome-${Date.now()}`,
        role: 'agent',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        rawText: 'Session reset. Ready for a new IT service request. How can I help you?',
      }
    ]);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      {/* ========================================================================= */}
      {/* MAIN CONVERSATIONAL WORKSPACE (Cols 1 to 8 on Desktop)                     */}
      {/* ========================================================================= */}
      <div className="lg:col-span-8 flex flex-col space-y-4 min-w-0">
        
        {/* Requester Bar & Session Controls */}
        <div className="p-3.5 rounded-2xl bg-[#0c1222]/90 border border-[#223254] flex flex-wrap items-center justify-between gap-3 shadow-md">
          <div className="flex items-center gap-2 text-xs flex-wrap">
            <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <User className="w-3.5 h-3.5" />
            </div>
            <span className="text-slate-400 font-medium">Employee Persona:</span>
            <input
              type="text"
              value={employeeName}
              onChange={(e) => setEmployeeName(e.target.value)}
              className="bg-[#121b2f] border border-[#223254] rounded-lg px-2.5 py-1 text-xs text-white font-medium focus:outline-none focus:border-cyan-500 transition-colors w-36 sm:w-44"
              title="Employee Name"
            />
            <input
              type="text"
              value={employeeEmail}
              onChange={(e) => setEmployeeEmail(e.target.value)}
              className="bg-[#121b2f] border border-[#223254] rounded-lg px-2.5 py-1 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500 transition-colors hidden sm:inline w-56"
              title="Employee Corporate Email"
            />
          </div>

          <div className="flex items-center gap-2">
            {conversationId && (
              <span className="font-mono text-[10px] text-cyan-300 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/20">
                Thread: {conversationId.slice(0, 8)}...
              </span>
            )}
            <button
              onClick={resetSession}
              className="px-2.5 py-1 rounded-lg text-xs text-slate-400 hover:text-white hover:bg-[#18243e] border border-transparent hover:border-[#223254] transition-colors cursor-pointer"
              title="Reset conversation state"
            >
              Reset Thread
            </button>
          </div>
        </div>

        {/* Quick Action Suggested Chips */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-[11px] text-slate-400 px-1">
            <span className="font-semibold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              Example IT Service Inquiries
            </span>
            <span className="text-[10px] text-slate-400 hidden sm:inline">Click any chip to load prompt</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {quickActions.map((qa, idx) => (
              <button
                key={idx}
                onClick={() => setInputPrompt(qa.prompt)}
                disabled={isProcessing}
                className="px-3 py-1.5 rounded-xl bg-[#121b2f] hover:bg-[#18243e] border border-[#223254] hover:border-cyan-500/40 text-xs text-slate-300 hover:text-cyan-200 transition-all text-left shadow-sm cursor-pointer disabled:opacity-50"
              >
                {qa.label}
              </button>
            ))}
          </div>
        </div>

        {/* Conversation Stream Container */}
        <div className="p-4 sm:p-5 rounded-2xl bg-[#0c1222]/95 border border-[#223254] shadow-xl shadow-black/30 min-h-[460px] max-h-[620px] overflow-y-auto space-y-5 flex flex-col">
          {messages.map((msg) => (
            <div key={msg.id} className="space-y-3">
              {/* User Message Bubble */}
              {msg.role === 'user' && (
                <div className="flex justify-end">
                  <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-gradient-to-r from-blue-600 to-cyan-600 p-4 text-white shadow-md shadow-blue-500/10 space-y-1">
                    <div className="flex items-center justify-between gap-4 text-[10px] text-cyan-100/80 pb-1 border-b border-white/10 font-mono">
                      <span>{msg.employeeName || employeeName}</span>
                      <span>{msg.timestamp}</span>
                    </div>
                    <p className="text-xs sm:text-sm font-normal leading-relaxed pt-1 whitespace-pre-wrap">
                      {msg.rawText}
                    </p>
                  </div>
                </div>
              )}

              {/* Agent Message Bubble */}
              {msg.role === 'agent' && (
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/10 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shrink-0 shadow-sm mt-0.5">
                    <Bot className="w-4 h-4" />
                  </div>

                  <div className="flex-1 space-y-3 min-w-0">
                    {/* Plain Text Intro if no structured card */}
                    {!msg.structured && (
                      <div className={`p-4 rounded-2xl rounded-tl-sm text-xs sm:text-sm leading-relaxed ${
                        msg.isError 
                          ? 'bg-rose-950/30 border border-rose-500/40 text-rose-200' 
                          : 'bg-[#121b2f] border border-[#223254] text-slate-200'
                      }`}>
                        {msg.isError && (
                          <div className="flex items-center gap-1.5 text-rose-400 font-semibold mb-1 text-xs uppercase">
                            <AlertCircle className="w-4 h-4" />
                            <span>Resolution Error</span>
                          </div>
                        )}
                        <p>{msg.rawText}</p>
                      </div>
                    )}

                    {/* STRUCTURED AGENT RESPONSE CARD */}
                    {msg.structured && (
                      <div className="p-5 rounded-2xl rounded-tl-sm bg-[#121b2f] border border-[#223254] space-y-4 shadow-lg shadow-black/20 animate-in fade-in-50 duration-200">
                        
                        {/* Header: Understood Issue & Outcome Pill */}
                        <div className="flex items-start justify-between gap-3 border-b border-[#223254]/80 pb-3">
                          <div className="flex items-center gap-2.5">
                            <div className={`p-2 rounded-xl ${
                              msg.actionType === 'resolve' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' :
                              msg.actionType === 'ask' || msg.outcome === 'CLARIFY' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                              msg.actionType === 'update_ticket' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30' :
                              msg.actionType === 'escalate' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                              msg.actionType === 'reject' ? 'bg-slate-500/10 text-slate-300 border border-slate-500/30' :
                              'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
                            }`}>
                              {msg.actionType === 'resolve' && <CheckCircle2 className="w-5 h-5" />}
                              {(msg.actionType === 'ask' || msg.outcome === 'CLARIFY') && <HelpCircle className="w-5 h-5" />}
                              {msg.actionType === 'update_ticket' && <RefreshCw className="w-5 h-5" />}
                              {msg.actionType === 'escalate' && <ShieldAlert className="w-5 h-5" />}
                              {msg.actionType === 'reject' && <AlertCircle className="w-5 h-5" />}
                              {msg.actionType === 'ticket' && <Layers className="w-5 h-5" />}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                                  Action:
                                </span>
                                <span className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                                  msg.actionType === 'resolve' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                                  msg.actionType === 'ask' || msg.outcome === 'CLARIFY' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                                  msg.actionType === 'update_ticket' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' :
                                  msg.actionType === 'escalate' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
                                  msg.actionType === 'reject' ? 'bg-slate-500/20 text-slate-300 border border-slate-500/30' :
                                  'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                                }`}>
                                  {msg.actionType === 'update_ticket' ? 'UPDATE TICKET (LINKED)' : (msg.outcome || msg.actionType)}
                                </span>
                              </div>
                              <span className="text-[11px] text-slate-400 font-mono">
                                Status: {msg.status || 'Processed'}
                              </span>
                            </div>
                          </div>

                          {msg.structured.policyId && (
                            <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                              {msg.structured.policyId}
                            </span>
                          )}
                        </div>

                        {/* Visual Structured Sections Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          {/* UNDERSTOOD */}
                          <div className="p-3 rounded-xl bg-[#0c1222] border border-[#223254]/70 space-y-1">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1">
                              <Check className="w-3 h-3" />
                              Understood
                            </span>
                            <p className="text-slate-200 font-medium">
                              {msg.structured.understood}
                            </p>
                          </div>

                          {/* POLICY */}
                          <div className="p-3 rounded-xl bg-[#0c1222] border border-[#223254]/70 space-y-1">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1">
                              <BookOpen className="w-3 h-3" />
                              Governing Policy
                            </span>
                            <p className="text-slate-200 font-medium">
                              {msg.structured.policy}
                            </p>
                          </div>
                        </div>

                        {/* DECISION & NEXT STEPS */}
                        <div className="p-3.5 rounded-xl bg-[#0c1222] border border-[#223254] space-y-2">
                          <div className="flex items-center gap-1.5 text-slate-300 text-xs font-bold uppercase tracking-wider">
                            <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
                            <span>Decision & Resolution Instructions</span>
                          </div>
                          <p className="text-xs text-slate-200 leading-relaxed whitespace-pre-line font-sans">
                            {msg.structured.nextStep}
                          </p>
                        </div>

                        {/* ESCALATION UI (If Human Review Required) */}
                        {msg.structured.escalation && (
                          <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/40 space-y-2.5 animate-in fade-in-50 duration-150">
                            <div className="flex items-center justify-between text-xs font-bold text-rose-300 uppercase tracking-wider">
                              <div className="flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                                <span>⚠ Human Review Required</span>
                              </div>
                              <span className="font-mono text-[10px] bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded border border-rose-500/30">
                                Priority Routing
                              </span>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-300 pt-1">
                              <div>
                                <span className="text-slate-400">Assigned Team:</span>{' '}
                                <span className="font-semibold text-rose-200">{msg.structured.escalation.team}</span>
                              </div>
                              <div>
                                <span className="text-slate-400">Governing Source:</span>{' '}
                                <span className="font-mono text-cyan-300">{msg.structured.escalation.source}</span>
                              </div>
                            </div>
                            <p className="text-xs text-rose-100/90 pt-1">
                              <span className="font-semibold text-slate-300">Next Action:</span> Request has been dispatched for specialist review per policy guidelines.
                            </p>
                          </div>
                        )}

                        {/* TICKET UI (If Created or Linked) */}
                        {msg.structured.ticket && (
                          <div className={`p-3.5 rounded-xl border space-y-2 ${
                            msg.structured.isLinkedExistingTicket
                              ? 'bg-cyan-950/20 border-cyan-500/40'
                              : 'bg-[#18243e]/80 border-amber-500/30'
                          }`}>
                            <div className="flex items-center justify-between text-xs">
                              <div className="flex items-center gap-2 font-bold">
                                {msg.structured.isLinkedExistingTicket ? (
                                  <>
                                    <RefreshCw className="w-4 h-4 text-cyan-400 shrink-0" />
                                    <span className="text-cyan-300">
                                      Active Ticket Updated: {msg.structured.ticket.ticket_id}
                                    </span>
                                  </>
                                ) : (
                                  <>
                                    <Layers className="w-4 h-4 text-amber-400 shrink-0" />
                                    <span className="text-amber-300">
                                      Service Ticket Created: {msg.structured.ticket.ticket_id}
                                    </span>
                                  </>
                                )}
                              </div>
                              <span className={`font-mono text-[10px] uppercase px-2 py-0.5 rounded-full border ${
                                msg.structured.isLinkedExistingTicket
                                  ? 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30'
                                  : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
                              }`}>
                                {msg.structured.isLinkedExistingTicket ? 'Linked Active' : msg.structured.ticket.priority}
                              </span>
                            </div>

                            <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                              <div>
                                <span className="text-slate-400">Assigned Queue:</span>{' '}
                                <span className="font-medium text-white">{msg.structured.ticket.assigned_team || 'IT Service Desk'}</span>
                              </div>
                              <div>
                                <span className="text-slate-400">Current Status:</span>{' '}
                                <span className="font-medium text-white">{msg.structured.ticket.status}</span>
                              </div>
                            </div>
                            {msg.structured.ticket.issue_summary && (
                              <div className="text-[11px] text-slate-300 font-mono pt-1 border-t border-[#223254]/50">
                                <span className="text-slate-400">Summary:</span> {msg.structured.ticket.issue_summary}
                              </div>
                            )}
                          </div>
                        )}

                        {/* INTERACTIVE CLARIFICATION UI (If Action: ASK) */}
                        {msg.followUpQuestions && msg.followUpQuestions.length > 0 && (
                          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-3">
                            <div className="flex items-center gap-2 text-amber-300 text-xs font-bold uppercase tracking-wider">
                              <HelpCircle className="w-4 h-4 text-amber-400 shrink-0" />
                              <span>Minimal Clarification Needed (Anti-Hallucination)</span>
                            </div>
                            <div className="space-y-1.5 text-xs text-amber-100">
                              {msg.followUpQuestions.map((q, i) => (
                                <div key={i} className="flex items-start gap-2 bg-[#0c1222]/80 p-2.5 rounded-lg border border-amber-500/20">
                                  <CornerDownRight className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                                  <span>{q}</span>
                                </div>
                              ))}
                            </div>

                            {/* Single-Click Preset Answers for Evaluator */}
                            <div className="space-y-1 pt-1">
                              <span className="text-[10px] uppercase font-semibold text-amber-300/80">
                                Quick Reply Options:
                              </span>
                              <div className="flex flex-wrap gap-1.5">
                                {clarificationPresets.map((preset, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => handleSendMessage(preset)}
                                    disabled={isProcessing}
                                    className="px-2.5 py-1 rounded-lg bg-[#0c1222] hover:bg-[#18243e] border border-amber-500/30 text-[11px] text-amber-200 hover:text-white transition-all text-left cursor-pointer disabled:opacity-50"
                                  >
                                    {preset}
                                  </button>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* SOURCE CITATIONS CARD */}
                        {msg.structured.sources && msg.structured.sources.length > 0 && (
                          <div className="pt-2 border-t border-[#223254]/60 space-y-1.5">
                            <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-semibold">
                              <BookOpen className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                              <span>Authoritative Source Policy Evidence:</span>
                            </div>
                            <div className="space-y-1">
                              {msg.structured.sources.map((s, idx) => (
                                <div key={idx} className="p-2 rounded-lg bg-[#0c1222] border border-[#223254]/60 text-[11px] text-slate-300 space-y-0.5">
                                  <div className="flex items-center gap-2 font-mono font-bold text-cyan-300">
                                    <span>{s.policy_id}</span>
                                    <span className="text-slate-400 font-sans font-normal">— {s.title}</span>
                                  </div>
                                  <p className="text-slate-400 italic">"{s.statement}"</p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Typing / Evaluating Indicator */}
          {isProcessing && (
            <div className="flex items-start gap-3 animate-in fade-in-50 duration-200">
              <div className="w-8 h-8 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shrink-0 animate-pulse">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-3.5 rounded-2xl rounded-tl-sm bg-[#121b2f] border border-[#223254] text-xs text-cyan-300 flex items-center gap-2.5 shadow-md">
                <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                <span>{evalStep || 'Analyzing request against corporate policies...'}</span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Error Notification Bar if any */}
        {errorMessage && (
          <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/40 text-xs text-rose-200 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-xs text-rose-300 hover:text-white underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Input Bar */}
        <div className="p-3.5 rounded-2xl bg-[#0c1222]/90 border border-[#223254] space-y-2 shadow-lg shadow-black/20">
          <div className="relative">
            <textarea
              ref={textareaRef}
              rows={2}
              value={inputPrompt}
              onChange={(e) => setInputPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Describe your IT issue (e.g., VPN expired, laptop won't boot, need software, guest Wi-Fi)..."
              disabled={isProcessing}
              className="w-full p-3 rounded-xl bg-[#121b2f] border border-[#223254] text-xs sm:text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition-colors leading-relaxed resize-none disabled:opacity-60"
            />
          </div>

          <div className="flex items-center justify-between pt-0.5">
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
              <Shield className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span className="hidden sm:inline">Press Enter to send, Shift+Enter for new line</span>
              <span className="sm:hidden">Grounded in Veridian Policies</span>
            </div>

            <button
              onClick={() => handleSendMessage()}
              disabled={isProcessing || !inputPrompt.trim()}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-[#080d1a] font-bold text-xs shadow-md shadow-cyan-500/20 hover:shadow-cyan-500/30 transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Evaluating...</span>
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5" />
                  <span>Send Request</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* RIGHT CONTEXT PANEL (Cols 9 to 12 on Desktop)                             */}
      {/* ========================================================================= */}
      <div className="lg:col-span-4 space-y-4">
        
        {/* Real-time Triage Context Card */}
        <div className="p-4 rounded-2xl bg-[#0c1222]/90 border border-[#223254] space-y-4 shadow-lg">
          <div className="flex items-center justify-between border-b border-[#223254]/70 pb-3">
            <div className="flex items-center gap-2 text-cyan-300 font-bold text-xs uppercase tracking-wider">
              <Bot className="w-4 h-4 text-cyan-400" />
              <span>Session Triage Inspector</span>
            </div>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          </div>

          {activeContext ? (
            <div className="space-y-3 text-xs">
              {/* Detected Issue */}
              <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Detected Intent & Classification
                </span>
                <div className="font-semibold text-white">
                  {activeContext.understood}
                </div>
              </div>

              {/* Resolution Status */}
              <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Policy Determination
                </span>
                <div className="font-mono text-cyan-300 font-bold">
                  {activeContext.decision}
                </div>
              </div>

              {/* Associated Ticket Info */}
              {activeContext.ticket && (
                <div className="p-3 rounded-xl bg-[#121b2f] border border-amber-500/30 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400">
                      Ticket Record
                    </span>
                    <span className="font-mono text-[10px] text-amber-300">
                      {activeContext.ticket.ticket_id}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-300 space-y-0.5">
                    <div><span className="text-slate-400">Priority:</span> {activeContext.ticket.priority}</div>
                    <div><span className="text-slate-400">Queue:</span> {activeContext.ticket.assigned_team || 'IT Operations'}</div>
                    <div><span className="text-slate-400">Status:</span> {activeContext.ticket.status}</div>
                  </div>
                </div>
              )}

              {/* Escalation Route */}
              {activeContext.escalation && (
                <div className="p-3 rounded-xl bg-rose-950/20 border border-rose-500/40 space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-rose-400">
                    Escalation Route
                  </span>
                  <div className="font-medium text-rose-200">
                    {activeContext.escalation.team}
                  </div>
                  <p className="text-[10px] text-slate-400">Dispatched via corporate security protocol</p>
                </div>
              )}
            </div>
          ) : (
            <div className="p-6 rounded-xl bg-[#121b2f]/60 border border-[#223254] text-center space-y-2">
              <Clock className="w-8 h-8 text-slate-400 mx-auto" />
              <p className="text-xs text-slate-300 font-medium">Awaiting Request</p>
              <p className="text-[11px] text-slate-400">
                Submit an IT issue in the main chat to observe real-time policy classification and triage routing.
              </p>
            </div>
          )}
        </div>

        {/* Corporate Policies Reference Quick-Check */}
        <div className="p-4 rounded-2xl bg-[#0c1222]/90 border border-[#223254] space-y-3 shadow-lg">
          <div className="flex items-center gap-2 text-indigo-300 font-bold text-xs uppercase tracking-wider">
            <BookOpen className="w-4 h-4 text-indigo-400" />
            <span>Policy Intelligence (11 Grounded)</span>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            All determinations follow authoritative policies from Section 1 & 2 of the Data Pack:
          </p>

          <div className="space-y-2 text-[11px]">
            <div className="p-2.5 rounded-xl bg-[#121b2f] border border-[#223254]/70 space-y-0.5">
              <div className="font-mono font-bold text-cyan-400">KB-01: Password Reset</div>
              <p className="text-slate-400">Self-service portal; locked after $\ge 5$ failed attempts.</p>
            </div>
            <div className="p-2.5 rounded-xl bg-[#121b2f] border border-[#223254]/70 space-y-0.5">
              <div className="font-mono font-bold text-cyan-400">KB-02: VPN Access</div>
              <p className="text-slate-400">90-day renewal cycle; contractor requires Form IT-VPN-C.</p>
            </div>
            <div className="p-2.5 rounded-xl bg-[#121b2f] border border-[#223254]/70 space-y-0.5">
              <div className="font-mono font-bold text-cyan-400">KB-03 + ASSET-01</div>
              <p className="text-slate-400">3-yr hardware check; early refresh requires Finance dual sign-off.</p>
            </div>
            <div className="p-2.5 rounded-xl bg-[#121b2f] border border-[#223254]/70 space-y-0.5">
              <div className="font-mono font-bold text-cyan-400">KB-09: Security Incidents</div>
              <p className="text-slate-400">Forwarding strictly prohibited; emergency P1 triage.</p>
            </div>
          </div>
        </div>

        {/* Closed Ticket Precedent Guardrails */}
        <div className="p-4 rounded-2xl bg-[#0c1222]/90 border border-[#223254] space-y-3 shadow-lg">
          <div className="flex items-center gap-2 text-amber-300 font-bold text-xs uppercase tracking-wider">
            <Layers className="w-4 h-4 text-amber-400" />
            <span>Precedent Enforcement</span>
          </div>
          <div className="space-y-2 text-[11px]">
            <div className="p-2.5 rounded-xl bg-[#121b2f] border border-[#223254]/70">
              <div className="flex items-center justify-between font-mono text-amber-300 font-semibold">
                <span>TK-1050: Admin Access</span>
                <span className="text-[10px] text-slate-400">Rejected</span>
              </div>
              <p className="text-slate-400 mt-0.5">Binding precedent: Unjustified privileged access rejected.</p>
            </div>
            <div className="p-2.5 rounded-xl bg-[#121b2f] border border-[#223254]/70">
              <div className="flex items-center justify-between font-mono text-amber-300 font-semibold">
                <span>TK-1043: Laptop Refresh</span>
                <span className="text-[10px] text-emerald-400">Approved</span>
              </div>
              <p className="text-slate-400 mt-0.5">3.2 years in service with dual IT + Finance sign-off.</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
