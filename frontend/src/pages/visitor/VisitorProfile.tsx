import React, { useState, useEffect } from 'react';
import { User, Mail, Phone, X, Loader2 } from 'lucide-react';
import { useVerification } from '../../context/VerificationContext';
import { useTranslation } from 'react-i18next';
import DigiLockerLogo from '../../components/DigiLockerLogo';

export default function VisitorProfile() {
  const { visitorProfile, updateVisitorProfile } = useVerification();
  const { t } = useTranslation();
  const [isEditing, setIsEditing] = useState(false);
  const [mobile, setMobile] = useState(visitorProfile?.mobile || '');
  const [email, setEmail] = useState(visitorProfile?.email || '');
  const [error, setError] = useState('');
  
  const [profileData, setProfileData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  if (!visitorProfile) return null;

  useEffect(() => {
    const userId = sessionStorage.getItem('visitorUserId');
    if (!userId) {
      setLoading(false);
      return;
    }
    
    fetch(`http://localhost:8000/api/v1/visitor/profile/${userId}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data) setProfileData(data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!mobile || !email) {
      setError('Mobile number and Email are required.');
      return;
    }
    updateVisitorProfile({ mobile, email });
    setIsEditing(false);
    setError('');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 fade-in relative">
      <div className="bg-white p-8 rounded-xl border border-gray-200 shadow-sm">
        <h2 className="text-2xl font-bold text-navy mb-6">{t('Visitor Profile')}</h2>
        
        <div className="flex items-start gap-8 mb-8 pb-8 border-b border-gray-200">
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0 border-4 border-white shadow-lg">
            <User size={40} className="text-gray-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-navy mb-1">{visitorProfile.mobile || 'Visitor'}</h3>
            <p className="text-light text-sm mb-4">Visitor Account</p>
            
            <div className="flex items-center gap-2 text-sm text-green-700 bg-green-50 w-fit px-3 py-1.5 rounded-full border border-green-200">
              <DigiLockerLogo className="w-5 h-5 object-contain" />
              <span className="font-semibold">DigiLocker Linked</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h4 className="font-semibold text-navy mb-4 border-b pb-2">Personal Information</h4>
            <div className="space-y-4">
              {loading ? (
                <div className="flex items-center gap-2 text-light"><Loader2 size={16} className="spin" /> Fetching profile...</div>
              ) : (
                <>
                  <div>
                    <label className="text-xs text-light font-semibold block mb-1">FULL NAME</label>
                    <div className="text-sm font-medium">{profileData?.name || 'Pending'}</div>
                  </div>
                  <div>
                    <label className="text-xs text-light font-semibold block mb-1">DATE OF BIRTH</label>
                    <div className="text-sm font-medium">{profileData?.dob || 'Pending'}</div>
                  </div>
                  <div>
                    <label className="text-xs text-light font-semibold block mb-1">ADDRESS</label>
                    <div className="text-sm font-medium">{profileData?.address || 'Pending'}</div>
                  </div>
                  <div>
                    <label className="text-xs text-light font-semibold block mb-1">VISITOR TYPE</label>
                    <div className="text-sm font-medium capitalize">{profileData?.user_type || 'Unknown'}</div>
                  </div>
                </>
              )}
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold text-navy mb-4 border-b pb-2">Contact Details</h4>
            <div className="space-y-4">
              <div>
                <label className="text-xs text-light font-semibold block mb-1 flex items-center gap-1"><Phone size={12}/> MOBILE NUMBER</label>
                <div className="text-sm font-medium">{visitorProfile.mobile}</div>
              </div>
              <div>
                <label className="text-xs text-light font-semibold block mb-1 flex items-center gap-1"><Mail size={12}/> EMAIL ADDRESS</label>
                <div className="text-sm font-medium">{visitorProfile.email}</div>
              </div>
            </div>
            
            <button 
              className="secondary-btn w-auto mt-6 text-sm py-2 px-4"
              onClick={() => {
                setMobile(visitorProfile.mobile);
                setEmail(visitorProfile.email);
                setIsEditing(true);
              }}
            >
              Update Contact Info
            </button>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {isEditing && (
        <div className="fixed inset-0 bg-navy/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 fade-in">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-navy">Update Contact Info</h3>
              <button className="text-light hover:text-navy" onClick={() => setIsEditing(false)}>
                <X size={20} />
              </button>
            </div>
            <p className="text-sm text-light mb-6">Modify your permitted contact details below. This will update your profile across the verification system.</p>
            
            <form onSubmit={handleSave}>
              <div className="input-group mb-4">
                <label className="input-label">Mobile Number</label>
                <input 
                  type="text" 
                  className="text-input w-full" 
                  value={mobile} 
                  onChange={(e) => setMobile(e.target.value)}
                />
              </div>
              
              <div className="input-group mb-6">
                <label className="input-label">Email Address</label>
                <input 
                  type="email" 
                  className="text-input w-full" 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              {error && <div className="text-red-500 text-sm mb-4">{error}</div>}

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                <button type="button" className="secondary-btn w-auto py-2 px-4" onClick={() => setIsEditing(false)}>Cancel</button>
                <button type="submit" className="primary-btn w-auto py-2 px-6">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
