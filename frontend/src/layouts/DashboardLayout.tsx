import React, { useState, useRef, useEffect } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Menu, X, Bell, UserCircle } from 'lucide-react';
import LanguageSelector from '../components/LanguageSelector';
import { useVerification } from '../context/VerificationContext';
import { useTranslation } from 'react-i18next';
import clsx from 'clsx';

export interface SidebarItem {
  icon: React.ReactNode;
  label: string;
  path: string;
}

interface DashboardLayoutProps {
  title: string;
  sidebarItems: SidebarItem[];
  userRole: 'VISITOR' | 'FORCE';
}

export default function DashboardLayout({ title, sidebarItems, userRole }: DashboardLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const location = useLocation();
  const { notifications, markAsRead, markAllAsRead, visitorProfile } = useVerification();
  const { t } = useTranslation();
  const dropdownRef = useRef<HTMLDivElement>(null);

  const roleNotifications = notifications.filter(n => n.role === userRole);
  const unreadCount = roleNotifications.filter(n => !n.read).length;

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const formatTimeAgo = (isoString: string) => {
    const diff = Math.floor((new Date().getTime() - new Date(isoString).getTime()) / 60000);
    if (diff < 1) return 'Just now';
    if (diff < 60) return `${diff}m ago`;
    if (diff < 1440) return `${Math.floor(diff/60)}h ago`;
    return `${Math.floor(diff/1440)}d ago`;
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className={clsx('sidebar', !isSidebarOpen && 'closed')}>
        <div className="sidebar-header" style={{ justifyContent: 'flex-end' }}>
          {isSidebarOpen && (
            <button className="icon-btn" onClick={() => setIsSidebarOpen(false)}>
              <X size={20} />
            </button>
          )}
        </div>

        <nav className="sidebar-nav">
          {sidebarItems.map((item, index) => (
            <Link 
              key={index} 
              to={item.path}
              className={clsx('nav-item', location.pathname === item.path && 'active')}
            >
              <span className="nav-icon">{item.icon}</span>
              {isSidebarOpen && <span className="nav-label">{t(item.label)}</span>}
            </Link>
          ))}
        </nav>
        
        <div className="sidebar-footer">
           <div className="nav-item">
             <UserCircle size={20} className="nav-icon" />
             {isSidebarOpen && (
               <div className="flex flex-col">
                 <span className="text-sm font-semibold">
                   {userRole === 'VISITOR' 
                     ? (visitorProfile?.digiLockerConnected ? 'Visitor (DigiLocker)' : visitorProfile?.mobile || 'Visitor') 
                     : 'Force Ops'}
                 </span>
               </div>
             )}
           </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="topbar relative">
          <div className="flex items-center gap-4 w-1/3">
            {!isSidebarOpen && (
              <button className="icon-btn mobile-menu" onClick={() => setIsSidebarOpen(true)}>
                <Menu size={20} />
              </button>
            )}
            <h1 className="text-xl font-bold text-navy hidden md:block">{t(title)}</h1>
          </div>
          
          <div className="flex-1 flex justify-center items-center gap-2">
            <img src="/logo.png" alt="Logo" style={{ height: '36px' }} onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }} />
            <span className="text-xl font-bold text-navy whitespace-nowrap tracking-wide">SATYA SHIELD</span>
          </div>
          <div className="topbar-actions flex items-center justify-end h-full w-1/3" style={{ gap: '32px' }}>
            <div className="relative h-10 flex items-center" ref={dropdownRef}>
              <button 
                className={clsx('icon-btn relative h-10 w-10 flex items-center justify-center', showNotifications && 'text-primary bg-orange-50')}
                onClick={() => setShowNotifications(!showNotifications)}
              >
                <Bell size={20} />
                {unreadCount > 0 && (
                  <span className="notification-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
                )}
              </button>

              {/* Notification Dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 z-50 overflow-hidden fade-in">
                  <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                    <h3 className="font-bold text-navy">Notifications</h3>
                    {unreadCount > 0 && (
                      <button className="text-xs font-semibold text-primary hover:underline" onClick={() => markAllAsRead(userRole)}>
                        Mark all as read
                      </button>
                    )}
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {roleNotifications.length === 0 ? (
                      <div className="p-8 text-center text-light text-sm">No notifications yet.</div>
                    ) : (
                      roleNotifications.map(n => (
                        <div 
                          key={n.id} 
                          className={clsx('p-4 border-b border-gray-100 transition-colors', !n.read ? 'bg-orange-50/50' : 'hover:bg-gray-50', n.linkTo && 'cursor-pointer')}
                          onClick={() => {
                            if (!n.read) markAsRead(n.id);
                            // If linking to a token, we could navigate here
                          }}
                        >
                          <div className="flex justify-between items-start mb-1">
                            <h4 className={clsx('text-sm', !n.read ? 'font-bold text-navy' : 'font-semibold text-gray-700')}>{n.title}</h4>
                            <span className="text-[10px] font-semibold text-gray-400 whitespace-nowrap ml-2">{formatTimeAgo(n.time)}</span>
                          </div>
                          <p className={clsx('text-xs', !n.read ? 'text-gray-700' : 'text-light')}>{n.message}</p>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="h-10 flex items-center" style={{ width: '120px' }}>
              <LanguageSelector />
            </div>
          </div>
        </header>
        
        <div className="content-area">
          <Outlet />
        </div>
      </main>

      <style>{`
        .dashboard-layout {
          display: flex;
          height: 100vh;
          background-color: var(--color-bg-soft);
          overflow: hidden;
        }

        .sidebar {
          width: 260px;
          background-color: var(--color-white);
          border-right: 1px solid var(--color-border);
          display: flex;
          flex-direction: column;
          transition: width 0.3s;
          flex-shrink: 0;
        }
        
        .sidebar.closed {
          width: 72px;
        }

        .sidebar-header {
          padding: 20px;
          display: flex;
          align-items: center;
          border-bottom: 1px solid var(--color-border);
          height: 72px;
          position: relative;
        }

        .icon-btn {
          background: transparent;
          border: none;
          color: var(--color-text-light);
          padding: 8px;
          border-radius: 8px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }
        
        .icon-btn:hover {
          background-color: var(--color-light-teal);
          color: var(--color-primary-teal);
        }

        .sidebar-nav {
          flex: 1;
          padding: 16px 12px;
          display: flex;
          flex-direction: column;
          gap: 4px;
          overflow-y: auto;
        }

        .nav-item {
          display: flex;
          align-items: center;
          padding: 12px;
          border-radius: 8px;
          color: var(--color-text-navy);
          text-decoration: none;
          transition: all 0.2s;
          white-space: nowrap;
          overflow: hidden;
        }

        .nav-item:hover {
          background-color: var(--color-bg-soft);
        }

        .nav-item.active {
          background-color: var(--color-light-teal);
          color: var(--color-primary-teal);
          font-weight: 600;
        }

        .nav-icon {
          flex-shrink: 0;
          margin-right: 12px;
        }
        
        .sidebar.closed .nav-icon {
          margin-right: 0;
        }

        .sidebar-footer {
          padding: 16px 12px;
          border-top: 1px solid var(--color-border);
        }

        .main-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-width: 0;
        }

        .topbar {
          height: 72px;
          background-color: var(--color-white);
          border-bottom: 1px solid var(--color-border);
          padding: 0 32px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .topbar-actions {
          display: flex;
          align-items: center;
        }

        .notification-badge {
          position: absolute;
          top: 4px;
          right: 4px;
          background-color: var(--color-error);
          color: white;
          font-size: 10px;
          font-weight: bold;
          border-radius: 10px;
          padding: 2px 6px;
          border: 2px solid var(--color-white);
        }

        .content-area {
          flex: 1;
          padding: 32px;
          overflow-y: auto;
        }

        /* Utility classes */
        .flex { display: flex; }
        .flex-col { flex-direction: column; }
        .items-center { align-items: center; }
        .justify-between { justify-content: space-between; }
        .gap-2 { gap: 8px; }
        .font-bold { font-weight: 700; }
        .font-semibold { font-weight: 600; }
        .text-xl { font-size: 20px; }
        .text-sm { font-size: 14px; }
        .text-navy { color: var(--color-text-navy); }
        .text-light { color: var(--color-text-light); }
        .whitespace-nowrap { white-space: nowrap; }
      `}</style>
    </div>
  );
}
