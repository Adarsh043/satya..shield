import { FileText } from 'lucide-react';
import { useLocation } from 'react-router-dom';

export default function PlaceholderPage() {
  const location = useLocation();
  const pageName = location.pathname.split('/').pop()?.replace(/-/g, ' ') || 'Page';

  return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-center fade-in">
      <FileText size={48} className="text-gray-300 mb-4" />
      <h2 className="text-2xl font-bold text-navy capitalize">{pageName}</h2>
      <p className="text-light mt-2 max-w-md">
        This section is currently under development. The functionality for this page will be available soon.
      </p>
    </div>
  );
}
