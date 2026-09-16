import { useVerification } from '../../context/VerificationContext';
import { useTranslation } from 'react-i18next';
import { FileText, AlertCircle, CheckCircle, Clock, LogOut, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

interface VisitorRequest {
  id: string;
  visitorName: string;
  documentType: string;
  documentSource: string;
  status: string;
  submittedAt: string;
  rejectionReason?: string;
}

export default function VisitorHome() {
  const { clearSession } = useVerification();
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [requests, setRequests] = useState<VisitorRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const userId = sessionStorage.getItem('visitorUserId');

  // Fetch real requests from the database
  const fetchRequests = async () => {
    if (!userId) {
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/api/v1/visitor/requests/${userId}`);
      if (res.ok) {
        const data = await res.json();
        setRequests(data);
      }
    } catch (err) {
      console.error("Error fetching requests:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!userId) {
      setLoading(false);
      return;
    }
    fetchRequests();
    // Poll for status updates every 5 seconds
    const intervalId = setInterval(fetchRequests, 5000);
    return () => clearInterval(intervalId);
  }, [userId]);

  const activeRequest = requests[0];

  const handleSignOut = () => {
    clearSession();
    sessionStorage.clear();
    navigate('/', { replace: true });
  };

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'VERIFIED': return 'text-green-600 bg-green-50';
      case 'REJECTED': return 'text-red-600 bg-red-50';
      case 'IN_PROGRESS': return 'text-blue-600 bg-blue-50';
      default: return 'text-yellow-600 bg-yellow-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'VERIFIED': return <CheckCircle size={24} className="text-green-600" />;
      case 'REJECTED': return <AlertCircle size={24} className="text-red-600" />;
      default: return <Clock size={24} className="text-yellow-600" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch(status) {
      case 'VERIFIED': return 'Verified / Accepted';
      case 'REJECTED': return 'Rejected';
      case 'IN_PROGRESS': return 'Verification In Progress';
      default: return 'Pending Verification';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-12">
        <Loader2 className="spin text-primary" size={32} />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 fade-in">
      <div className="bg-white p-8 rounded-xl border border-gray-200 shadow-sm">
        <h2 className="text-2xl font-bold text-navy mb-2">{t('Welcome Back')}</h2>
        <p className="text-light mb-8">{t('View your current verification status or submit a new document.')}</p>

        {requests.length > 0 ? (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-navy mb-4">{t('Verification History')}</h3>
            {requests.map((req) => (
              <div key={req.id} className="border border-gray-200 rounded-lg p-6 bg-gray-50">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-lg font-semibold text-navy mb-1">{t('Verification Token')}</h3>
                    <p className="text-2xl font-bold text-primary tracking-wider">{req.id}</p>
                  </div>
                  <div className={`flex items-center gap-2 px-4 py-2 rounded-full font-medium ${getStatusColor(req.status)}`}>
                    {getStatusIcon(req.status)}
                    {getStatusLabel(req.status)}
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div>
                    <span className="block text-xs text-light font-semibold mb-1">{t('SUBMITTED AT')}</span>
                    <span className="text-sm font-medium">
                      {new Date(req.submittedAt).toLocaleString('en-IN', {
                        day: '2-digit', month: 'short',
                        hour: '2-digit', minute: '2-digit', hour12: true
                      })}
                    </span>
                  </div>
                  <div>
                    <span className="block text-xs text-light font-semibold mb-1">{t('DOCUMENT')}</span>
                    <span className="text-sm font-medium">{req.documentType}</span>
                  </div>
                  <div>
                    <span className="block text-xs text-light font-semibold mb-1">{t('NAME')}</span>
                    <span className="text-sm font-medium">{req.visitorName}</span>
                  </div>
                  <div>
                    <span className="block text-xs text-light font-semibold mb-1">{t('SOURCE')}</span>
                    <span className="text-sm font-medium">{req.documentSource}</span>
                  </div>
                </div>

                {req.status === 'REJECTED' && req.rejectionReason && (
                  <div className="bg-red-50 border border-red-200 p-4 rounded-lg text-red-700 text-sm mt-4">
                    <strong>{t('Reason for Rejection:')}</strong> {req.rejectionReason}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
            <FileText size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold text-navy mb-2">{t('No Active Verifications')}</h3>
            <p className="text-light mb-6">{t("You haven't submitted any documents for verification yet.")}</p>
          </div>
        )}

        <div className="mt-8 flex justify-end gap-4">
          <button 
            className="secondary-btn w-auto flex items-center gap-2"
            onClick={handleSignOut}
          >
            <LogOut size={18} />
            Sign Out
          </button>
          <button 
            className="primary-btn w-auto"
            onClick={() => navigate('/visitor-dashboard/submit')}
          >
            <FileText size={18} />
            Submit New Document
          </button>
        </div>
      </div>
    </div>
  );
}
