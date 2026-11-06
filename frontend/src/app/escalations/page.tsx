'use client';

import React, { useEffect, useState } from 'react';
import { Header } from '@/components/Header';
import { api, Escalation } from '@/lib/api';
import {
  AlertTriangle,
  Search,
  Filter,
  CheckCircle,
  Clock,
  User,
  MessageSquare,
  RefreshCw,
  Send,
  ShieldAlert
} from 'lucide-react';

export default function EscalationsPage() {
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('pending');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [selectedEscalation, setSelectedEscalation] = useState<Escalation | null>(null);
  const [staffResponse, setStaffResponse] = useState('');
  const [updating, setUpdating] = useState(false);

  const loadEscalations = async () => {
    try {
      setLoading(true);
      const data = await api.getEscalations(
        statusFilter === 'all' ? undefined : statusFilter,
        priorityFilter === 'all' ? undefined : priorityFilter
      );
      setEscalations(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEscalations();
  }, [statusFilter, priorityFilter]);

  const handleResolve = async (status: string) => {
    if (!selectedEscalation) return;
    try {
      setUpdating(true);
      await api.updateEscalation(selectedEscalation.id, {
        status,
        staff_response: staffResponse || undefined,
      });
      loadEscalations();
      setSelectedEscalation(null);
      setStaffResponse('');
    } catch (err) {
      console.error(err);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Header
        title="Escalation Management"
        subtitle="Human-in-the-loop triage: review high-priority complaints, refunds, and AI edge cases."
        action={
          <button
            onClick={loadEscalations}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        }
      />

      <div className="flex-1 p-8 space-y-6 overflow-y-auto">
        {/* Filters */}
        <div className="flex flex-wrap items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Status:</span>
            {['all', 'pending', 'in_progress', 'resolved'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition-all ${
                  statusFilter === st
                    ? 'bg-sky-600 text-white shadow-xs'
                    : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {st.replace(/_/g, ' ')}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Priority:</span>
            {['all', 'urgent', 'high', 'normal', 'low'].map((pr) => (
              <button
                key={pr}
                onClick={() => setPriorityFilter(pr)}
                className={`px-2.5 py-1 rounded-md text-xs font-medium capitalize transition-all ${
                  priorityFilter === pr
                    ? 'bg-slate-800 text-white'
                    : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {pr}
              </button>
            ))}
          </div>
        </div>

        {/* Escalation Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {loading ? (
            <div className="col-span-full py-12 text-center text-xs text-slate-400">
              Loading escalations...
            </div>
          ) : escalations.length === 0 ? (
            <div className="col-span-full py-12 text-center text-xs text-slate-400">
              No escalations match the selected filters. Good work!
            </div>
          ) : (
            escalations.map((esc) => {
              const isUrgent = esc.priority === 'urgent';
              const isHigh = esc.priority === 'high';
              const isResolved = esc.status === 'resolved';

              return (
                <div
                  key={esc.id}
                  className={`bg-white rounded-xl border p-5 shadow-xs flex flex-col justify-between transition-all hover:shadow-md ${
                    isUrgent
                      ? 'border-red-300 ring-1 ring-red-200'
                      : isHigh
                      ? 'border-amber-300'
                      : 'border-slate-200'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <span className="font-mono text-xs font-bold text-slate-500">
                        ESC #{esc.id}
                      </span>
                      <div className="flex gap-1.5">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                            isUrgent
                              ? 'bg-red-100 text-red-800'
                              : isHigh
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-slate-100 text-slate-700'
                          }`}
                        >
                          {esc.priority}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                            isResolved
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-sky-100 text-sky-800'
                          }`}
                        >
                          {esc.status}
                        </span>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-slate-900">
                        {esc.guest?.first_name} {esc.guest?.last_name}
                      </h4>
                      <p className="text-[11px] text-slate-400">{esc.guest?.email}</p>
                    </div>

                    <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs text-slate-700">
                      <span className="font-semibold text-slate-500 text-[10px] uppercase block mb-0.5">
                        Inquiry:
                      </span>
                      &ldquo;{esc.inquiry_text}&rdquo;
                    </div>

                    <div className="text-[11px] text-amber-900 bg-amber-50/70 p-2 rounded border border-amber-100">
                      <span className="font-bold">Reason:</span> {esc.escalation_reason}
                    </div>

                    {esc.staff_response && (
                      <div className="text-[11px] text-emerald-900 bg-emerald-50 p-2 rounded border border-emerald-100">
                        <span className="font-bold">Staff Resolution:</span> {esc.staff_response}
                      </div>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-[10px] text-slate-400 font-mono">
                      {new Date(esc.created_at).toLocaleString([], {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                    {!isResolved && (
                      <button
                        onClick={() => {
                          setSelectedEscalation(esc);
                          setStaffResponse('');
                        }}
                        className="px-3 py-1 bg-slate-800 hover:bg-slate-900 text-white font-semibold text-xs rounded-md shadow-xs transition-all"
                      >
                        Action / Resolve
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Modal for Action / Staff Resolution */}
        {selectedEscalation && (
          <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="font-bold text-slate-900 text-sm">
                  Resolve Escalation #{selectedEscalation.id}
                </h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-100 text-red-700">
                  {selectedEscalation.priority}
                </span>
              </div>

              <div className="space-y-2 text-xs">
                <p>
                  <span className="font-semibold text-slate-600">Guest:</span>{' '}
                  {selectedEscalation.guest?.first_name} {selectedEscalation.guest?.last_name} (
                  {selectedEscalation.guest?.email})
                </p>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                  <span className="font-semibold text-slate-500 block mb-1">Guest Inquiry:</span>
                  {selectedEscalation.inquiry_text}
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">
                    Staff Response / Resolution Note
                  </label>
                  <textarea
                    rows={4}
                    value={staffResponse}
                    onChange={(e) => setStaffResponse(e.target.value)}
                    placeholder="Enter resolution notes, actions taken, or reply sent to guest..."
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setSelectedEscalation(null)}
                  className="px-3 py-2 rounded-lg border border-slate-200 text-slate-600 font-medium text-xs"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => handleResolve('in_progress')}
                  disabled={updating}
                  className="px-3 py-2 rounded-lg bg-sky-600 hover:bg-sky-700 text-white font-semibold text-xs disabled:opacity-50"
                >
                  Mark In Progress
                </button>
                <button
                  type="button"
                  onClick={() => handleResolve('resolved')}
                  disabled={updating}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs disabled:opacity-50 shadow-xs"
                >
                  Mark Resolved
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

