import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, Eye } from 'lucide-react';
import clsx from 'clsx';

interface Appointment {
  booking_number: string;
  visitor_name: string;
  document_type: string;
  source: string;
  status: string;
  created_at: string;
}

export default function ForceHistory() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [requests, setRequests] = useState<Appointment[]>([]);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/v1/officer/appointments');
        if (res.ok) {
          const data = await res.json();
          setRequests(data);
        }
      } catch (err) {
        console.error("Error fetching appointments:", err);
      }
    };
    fetchAppointments();
  }, []);

  // Filter for completed/rejected verifications only
  const historyRequests = requests.filter(req => req.status === 'VERIFIED' || req.status === 'REJECTED');

  const filteredRequests = historyRequests.filter(req => {
    const matchesSearch = (req.booking_number?.toLowerCase() || '').includes(searchTerm.toLowerCase()) || 
                          (req.visitor_name?.toLowerCase() || '').includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || (req.status || '').includes(statusFilter);
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
          <h2 className="text-2xl font-bold text-navy">Operations History</h2>
          <p className="text-light text-sm mt-1">Archive of all completed and rejected verifications.</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex flex-col md:flex-row justify-between items-center bg-gray-50/50 gap-4">
          <div className="relative w-full md:w-64">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-light" />
            <input 
              type="text" 
              placeholder={t('Search Token or Name...')}
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
              <option value="VERIFIED">Verified</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 text-xs font-bold text-light uppercase tracking-wider border-b border-gray-200">
                <th className="p-4 pl-6">Token</th>
                <th className="p-4">Visitor</th>
                <th className="p-4">Document</th>
                <th className="p-4">Submitted At</th>
                <th className="p-4">Status</th>
                <th className="p-4">Risk</th>
                <th className="p-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredRequests.map(req => (
                <tr key={req.booking_number} className="hover:bg-gray-50/80 transition-colors">
                  <td className="p-4 pl-6 font-semibold text-primary">{req.booking_number}</td>
                  <td className="p-4 font-medium text-navy">{req.visitor_name}</td>
                  <td className="p-4 text-light">{req.document_type}</td>
                  <td className="p-4 text-light text-sm">{formatDate(req.created_at)}</td>
                  <td className="p-4">
                    <span className={clsx('px-2.5 py-1 rounded-full text-xs font-bold whitespace-nowrap', 
                      req.status === 'VERIFIED' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    )}>
                      {req.status}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-gray-500 bg-gray-100 px-2.5 py-1 rounded text-xs font-bold">
                      RESOLVED
                    </span>
                  </td>
                  <td className="p-4">
                    <button 
                      onClick={() => navigate(`/force-dashboard/verify/${req.booking_number}`)}
                      className="text-sm font-semibold text-primary hover:underline flex items-center gap-1"
                    >
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
