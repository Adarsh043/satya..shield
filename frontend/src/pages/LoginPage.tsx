
import AuthCard from '../components/AuthCard';
import LanguageSelector from '../components/LanguageSelector';
import { useTranslation } from 'react-i18next';

export default function LoginPage() {
  const { t } = useTranslation();

  return (
    <div className="h-screen flex flex-col lg:flex-row relative bg-white overflow-hidden w-full">
      {/* Top Tricolour Line */}
      <div className="absolute top-0 left-0 w-full h-1 flex z-50">
        <div className="h-full flex-1" style={{backgroundColor: '#FF9933'}}></div>
        <div className="h-full bg-white flex-1"></div>
        <div className="h-full flex-1" style={{backgroundColor: '#138808'}}></div>
      </div>

      {/* Top right language selector */}
      <div className="absolute top-4 right-4 z-50">
        <LanguageSelector />
      </div>

      {/* Left Side - Branding Hero (Static Image) */}
      <div className="relative w-full lg:w-50 h-[40vh] lg:h-full overflow-hidden shrink-0 border-r border-black/5" style={{backgroundColor: '#FDFBF7'}}>
        <img 
          src="/login-left-panel-2.jpg" 
          alt="Satya Shield Branding" 
          className="w-full h-full object-cover object-center"
        />
      </div>

      {/* Right Side - Auth Section */}
      <div className="w-full lg:w-50 flex items-center justify-center p-6 lg:p-12 relative overflow-hidden bg-white h-[60vh] lg:h-full overflow-y-auto">
        
        {/* Flag swipe top right */}
        <div className="absolute top-0 right-0 w-72 h-48 pointer-events-none overflow-hidden">
          <div className="absolute top-[-20px] right-[-20px] w-120pct h-30px transform rotate-12 shadow-sm" style={{backgroundColor: '#FF9933'}}></div>
          <div className="absolute top-[5px] right-[-20px] w-120pct h-30px bg-white transform rotate-12 shadow-sm flex items-center justify-center"><div className="w-8 h-8 rounded-full border border-blue-800 opacity-50"></div></div>
          <div className="absolute top-[30px] right-[-20px] w-120pct h-30px transform rotate-12 shadow-sm" style={{backgroundColor: '#138808'}}></div>
        </div>

        {/* Top right text */}
        <div className="absolute top-20 right-10 text-right pointer-events-none hidden lg:block z-10">
           <p className="font-bold text-dark-green text-15px leading-tight">
             {t('app.footer_top')}<br/>{t('app.footer_sub')}
           </p>
           <p className="text-9px font-bold text-navy/70 tracking-0-05em mt-2 leading-snug">
             SAFE BORDERS<br/>STRONGER TOMORROW
           </p>
        </div>
        {/* Monuments footer skyline */}
        <div className="absolute bottom-0 left-0 w-full h-32 opacity-15 pointer-events-none flex items-end justify-center">
           <svg viewBox="0 0 1000 200" className="w-full h-full object-cover" preserveAspectRatio="none">
             <path d="M0,200 L1000,200 L1000,180 Q980,180 970,160 Q950,120 930,160 L920,170 L890,170 Q870,120 850,150 Q830,100 810,140 L790,160 Q750,100 700,120 Q650,80 600,100 Q550,50 500,100 Q450,20 400,90 L380,120 Q350,80 300,130 L280,150 Q230,100 200,160 L180,170 L150,140 Q100,100 50,150 L30,170 L0,180 Z" fill="#9CA3AF" />
             <rect x="0" y="195" width="1000" height="5" fill="#9CA3AF" />
           </svg>
        </div>


        
        <div className="absolute bottom-4 left-0 w-full text-center pointer-events-none z-10 flex flex-col items-center">
           <p className="text-9px font-bold tracking-0-15em text-navy/40">
              {t('app.footer_nation')}
           </p>
           {/* Tricolor underline */}
           <div className="w-24 h-[3px] mt-1 flex">
             <div className="h-full flex-1" style={{backgroundColor: '#FF9933'}}></div>
             <div className="h-full" style={{backgroundColor: '#000080', width: '3px'}}></div>
             <div className="h-full flex-1" style={{backgroundColor: '#138808'}}></div>
           </div>
        </div>

        {/* Authentication Card */}
        <div className="relative z-10 w-full max-w-460px lg:mt-0" style={{marginTop: '4rem'}}>
          <AuthCard />
        </div>

      </div>
    </div>
  );
}
