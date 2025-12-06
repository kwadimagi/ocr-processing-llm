'use client';

import { useEffect, useState } from 'react';
import { getUserInvoices } from '@/lib/api';
import type { Invoice } from '@/types';

export function InvoiceDashboard() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getUserInvoices()
      .then(setInvoices)
      .catch(err => console.error('Failed to load invoices:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-center py-4">Loading invoices...</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Your Invoices</h2>
      {invoices.length === 0 ? (
        <p className="text-gray">No invoices processed yet.</p>
      ) : (
        <div className="grid gap-3">
          {invoices.map(invoice => (
            <div 
              key={invoice.id} 
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{invoice.vendor_name}</h3>
                  <p className="text-sm text-gray-600">#{invoice.invoice_number}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  invoice.status === 'paid' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {invoice.status}
                </span>
              </div>
              <div className="mt-2 flex justify-between items-center">
                <span className="text-lg font-bold">
                  {invoice.currency} {invoice.total_amount.toLocaleString()}
                </span>
                <span className="text-sm text-gray-500">
                  Due: {invoice.due_date ? new Date(invoice.due_date).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}