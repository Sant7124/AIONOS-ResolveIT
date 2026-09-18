import React, { useState } from 'react';
import { 
  Search, 
  BookOpen, 
  Clock, 
  AlertCircle, 
  CheckCircle2, 
  ShieldAlert, 
  FileText, 
  ChevronDown, 
  ChevronUp, 
  ExternalLink,
  Shield,
  Layers,
  X
} from 'lucide-react';
import { Policy } from '../types';

interface KnowledgeBaseViewProps {
  policies: Policy[];
  isLoading?: boolean;
}

export const KnowledgeBaseView: React.FC<KnowledgeBaseViewProps> = ({ 
  policies,
  isLoading = false 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [expandedPolicyId, setExpandedPolicyId] = useState<string | null>(null);

  const categories = ['All', ...Array.from(new Set(policies.map(p => p.category)))];

  const filteredPolicies = policies.filter(p => {
    const query = searchQuery.toLowerCase();
    const matchesSearch = 
      p.title.toLowerCase().includes(query) ||
      p.content.toLowerCase().includes(query) ||
      p.id.toLowerCase().includes(query) ||
      p.summary.toLowerCase().includes(query) ||
      p.prerequisites.some(pre => pre.toLowerCase().includes(query)) ||
      (p.sla && p.sla.toLowerCase().includes(query));
      
    const matchesCategory = selectedCategory === 'All' || p.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const toggleExpand = (id: string) => {
    setExpandedPolicyId(prev => prev === id ? null : id);
  };

  return (
    <div className="space-y-6">
      {/* Header & Filter Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-cyan-400" />
            Veridian Knowledge Base & IT Policies
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Official corporate policies from Data Pack (KB-01 to KB-10 & Asset Management Policy Extract)
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search policies, SLAs, or conditions..."
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
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs no-scrollbar">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-xl whitespace-nowrap border transition-all cursor-pointer ${
              selectedCategory === cat
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-semibold shadow-sm shadow-cyan-500/10'
                : 'bg-[#121b2f]/80 text-slate-400 border-[#223254] hover:text-slate-200 hover:border-slate-600'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="p-5 rounded-2xl bg-[#121b2f]/60 border border-[#223254] animate-pulse space-y-3">
              <div className="h-4 bg-[#18243e] rounded w-1/3" />
              <div className="h-16 bg-[#18243e] rounded" />
              <div className="h-4 bg-[#18243e] rounded w-1/2" />
            </div>
          ))}
        </div>
      )}

      {/* Empty State: No Policies Loaded */}
      {!isLoading && policies.length === 0 && (
        <div className="p-12 rounded-2xl bg-[#0c1222]/80 border border-[#223254] text-center space-y-3">
          <BookOpen className="w-10 h-10 text-slate-500 mx-auto" />
          <h3 className="text-sm font-bold text-white">No Policies Found in Database</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Please run the backend database seeding script (<code className="text-cyan-300 font-mono">python -m app.database.seed</code>) to populate KB-01 through KB-10.
          </p>
        </div>
      )}

      {/* No Search Results */}
      {!isLoading && policies.length > 0 && filteredPolicies.length === 0 && (
        <div className="p-10 rounded-2xl bg-[#0c1222]/80 border border-[#223254] text-center space-y-3">
          <AlertCircle className="w-8 h-8 text-amber-400 mx-auto" />
          <h3 className="text-sm font-bold text-white">No Policies Matching "{searchQuery}"</h3>
          <p className="text-xs text-slate-400">
            Try searching for another keyword like "VPN", "password", "laptop", "printer", or "phishing".
          </p>
          <button
            onClick={() => { setSearchQuery(''); setSelectedCategory('All'); }}
            className="px-3.5 py-1.5 rounded-lg bg-[#18243e] hover:bg-[#223254] text-slate-200 text-xs transition-colors"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Policy Grid */}
      {!isLoading && filteredPolicies.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredPolicies.map((policy) => {
            const isExpanded = expandedPolicyId === policy.id;
            return (
              <div
                key={policy.id}
                className={`p-5 rounded-2xl bg-[#0c1222]/90 border transition-all flex flex-col justify-between space-y-4 shadow-lg ${
                  isExpanded ? 'border-cyan-500/50 bg-[#121b2f]/90' : 'border-[#223254] hover:border-cyan-500/30'
                }`}
              >
                <div className="space-y-3">
                  {/* Top Bar: ID, Title, Category */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-2.5">
                      <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shrink-0">
                        {policy.id}
                      </span>
                      <div>
                        <h3 className="text-sm font-bold text-white leading-tight">
                          {policy.title}
                        </h3>
                        <span className="text-[10px] uppercase font-mono text-slate-400">
                          {policy.category}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => toggleExpand(policy.id)}
                      className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-[#18243e] transition-colors"
                      title={isExpanded ? "Collapse policy details" : "Expand policy details"}
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>

                  {/* Summary */}
                  <p className="text-xs text-slate-300 leading-relaxed font-sans">
                    {policy.summary}
                  </p>

                  {/* Verbatim Source Quote Snippet */}
                  <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254]/70 text-xs text-slate-300 space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                      <FileText className="w-3 h-3 text-cyan-400" />
                      Data Pack Statement
                    </span>
                    <p className="text-[11px] text-slate-300 italic leading-relaxed">
                      "{policy.content}"
                    </p>
                  </div>

                  {/* Expandable Extended Details */}
                  {isExpanded && (
                    <div className="pt-2 border-t border-[#223254]/70 space-y-3 text-xs animate-in fade-in-50 duration-150">
                      {/* Prerequisites / Conditions */}
                      {policy.prerequisites && policy.prerequisites.length > 0 && (
                        <div className="space-y-1">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-300">
                            Prerequisites & Governance Conditions:
                          </span>
                          <ul className="space-y-1 text-[11px] text-slate-300">
                            {policy.prerequisites.map((pre, i) => (
                              <li key={i} className="flex items-start gap-1.5">
                                <span className="text-cyan-400 font-bold">•</span>
                                <span>{pre}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Required Approvals */}
                      <div className="space-y-1">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-amber-300">
                          Sign-Off & Approval Authority:
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {policy.approvals_required && policy.approvals_required.length > 0 ? (
                            policy.approvals_required.map((appr, i) => (
                              <span key={i} className="font-mono text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                                {appr}
                              </span>
                            ))
                          ) : (
                            <span className="text-[11px] text-emerald-300 flex items-center gap-1">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                              Zero approvals needed (Direct Self-Service)
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Escalation Rules */}
                      {policy.resolution_type && (
                        <div className="space-y-1">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-300">
                            Resolution Workflow:
                          </span>
                          <p className="text-[11px] text-slate-300">
                            {policy.resolution_type}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Bottom Metadata Badges */}
                <div className="pt-2 border-t border-[#223254]/50 flex flex-wrap items-center justify-between gap-2 text-[11px]">
                  {policy.sla ? (
                    <span className="flex items-center gap-1 text-slate-400">
                      <Clock className="w-3.5 h-3.5 text-cyan-400" />
                      <span className="font-mono">{policy.sla}</span>
                    </span>
                  ) : (
                    <span className="text-slate-400">Instant Fulfillment</span>
                  )}

                  <button
                    onClick={() => toggleExpand(policy.id)}
                    className="text-[11px] text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1 transition-colors"
                  >
                    <span>{isExpanded ? 'Show Less' : 'Full Policy Details'}</span>
                    {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
