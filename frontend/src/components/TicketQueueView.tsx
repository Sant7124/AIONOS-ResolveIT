import React, { useState } from 'react';
import { 
  Layers, 
  AlertCircle, 
  CheckCircle2, 
  Search, 
  ShieldAlert, 
  Clock, 
  User, 
  X, 
  ExternalLink,
  BookOpen,
  ArrowUpRight,
  Filter,
  Check
} from 'lucide-react';
import { Ticket, TicketFilterTab } from '../types';

interface TicketQueueViewProps {
  tickets: Ticket[];
  isLoading?: boolean;
}

export const TicketQueueView: React.FC<TicketQueueViewProps> = ({ 
  tickets,
  isLoading = false 
}) => {
  const [filter, setFilter] = useState<TicketFilterTab>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);

  const filteredTickets = tickets.filter((ticket) => {
    const statusLower = ticket.status.toLowerCase();
    let matchesFilter = true;

    if (filter === 'ACTIVE') {
      matchesFilter = ticket.is_active;
    } else if (filter === 'RESOLVED') {
      matchesFilter = statusLower.includes('resolved') || statusLower.includes('closed') && !statusLower.includes('rejected');
    } else if (filter === 'REJECTED') {
      matchesFilter = statusLower.includes('rejected') || statusLower.includes('denied');
    } else if (filter === 'CLOSED') {
      matchesFilter = !ticket.is_active;
    }

    const query = searchQuery.toLowerCase();
    const matchesSearch = 
      ticket.ticket_id.toLowerCase().includes(query) ||
      ticket.employee.toLowerCase().includes(query) ||
      ticket.issue_summary.toLowerCase().includes(query) ||
      ticket.status.toLowerCase().includes(query) ||
      ticket.policy_id.toLowerCase().includes(query);

    return matchesFilter && matchesSearch;
  });

  const getStatusBadge = (status: string, isActive: boolean) => {
    const sLower = status.toLowerCase();
    if (sLower.includes('resolved') || sLower.includes('fulfilled')) {
      return (
        <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <CheckCircle2 className="w-3 h-3" />
          {status}
        </span>
      );
    }
    if (sLower.includes('escalated') || sLower.includes('security') || sLower.includes('critical')) {
      return (
        <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-rose-500/15 text-rose-300 border border-rose-500/30">
          <ShieldAlert className="w-3 h-3 text-rose-400" />
          {status}
        </span>
      );
    }
    if (sLower.includes('rejected') || sLower.includes('denied')) {
      return (
        <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-500/15 text-slate-300 border border-slate-500/30">
          <AlertCircle className="w-3 h-3" />
          {status}
        </span>
      );
    }
    if (isActive) {
      return (
        <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30">
          <Clock className="w-3 h-3 text-amber-400" />
          {status}
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-slate-500/10 text-slate-300 border border-slate-500/20">
        {status}
      </span>
    );
  };

  const getPriorityBadge = (priority?: string) => {
    const p = (priority || 'P3 - Medium').toUpperCase();
    if (p.includes('P1') || p.includes('CRITICAL')) {
      return <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">P1 CRITICAL</span>;
    }
    if (p.includes('P2') || p.includes('HIGH')) {
      return <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">P2 HIGH</span>;
    }
    return <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">P3 STANDARD</span>;
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-amber-400" />
            Service Desk Ticket Queue & Precedents
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Section 3 of the Data Pack — Historical Precedents (TK-1042–TK-1051) & Active Cases
          </p>
        </div>

        {/* Search & Filter Tabs */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative w-64 sm:w-72">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search ID, employee, issue..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-[#0c1222] border border-[#223254] text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-amber-500 transition-colors shadow-sm"
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

          <div className="flex items-center bg-[#0c1222] p-1 rounded-xl border border-[#223254] text-xs">
            {(['ALL', 'ACTIVE', 'RESOLVED', 'REJECTED', 'CLOSED'] as TicketFilterTab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setFilter(tab)}
                className={`px-3 py-1 rounded-lg font-medium transition-all cursor-pointer ${
                  filter === tab
                    ? 'bg-[#18243e] text-amber-300 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {tab === 'ALL' && `All (${tickets.length})`}
                {tab === 'ACTIVE' && 'Active'}
                {tab === 'RESOLVED' && 'Resolved'}
                {tab === 'REJECTED' && 'Rejected'}
                {tab === 'CLOSED' && 'Closed'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Ticket Table */}
      <div className="rounded-2xl border border-[#223254] bg-[#0c1222]/95 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#121b2f] border-b border-[#223254] text-slate-400 font-medium uppercase text-[10px] tracking-wider">
              <tr>
                <th className="px-4 py-3.5">Ticket ID</th>
                <th className="px-4 py-3.5">Requester</th>
                <th className="px-4 py-3.5">Issue Summary</th>
                <th className="px-4 py-3.5">Priority</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-4 py-3.5">Governing Policy</th>
                <th className="px-4 py-3.5">Precedent Significance</th>
                <th className="px-4 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#223254]/50">
              {filteredTickets.map((t) => (
                <tr 
                  key={t.ticket_id} 
                  onClick={() => setSelectedTicket(t)}
                  className="hover:bg-[#18243e]/50 transition-colors cursor-pointer group"
                >
                  <td className="px-4 py-3.5 font-mono font-bold text-cyan-400">
                    {t.ticket_id}
                  </td>
                  <td className="px-4 py-3.5 font-medium text-slate-200 whitespace-nowrap">
                    {t.employee}
                  </td>
                  <td className="px-4 py-3.5 text-slate-300 max-w-xs font-normal truncate">
                    {t.issue_summary}
                  </td>
                  <td className="px-4 py-3.5 whitespace-nowrap">
                    {getPriorityBadge(t.priority)}
                  </td>
                  <td className="px-4 py-3.5 whitespace-nowrap">
                    {getStatusBadge(t.status, t.is_active)}
                  </td>
                  <td className="px-4 py-3.5 whitespace-nowrap">
                    <span className="font-mono text-[11px] px-2.5 py-0.5 rounded-lg bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                      {t.policy_id}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-slate-400 text-[11px] max-w-sm truncate font-sans">
                    {t.precedent_value}
                  </td>
                  <td className="px-4 py-3.5 text-right whitespace-nowrap">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedTicket(t);
                      }}
                      className="text-cyan-400 hover:text-cyan-300 p-1 rounded-lg hover:bg-cyan-500/10 transition-colors"
                      title="Inspect ticket details and audit trail"
                    >
                      <ArrowUpRight className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Empty / No Results State */}
        {filteredTickets.length === 0 && (
          <div className="p-12 text-center space-y-2">
            <Layers className="w-8 h-8 text-slate-500 mx-auto" />
            <p className="text-xs text-slate-300 font-medium">No tickets match the selected filter or search</p>
            <p className="text-[11px] text-slate-400">Try adjusting your query or resetting filter tabs.</p>
          </div>
        )}
      </div>

      {/* ========================================================================= */}
      {/* TICKET DETAIL INSPECTOR MODAL                                             */}
      {/* ========================================================================= */}
      {selectedTicket && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in-50 duration-150">
          <div 
            className="w-full max-w-2xl rounded-2xl bg-[#0e1626] border border-[#223254] shadow-2xl shadow-black/70 overflow-hidden flex flex-col max-h-[90vh]"
            role="dialog"
            aria-modal="true"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#223254]/70 bg-[#121b2f]">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                  <Layers className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-bold text-white">
                      {selectedTicket.ticket_id}
                    </span>
                    {getStatusBadge(selectedTicket.status, selectedTicket.is_active)}
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Enterprise IT Ticket & Precedent Inspector
                  </p>
                </div>
              </div>

              <button
                onClick={() => setSelectedTicket(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#18243e] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4 overflow-y-auto text-xs">
              {/* Requester & Metadata Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Requester</span>
                  <div className="font-semibold text-white truncate">{selectedTicket.employee}</div>
                </div>

                <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Priority</span>
                  <div>{getPriorityBadge(selectedTicket.priority)}</div>
                </div>

                <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Assigned Team</span>
                  <div className="font-semibold text-cyan-300 truncate">
                    {selectedTicket.assigned_team || 'IT Service Desk'}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Policy Citation</span>
                  <div className="font-mono font-bold text-cyan-400">{selectedTicket.policy_id}</div>
                </div>
              </div>

              {/* Issue Summary & Description */}
              <div className="p-4 rounded-xl bg-[#121b2f] border border-[#223254] space-y-2">
                <span className="text-[10px] uppercase font-bold text-slate-400">
                  Issue Summary
                </span>
                <p className="text-sm font-medium text-white">
                  {selectedTicket.issue_summary}
                </p>
                {selectedTicket.description && (
                  <p className="text-xs text-slate-300 pt-1 border-t border-[#223254]/50">
                    {selectedTicket.description}
                  </p>
                )}
              </div>

              {/* Resolution Notes */}
              <div className="p-4 rounded-xl bg-[#121b2f] border border-[#223254] space-y-2">
                <span className="text-[10px] uppercase font-bold text-slate-400">
                  Resolution Notes & Precedent Value
                </span>
                <p className="text-xs text-slate-200 leading-relaxed bg-[#0c1222] p-3 rounded-lg border border-[#223254]/60 whitespace-pre-line font-mono">
                  {selectedTicket.resolution_note || selectedTicket.precedent_value}
                </p>
              </div>

              {/* Precedent Enforcement Rule */}
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-200 space-y-1">
                <span className="text-[10px] uppercase font-bold text-amber-400 flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5" />
                  Binding Governance Role
                </span>
                <p className="text-[11px] leading-relaxed">
                  {selectedTicket.precedent_value}
                </p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between px-6 py-3 border-t border-[#223254]/70 bg-[#121b2f] text-xs">
              <span className="font-mono text-slate-400 text-[11px]">
                Precedent Type: {selectedTicket.is_active ? 'Active Open Case' : 'Closed Historical Rule'}
              </span>
              <button
                onClick={() => setSelectedTicket(null)}
                className="px-4 py-1.5 rounded-lg bg-[#18243e] hover:bg-[#223254] text-slate-200 text-xs font-medium transition-colors"
              >
                Close Ticket
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
