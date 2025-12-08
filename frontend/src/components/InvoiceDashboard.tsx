'use client';

import { useEffect, useState } from 'react';
import { getUserInvoices } from '@/lib/api';
import { exportToCSV, exportToExcel, exportToPDF } from '@/lib/exportUtils';
import type { Invoice } from '@/types';
import { Download, FileSpreadsheet, FileText } from 'lucide-react';

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
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Your Invoices</h2>
        {invoices.length > 0 && (
          <div className="flex gap-2">
            <button
              onClick={() => exportToCSV(invoices)}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
              title="Export to CSV"
            >
              <FileText size={16} />
              CSV
            </button>
            <button
              onClick={() => exportToExcel(invoices)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
              title="Export to Excel"
            >
              <FileSpreadsheet size={16} />
              Excel
            </button>
            <button
              onClick={() => exportToPDF(invoices)}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
              title="Export to PDF"
            >
              <Download size={16} />
              PDF
            </button>
          </div>
        )}
      </div>
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