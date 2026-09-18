import React from 'react';
import { 
  Bot, 
  Layers, 
  BookOpen, 
  CheckSquare, 
  FileText, 
  ShieldCheck,
  PlusCircle,
  Activity,
  Server
} from 'lucide-react';
import { ActiveTab } from '../types';

interface SidebarProps {
  activeTab: ActiveTab;
  setActiveTab: (tab: ActiveTab) => void;
  onNewRequest: () => void;
  policyCount: number;
  ticketCount: number;
  requestCount: number;
  onOpenStatusModal?: () => void;
  isConnected: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  onNewRequest,
  policyCount,
  ticketCount,
  requestCount,
  onOpenStatusModal,
  isConnected,
}) => {
  const navItems = [
    {
      id: 'workspace' as ActiveTab,
      label: 'Agent Workspace',
      icon: Bot,
      badge: 'Live',
      badgeColor: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
    },
    {
      id: 'requests' as ActiveTab,
      label: 'My Requests',
      icon: CheckSquare,
      badge: `${requestCount}`,
      badgeColor: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30'
    },
    {
      id: 'tickets' as ActiveTab,
      label: 'Active Tickets',
      icon: Layers,
      badge: `${ticketCount}`,
      badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30'
    },
    {
      id: 'policies' as ActiveTab,
      label: 'Knowledge Base',
      icon: BookOpen,
      badge: `${policyCount}`,
      badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
    },
    {
      id: 'audit' as ActiveTab,
      label: 'Audit Trail',
      icon: FileText,
      badge: null,
      badgeColor: ''
    },
  ];

  return (
    <aside className="w-full lg:w-64 bg-[#0c1222]/90 border-r border-[#223254]/60 p-4 flex flex-col justify-between shrink-0 space-y-6">
      <div className="space-y-5">
        {/* Primary Action Button: New Request */}
        <button
          onClick={() => {
            onNewRequest();
            setActiveTab('workspace');
          }}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-[#080d1a] font-bold text-xs shadow-lg shadow-cyan-500/20 hover:shadow-cyan-500/30 transition-all cursor-pointer group"
        >
          <PlusCircle className="w-4 h-4 transition-transform group-hover:rotate-90 duration-200" />
          <span>New Request</span>
        </button>

        {/* Navigation Section */}
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-2">
            Service Console
          </span>
          <nav className="mt-2 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/5 font-semibold'
                      : 'text-slate-300 hover:bg-[#18243e]/60 hover:text-white border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${item.badgeColor}`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Grounding Guarantees Callout */}
        <div className="p-3.5 rounded-xl bg-[#121b2f]/90 border border-[#223254] text-xs space-y-2">
          <div className="flex items-center gap-1.5 text-cyan-300 font-semibold text-[11px] uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>Policy Guardrails</span>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            Strictly grounded in Veridian Corp KB-01–KB-10 & Asset Management Policy. Zero policy hallucination.
          </p>
          <div className="pt-2 border-t border-[#223254]/60 flex items-center justify-between text-[10px] text-slate-400 font-mono">
            <span>Precedents</span>
            <span className="text-amber-300 font-semibold">10 Tickets Synced</span>
          </div>
        </div>
      </div>

      {/* System Status & Footer */}
      <div className="space-y-3 pt-4 border-t border-[#223254]/50">
        {onOpenStatusModal && (
          <button
            onClick={onOpenStatusModal}
            className="w-full flex items-center justify-between p-2.5 rounded-xl bg-[#121b2f] hover:bg-[#18243e] border border-[#223254] hover:border-cyan-500/30 text-xs text-slate-300 transition-all cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <Server className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[11px] font-medium">System Status</span>
            </div>
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-rose-400'}`} />
          </button>
        )}

        <div className="text-[11px] text-slate-400 space-y-0.5 px-1">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-slate-300">AIONOS ResolveIT</span>
            <span className="font-mono text-cyan-400 text-[10px]">v1.0.0</span>
          </div>
          <div className="text-[10px] text-slate-400">
            AI-Powered Internal IT Service & Resolution Agent
          </div>
        </div>
      </div>
    </aside>
  );
};
