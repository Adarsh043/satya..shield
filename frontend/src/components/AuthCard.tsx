import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { ShieldCheck, Users } from 'lucide-react';
import ForceLogin from './ForceLogin';
import VisitorLogin from './VisitorLogin';
import clsx from 'clsx';

export default function AuthCard() {
  const { t } = useTranslation();
  const [accessType, setAccessType] = useState<'force' | 'visitor'>('force');

  return (
    <div className="bg-white border border-gray-200 rounded-20px p-8 lg:p-10 shadow-card w-full">
      <div className="text-center mb-8">
        <span className="text-10px font-bold tracking-0-15em text-navy/50 uppercase">
          {t('app.secure_access')}
        </span>
        <h2 className="text-22px font-extrabold mt-1 mb-1.5" style={{color: '#2D3748'}}>
          {t('app.sign_in')}
        </h2>
        <p className="text-gray-500 text-13px">
          {t('app.select_type')}
        </p>
      </div>

      <div className="flex gap-4 mb-8">
        <button 
          className={clsx(
            'flex-1 flex flex-col items-center justify-end py-3 px-2 rounded-xl transition-all min-h-[96px] relative overflow-hidden',
            accessType === 'force' 
              ? 'border border-force shadow-force' 
              : 'border border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
          )}
          style={accessType === 'force' ? {
            backgroundColor: '#FFF4EA', /* Light orange */
          } : {}}
          onClick={() => setAccessType('force')}
        >
          {/* Emblem Background */}
          {accessType === 'force' && (
            <div 
              className="absolute inset-x-0 -top-4 bottom-8 opacity-30 mix-blend-multiply pointer-events-none"
              style={{
                backgroundImage: 'url(/army-emblem.png)',
                backgroundSize: 'contain',
                backgroundPosition: 'top center',
                backgroundRepeat: 'no-repeat'
              }}
            />
          )}

          <div className="relative z-10 mt-auto flex flex-col items-center w-full pt-10">
            <span className={clsx("text-[14px] font-black uppercase tracking-wide", accessType === 'force' ? "text-[#F58220]" : "text-navy")}>{t('app.force')}</span>
            <span className="text-[11px] text-gray-500 font-medium leading-tight">{t('app.force_desc')}</span>
          </div>
        </button>

        <button 
          className={clsx(
            'flex-1 flex flex-col items-center justify-center py-3 px-2 rounded-xl transition-all min-h-[96px]',
            accessType === 'visitor' 
              ? 'border border-visitor bg-visitor-gradient shadow-visitor' 
              : 'border border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
          )}
          onClick={() => setAccessType('visitor')}
        >
          <div className="mb-0.5 h-11 flex items-center justify-center">
            <Users size={32} strokeWidth={2} className={clsx(accessType === 'visitor' ? "text-dark-green" : "text-navy/50")} />
          </div>
          <span className={clsx("text-[14px] font-black uppercase tracking-wide", accessType === 'visitor' ? "text-dark-green" : "text-navy")}>{t('app.visitor')}</span>
          <span className="text-[11px] text-gray-500 font-medium leading-tight">{t('app.visitor_desc')}</span>
        </button>
      </div>

      <div className="min-h-220px">
        {accessType === 'force' ? <ForceLogin /> : <VisitorLogin />}
      </div>

      {/* Footer */}
      <div className="mt-8 flex items-center justify-center gap-2 text-navy/40">
        <ShieldCheck size={14} />
        <span className="text-9px font-medium tracking-wide">Protected Access <span className="mx-1">|</span> All activities are monitored and logged</span>
      </div>
    </div>
  );
}
