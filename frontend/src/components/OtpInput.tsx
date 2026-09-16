import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

interface OtpInputProps {
  onVerify: (otp: string) => void;
  onBack: () => void;
  isLoading?: boolean;
  error?: string | null;
  success?: boolean;
  message?: string;
  resendDelay?: number;
}

export default function OtpInput({ 
  onVerify, 
  onBack, 
  isLoading = false, 
  error = null, 
  success = false,
  message,
  resendDelay = 60
}: OtpInputProps) {
  const { t } = useTranslation();
  const [otp, setOtp] = useState<string[]>(new Array(6).fill(''));
  const [activeOtpIndex, setActiveOtpIndex] = useState<number>(0);
  const [countdown, setCountdown] = useState<number>(resendDelay);
  const inputRef = useRef<HTMLInputElement>(null);

  const displayMessage = message || t('app.otp_desc_mobile');

  useEffect(() => {
    inputRef.current?.focus();
  }, [activeOtpIndex]);

  useEffect(() => {
    if (countdown > 0) {
      const timerId = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timerId);
    }
  }, [countdown]);

  const handleChange = ({ target }: React.ChangeEvent<HTMLInputElement>, index: number) => {
    const { value } = target;
    const newOtp = [...otp];
    newOtp[index] = value.substring(value.length - 1);
    setOtp(newOtp);
    if (!value) setActiveOtpIndex(index - 1);
    else if (index < 5) setActiveOtpIndex(index + 1);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === 'Backspace') {
      e.preventDefault();
      const newOtp = [...otp];
      if (otp[index]) {
        newOtp[index] = '';
        setOtp(newOtp);
      } else if (index > 0) {
        newOtp[index - 1] = '';
        setOtp(newOtp);
        setActiveOtpIndex(index - 1);
      }
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').slice(0, 6).split('');
    if (pastedData.length > 0) {
      const newOtp = [...otp];
      pastedData.forEach((char, index) => {
        if (index < 6 && /^[0-9]$/.test(char)) {
          newOtp[index] = char;
        }
      });
      setOtp(newOtp);
      setActiveOtpIndex(Math.min(pastedData.length, 5));
    }
  };

  const submitOtp = () => {
    const otpValue = otp.join('');
    if (otpValue.length === 6) {
      onVerify(otpValue);
    }
  };

  const handleResend = () => {
    setCountdown(resendDelay);
    setOtp(new Array(6).fill(''));
    setActiveOtpIndex(0);
  };

  return (
    <div className="otp-container fade-in">
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
        <button 
          onClick={onBack} 
          disabled={isLoading || success}
          style={{ background: 'none', border: 'none', color: 'var(--color-text-light)', display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          <ArrowLeft size={20} />
          <span>{t('app.back')}</span>
        </button>
      </div>

      <h3 style={{ fontSize: '20px', fontWeight: 600, marginBottom: '8px' }}>{t('app.otp_title')}</h3>
      <p style={{ color: 'var(--color-text-light)', fontSize: '14px', marginBottom: '32px' }}>
        {displayMessage}
      </p>

      <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginBottom: '24px' }}>
        {otp.map((_, index) => (
          <input
            key={index}
            ref={index === activeOtpIndex ? inputRef : null}
            type="text"
            className={clsx('otp-input-box', error && 'otp-input-error', success && 'otp-input-success')}
            value={otp[index]}
            onChange={(e) => handleChange(e, index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            onPaste={handlePaste}
            disabled={isLoading || success}
          />
        ))}
      </div>

      {error && (
        <div className="error-text" style={{ justifyContent: 'center', marginBottom: '20px' }}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div style={{ color: 'var(--color-primary-teal)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '20px' }}>
          <CheckCircle2 size={16} />
          <span>Verification successful</span>
        </div>
      )}

      <button 
        className="primary-btn" 
        onClick={submitOtp} 
        disabled={otp.join('').length !== 6 || isLoading || success}
        style={{ marginBottom: '24px' }}
      >
        {isLoading ? <Loader2 size={20} className="spin" /> : t('app.verify')}
      </button>

      <div style={{ textAlign: 'center', fontSize: '14px' }}>
        {countdown > 0 ? (
          <span style={{ color: 'var(--color-text-light)' }}>
            {t('app.resend_otp')} in <span style={{ fontWeight: 600 }}>00:{countdown.toString().padStart(2, '0')}</span>
          </span>
        ) : (
          <button className="text-btn" onClick={handleResend} disabled={isLoading || success}>
            {t('app.resend_otp')}
          </button>
        )}
      </div>

      <style>{`
        .otp-input-box {
          width: 48px;
          height: 56px;
          border-radius: 8px;
          border: 1.5px solid var(--color-border);
          text-align: center;
          font-size: 24px;
          font-weight: 600;
          color: var(--color-text-navy);
          outline: none;
          transition: all 0.2s;
        }
        .otp-input-box:focus {
          border-color: var(--color-primary-teal);
          box-shadow: 0 0 0 3px var(--color-light-teal);
        }
        .otp-input-error {
          border-color: var(--color-error);
          background-color: var(--color-error-bg);
        }
        .otp-input-success {
          border-color: var(--color-primary-teal);
          background-color: var(--color-light-teal);
        }
      `}</style>
    </div>
  );
}
