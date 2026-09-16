import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Lock, Loader2, Contact, EyeOff, Eye, IdCard } from 'lucide-react';
import OtpInput from './OtpInput';

export default function ForceLogin() {
  const { t } = useTranslation();
  const [serviceId, setServiceId] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [step, setStep] = useState<'credentials' | 'otp'>('credentials');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const navigate = useNavigate();

  const handleCredentialsSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    
    setTimeout(() => {
      setIsLoading(false);
      if (serviceId && password) {
        setStep('otp');
      } else {
        setError("Invalid Service ID or password.");
      }
    }, 1000);
  };

  const handleOtpVerify = (otp: string) => {
    setIsLoading(true);
    setError(null);
    
    setTimeout(() => {
      setIsLoading(false);
      if (otp === '123456') {
        navigate('/force-dashboard');
      } else {
        setError("Incorrect verification code. Please try again.");
      }
    }, 1500);
  };

  if (step === 'otp') {
    return (
      <div className="w-full">
        <OtpInput 
          onVerify={handleOtpVerify} 
          onBack={() => { setStep('credentials'); setError(null); }} 
          isLoading={isLoading} 
          error={error}
          message={t('app.otp_desc_mobile')}
        />
      </div>
    );
  }

  return (
    <form onSubmit={handleCredentialsSubmit} className="flex flex-col w-full h-240px justify-between fade-in">
      <div className="flex flex-col gap-4">
        {/* Service ID Input */}
        <div>
          <label className="block text-12px font-bold text-navy mb-1.5">{t('app.service_id')}</label>
          <div className="relative flex items-center">
            <div className="absolute left-3 flex items-center justify-center w-5 h-5 pointer-events-none">
              <IdCard size={16} className="text-navy/70" />
            </div>
            <input 
              type="text" 
              className="w-full h-52px pl-10 pr-4 rounded-lg border border-gray-200 bg-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-13px font-medium text-navy placeholder:text-gray-400 placeholder:font-normal"
              placeholder={t('app.service_id')}
              value={serviceId}
              onChange={(e) => setServiceId(e.target.value)}
            />
          </div>
        </div>

        {/* Password Input */}
        <div className="flex flex-col gap-0.5">
          <label className="block text-12px font-bold text-navy mb-1.5">{t('app.password')}</label>
          <div className="relative flex items-center">
            <div className="absolute left-3 flex items-center justify-center w-5 h-5 pointer-events-none">
              <Lock size={16} className="text-navy/70" />
            </div>
            <input 
              type={showPassword ? 'text' : 'password'} 
              className="w-full h-52px pl-10 pr-10 rounded-lg border border-gray-200 bg-white focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all text-13px font-medium text-navy placeholder:text-gray-400 placeholder:font-normal"
              placeholder={t('app.password')}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button 
              type="button" 
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 flex items-center justify-center w-5 h-5 text-gray-400 hover:text-gray-600 transition-colors"
            >
               {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
            </button>
          </div>
          <div className="flex justify-end mt-1.5">
             <button type="button" className="text-11px font-bold text-orange-500 text-orange-500-hover:hover transition-colors">
               {t('app.forgot_password')}
             </button>
          </div>
        </div>

        {error && (
          <div className="text-red-500 text-xs font-semibold text-center mt-1">
            {error}
          </div>
        )}
      </div>

      <button 
        type="submit" 
        className="w-full h-52px bg-dark-green bg-dark-green-hover:hover text-white rounded-lg font-bold flex items-center justify-center gap-2 transition-all shadow-md disabled:opacity-50 mt-4"
        disabled={isLoading || !serviceId || !password}
      >
        {isLoading ? <Loader2 size={20} className="animate-spin" /> : (
          <>
            <Lock size={16} className="mr-1" />
            <span className="font-semibold text-15px">{t('app.sign_in_btn')}</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="ml-1"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
          </>
        )}
      </button>
    </form>
  );
}
