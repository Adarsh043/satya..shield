import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Loader2, Smartphone, Mail, FileText, Fingerprint } from 'lucide-react';
import { useVerification } from '../context/VerificationContext';
import OtpInput from './OtpInput';
import clsx from 'clsx';

export default function VisitorLogin() {
  const { t } = useTranslation();
  const { updateVisitorProfile } = useVerification();
  const [visitorType, setVisitorType] = useState<'indian' | 'foreign'>('indian');
  const [indianIdType, setIndianIdType] = useState<'mobile' | 'aadhaar'>('mobile');
  const [step, setStep] = useState<'credentials' | 'otp'>('credentials');
  
  // Indian Citizen
  const [mobileNumber, setMobileNumber] = useState('');
  const [aadhaarNumber, setAadhaarNumber] = useState('');
  
  // Foreign National
  const [passport, setPassport] = useState('');
  const [email, setEmail] = useState('');
  const [sessionId, setSessionId] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Clear any existing session data when the login component mounts
  useEffect(() => {
    sessionStorage.clear();
  }, []);

  const navigate = useNavigate();

  const handleContinue = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    
    let idType = '';
    let idValue = '';
    
    if (visitorType === 'indian') {
      if (indianIdType === 'mobile' && mobileNumber) {
        idType = 'mobile';
        idValue = mobileNumber;
      } else if (indianIdType === 'aadhaar' && aadhaarNumber) {
        idType = 'aadhaar';
        idValue = aadhaarNumber;
      } else {
        setError("Please fill in the required field.");
        setIsLoading(false);
        return;
      }
    } else {
      if (passport && email) {
        idType = 'passport';
        idValue = passport;
      } else {
        setError("Please fill in all required fields.");
        setIsLoading(false);
        return;
      }
    }

    try {
      const res = await fetch('http://localhost:8000/api/v1/visitor/request-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          visitor_type: visitorType,
          id_type: idType,
          id_value: idValue,
          email: visitorType === 'foreign' ? email : undefined
        })
      });
      
      if (!res.ok) throw new Error("Failed to request OTP");
      
      const data = await res.json();
      setSessionId(data.session_id);
      setStep('otp');
    } catch (err) {
      setError("An error occurred connecting to the server.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleOtpVerify = async (otp: string) => {
    setIsLoading(true);
    setError(null);
    
    let idType = '';
    let idValue = '';
    
    if (visitorType === 'indian') {
      if (indianIdType === 'mobile' && mobileNumber) {
        idType = 'mobile';
        idValue = mobileNumber;
      } else if (indianIdType === 'aadhaar' && aadhaarNumber) {
        idType = 'aadhaar';
        idValue = aadhaarNumber;
      }
    } else {
      if (passport && email) {
        idType = 'passport';
        idValue = passport;
      }
    }

    try {
      const res = await fetch('http://localhost:8000/api/v1/visitor/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          otp: otp,
          id_value: idValue,
          id_type: idType,
          visitor_type: visitorType
        })
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || "Incorrect verification code. Please try again.");
      }
      
      const data = await res.json();
      sessionStorage.setItem('visitorToken', data.token);
      sessionStorage.setItem('visitorUserId', data.user_id.toString());
      sessionStorage.setItem('visitorType', data.visitor_type || visitorType);
      
      updateVisitorProfile({
        mobile: mobileNumber || '',
        email: email || '',
        digiLockerConnected: false
      });
      
      if (!data.profile_complete) {
        navigate('/complete-profile');
      } else {
        navigate('/visitor-dashboard');
      }
    } catch (err: any) {
      setError(err.message || "An error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  if (step === 'otp') {
    return (
      <div className="w-full">
        <OtpInput 
          onVerify={handleOtpVerify} 
          onBack={() => { setStep('credentials'); setError(null); }} 
          isLoading={isLoading} 
          error={error} 
          message={
            visitorType === 'indian' 
              ? t('app.otp_desc_mobile')
              : t('app.otp_desc_email')
          }
        />
      </div>
    );
  }

  return (
    <form onSubmit={handleContinue} className="flex flex-col w-full h-full min-h-[260px] justify-between fade-in">
      <div className="flex flex-col gap-4">
        {/* Toggle */}
        <div className="flex gap-1 bg-gray-100/70 p-1 rounded-lg border border-gray-100">
          <button 
            className={clsx(
              'flex-1 py-2 rounded-md text-[13px] font-bold transition-all',
              visitorType === 'indian' 
                ? 'bg-white text-primary shadow-sm' 
                : 'text-gray-500 hover:text-navy'
            )}
            onClick={() => { setVisitorType('indian'); setError(null); }}
            type="button"
          >
            {t('app.indian_citizen')}
          </button>
          <button 
            className={clsx(
              'flex-1 py-2 rounded-md text-[13px] font-bold transition-all',
              visitorType === 'foreign' 
                ? 'bg-white text-primary shadow-sm' 
                : 'text-gray-500 hover:text-navy'
            )}
            onClick={() => { setVisitorType('foreign'); setError(null); }}
            type="button"
          >
            {t('app.foreign_national')}
          </button>
        </div>

        {visitorType === 'indian' ? (
          <div className="flex flex-col gap-4 fade-in">
            <div className="flex gap-6 h-5">
              <label className="flex items-center gap-2 text-[13px] font-semibold text-navy cursor-pointer">
                <input 
                  type="radio" 
                  name="indianIdType" 
                  className="accent-primary w-4 h-4"
                  checked={indianIdType === 'mobile'} 
                  onChange={() => setIndianIdType('mobile')} 
                />
                {t('app.mobile_number')}
              </label>
              <label className="flex items-center gap-2 text-[13px] font-semibold text-navy cursor-pointer">
                <input 
                  type="radio" 
                  name="indianIdType" 
                  className="accent-primary w-4 h-4"
                  checked={indianIdType === 'aadhaar'} 
                  onChange={() => setIndianIdType('aadhaar')} 
                />
                {t('app.aadhaar_number')}
              </label>
            </div>

            {indianIdType === 'mobile' ? (
              <div className="fade-in">
                <label className="block text-[12px] font-bold text-navy mb-1.5">{t('app.mobile_number')}</label>
                <div className="relative flex items-center">
                  <div className="absolute left-3 flex items-center justify-center w-5 h-5 pointer-events-none">
                    <Smartphone size={16} className="text-navy/70" />
                  </div>
                  <input 
                    type="text" 
                    className="w-full h-[52px] pl-10 pr-4 rounded-lg border border-gray-200 bg-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-[13px] font-medium text-navy placeholder:text-gray-400 placeholder:font-normal" 
                    placeholder={t('app.mobile_number')}
                    value={mobileNumber}
                    onChange={(e) => setMobileNumber(e.target.value)}
                  />
                </div>
              </div>
            ) : (
              <div className="fade-in">
                <label className="block text-[12px] font-bold text-navy mb-1.5">{t('app.aadhaar_number')}</label>
                <div className="relative flex items-center">
                  <div className="absolute left-3 flex items-center justify-center w-5 h-5 pointer-events-none">
                    <Fingerprint size={16} className="text-navy/70" />
                  </div>
                  <input 
                    type="text" 
                    className="w-full h-[52px] pl-10 pr-4 rounded-lg border border-gray-200 bg-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-[13px] font-medium text-navy placeholder:text-gray-400 placeholder:font-normal" 
                    placeholder={t('app.aadhaar_number')}
                    value={aadhaarNumber}
                    onChange={(e) => setAadhaarNumber(e.target.value)}
                  />
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col gap-3 fade-in">
            <div>
              <label className="block text-[12px] font-bold text-navy mb-1.5">{t('app.passport_number')}</label>
              <div className="relative flex items-center">
                <div className="absolute left-3 flex items-center justify-center w-5 h-5 pointer-events-none">
                  <FileText size={16} className="text-navy/70" />
                </div>
                <input 
                  type="text" 
                  className="w-full h-[52px] pl-10 pr-4 rounded-lg border border-gray-200 bg-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-[13px] font-medium text-navy placeholder:text-gray-400 placeholder:font-normal" 
                  placeholder={t('app.passport_number')}
                  value={passport}
                  onChange={(e) => setPassport(e.target.value)}
                />
              </div>
            </div>
            <div>
              <label className="block text-[12px] font-bold text-navy mb-1.5">{t('app.email_address')}</label>
              <div className="relative flex items-center">
                <div className="absolute left-3 flex items-center justify-center w-5 h-5 pointer-events-none">
                  <Mail size={16} className="text-navy/70" />
                </div>
                <input 
                  type="email" 
                  className="w-full h-[52px] pl-10 pr-4 rounded-lg border border-gray-200 bg-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-[13px] font-medium text-navy placeholder:text-gray-400 placeholder:font-normal" 
                  placeholder={t('app.email_address')}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="text-red-500 text-xs font-semibold text-center mt-1">
            {error}
          </div>
        )}
      </div>

      <div className="mt-4 flex flex-col gap-4">
        <button 
          type="submit" 
          className="w-full h-52px bg-dark-green bg-dark-green-hover:hover text-white rounded-lg font-bold flex items-center justify-center gap-2 transition-all shadow-md disabled:opacity-50"
          disabled={
            isLoading || 
            (visitorType === 'indian' ? (indianIdType === 'mobile' ? !mobileNumber : !aadhaarNumber) : (!passport || !email))
          }
        >
          {isLoading ? <Loader2 size={20} className="animate-spin" /> : (
            <>
              <span className="font-semibold text-15px">{t('app.continue')}</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="ml-1"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
            </>
          )}
        </button>

        {visitorType === 'indian' && (
          <div className="fade-in">
            {/* OR Divider */}
            <div className="flex items-center justify-center gap-4 my-2">
              <div className="h-[1px] bg-gray-200 flex-1"></div>
              <span className="text-10px font-bold text-gray-400 uppercase">OR</span>
              <div className="h-[1px] bg-gray-200 flex-1"></div>
            </div>

            {/* Government SSO Button */}
            <button type="button" className="w-full flex items-center justify-between p-3.5 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-all mt-2">
              <div className="flex items-center gap-4">
                <img src="/ashoka-emblem.svg" alt="Ashoka Emblem" className="w-8 h-8 opacity-80" />
                <div className="text-left">
                  <h4 className="text-13px font-bold text-navy">Login with Government SSO</h4>
                  <p className="text-11px font-medium text-navy/60">ePramaan / DigiLocker</p>
                </div>
              </div>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400"><path d="m9 18 6-6-6-6"/></svg>
            </button>
          </div>
        )}
      </div>
    </form>
  );
}
