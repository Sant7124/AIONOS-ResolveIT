import React, { useState } from 'react';
import { CheckSquare, ArrowRight, User, Calendar, Search, X, BookOpen, Clock } from 'lucide-react';
import { EmployeeRequest } from '../types';

interface ScenariosViewProps {
  requests: EmployeeRequest[];
  onSelectRequest: (request: EmployeeRequest) => void;
}

export const ScenariosView: React.FC<ScenariosViewProps> = ({ requests, onSelectRequest }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const categories = ['All', ...Array.from(new Set(requests.map(r => r.category || 'General IT')))];

  const filteredRequests = requests.filter((req) => {
    const q = searchQuery.toLowerCase();
    const matchesSearch = 
      req.request_id.toLowerCase().includes(q) ||
      req.employee.toLowerCase().includes(q) ||
      req.request.toLowerCase().includes(q) ||
      (req.expected_policy_id && req.expected_policy_id.toLowerCase().includes(q)) ||
      (req.category && req.category.toLowerCase().includes(q));

    const matchesCategory = selectedCategory === 'All' || (req.category || 'General IT') === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-indigo-400" />
            My Requests & Benchmark Scenarios (15 Data Pack Cases)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Section 2 of the Data Pack — Click any employee request to evaluate with AIONOS ResolveIT
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search request ID, employee, issue..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-8 py-2 rounded-xl bg-[#0c1222] border border-[#223254] text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors shadow-sm"
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
                ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40 font-semibold shadow-sm'
                : 'bg-[#121b2f]/80 text-slate-400 border-[#223254] hover:text-slate-200 hover:border-slate-600'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Grid of Requests */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredRequests.map((req) => (
          <div
            key={req.request_id}
            className="p-5 rounded-2xl bg-[#0c1222]/95 border border-[#223254] hover:border-indigo-500/50 transition-all flex flex-col justify-between space-y-4 shadow-lg group cursor-pointer"
            onClick={() => onSelectRequest(req)}
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold px-2.5 py-1 rounded-lg bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                  {req.request_id}
                </span>
                <span className="flex items-center gap-1 text-[11px] text-slate-400 font-mono">
                  <Calendar className="w-3 h-3 text-slate-400" />
                  {req.date_opened}
                </span>
              </div>

              {/* Employee Info */}
              <div className="flex items-center gap-2 text-xs text-slate-300">
                <User className="w-4 h-4 text-cyan-400 shrink-0" />
                <span className="font-semibold text-white">{req.employee}</span>
                <span className="text-[10px] text-slate-400 font-mono truncate">({req.email})</span>
              </div>

              {/* Raw Request Text */}
              <div className="p-3 rounded-xl bg-[#121b2f] border border-[#223254]/70 text-xs text-cyan-100 font-sans italic leading-relaxed">
                "{req.request}"
              </div>

              {/* Policy Grounding Expectations */}
              <div className="space-y-1 text-[11px] pt-1">
                <div className="flex items-center gap-1.5 text-slate-400">
                  <BookOpen className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                  <span>Expected:</span>
                  <span className="font-mono font-semibold text-emerald-400">
                    {req.expected_policy_id || 'Clarification Prompt'}
                  </span>
                  {req.cross_reference_policy_id && (
                    <span className="font-mono text-amber-300">
                      + {req.cross_reference_policy_id}
                    </span>
                  )}
                </div>
                {req.category && (
                  <div className="text-[10px] text-slate-400 uppercase font-mono">
                    Category: {req.category}
                  </div>
                )}
              </div>
            </div>

            {/* Action Button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                onSelectRequest(req);
              }}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition-all group-hover:border-indigo-400 cursor-pointer shadow-sm"
            >
              <span>Test in ResolveIT</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        ))}
      </div>

      {filteredRequests.length === 0 && (
        <div className="p-12 rounded-2xl bg-[#0c1222]/80 border border-[#223254] text-center space-y-2">
          <CheckSquare className="w-8 h-8 text-slate-500 mx-auto" />
          <h3 className="text-sm font-bold text-white">No requests match "{searchQuery}"</h3>
          <p className="text-xs text-slate-400">Try searching by employee name or clearing filters.</p>
        </div>
      )}
    </div>
  );
};
