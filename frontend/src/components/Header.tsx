import React from 'react';
import { Shield, Calendar, Cpu, AlertTriangle, Menu, X, Activity } from 'lucide-react';
import { HealthCheckResponse, SystemInfo } from '../types';

interface HeaderProps {
  health: HealthCheckResponse | null;
  systemInfo: SystemInfo | null;
  isConnected: boolean;
  onOpenStatusModal?: () => void;
  onToggleMobileMenu?: () => void;
  isMobileMenuOpen?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ 
  health: _health, 
  systemInfo, 
  isConnected,
  onOpenStatusModal,
  onToggleMobileMenu,
  isMobileMenuOpen = false
}) => {
  return (
    <header className="glass-header sticky top-0 z-30 px-4 sm:px-6 py-3 border-b border-[#223254]/70 bg-[#0c1222]/95 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand & Identity */}
        <div className="flex items-center gap-3">
          {/* Mobile Menu Toggle Button */}
          {onToggleMobileMenu && (
            <button
              onClick={onToggleMobileMenu}
              className="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-[#18243e] transition-colors"
              aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          )}

          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-md shadow-cyan-500/10 shrink-0">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-bold tracking-tight text-white flex items-center gap-2 uppercase">
                AIONOS ResolveIT
                <span className="hidden sm:inline text-[10px] font-semibold tracking-wider px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                  ENTERPRISE
                </span>
              </h1>
            </div>
            <p className="text-[11px] sm:text-xs text-slate-400 font-medium tracking-tight">
              AI-Powered Internal IT Service & Resolution Agent
            </p>
          </div>
        </div>

        {/* Operational Status Badges */}
        <div className="flex items-center gap-2 sm:gap-3 text-xs">
          {/* Simulation Anchor Banner */}
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#121b2f] border border-[#223254] text-slate-300">
            <Calendar className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-mono text-[11px] text-cyan-200">Sep 21–25, 2026</span>
          </div>

          {/* AI Provider Badge */}
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#121b2f] border border-[#223254] text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-slate-400">Rules Engine:</span>
            <span className="font-mono text-[11px] text-indigo-200 uppercase font-medium">
              {systemInfo?.active_llm_provider || 'Hybrid'}
            </span>
          </div>

          {/* Backend Health Connection Pill */}
          <button
            onClick={onOpenStatusModal}
            title="Click to view full system diagnostics"
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-[11px] font-medium transition-all cursor-pointer hover:brightness-110 ${
              isConnected 
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20' 
                : 'bg-rose-500/10 border-rose-500/30 text-rose-300 hover:bg-rose-500/20'
            }`}
          >
            {isConnected ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="font-semibold">Backend Live</span>
              </>
            ) : (
              <>
                <AlertTriangle className="w-3 h-3 text-rose-400" />
                <span>Backend Offline</span>
              </>
            )}
            <Activity className="w-3 h-3 text-slate-400 ml-0.5 hidden sm:inline" />
          </button>
        </div>
      </div>
    </header>
  );
};
