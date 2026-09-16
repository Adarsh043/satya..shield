import { useState } from 'react';
import { useVerification } from '../../context/VerificationContext';
import { useTranslation } from 'react-i18next';
import { Search, Filter, Eye } from 'lucide-react';
import clsx from 'clsx';

export default function VisitorHistory() {
  const { requests } = useVerification();
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Filter for completed/rejected verifications only
  const historyRequests = requests.filter(req => req.status === 'Verified / Accepted' || req.status === 'Rejected');

  const filteredRequests = historyRequests.filter(req => {
    const matchesSearch = req.id.toLowerCase().includes(searchTerm.toLowerCase()) || req.documentType.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || req.status.includes(statusFilter);
    return matchesSearch && matchesStatus;
  });

  const formatDate = (isoString: string) => {
    return new Date(isoString).toLocaleString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit', hour12: true
    });
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-navy">Verification History</h2>
          <p className="text-light text-sm mt-1">View your past completed and rejected verification requests.</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex flex-col md:flex-row justify-between items-center bg-gray-50/50 gap-4">
          <div className="relative w-full md:w-64">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-light" />
            <input 
              type="text" 
              placeholder={t('Search Token or Document...')}
              className="w-full pl-10 pr-4 h-10 border border-gray-300 rounded-lg text-sm outline-none focus:border-primary" 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2 w-full md:w-auto h-10">
            <Filter size={16} className="text-light" />
            <select 
              className="text-sm border border-gray-300 rounded-lg h-10 px-3 outline-none focus:border-primary bg-white"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="Verified">Verified</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 text-xs font-bold text-light uppercase tracking-wider border-b border-gray-200">
                <th className="p-4 pl-6">Token Number</th>
                <th className="p-4">Document Type</th>
                <th className="p-4">Submitted At</th>
                <th className="p-4">Verification Date</th>
                <th className="p-4">Status</th>
                <th className="p-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredRequests.map(req => (
                <tr key={req.id} className="hover:bg-gray-50/80 transition-colors">
                  <td className="p-4 pl-6 font-semibold text-primary">{req.id}</td>
                  <td className="p-4 font-medium text-navy">{req.documentType}</td>
                  <td className="p-4 text-light text-sm">{formatDate(req.submittedAt)}</td>
                  <td className="p-4 text-light text-sm">
                    {req.status === 'Verified / Accepted' ? formatDate(req.verifiedAt!) : formatDate(req.rejectedAt!)}
                  </td>
                  <td className="p-4">
                    <span className={clsx('px-2.5 py-1 rounded-full text-xs font-bold whitespace-nowrap', 
                      req.status === 'Verified / Accepted' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    )}>
                      {req.status === 'Verified / Accepted' ? 'VERIFIED' : 'REJECTED'}
                    </span>
                  </td>
                  <td className="p-4">
                    <button className="text-sm font-semibold text-primary hover:underline flex items-center gap-1">
                      <Eye size={14}/> View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {filteredRequests.length === 0 && (
            <div className="p-8 text-center text-light">
              No history records found.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
