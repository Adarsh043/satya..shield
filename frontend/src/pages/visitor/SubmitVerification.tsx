import { useState, useRef, useEffect } from 'react';
import { useVerification } from '../../context/VerificationContext';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { UploadCloud, Camera, CheckCircle2, ArrowRight, Loader2, User, Calendar } from 'lucide-react';
import DigiLockerLogo from '../../components/DigiLockerLogo';
import clsx from 'clsx';

// Document options per visitor type
const INDIAN_DOCS = [
  { value: 'Aadhaar Card', label: 'Aadhaar Card' },
  { value: 'PAN Card', label: 'PAN Card' },
  { value: 'Voter ID', label: 'Voter ID (EPIC)' },
  { value: 'Driving Licence', label: 'Driving Licence' },
  { value: 'Passport', label: 'Passport (Indian)' },
  { value: 'NREGA Job Card', label: 'NREGA Job Card' },
  { value: 'Arms Licence', label: 'Arms Licence' },
  { value: 'Senior Citizen Card', label: 'Senior Citizen Card' },
];

const FOREIGN_DOCS = [
  { value: 'Passport', label: 'Passport' },
  { value: 'Visa', label: 'Visa Document' },
  { value: 'National ID', label: 'National ID Card' },
  { value: 'Overseas Citizen of India (OCI)', label: 'OCI Card' },
  { value: 'Person of Indian Origin (PIO)', label: 'PIO Card' },
  { value: 'Diplomatic ID', label: 'Diplomatic / Official ID' },
  { value: 'Residence Permit', label: 'Residence Permit' },
];

export default function SubmitVerification() {
  const { addRequest } = useVerification();
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [profileLoading, setProfileLoading] = useState(true);

  // Detect visitor type from session
  const visitorType = sessionStorage.getItem('visitorType') || 'indian';
  const isIndian = visitorType === 'indian';
  const docOptions = isIndian ? INDIAN_DOCS : FOREIGN_DOCS;

  // Form State – name & dob auto-filled from profile
  const [fullName, setFullName] = useState('');
  const [dob, setDob] = useState('');
  const [nationality, setNationality] = useState('');
  const [documentType, setDocumentType] = useState(docOptions[0].value);
  const [digiLockerState, setDigiLockerState] = useState<'not_connected' | 'connecting' | 'connected' | 'failed'>('not_connected');

  const [documentImage, setDocumentImage] = useState<string | null>(null);
  const [documentSource, setDocumentSource] = useState<'Upload' | 'Camera Scan'>('Upload');
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isProcessingScan, setIsProcessingScan] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Auto-fetch profile on mount
  useEffect(() => {
    const userId = sessionStorage.getItem('visitorUserId');
    if (!userId) { setProfileLoading(false); return; }

    fetch(`http://localhost:8000/api/v1/visitor/profile/${userId}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data) {
          if (data.name) setFullName(data.name);
          if (data.dob) setDob(data.dob);
        }
      })
      .catch(() => {})
      .finally(() => setProfileLoading(false));
  }, []);

  const handleDigiLocker = () => {
    setDigiLockerState('connecting');
    setTimeout(() => setDigiLockerState('connected'), 2000);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setDocumentImage(reader.result as string);
        setDocumentSource('Upload');
      };
      reader.readAsDataURL(file);
    }
  };

  const startCamera = async () => {
    setIsCameraOpen(true);
    setStep(3);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch {
      alert('Camera access denied or unavailable.');
      setIsCameraOpen(false);
      setStep(2);
    }
  };

  const captureImage = () => {
    setIsProcessingScan(true);
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      canvas.getContext('2d')?.drawImage(videoRef.current, 0, 0);
      setTimeout(() => {
        setDocumentImage(canvas.toDataURL('image/jpeg'));
        setDocumentSource('Camera Scan');
        setIsProcessingScan(false);
        stopCamera();
        setStep(2);
      }, 1000);
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      (videoRef.current.srcObject as MediaStream).getTracks().forEach(t => t.stop());
    }
    setIsCameraOpen(false);
  };

  const dataURLtoFile = (dataurl: string, filename: string) => {
    const arr = dataurl.split(',');
    const mime = arr[0].match(/:(.*?);/)?.[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) u8arr[n] = bstr.charCodeAt(n);
    return new File([u8arr], filename, { type: mime });
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      if (!documentImage) throw new Error('No document image');
      const userId = sessionStorage.getItem('visitorUserId');
      if (!userId) throw new Error('Session expired. Please log in again.');

      const formData = new FormData();
      formData.append('document', dataURLtoFile(documentImage, 'document.jpg'));
      formData.append('source', 'UPLOAD');
      formData.append('user_id', userId);
      formData.append('claimed_document_type', documentType);

      const res = await fetch('http://localhost:8000/api/v1/citizen/book', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Upload failed');
      
      // Update global context
      addRequest({
        visitorName: fullName,
        documentType: documentType,
        documentSource: documentSource,
        details: {
          fullName: fullName,
          dob: dob,
          nationality: nationality || undefined,
          digiLockerConnected: digiLockerState === 'connected'
        }
      });
      
      setStep(4);
    } catch (err: any) {
      alert(err.message || 'Failed to submit document to backend.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 fade-in pb-12">
      {/* Stepper */}
      <div className="flex justify-between items-center mb-8 px-4 relative">
        <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-200 -z-10 -translate-y-1/2 rounded"></div>
        <div className="absolute top-1/2 left-0 h-1 bg-primary -z-10 -translate-y-1/2 rounded transition-all duration-300" style={{ width: `${((step > 3 ? 3 : step - 1) / 3) * 100}%` }}></div>
        {[1, 2, 3, 4].map(s => (
          <div key={s} className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-colors ${step >= s ? 'bg-primary text-white shadow-md' : 'bg-gray-200 text-gray-500'}`}>{s}</div>
        ))}
      </div>

      <div className="bg-white p-8 rounded-xl border border-gray-200 shadow-sm">

        {/* ── STEP 1: Personal Details ── */}
        {step === 1 && (
          <div className="fade-in">
            <h2 className="text-xl font-bold text-navy mb-4">Step 1: Personal Details</h2>

            {/* DigiLocker */}
            <div className="bg-orange-50 border border-orange-200 p-4 rounded-lg mb-6 flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="flex items-center gap-3">
                <DigiLockerLogo className="w-12 h-12 object-contain" />
                <div>
                  <h4 className="font-semibold text-navy">{t('Connect with DigiLocker')}</h4>
                  <p className="text-xs text-light">Fast and secure identity verification</p>
                </div>
              </div>
              <button
                onClick={handleDigiLocker}
                disabled={digiLockerState !== 'not_connected'}
                className={clsx('px-6 py-2 rounded-lg text-sm font-bold transition-all shadow-sm',
                  digiLockerState === 'connected' ? 'bg-green-100 text-green-800 border border-green-300' :
                  digiLockerState === 'connecting' ? 'bg-orange-100 text-orange-800 border border-orange-300 opacity-80' :
                  'bg-white border border-gray-300 text-navy hover:border-primary hover:text-primary'
                )}
              >
                {digiLockerState === 'not_connected' && 'Connect'}
                {digiLockerState === 'connecting' && 'Connecting...'}
                {digiLockerState === 'connected' && 'Connected ✓'}
              </button>
            </div>

            {profileLoading ? (
              <div className="flex items-center justify-center py-8 gap-3 text-light">
                <Loader2 size={20} className="spin text-primary" />
                <span className="text-sm">Fetching your profile...</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Document Type */}
                <div className="input-group md:col-span-2">
                  <label className="input-label text-navy font-bold mb-2">Select Document Type to Submit</label>
                  <select
                    className="text-input w-full shadow-sm"
                    value={documentType}
                    onChange={e => setDocumentType(e.target.value)}
                  >
                    {docOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                {/* Visitor type badge */}
                <div className="md:col-span-2 flex items-center gap-2">
                  <span className={clsx('text-xs font-bold px-3 py-1 rounded-full',
                    isIndian ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'
                  )}>
                    {isIndian ? '🇮🇳 Indian Citizen' : '🌐 Foreign National'}
                  </span>
                  <span className="text-xs text-light">Document options are filtered based on your visitor type.</span>
                </div>
              </div>
            )}

            <div className="flex justify-end mt-8 pt-4 border-t border-gray-100">
              <button
                className="primary-btn w-auto flex items-center gap-2"
                disabled={profileLoading}
                onClick={() => setStep(2)}
              >
                Continue <ArrowRight size={18} />
              </button>
            </div>
          </div>
        )}

        {/* ── STEP 2: Provide Document ── */}
        {step === 2 && (
          <div className="fade-in">
            <h2 className="text-xl font-bold text-navy mb-1">Step 2: Provide Document</h2>
            <p className="text-sm text-light mb-2">
              Please provide a clear scan or image of your <span className="font-semibold text-navy">{documentType}</span>.
            </p>

            {/* Mismatch warning */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-2 mb-6 text-xs text-amber-700 font-medium">
              ⚠ Ensure the document you upload matches the selected type above. The AI will verify this automatically.
            </div>

            {!documentImage ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <label className="border-2 border-dashed border-gray-300 hover:border-primary rounded-xl p-8 flex flex-col items-center justify-center bg-gray-50 hover:bg-orange-50 cursor-pointer transition-all group h-64">
                  <UploadCloud size={48} className="text-gray-400 group-hover:text-primary mb-4 transition-colors" />
                  <h3 className="font-bold text-navy mb-2">Upload Document</h3>
                  <p className="text-xs text-light text-center">Select a file from your device<br />(JPG, PNG, PDF)</p>
                  <input type="file" accept="image/*" className="hidden" onChange={handleFileUpload} />
                </label>

                <button onClick={startCamera} className="border-2 border-dashed border-gray-300 hover:border-primary rounded-xl p-8 flex flex-col items-center justify-center bg-gray-50 hover:bg-orange-50 cursor-pointer transition-all group h-64 w-full">
                  <Camera size={48} className="text-gray-400 group-hover:text-primary mb-4 transition-colors" />
                  <h3 className="font-bold text-navy mb-2">Scan Document</h3>
                  <p className="text-xs text-light text-center">Use your camera to scan<br />the physical document directly</p>
                </button>
              </div>
            ) : (
              <div className="border border-gray-200 rounded-xl p-6 bg-gray-50 text-center">
                <CheckCircle2 size={48} className="mx-auto text-green-500 mb-4" />
                <h3 className="text-xl font-bold text-navy mb-2">Document Ready ✓</h3>
                <p className="text-sm text-light mb-1">Your <span className="font-semibold text-navy">{documentType}</span> has been successfully provided.</p>
                <p className="text-xs text-light mb-6">Source: <span className="font-semibold">{documentSource}</span></p>
                <img src={documentImage} alt="Document Preview" className="w-full max-w-sm h-48 object-contain bg-white border border-gray-200 rounded-lg mb-6 mx-auto shadow-sm" />
                <button className="secondary-btn w-auto py-2 px-6" onClick={() => setDocumentImage(null)}>Retake / Replace</button>
              </div>
            )}

            <div className="flex justify-between mt-8 pt-4 border-t border-gray-100">
              <button className="secondary-btn w-auto py-2 px-6" onClick={() => setStep(1)}>Back</button>
              {documentImage && (
                <button className="primary-btn w-auto py-2 px-6 flex items-center gap-2" onClick={handleSubmit} disabled={isLoading}>
                  {isLoading ? <Loader2 size={18} className="spin" /> : 'Submit Verification'}
                  {!isLoading && <ArrowRight size={18} />}
                </button>
              )}
            </div>
          </div>
        )}

        {/* ── STEP 3: Camera Scan ── */}
        {step === 3 && (
          <div className="fade-in">
            <h2 className="text-xl font-bold text-navy mb-2">Scan Document</h2>
            <p className="text-sm text-light mb-6">Place your complete document inside the frame. Ensure good lighting.</p>

            <div className="relative bg-black rounded-xl overflow-hidden aspect-video flex items-center justify-center shadow-inner">
              {isCameraOpen
                ? <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover"></video>
                : <p className="text-white">Starting camera...</p>
              }
              <div className="absolute inset-0 border-[60px] border-black/60 z-10 pointer-events-none flex items-center justify-center">
                <div className="w-full h-full border-2 border-dashed border-white/80 rounded-lg relative">
                  <div className="absolute -top-1 -left-1 w-6 h-6 border-t-4 border-l-4 border-primary"></div>
                  <div className="absolute -top-1 -right-1 w-6 h-6 border-t-4 border-r-4 border-primary"></div>
                  <div className="absolute -bottom-1 -left-1 w-6 h-6 border-b-4 border-l-4 border-primary"></div>
                  <div className="absolute -bottom-1 -right-1 w-6 h-6 border-b-4 border-r-4 border-primary"></div>
                </div>
              </div>
              {isProcessingScan && (
                <div className="absolute inset-0 bg-black/80 z-20 flex flex-col items-center justify-center text-white">
                  <Loader2 size={48} className="spin text-primary mb-4" />
                  <p className="font-bold">Processing Scan...</p>
                </div>
              )}
            </div>

            <div className="flex justify-between mt-8 pt-4 border-t border-gray-100">
              <button className="secondary-btn w-auto py-2 px-6" onClick={() => { stopCamera(); setStep(2); }}>Cancel</button>
              <button className="primary-btn w-auto py-2 px-8 flex items-center gap-2" onClick={captureImage} disabled={isProcessingScan || !isCameraOpen}>
                <Camera size={18} /> Capture
              </button>
            </div>
          </div>
        )}

        {/* ── STEP 4: Success ── */}
        {step === 4 && (
          <div className="fade-in text-center py-12">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-green-50 rounded-full mb-6">
              <CheckCircle2 size={48} className="text-green-500" />
            </div>
            <h2 className="text-2xl font-bold text-navy mb-2">Submission Successful</h2>
            <p className="text-light mb-2 max-w-md mx-auto">Your <span className="font-semibold text-navy">{documentType}</span> verification request has been securely submitted and added to the queue.</p>
            <p className="text-xs text-light mb-8">The officer will verify your identity. Please present your booking number at the counter.</p>
            <button className="primary-btn w-auto mx-auto py-3 px-8 shadow-md" onClick={() => navigate('/visitor-dashboard')}>
              Go to Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
