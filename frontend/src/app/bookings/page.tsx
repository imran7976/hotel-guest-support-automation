'use client';

import React, { useEffect, useState } from 'react';
import { Header } from '@/components/Header';
import { api, Booking } from '@/lib/api';
import {
  CalendarCheck2,
  Search,
  Filter,
  CheckCircle,
  AlertCircle,
  Clock,
  Edit3,
  XCircle,
  RefreshCw,
  BedDouble,
  DollarSign
} from 'lucide-react';

export default function BookingsPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchRef, setSearchRef] = useState('');
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [actionType, setActionType] = useState<'modify' | 'cancel' | null>(null);
  const [reason, setReason] = useState('');
  const [newCheckIn, setNewCheckIn] = useState('');
  const [newCheckOut, setNewCheckOut] = useState('');
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const loadBookings = async () => {
    try {
      setLoading(true);
      const data = await api.getBookings(statusFilter);
      setBookings(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadBookings();
  }, [statusFilter]);

  const handleActionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBooking) return;
    try {
      setSubmitting(true);
      setActionMessage(null);
      if (actionType === 'modify') {
        const res = await api.submitModification(selectedBooking.id, {
          new_check_in_date: newCheckIn || undefined,
          new_check_out_date: newCheckOut || undefined,
          reason,
        });
        setActionMessage(res.message);
      } else if (actionType === 'cancel') {
        const res = await api.submitCancellation(selectedBooking.id, {
          reason,
          request_refund: true,
        });
        setActionMessage(res.message);
      }
      loadBookings();
      setReason('');
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const filteredBookings = bookings.filter(
    (b) =>
      b.booking_reference.toLowerCase().includes(searchRef.toLowerCase()) ||
      b.guest?.first_name.toLowerCase().includes(searchRef.toLowerCase()) ||
      b.guest?.last_name.toLowerCase().includes(searchRef.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      <Header
        title="Booking Management"
        subtitle="Manage simulated hotel reservations, room inventories, modifications, and cancellation requests."
        action={
          <button
            onClick={loadBookings}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        }
      />

      <div className="flex-1 p-8 space-y-6 overflow-y-auto">
        {/* Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200">
          <div className="relative w-full sm:w-80">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={searchRef}
              onChange={(e) => setSearchRef(e.target.value)}
              placeholder="Search reference or guest name..."
              className="w-full pl-9 pr-3 py-2 bg-slate-50 rounded-lg border border-slate-200 text-xs focus:ring-2 focus:ring-sky-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-500">Status:</span>
            {['all', 'confirmed', 'pending_modification', 'pending_cancellation', 'cancelled'].map((st) => (
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
        </div>

        {/* Bookings Table */}
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-6 py-3.5 font-semibold">Booking Ref</th>
                <th className="px-6 py-3.5 font-semibold">Guest</th>
                <th className="px-6 py-3.5 font-semibold">Room Type</th>
                <th className="px-6 py-3.5 font-semibold">Dates</th>
                <th className="px-6 py-3.5 font-semibold">Total</th>
                <th className="px-6 py-3.5 font-semibold">Status</th>
                <th className="px-6 py-3.5 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400">
                    Loading reservations...
                  </td>
                </tr>
              ) : filteredBookings.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400">
                    No bookings found.
                  </td>
                </tr>
              ) : (
                filteredBookings.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-50/80 transition-all">
                    <td className="px-6 py-4 font-mono font-bold text-sky-700">
                      {b.booking_reference}
                    </td>
                    <td className="px-6 py-4">
                      <p className="font-semibold text-slate-800">
                        {b.guest?.first_name} {b.guest?.last_name}
                      </p>
                      <p className="text-[11px] text-slate-400">{b.guest?.email}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-medium text-slate-700">
                        {b.room?.room_type || 'Deluxe Suite'}
                      </span>
                      <p className="text-[11px] text-slate-400">Room #{b.room?.room_number}</p>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-slate-700 font-medium">{b.check_in_date}</p>
                      <p className="text-[11px] text-slate-400">to {b.check_out_date}</p>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-800">
                      ${b.total_amount}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          b.status === 'confirmed'
                            ? 'bg-emerald-100 text-emerald-800'
                            : b.status === 'cancelled'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {b.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button
                        onClick={() => {
                          setSelectedBooking(b);
                          setActionType('modify');
                          setActionMessage(null);
                        }}
                        className="px-2.5 py-1 rounded-md border border-slate-200 text-slate-600 hover:bg-slate-100 font-semibold"
                      >
                        Modify
                      </button>
                      <button
                        onClick={() => {
                          setSelectedBooking(b);
                          setActionType('cancel');
                          setActionMessage(null);
                        }}
                        className="px-2.5 py-1 rounded-md border border-red-200 text-red-600 hover:bg-red-50 font-semibold"
                      >
                        Cancel
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Modal for Action Request */}
        {selectedBooking && actionType && (
          <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="font-bold text-slate-900 text-sm">
                  {actionType === 'modify' ? 'Request Modification' : 'Request Cancellation & Refund'}
                </h3>
                <span className="font-mono text-xs text-sky-600 font-bold">
                  {selectedBooking.booking_reference}
                </span>
              </div>

              {actionMessage && (
                <div className="p-3 rounded-lg bg-sky-50 border border-sky-200 text-sky-800 text-xs">
                  {actionMessage}
                </div>
              )}

              <form onSubmit={handleActionSubmit} className="space-y-3 text-xs">
                {actionType === 'modify' && (
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="font-semibold text-slate-700 block mb-1">New Check-In</label>
                      <input
                        type="date"
                        value={newCheckIn}
                        onChange={(e) => setNewCheckIn(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                      />
                    </div>
                    <div>
                      <label className="font-semibold text-slate-700 block mb-1">New Check-Out</label>
                      <input
                        type="date"
                        value={newCheckOut}
                        onChange={(e) => setNewCheckOut(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                      />
                    </div>
                  </div>
                )}

                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Reason for Request</label>
                  <textarea
                    rows={3}
                    required
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Provide guest reason or modification context..."
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs"
                  />
                </div>

                <p className="text-[11px] text-slate-400">
                  Note: In compliance with hotel policy, cancellations and modifications are placed into
                  a pending state and automatically create an escalation ticket for human manager authorization.
                </p>

                <div className="flex justify-end gap-2 pt-3">
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedBooking(null);
                      setActionType(null);
                    }}
                    className="px-3 py-2 rounded-lg border border-slate-200 text-slate-600 font-medium"
                  >
                    Close
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className={`px-4 py-2 rounded-lg text-white font-semibold shadow-xs disabled:opacity-50 ${
                      actionType === 'modify' ? 'bg-sky-600 hover:bg-sky-700' : 'bg-red-600 hover:bg-red-700'
                    }`}
                  >
                    {submitting ? 'Submitting...' : 'Submit to Management'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

