import { ShieldCheck, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function ForceDashboard() {
  const navigate = useNavigate();
  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <ShieldCheck size={32} color="var(--color-primary-teal)" />
          <h1 style={{ color: 'var(--color-primary-teal)' }}>SATYA SHIELD</h1>
        </div>
        <button className="secondary-btn" style={{ width: 'auto' }} onClick={() => navigate('/')}>
          <LogOut size={18} />
          Sign Out
        </button>
      </header>
      <div style={{ backgroundColor: 'white', padding: '32px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
        <h2>Force Personnel Dashboard</h2>
        <p style={{ marginTop: '16px', color: 'var(--color-text-light)' }}>
          Welcome to the secure operations center. Your identity has been verified.
        </p>
      </div>
    </div>
  );
}
