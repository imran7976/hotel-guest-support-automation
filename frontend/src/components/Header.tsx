'use client';

import React from 'react';
import { Bell, ShieldCheck, Sparkles } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export function Header({ title, subtitle, action }: HeaderProps) {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      <div>
        <h2 className="text-lg font-bold text-slate-800">{title}</h2>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {action}

        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium">
          <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
          <span>AI Safeguards Active</span>
        </div>

        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-sky-50 border border-sky-200 text-sky-700 text-xs font-medium">
          <Sparkles className="h-3.5 w-3.5 text-sky-600" />
          <span>RAG Knowledge Enabled</span>
        </div>

        <div className="h-8 w-px bg-slate-200" />

        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-slate-800 text-white flex items-center justify-center font-bold text-xs shadow-sm">
            FO
          </div>
          <div className="text-left hidden sm:block">
            <p className="text-xs font-semibold text-slate-800 leading-none">Front Desk</p>
            <p className="text-[10px] text-slate-400 mt-0.5">Duty Manager</p>
          </div>
        </div>
      </div>
    </header>
  );
}

