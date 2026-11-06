import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'AI Hotel Support Automation Platform - Grand Azure',
  description: 'AI-Powered Hotel Guest Support Automation Platform integrating FastAPI, OpenAI, RAG, and n8n.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-50 min-h-screen text-slate-800 antialiased flex">
        <Sidebar />
        <main className="flex-1 ml-64 min-h-screen flex flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}

