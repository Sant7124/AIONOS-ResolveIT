import React, { useState } from 'react';
import { 
  FileText, 
  Clock, 
  Search, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  Layers, 
  ArrowUpRight, 
  Code, 
  X,
  Filter,
  Check
} from 'lucide-react';
import { AuditEvent } from '../types';

interface AuditFeedProps {
  events: AuditEvent[];
  isLoading?: boolean;
  onRefresh?: () => void;
}

export const AuditFeed: React.FC<AuditFeedProps> = ({ 
  events, 
  isLoading = false,
  onRefresh 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedActionFilter, setSelectedActionFilter] = useState<string>('ALL');
  const [selectedEventForModal, setSelectedEventForModal] = useState<AuditEvent | null>(null);

  const filteredEvents = events.filter((ev) => {
    const actionNormalized = (ev.action || '').toUpperCase();
    let matchesAction = true;
    if (selectedActionFilter !== 'ALL') {
      matchesAction = actionNormalized.includes(selectedActionFilter);
    }

    const query = searchQuery.toLowerCase();
    const matchesSearch = 
      ev.id.toLowerCase().includes(query) ||
      (ev.employee && ev.employee.toLowerCase().includes(query)) ||
      (ev.request && ev.request.toLowerCase().includes(query)) ||
      (ev.summary && ev.summary.toLowerCase().includes(query)) ||
      (ev.policyId && ev.policyId.toLowerCase().includes(query)) ||
      (ev.ticketId && ev.ticketId.toLowerCase().includes(query));

    return matchesAction && matchesSearch;
  });

  const getActionBadge = (action: string) => {
    const a = action.toUpperCase();
    if (a.includes('RESOLVE')) {
      return (
        <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
          RESOLVE
        </span>
      );
    }
    if (a.includes('CLARIFY') || a.includes('ASK') || a.includes('FOLLOW_UP')) {
      return (
        <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
          CLARIFY
        </span>
      );
    }
    if (a.includes('UPDATE_TICKET')) {
      return (
        <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
          UPDATE TICKET
        </span>
      );
    }
    if (a.includes('TICKET')) {
      return (
        <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
          CREATE TICKET
        </span>
      );
    }
    if (a.includes('ESCALATE')) {
      return (
        <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-300 border border-rose-500/30">
          ESCALATE
        </span>
      );
    }
    if (a.includes('REJECT')) {
      return (
        <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-500/15 text-slate-300 border border-slate-500/30">
          REJECT
        </span>
      );
    }
    return (
      <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-500/15 text-slate-300 border border-slate-500/30">
        {action}
      </span>
    );
  };

  const actionTabs = ['ALL', 'RESOLVE', 'TICKET', 'UPDATE_TICKET', 'ESCALATE', 'REJECT', 'CLARIFY'];

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            Immutable Agent Audit Trail
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time, tamper-evident chronological ledger populated directly from backend SQLite events
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={isLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#0c1222] hover:bg-[#18243e] border border-[#223254] text-xs text-slate-300 hover:text-white transition-colors disabled:opacity-50 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
              <span>Sync Audit</span>
            </button>
          )}

          <span className="font-mono text-xs px-3 py-1 rounded-xl bg-[#0c1222] border border-[#223254] text-cyan-300 font-semibold">
            {events.length} Events Synced
          </span>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search audit ID, employee, ticket..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-8 py-2 rounded-xl bg-[#0c1222] border border-[#223254] text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-cyan-500 transition-colors shadow-sm"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Action Filter Pills */}
        <div className="flex items-center gap-1 overflow-x-auto pb-1 text-xs no-scrollbar">
          {actionTabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setSelectedActionFilter(tab)}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all cursor-pointer whitespace-nowrap ${
                selectedActionFilter === tab
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                  : 'bg-[#0c1222] text-slate-400 border border-[#223254] hover:text-slate-200'
              }`}
            >
              {tab === 'ALL' ? 'All Actions' : tab}
            </button>
          ))}
        </div>
      </div>

      {/* Timeline Stream */}
      {filteredEvents.length === 0 ? (
        <div className="p-12 rounded-2xl bg-[#0c1222]/80 border border-[#223254] text-center space-y-3">
          <Clock className="w-8 h-8 text-slate-500 mx-auto" />
          <h3 className="text-sm font-bold text-white">No Audit Events Match Query</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Run an evaluation in the Agent Workspace to generate real, verifiable audit records.
          </p>
        </div>
      ) : (
        <div className="rounded-2xl border border-[#223254] bg-[#0c1222]/95 overflow-hidden divide-y divide-[#223254]/50 shadow-xl">
          {filteredEvents.map((ev) => {
            const dateObj = new Date(ev.timestamp);
            const timeStr = isNaN(dateObj.getTime()) ? ev.timestamp : dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            const dateStr = isNaN(dateObj.getTime()) ? '' : dateObj.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });

            return (
              <div 
                key={ev.id} 
                className="p-4 hover:bg-[#18243e]/30 transition-colors space-y-2.5 cursor-pointer group"
                onClick={() => setSelectedEventForModal(ev)}
              >
                <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                      {ev.id}
                    </span>
                    <span className="font-mono text-slate-400 text-[11px]">
                      {timeStr} {dateStr && `• ${dateStr}`}
                    </span>
                    <span className="font-semibold text-white">
                      {ev.employee}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {ev.ticketId && (
                      <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
                        {ev.ticketId}
                      </span>
                    )}
                    {ev.policyId && (
                      <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                        {ev.policyId}
                      </span>
                    )}
                    {getActionBadge(ev.action)}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedEventForModal(ev);
                      }}
                      className="p-1 rounded text-slate-400 hover:text-cyan-300 hover:bg-[#18243e]"
                      title="Inspect Raw Event Payload"
                    >
                      <Code className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* Inquiry Statement */}
                <div className="text-xs text-slate-300 italic pl-1 border-l-2 border-cyan-500/40">
                  "{ev.request}"
                </div>

                {/* Resolution Summary */}
                <div className="text-[11px] text-slate-300 bg-[#121b2f] p-2.5 rounded-xl border border-[#223254]/50 leading-relaxed flex items-start justify-between gap-2">
                  <span>{ev.summary}</span>
                  <ArrowUpRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 shrink-0 transition-colors" />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ========================================================================= */}
      {/* RAW AUDIT JSON INSPECTOR MODAL                                            */}
      {/* ========================================================================= */}
      {selectedEventForModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in-50 duration-150">
          <div 
            className="w-full max-w-xl rounded-2xl bg-[#0e1626] border border-[#223254] shadow-2xl shadow-black/70 overflow-hidden flex flex-col max-h-[90vh]"
            role="dialog"
            aria-modal="true"
          >
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#223254]/70 bg-[#121b2f]">
              <div className="flex items-center gap-2.5">
                <Code className="w-4 h-4 text-cyan-400" />
                <span className="font-mono text-sm font-bold text-white">
                  Audit Payload: {selectedEventForModal.id}
                </span>
              </div>
              <button
                onClick={() => setSelectedEventForModal(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#18243e] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 overflow-y-auto text-xs">
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Tamper-Evident Event Structure
                </span>
                <pre className="p-4 rounded-xl bg-[#070b14] border border-[#223254] text-cyan-300 font-mono text-[11px] overflow-x-auto leading-relaxed">
                  {JSON.stringify(selectedEventForModal, null, 2)}
                </pre>
              </div>
            </div>

            <div className="flex items-center justify-end px-6 py-3 border-t border-[#223254]/70 bg-[#121b2f]">
              <button
                onClick={() => setSelectedEventForModal(null)}
                className="px-4 py-1.5 rounded-lg bg-[#18243e] hover:bg-[#223254] text-slate-200 text-xs font-medium transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
