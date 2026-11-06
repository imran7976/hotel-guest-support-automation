'use client';

import React, { useEffect, useState } from 'react';
import { Header } from '@/components/Header';
import { api, DashboardKPIs } from '@/lib/api';
import {
  MessageSquare,
  Bot,
  AlertTriangle,
  Clock,
  TrendingUp,
  RefreshCw,
  Sparkles,
  ArrowUpRight,
  Activity,
  CheckCircle2
} from 'lucide-react';

export default function DashboardPage() {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDashboardKPIs();
      setKpis(data);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend API');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="flex-1 flex flex-col">
      <Header
        title="Guest Operations Dashboard"
        subtitle="Live automated inquiry triage, AI resolution metrics, and front-desk escalation queue."
        action={
          <button
            onClick={loadData}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        }
      />

      <div className="p-8 space-y-8 flex-1">
        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button onClick={loadData} className="underline text-xs font-semibold">Retry</button>
          </div>
        )}

        {/* Top KPI Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Total Inquiries */}
          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Inquiries</span>
              <div className="h-8 w-8 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center">
                <MessageSquare className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-slate-900">
                {loading ? '...' : kpis?.total_inquiries ?? 0}
              </span>
              <span className="text-xs text-slate-500 font-medium">
                ({kpis?.today_inquiries ?? 0} today)
              </span>
            </div>
            <p className="mt-2 text-[11px] text-slate-400">Processed across Web, Email & n8n</p>
          </div>

          {/* AI Automated Resolutions */}
          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">AI Resolved</span>
              <div className="h-8 w-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <Bot className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-emerald-600">
                {loading ? '...' : kpis?.ai_resolved_inquiries ?? 0}
              </span>
              <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">
                {kpis?.resolution_rate_percent ?? 100}% Rate
              </span>
            </div>
            <p className="mt-2 text-[11px] text-slate-400">Grounded via Hotel RAG policies</p>
          </div>

          {/* Pending Escalations */}
          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Pending Escalations</span>
              <div className="h-8 w-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                <AlertTriangle className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-amber-600">
                {loading ? '...' : kpis?.pending_escalations ?? 0}
              </span>
              <span className="text-xs text-slate-500">
                ({kpis?.resolved_escalations ?? 0} resolved)
              </span>
            </div>
            <p className="mt-2 text-[11px] text-slate-400">Requires front-desk staff action</p>
          </div>

          {/* Avg Response Time */}
          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs hover:border-slate-300 transition-all">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">Avg Latency</span>
              <div className="h-8 w-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                <Clock className="h-4 w-4" />
              </div>
            </div>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-slate-900">
                {loading ? '...' : `${kpis?.average_response_time_ms ?? 840}ms`}
              </span>
              <span className="text-xs font-semibold text-emerald-600">FastAPI</span>
            </div>
            <p className="mt-2 text-[11px] text-slate-400">Real-time classification & generation</p>
          </div>
        </div>

        {/* Main Section: Categories and Recent Activities */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Inquiry Categories */}
          <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h3 className="font-bold text-slate-800 text-sm">Inquiry Distribution</h3>
                <p className="text-xs text-slate-400 mt-0.5">Top guest inquiry topics</p>
              </div>
              <TrendingUp className="h-4 w-4 text-slate-400" />
            </div>

            <div className="mt-5 space-y-4">
              {kpis?.category_distribution && kpis.category_distribution.length > 0 ? (
                kpis.category_distribution.map((cat, idx) => (
                  <div key={idx} className="space-y-1.5">
                    <div className="flex justify-between text-xs font-medium">
                      <span className="text-slate-700 capitalize">
                        {cat.category.replace(/_/g, ' ')}
                      </span>
                      <span className="text-slate-500 font-mono">
                        {cat.count} ({cat.percentage}%)
                      </span>
                    </div>
                    <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-sky-500 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${Math.max(cat.percentage, 4)}%` }}
                      />
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">
                  No categorized inquiries recorded yet.
                </div>
              )}
            </div>
          </div>

          {/* Live Recent Support Activities */}
          <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h3 className="font-bold text-slate-800 text-sm">Recent Guest Activity Feed</h3>
                <p className="text-xs text-slate-400 mt-0.5">Real-time inquiries and staff actions from database</p>
              </div>
              <Activity className="h-4 w-4 text-sky-500" />
            </div>

            <div className="mt-4 divide-y divide-slate-100">
              {kpis?.recent_activities && kpis.recent_activities.length > 0 ? (
                kpis.recent_activities.map((act) => (
                  <div key={act.id} className="py-3 flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div
                        className={`mt-1 h-7 w-7 rounded-full flex items-center justify-center shrink-0 ${
                          act.type === 'inquiry'
                            ? 'bg-sky-50 text-sky-600'
                            : 'bg-emerald-50 text-emerald-600'
                        }`}
                      >
                        {act.type === 'inquiry' ? (
                          <MessageSquare className="h-3.5 w-3.5" />
                        ) : (
                          <CheckCircle2 className="h-3.5 w-3.5" />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="text-xs font-semibold text-slate-800">{act.title}</p>
                          {act.priority === 'urgent' && (
                            <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-red-100 text-red-700">
                              URGENT
                            </span>
                          )}
                          {act.priority === 'high' && (
                            <span className="px-1.5 py-0.2 rounded text-[10px] font-bold bg-amber-100 text-amber-700">
                              HIGH
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{act.description}</p>
                      </div>
                    </div>
                    <span className="text-[11px] text-slate-400 font-mono shrink-0">
                      {act.timestamp}
                    </span>
                  </div>
                ))
              ) : (
                <div className="text-center py-12 text-xs text-slate-400">
                  No guest activities logged yet. Submit a message in AI Support Chat to watch live feed!
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

