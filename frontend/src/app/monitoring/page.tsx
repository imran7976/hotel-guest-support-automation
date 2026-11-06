'use client';

import React, { useEffect, useState } from 'react';
import { Header } from '@/components/Header';
import { api, WorkflowLog } from '@/lib/api';
import {
  Workflow,
  CheckCircle2,
  AlertCircle,
  Clock,
  RotateCcw,
  RefreshCw,
  Terminal,
  Activity,
  Layers
} from 'lucide-react';

interface WorkflowMeta {
  name: string;
  file: string;
  trigger: string;
  status: 'active' | 'standby';
  description: string;
}

const n8nWorkflows: WorkflowMeta[] = [
  {
    name: 'Guest Inquiry Processing',
    file: '01_guest_inquiry_processing.json',
    trigger: 'POST /webhook/guest-inquiry',
    status: 'active',
    description: 'Ingests external inquiry payloads, runs FastAPI AI intent classification, saves conversation, and checks escalation.',
  },
  {
    name: 'Complaint Escalation',
    file: '02_complaint_escalation.json',
    trigger: 'POST /webhook/complaint-escalation',
    status: 'active',
    description: 'Triages complaints, assigns urgent priority, syncs MySQL records, and dispatches automated alerts to Duty Manager.',
  },
  {
    name: 'Automated Guest Follow-up',
    file: '03_automated_guest_followup.json',
    trigger: 'Schedule (Every 4h)',
    status: 'active',
    description: 'Scans unresolved guest tickets, drafts warm courtesy follow-up messages, and queues them for delivery.',
  },
  {
    name: 'Daily Support Summary',
    file: '04_daily_support_summary.json',
    trigger: 'Cron (Daily 23:00)',
    status: 'active',
    description: 'Calculates inquiry statistics, aggregates category breakdown, formats executive AI digest, and alerts General Manager.',
  },
  {
    name: 'Workflow Error Monitoring',
    file: '05_workflow_error_monitoring.json',
    trigger: 'Global Error Trigger',
    status: 'active',
    description: 'Catches execution stack traces, records failure logs in MySQL, alerts Ops Admin, and orchestrates retries.',
  },
];

export default function AutomationMonitoringPage() {
  const [logs, setLogs] = useState<WorkflowLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWorkflow, setSelectedWorkflow] = useState('all');

  const loadLogs = async () => {
    try {
      setLoading(true);
      const data = await api.getWorkflowLogs(
        selectedWorkflow === 'all' ? undefined : selectedWorkflow
      );
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, [selectedWorkflow]);

  // Compute metrics per workflow
  const getWorkflowStats = (name: string) => {
    const wfLogs = logs.filter((l) => l.workflow_name.toLowerCase().includes(name.toLowerCase()));
    const successCount = wfLogs.filter((l) => l.status === 'success').length;
    const failureCount = wfLogs.filter((l) => l.status === 'failed').length;
    const lastLog = wfLogs.length > 0 ? wfLogs[0] : null;

    return {
      total: wfLogs.length,
      successCount,
      failureCount,
      lastExecution: lastLog ? new Date(lastLog.created_at).toLocaleString() : 'Standby / Initialized',
    };
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Header
        title="Automation Monitoring (n8n Integration)"
        subtitle="Live orchestration health, webhook triggers, execution telemetry, and failure containment."
        action={
          <button
            onClick={loadLogs}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </button>
        }
      />

      <div className="flex-1 p-8 space-y-8 overflow-y-auto">
        {/* Workflows Status Cards */}
        <div>
          <h3 className="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2">
            <Layers className="h-4 w-4 text-sky-600" />
            Configured n8n Automation Workflows ({n8nWorkflows.length})
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {n8nWorkflows.map((wf) => {
              const stats = getWorkflowStats(wf.name);

              return (
                <div
                  key={wf.name}
                  className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between hover:border-slate-300 transition-all"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="h-8 w-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xs">
                        <Workflow className="h-4 w-4" />
                      </div>
                      <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        Active
                      </span>
                    </div>

                    <div>
                      <h4 className="font-bold text-slate-900 text-sm">{wf.name}</h4>
                      <p className="text-[11px] font-mono text-sky-600 mt-0.5">{wf.file}</p>
                    </div>

                    <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
                      {wf.description}
                    </p>

                    <div className="p-2 rounded-lg bg-slate-50 border border-slate-100 text-[11px]">
                      <span className="text-slate-400 block text-[9px] uppercase font-bold">Trigger:</span>
                      <span className="font-mono text-slate-700 font-semibold">{wf.trigger}</span>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-mono">
                    <span className="text-emerald-700 font-semibold">{stats.successCount} OK</span>
                    <span className="text-red-700 font-semibold">{stats.failureCount} ERR</span>
                    <span className="text-[10px] text-slate-400">{stats.lastExecution}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Real-time Execution Logs from Database */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <Terminal className="h-4 w-4 text-slate-700" />
                Live Execution Telemetry Logs
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Real-time records captured from MySQL `workflow_logs` table
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 font-medium">Filter:</span>
              <select
                value={selectedWorkflow}
                onChange={(e) => setSelectedWorkflow(e.target.value)}
                className="px-3 py-1.5 border border-slate-200 rounded-lg text-xs bg-slate-50"
              >
                <option value="all">All Workflows</option>
                {n8nWorkflows.map((w) => (
                  <option key={w.name} value={w.name}>
                    {w.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 text-[10px] uppercase font-semibold border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3">Log ID</th>
                  <th className="px-4 py-3">Workflow Name</th>
                  <th className="px-4 py-3">Trigger Event</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Details / Payload</th>
                  <th className="px-4 py-3 text-right">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-slate-400 font-sans">
                      Loading execution logs...
                    </td>
                  </tr>
                ) : logs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-slate-400 font-sans">
                      No workflow logs recorded yet. Send an inquiry via chat or webhook to populate.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => {
                    const isSuccess = log.status === 'success';
                    return (
                      <tr key={log.id} className="hover:bg-slate-50/80">
                        <td className="px-4 py-3 font-bold text-slate-600">#{log.id}</td>
                        <td className="px-4 py-3 font-semibold font-sans text-slate-900">
                          {log.workflow_name}
                        </td>
                        <td className="px-4 py-3 text-slate-500">{log.trigger_event}</td>
                        <td className="px-4 py-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              isSuccess
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {log.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-sans text-slate-600 max-w-xs truncate">
                          {log.error_message ? (
                            <span className="text-red-600 font-semibold">{log.error_message}</span>
                          ) : log.payload_json ? (
                            JSON.stringify(log.payload_json)
                          ) : (
                            'Execution recorded successfully.'
                          )}
                        </td>
                        <td className="px-4 py-3 text-right text-slate-400">
                          {new Date(log.created_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit',
                          })}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

