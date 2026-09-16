import { useState, useEffect, useRef } from 'react';
import { UserCheck, LogOut, UploadCloud, FileCheck2, Loader2, CheckCircle2, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function VisitorDashboard() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [bookingNumber, setBookingNumber] = useState<string | null>(null);
  const [bookingStatus, setBookingStatus] = useState<string>('NONE'); // NONE, PENDING, VERIFIED, REJECTED
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSignOut = () => {
    // Completely clear any local auth state here for a fresh session
    sessionStorage.clear();
    navigate('/', { replace: true });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append("document", file);
    formData.append("source", "UPLOAD");

    try {
      const res = await fetch('http://localhost:8000/api/v1/citizen/book', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      setBookingNumber(data.booking_number);
      setBookingStatus('PENDING');
    } catch (err) {
      console.error(err);
      setError("Failed to submit document. Ensure backend is running.");
    } finally {
      setIsUploading(false);
    }
  };

  // Poll for status once we have a booking number
  useEffect(() => {
    if (!bookingNumber || bookingStatus !== 'PENDING') return;

    const intervalId = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/citizen/status/${bookingNumber}`);
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'VERIFIED' || data.status === 'REJECTED') {
            setBookingStatus(data.status);
            clearInterval(intervalId); // stop polling
          }
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(intervalId);
  }, [bookingNumber, bookingStatus]);

  // Determine if we show the sign out button
  // Rule: hidden while PENDING. Appears on VERIFIED, REJECTED, or before starting upload.
  const canSignOut = bookingStatus !== 'PENDING';

  return (
    <div className="min-h-screen bg-[#FDFBF7] flex flex-col items-center p-6">
      
      <header className="w-full max-w-3xl flex justify-between items-center mb-8 bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <div className="flex items-center gap-3">
          <div className="bg-green-100 p-2 rounded-lg text-green-700">
            <UserCheck size={28} />
          </div>
          <h1 className="font-bold text-xl text-navy">Satya Shield <span className="font-normal text-gray-500">Visitor Portal</span></h1>
        </div>
        
        {canSignOut && (
          <button 
            className="flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-gray-600 hover:bg-gray-100 transition-colors border border-gray-200"
            onClick={handleSignOut}
          >
            <LogOut size={18} />
            Sign Out
          </button>
        )}
      </header>

      <div className="w-full max-w-3xl bg-white p-8 rounded-2xl shadow-lg border border-gray-100 relative overflow-hidden">
        {/* Decorative Top Line */}
        <div className="absolute top-0 left-0 w-full h-1 flex">
          <div className="h-full flex-1" style={{backgroundColor: '#FF9933'}}></div>
          <div className="h-full bg-white flex-1"></div>
          <div className="h-full flex-1" style={{backgroundColor: '#138808'}}></div>
        </div>

        {bookingStatus === 'NONE' && (
          <div className="fade-in text-center flex flex-col items-center">
            <h2 className="text-2xl font-bold text-navy mb-2">Upload ID Document</h2>
            <p className="text-light mb-8 max-w-md">Please upload a clear picture of your Aadhaar Card, Passport, or other valid ID for verification.</p>
            
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              onChange={handleFileChange}
              accept="image/*"
            />
            
            {!file ? (
              <div 
                className="border-2 border-dashed border-gray-300 w-full rounded-xl p-12 flex flex-col items-center justify-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="bg-blue-100 p-4 rounded-full text-blue-600 mb-4">
                  <UploadCloud size={40} />
                </div>
                <h3 className="font-bold text-lg mb-1">Click to browse or drag file</h3>
                <p className="text-sm text-gray-500">Supports JPG, PNG, PDF</p>
              </div>
            ) : (
              <div className="border border-green-200 bg-green-50 w-full rounded-xl p-6 flex flex-col items-center text-green-800">
                <FileCheck2 size={48} className="mb-4 text-green-600" />
                <h3 className="font-bold text-lg mb-1">{file.name}</h3>
                <p className="text-sm opacity-80 mb-6">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                
                <div className="flex gap-4 w-full justify-center">
                  <button className="secondary-btn w-auto" onClick={() => setFile(null)}>Change File</button>
                  <button 
                    className="primary-btn w-auto flex items-center gap-2" 
                    onClick={handleUpload}
                    disabled={isUploading}
                  >
                    {isUploading ? <Loader2 className="animate-spin" size={20}/> : <UploadCloud size={20}/>}
                    {isUploading ? 'Uploading...' : 'Submit Document'}
                  </button>
                </div>
              </div>
            )}
            {error && <div className="text-red-500 mt-4 font-semibold text-sm">{error}</div>}
          </div>
        )}

        {bookingStatus === 'PENDING' && (
          <div className="fade-in text-center flex flex-col items-center py-12">
            <div className="w-24 h-24 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin mb-6"></div>
            <h2 className="text-3xl font-bold text-navy mb-2">Awaiting Verification</h2>
            <p className="text-light mb-8 max-w-md">Your document has been submitted. Please present this Booking Number to the officer.</p>
            
            <div className="bg-gray-100 p-6 rounded-xl border border-gray-200 shadow-inner">
               <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">Booking Number</p>
               <p className="font-mono text-4xl font-bold text-navy tracking-wider">{bookingNumber}</p>
            </div>
            
            <p className="mt-8 text-sm text-yellow-600 font-semibold bg-yellow-50 px-4 py-2 rounded-full flex items-center gap-2">
              <Loader2 className="animate-spin" size={16} /> Officer is reviewing your document...
            </p>
          </div>
        )}

        {bookingStatus === 'VERIFIED' && (
          <div className="fade-in text-center flex flex-col items-center py-12">
            <div className="bg-green-100 text-green-600 p-6 rounded-full mb-6 shadow-sm">
              <CheckCircle2 size={64} />
            </div>
            <h2 className="text-3xl font-bold text-green-700 mb-2">Verification Approved</h2>
            <p className="text-light mb-8 max-w-md">Your identity has been verified by the officer. You are cleared to proceed.</p>
            
            <div className="bg-gray-100 px-6 py-3 rounded-lg border border-gray-200 mb-8 inline-block">
               <span className="font-mono text-xl font-bold text-gray-700">{bookingNumber}</span>
            </div>
          </div>
        )}

        {bookingStatus === 'REJECTED' && (
          <div className="fade-in text-center flex flex-col items-center py-12">
            <div className="bg-red-100 text-red-600 p-6 rounded-full mb-6 shadow-sm">
              <AlertTriangle size={64} />
            </div>
            <h2 className="text-3xl font-bold text-red-700 mb-2">Verification Rejected</h2>
            <p className="text-light mb-8 max-w-md">The officer has rejected this document. Please step aside or consult the personnel desk.</p>
          </div>
        )}

      </div>
    </div>
  );
}
