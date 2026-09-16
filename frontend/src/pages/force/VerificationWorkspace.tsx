import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { AlertTriangle, FileText, CheckCircle2, Camera, User, Loader2 } from 'lucide-react';
import clsx from 'clsx';

export default function VerificationWorkspace() {
  const { id } = useParams<{ id: string }>();
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [req, setReq] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  // Persisted Workspace State
  const [activeTab, setActiveTab] = useState<'CAPTURE' | 'RISK' | 'FORENSICS' | 'BIOMETRICS' | 'DATA' | 'AUDIT'>(() => {
    return (sessionStorage.getItem(`tab_${id}`) as any) || 'CAPTURE';
  });
  const [faceImage, setFaceImage] = useState<string | null>(() => {
    return sessionStorage.getItem(`face_${id}`) || null;
  });
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [aiResults, setAiResults] = useState<any>(() => {
    const saved = sessionStorage.getItem(`ai_${id}`);
    return saved ? JSON.parse(saved) : null;
  });
  
  const videoRef = useRef<HTMLVideoElement>(null);

  // Save progress to session storage
  useEffect(() => {
    if (id) {
      try {
        sessionStorage.setItem(`tab_${id}`, activeTab);
        if (aiResults) sessionStorage.setItem(`ai_${id}`, JSON.stringify(aiResults));
        if (faceImage) sessionStorage.setItem(`face_${id}`, faceImage);
      } catch (e) {
        console.warn("sessionStorage quota exceeded, progress may not be fully saved.", e);
      }
    }
  }, [id, activeTab, faceImage, aiResults]);
  
  // Modals
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');

  // Fetch Appointment Details
  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/v1/officer/appointments/${id}`);
        if (res.ok) {
          const data = await res.json();
          setReq(data);
        } else {
          console.error("Failed to load details");
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchDetails();
  }, [id]);

  if (loading) return <div className="p-8 flex justify-center"><Loader2 className="spin text-primary" size={32}/></div>;
  if (!req) return <div className="p-8">Token not found.</div>;

  const startCamera = async () => {
    setIsCameraOpen(true);
    setActiveTab('CAPTURE');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      alert("Camera access denied or unavailable.");
      setIsCameraOpen(false);
    }
  };

  const captureFace = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      const MAX_WIDTH = 800;
      let width = videoRef.current.videoWidth;
      let height = videoRef.current.videoHeight;
      
      if (width > MAX_WIDTH) {
        height = Math.round((height * MAX_WIDTH) / width);
        width = MAX_WIDTH;
      }

      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0, width, height);
        // Heavily compress to avoid QuotaExceededError
        setFaceImage(canvas.toDataURL('image/jpeg', 0.6));
        stopCamera();
      }
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
    }
    setIsCameraOpen(false);
  };

  // Helper to convert dataURL to File
  const dataURLtoFile = (dataurl: string, filename: string) => {
    let arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)?.[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type:mime});
  }

  const runAIVerification = async () => {
    if (!faceImage) {
      alert("Please capture a live face first!");
      setActiveTab('FACE');
      return;
    }

    setIsVerifying(true);
    try {
      const selfieFile = dataURLtoFile(faceImage, 'selfie.jpg');
      const formData = new FormData();
      formData.append('selfie', selfieFile);

      const res = await fetch(`http://localhost:8000/api/v1/officer/verify/${req.booking_number}`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) throw new Error("AI Verification failed");
      
      const data = await res.json();
      setAiResults(data);
      setReq({ ...req, status: 'IN_PROGRESS' });
      setActiveTab('RISK');
    } catch (err) {
      console.error(err);
      alert("Verification pipeline error.");
    } finally {
      setIsVerifying(false);
    }
  };

  const handleUpdateStatus = async (status: string, reason?: string) => {
    try {
      await fetch(`http://localhost:8000/api/v1/officer/status/${req.booking_number}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, rejection_reason: reason })
      });
      navigate('/force-dashboard');
    } catch (err) {
      console.error(err);
      alert("Failed to update status");
    }
  };

  return (
    <div className="flex flex-col gap-6 min-h-[calc(100vh-140px)]">
      
      {/* TOP: Document Preview */}
      <div className="w-full flex flex-col gap-4">
        <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col lg:flex-row gap-4 items-center">
          <div className="flex justify-between items-center mb-4 border-b border-gray-100 pb-2">
            <h3 className="font-bold text-navy flex items-center gap-2"><FileText size={18}/> {t('Document Preview')}</h3>
            <span className="text-xs font-semibold px-2 py-1 bg-gray-100 rounded">{req.document_type}</span>
          </div>
          
          <div className="flex-1 w-full lg:w-1/2 bg-gray-100 rounded-lg overflow-hidden flex items-center justify-center relative border border-gray-200 group cursor-zoom-in h-64 lg:h-48">
            {req.document_url ? (
               <img src={req.document_url} alt="Document" className="w-full h-full object-contain transition-transform group-hover:scale-105" />
            ) : (
               <p className="text-light text-sm text-center p-4">No document image provided.</p>
            )}
          </div>

          <div className="flex-1 w-full lg:w-1/2 bg-gray-50 p-4 rounded-lg border border-gray-100 flex flex-col justify-center space-y-4">
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-light">Token Number:</span>
              <span className="text-navy">{req.booking_number}</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-light">Source:</span>
              <span className={clsx("font-bold", req.source === 'DIGILOCKER' ? 'text-green-600' : 'text-primary')}>{req.source}</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="font-semibold text-light">Submitted At:</span>
              <span className="text-navy">
                {new Date(req.created_at).toLocaleString('en-IN')}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* BOTTOM: Verification Workspace */}
      <div className="w-full flex-1 bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col overflow-hidden min-h-[600px]">
        
        {/* Header */}
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold text-navy">Workspace: {req.booking_number}</h2>
            <p className="text-xs text-light">Applicant: {req.visitor_name}</p>
          </div>
          <div className="flex gap-2">
            <span className={clsx('px-3 py-1 rounded-full text-xs font-bold', 
              req.status === 'VERIFIED' ? 'bg-green-100 text-green-800' :
              req.status === 'REJECTED' ? 'bg-red-100 text-red-800' : 
              req.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'
            )}>
              {req.status}
            </span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 px-2 pt-2 gap-2 bg-white flex-wrap">
          {['CAPTURE', 'RISK', 'FORENSICS', 'BIOMETRICS', 'DATA', 'AUDIT'].map(tab => (
            <button 
              key={tab}
              className={clsx('px-4 py-3 text-sm font-semibold rounded-t-lg transition-colors whitespace-nowrap', 
                activeTab === tab ? 'bg-gray-50 text-primary border-t border-l border-r border-gray-200' : 'text-light hover:bg-gray-50'
              )}
              onClick={() => setActiveTab(tab as any)}
            >
              {tab === 'CAPTURE' && 'Live Capture'}
              {tab === 'RISK' && 'AI Fusion Risk'}
              {tab === 'FORENSICS' && 'Digital Forensics'}
              {tab === 'BIOMETRICS' && 'Biometrics'}
              {tab === 'DATA' && 'Data Extraction'}
              {tab === 'AUDIT' && 'Audit Trail'}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
          
          {activeTab === 'CAPTURE' && (
            <div className="space-y-6 fade-in">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-navy">Live Face Capture</h3>
                {!isCameraOpen && !faceImage && (
                  <button className="secondary-btn w-auto py-1.5 px-3 text-sm" onClick={startCamera}>
                    <Camera size={16} /> Open Camera
                  </button>
                )}
              </div>

              <div className="border border-gray-200 rounded-xl overflow-hidden bg-white shadow-sm flex flex-col max-w-md mx-auto">
                <div className="bg-gray-100 p-2 text-center text-xs font-bold text-light uppercase border-b border-gray-200">Officer Counter Capture</div>
                <div className="flex-1 min-h-[300px] bg-black relative flex items-center justify-center">
                  {faceImage ? (
                    <img src={faceImage} alt="Captured Face" className="w-full h-full object-cover" />
                  ) : isCameraOpen ? (
                    <video ref={videoRef} autoPlay playsInline className="w-full h-full object-cover"></video>
                  ) : (
                    <div className="text-white flex flex-col items-center">
                      <User size={32} className="mb-2 opacity-50"/>
                      <span className="text-sm opacity-50">No capture yet</span>
                    </div>
                  )}

                  {isCameraOpen && (
                     <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
                       <button className="bg-white text-navy font-bold rounded-full w-12 h-12 flex items-center justify-center shadow-lg hover:scale-105 transition-transform" onClick={captureFace}>
                         <Camera size={20} />
                       </button>
                     </div>
                  )}
                </div>
              </div>
              
              {faceImage && !aiResults && (
                <div className="text-center mt-6">
                  <button onClick={runAIVerification} disabled={isVerifying} className="primary-btn w-auto text-lg px-8 py-3 shadow-xl flex items-center gap-2 mx-auto">
                    {isVerifying ? <Loader2 className="spin" size={24}/> : 'Run AI Verification Pipeline'}
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === 'RISK' && (
            <div className="space-y-6 fade-in">
              <h3 className="font-bold text-navy mb-4">SentinelID Evidence Fusion (FTM)</h3>
              {!aiResults ? (
                 <div className="bg-white p-8 rounded-xl border border-gray-200 text-center shadow-sm">
                   <p className="text-light">Run the AI Verification Pipeline in the CAPTURE tab to see results.</p>
                 </div>
              ) : (
                <div className="flex gap-6 items-start">
                  <div className="w-1/3 bg-white p-6 rounded-xl border border-gray-200 shadow-sm text-center">
                    <h4 className="text-sm font-semibold text-light mb-4 uppercase tracking-wide">Overall Risk</h4>
                    <div className={clsx("inline-flex items-center justify-center w-24 h-24 rounded-full border-8 mb-2",
                       aiResults.overall_risk === 'LOW_GREEN' ? 'border-green-400 text-green-600' :
                       aiResults.overall_risk === 'MEDIUM_AMBER' ? 'border-yellow-400 text-yellow-600' :
                       'border-red-400 text-red-600'
                    )}>
                      <span className="text-sm font-bold">{aiResults.overall_risk.split('_')[0]}</span>
                    </div>
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <h4 className="text-xs font-bold text-light uppercase mb-2">Trust Score</h4>
                      <div className="text-2xl font-bold text-navy">{Math.round(aiResults.trust_score)}%</div>
                    </div>
                  </div>

                  <div className="w-2/3 bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <h4 className="text-sm font-semibold text-navy mb-4 border-b pb-2">High-Priority Evidence</h4>
                    <ul className="space-y-3 text-sm">
                      {aiResults.modules.filter((m: any) => m.status === 'FAIL' || m.status === 'WARNING').map((mod: any, idx: number) => (
                        <li key={idx} className="flex flex-col p-2 bg-gray-50 rounded border-l-4 border-red-500">
                           <div className="flex justify-between font-bold text-navy">
                              <span>{mod.module_name}</span>
                              <span className="text-red-600">{mod.status}</span>
                           </div>
                           <p className="text-xs text-red-700 mt-1">{mod.reasons?.[0] || 'Anomaly detected'}</p>
                        </li>
                      ))}
                      {aiResults.modules.filter((m: any) => m.status === 'FAIL' || m.status === 'WARNING').length === 0 && (
                        <p className="text-green-600 text-sm font-semibold p-4 text-center bg-green-50 rounded">All SentinelID verification stages cleared.</p>
                      )}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {(activeTab === 'FORENSICS' || activeTab === 'BIOMETRICS' || activeTab === 'DATA' || activeTab === 'AUDIT') && (
             <div className="space-y-4 fade-in">
               <h3 className="font-bold text-navy mb-2">{activeTab} Modules</h3>
               {!aiResults ? (
                 <div className="bg-white p-8 rounded-xl border border-gray-200 text-center shadow-sm">
                   <p className="text-light text-sm">Execute the pipeline to populate modules.</p>
                 </div>
               ) : (
                 <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 space-y-3">
                   {aiResults.modules.filter((m: any) => {
                     if (activeTab === 'FORENSICS') return ['fft_frequency_forensics', 'photo_splicing_detector', 'micro_typography', 'perceptual_deduplication'].includes(m.module_name);
                     if (activeTab === 'BIOMETRICS') return ['liveness_pad_detector', 'biometric_face_verifier', 'face_morph_detector'].includes(m.module_name);
                     if (activeTab === 'DATA') return ['cross_field_correlator', 'document_classifier', 'deterministic_checksums', 'roi_text_extractor', 'pii_redactor', 'preflight_intake'].includes(m.module_name);
                     return true; // AUDIT shows everything
                   }).map((mod: any, idx: number) => (
                      <div key={idx} className="border border-gray-100 p-3 rounded-lg flex flex-col">
                         <div className="flex justify-between items-center mb-1">
                           <span className="text-navy font-bold text-sm uppercase">{mod.module_name.replace(/_/g, ' ')}</span>
                           <span className={clsx("font-bold text-xs px-2 py-1 rounded", 
                             mod.status === 'PASS' ? 'bg-green-100 text-green-700' : 
                             mod.status === 'WARNING' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                           )}>
                             {mod.status} ({Math.round(mod.confidence * 100)}%)
                           </span>
                         </div>
                         <p className="text-xs text-light mb-2">{mod.reasons?.[0]}</p>
                         <div className="text-[10px] text-gray-400">Exec: {Math.round(mod.execution_time_ms)}ms</div>
                      </div>
                   ))}
                 </div>
               )}
             </div>
          )}

        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-gray-200 bg-white flex justify-end gap-4 shadow-[0_-4px_12px_rgba(0,0,0,0.02)] z-10">
          <button 
            className="px-6 py-2 rounded-lg font-bold text-red-600 border border-red-200 hover:bg-red-50 transition-colors disabled:opacity-50"
            onClick={() => setShowRejectModal(true)}
            disabled={req.status === 'VERIFIED' || req.status === 'REJECTED' || !aiResults}
          >
            REJECT VERIFICATION
          </button>
          <button 
            className="px-8 py-2 rounded-lg font-bold text-white bg-green-600 hover:bg-green-700 transition-colors shadow-md disabled:opacity-50"
            onClick={() => handleUpdateStatus('VERIFIED')}
            disabled={req.status === 'VERIFIED' || req.status === 'REJECTED' || !aiResults}
          >
            ACCEPT VERIFICATION
          </button>
        </div>

      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-navy/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 fade-in">
            <h3 className="text-lg font-bold text-navy mb-2">Reject Verification</h3>
            <p className="text-sm text-light mb-4">Please provide a reason for rejecting this verification. The visitor will be notified.</p>
            
            <textarea 
              className="w-full border border-gray-300 rounded-lg p-3 text-sm mb-4 outline-none focus:border-red-500 min-h-[100px]"
              placeholder="Enter rejection reason..."
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
            ></textarea>
            
            <div className="flex justify-end gap-3">
              <button className="secondary-btn w-auto py-2 px-4" onClick={() => setShowRejectModal(false)}>Cancel</button>
              <button className="bg-red-600 text-white font-semibold rounded-lg py-2 px-4 hover:bg-red-700" onClick={() => handleUpdateStatus('REJECTED', rejectionReason)} disabled={!rejectionReason}>
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
