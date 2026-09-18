import React from 'react';
import { 
  X, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle, 
  Calendar, 
  Cpu, 
  Database, 
  BookOpen, 
  Layers, 
  FileText,
  Activity
} from 'lucide-react';
import { HealthCheckResponse, SystemInfo } from '../types';

interface SystemStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  health: HealthCheckResponse | null;
  systemInfo: SystemInfo | null;
  isConnected: boolean;
  onRetryConnection: () => void;
}

export const SystemStatusModal: React.FC<SystemStatusModalProps> = ({
  isOpen,
  onClose,
  health,
  systemInfo,
  isConnected,
  onRetryConnection,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in-50 duration-150">
      <div 
        className="w-full max-w-xl rounded-2xl bg-[#0e1626] border border-[#223254] shadow-2xl shadow-black/60 overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="system-status-title"
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#223254]/70 bg-[#121b2f]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h2 id="system-status-title" className="text-sm font-bold text-white tracking-wide">
                AIONOS ResolveIT — System Diagnostics
              </h2>
              <p className="text-[11px] text-slate-400">
                Live environment metrics, grounded datasets & compliance verification
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#18243e] transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 overflow-y-auto">
          {/* Connection Status Card */}
          <div className={`p-4 rounded-xl border flex items-center justify-between ${
            isConnected
              ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
              : 'bg-rose-950/20 border-rose-500/30 text-rose-300'
          }`}>
            <div className="flex items-center gap-3">
              {isConnected ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
              ) : (
                <AlertTriangle className="w-6 h-6 text-rose-400 shrink-0" />
              )}
              <div>
                <div className="font-semibold text-xs uppercase tracking-wider">
                  {isConnected ? 'FastAPI Backend Operational' : 'Backend Service Offline'}
                </div>
                <div className="text-[11px] text-slate-300">
                  {isConnected 
                    ? `Connected to ${health?.service || 'Veridian IT Service Engine'} v${health?.version || '1.0.0'}`
                    : 'Unable to connect to http://127.0.0.1:8000. Please start uvicorn backend.'}
                </div>
              </div>
            </div>
            {!isConnected && (
              <button
                onClick={onRetryConnection}
                className="px-3 py-1.5 rounded-lg bg-rose-500 text-white text-xs font-semibold hover:bg-rose-400 transition-colors shadow-sm"
              >
                Retry
              </button>
            )}
          </div>

          {/* Core Configuration Parameters */}
          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Operational Anchor & Guardrails
            </span>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] space-y-1">
                <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                  <Calendar className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Temporal Anchor</span>
                </div>
                <div className="font-mono text-cyan-300 font-semibold text-xs">
                  {systemInfo?.simulation_base_date || 'Sep 21, 2026'}
                </div>
                <p className="text-[10px] text-slate-400">Simulation window: Sep 21–25, 2026</p>
              </div>

              <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] space-y-1">
                <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
                  <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Active Agent Engine</span>
                </div>
                <div className="font-mono text-indigo-300 font-semibold text-xs uppercase">
                  {systemInfo?.active_llm_provider || 'Hybrid Rules + NLP'}
                </div>
                <p className="text-[10px] text-slate-400">Deterministic policy boundaries</p>
              </div>
            </div>
          </div>

          {/* Database Entities Counts */}
          <div className="space-y-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Authoritative Datasets Synced
            </span>
            <div className="grid grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] text-center space-y-1">
                <BookOpen className="w-4 h-4 text-cyan-400 mx-auto" />
                <div className="font-mono text-lg font-bold text-white">
                  {systemInfo?.counts.policies ?? 11}
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wide">Policies (KB + Asset)</div>
              </div>

              <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] text-center space-y-1">
                <Layers className="w-4 h-4 text-amber-400 mx-auto" />
                <div className="font-mono text-lg font-bold text-white">
                  {systemInfo?.counts.tickets ?? 10}
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wide">Historical Precedents</div>
              </div>

              <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254] text-center space-y-1">
                <FileText className="w-4 h-4 text-indigo-400 mx-auto" />
                <div className="font-mono text-lg font-bold text-white">
                  {systemInfo?.counts.employee_requests ?? 15}
                </div>
                <div className="text-[10px] text-slate-400 uppercase tracking-wide">Employee Requests</div>
              </div>
            </div>
          </div>

          {/* Compliance & Zero Hallucination Guarantee */}
          <div className="p-3.5 rounded-xl bg-[#121b2f] border border-[#223254] space-y-2">
            <div className="flex items-center gap-2 text-cyan-300 text-xs font-semibold">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span>Anti-Hallucination & Governance Policy</span>
            </div>
            <p className="text-[11px] text-slate-300 leading-relaxed">
              AIONOS ResolveIT is strictly bounded by the Data Pack specification. All agent decisions cite official policy identifiers and produce immutable audit events. Closed ticket precedents (e.g. TK-1050 admin access denial) are treated as binding governance rules.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-[#223254]/70 bg-[#121b2f] text-xs">
          <span className="text-slate-400 font-mono text-[11px]">
            Veridian IT Enterprise Service Desk • ISO/IEC 20000 & ITIL Aligned
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-[#18243e] hover:bg-[#223254] text-slate-200 text-xs font-medium transition-colors"
          >
            Close Diagnostics
          </button>
        </div>
      </div>
    </div>
  );
};
