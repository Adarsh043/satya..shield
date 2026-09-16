import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Loader2, User, Calendar, MapPin } from 'lucide-react';

export default function CompleteProfile() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  
  const [name, setName] = useState('');
  const [dob, setDob] = useState('');
  const [address, setAddress] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !dob || !address) {
      setError("Please fill in all fields.");
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    const userId = sessionStorage.getItem('visitorUserId');
    if (!userId) {
      setError("Session expired. Please log in again.");
      setIsLoading(false);
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/api/v1/visitor/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: parseInt(userId, 10),
          name,
          dob,
          address
        })
      });
      
      if (!res.ok) {
        throw new Error("Failed to save profile.");
      }
      
      // Update successful, redirect to dashboard
      navigate('/visitor-dashboard');
    } catch (err: any) {
      setError(err.message || "An error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-100 max-w-md w-full fade-in">
        <h2 className="text-2xl font-bold text-navy mb-2">Complete Your Profile</h2>
        <p className="text-light text-sm mb-6">Before submitting documents, please provide your basic information.</p>
        
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm mb-6">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-navy mb-1">Full Name</label>
            <div className="relative">
              <User size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input 
                type="text" 
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none" 
                placeholder="John Doe"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-bold text-navy mb-1">Date of Birth</label>
            <div className="relative">
              <Calendar size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input 
                type="date" 
                value={dob}
                onChange={(e) => setDob(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none" 
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-bold text-navy mb-1">Address</label>
            <div className="relative">
              <MapPin size={18} className="absolute left-3 top-3 text-gray-400" />
              <textarea 
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary outline-none h-24 resize-none" 
                placeholder="Full address..."
              ></textarea>
            </div>
          </div>
          
          <button type="submit" disabled={isLoading} className="primary-btn w-full mt-4 flex items-center justify-center h-12">
            {isLoading ? <Loader2 className="spin" size={20} /> : 'Save Profile & Continue'}
          </button>
        </form>
      </div>
    </div>
  );
}
