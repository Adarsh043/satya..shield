import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

const languages = [
  { code: 'en', name: 'English' },
  { code: 'hi', name: 'हिंदी' },
  { code: 'ur', name: 'اردو' },
  { code: 'ne', name: 'नेपाली' },
  { code: 'dz', name: 'Dzongkha' },
  { code: 'de', name: 'Deutsch' },
  { code: 'es', name: 'Español' },
  { code: 'fr', name: 'Français' }
];

export default function LanguageSelector() {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const currentLang = languages.find(l => l.code === i18n.language) || languages[0];

  return (
    <div className="relative z-50" ref={dropdownRef}>
      <button 
        className="flex items-center gap-1 bg-white border border-gray-200 px-3 py-1 rounded-full text-navy font-semibold text-xs hover:border-gray-300 shadow-sm transition-colors"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Select language"
      >
        <span style={{ fontSize: '14px' }}>🌐</span>
        <span>{currentLang.name}</span>
        <span className="text-10px" style={{ marginLeft: '2px' }}>▼</span>
      </button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-32 bg-white rounded-lg shadow-lg border border-gray-100 overflow-hidden">
          <ul className="py-1">
            {languages.map(lang => (
              <li key={lang.code}>
                <button 
                  type="button"
                  className={`w-full text-left px-4 py-2 text-xs transition-colors ${i18n.language === lang.code ? 'bg-gray-50 text-navy font-bold' : 'text-gray-600 hover:bg-gray-50'}`}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    i18n.changeLanguage(lang.code);
                    setIsOpen(false);
                  }}
                >
                  {lang.name}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
