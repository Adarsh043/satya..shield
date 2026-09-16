import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Clock, AlertTriangle, Search, Filter } from 'lucide-react';
import clsx from 'clsx';

interface Appointment {
  booking_number: string;
  visitor_name: string;
  document_type: string;
  source: string;
  status: string;
  created_at: string;
}

export default function ForceOverview() {
  const [requests, setRequests] = useState<Appointment[]>([]);
  const { t } = useTranslation();
  const navigate = useNavigate();

  const kpis = [
    { label: 'Total Requests', value: requests.length, icon: <ShieldCheck size={24} />, color: 'text-primary bg-primary/10' },
    { label: 'Pending', value: requests.filter(r => r.status === 'PENDING' || r.status === 'IN_PROGRESS').length, icon: <Clock size={24} />, color: 'text-yellow-600 bg-yellow-100' },
    { label: 'Verified', value: requests.filter(r => r.status === 'VERIFIED').length, icon: <ShieldCheck size={24} />, color: 'text-green-600 bg-green-100' },
    { label: 'Rejected', value: requests.filter(r => r.status === 'REJECTED').length, icon: <AlertTriangle size={24} />, color: 'text-red-600 bg-red-100' }
  ];

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
    const intervalId = setInterval(fetchAppointments, 5000); // Poll every 5 seconds
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="space-y-6 fade-in">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-navy">Operations Command Centre</h2>
          <p className="text-light text-sm mt-1">Real-time verification queue and security metrics.</p>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {kpis.map((kpi, idx) => (
          <div key={idx} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-light mb-1">{kpi.label}</p>
              <h3 className="text-2xl font-bold text-navy">{kpi.value}</h3>
            </div>
            <div className={`p-3 rounded-full ${kpi.color}`}>
              {kpi.icon}
            </div>
          </div>
        ))}
      </div>

      {/* Queue */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-gray-200 flex justify-between items-center bg-gray-50/50">
          <h3 className="font-bold text-navy">{t('Verification Queue')}</h3>
          <div className="flex gap-4">
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-light" />
              <input type="text" placeholder="Search Token..." className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm outline-none focus:border-primary" />
            </div>
            <button className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 text-navy">
              <Filter size={16} /> Filter
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 text-xs font-bold text-light uppercase tracking-wider border-b border-gray-200">
                <th className="p-4 pl-6">Token Number</th>
                <th className="p-4">Visitor Name</th>
                <th className="p-4">Document Type</th>
                <th className="p-4">Submitted At</th>
                <th className="p-4">Status</th>
                <th className="p-4">Risk</th>
                <th className="p-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {requests.filter(req => req.status === 'PENDING' || req.status === 'IN_PROGRESS').map(req => (
                <tr key={req.booking_number} className="hover:bg-gray-50/80 transition-colors">
                  <td className="p-4 pl-6 font-semibold text-primary">{req.booking_number}</td>
                  <td className="p-4 font-medium text-navy">{req.visitor_name}</td>
                  <td className="p-4 text-light">{req.document_type}</td>
                  <td className="p-4 text-light text-sm">
                    {new Date(req.created_at).toLocaleString('en-IN', {
                      day: '2-digit', month: 'short', year: 'numeric',
                      hour: '2-digit', minute: '2-digit', hour12: true
                    })}
                  </td>
                  <td className="p-4">
                    <span className={clsx('px-2.5 py-1 rounded-full text-xs font-semibold whitespace-nowrap', 
                      req.status === 'PENDING' && 'bg-yellow-100 text-yellow-800',
                      req.status === 'IN_PROGRESS' && 'bg-blue-100 text-blue-800'
                    )}>
                      {req.status}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="text-gray-500 bg-gray-100 px-2.5 py-1 rounded text-xs font-bold">
                      PENDING
                    </span>
                  </td>
                  <td className="p-4">
                    <button 
                      className="primary-btn w-auto py-1.5 px-4 text-xs font-semibold rounded-lg transition-all"
                      onClick={() => navigate(`/force-dashboard/verify/${req.booking_number}`)}
                    >
                      Verify
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {requests.length === 0 && (
            <div className="p-8 text-center text-light">
              No verification requests in the queue.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
