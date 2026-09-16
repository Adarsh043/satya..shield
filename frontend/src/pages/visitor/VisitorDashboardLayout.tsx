import { LayoutDashboard, FileText, History, Bell, User, HelpCircle } from 'lucide-react';
import DashboardLayout, { type SidebarItem } from '../../layouts/DashboardLayout';
import { useTranslation } from 'react-i18next';

export default function VisitorDashboardLayout() {
  const { t } = useTranslation();
  
  const sidebarItems: SidebarItem[] = [
    { icon: <LayoutDashboard size={20} />, label: t('dashboard.visitor.home') || 'Dashboard', path: '/visitor-dashboard' },
    { icon: <FileText size={20} />, label: t('dashboard.visitor.submit') || 'Submit Document', path: '/visitor-dashboard/submit' },
    { icon: <History size={20} />, label: t('dashboard.visitor.history') || 'Verification History', path: '/visitor-dashboard/history' },
    { icon: <Bell size={20} />, label: t('dashboard.visitor.notifications') || 'Notifications', path: '/visitor-dashboard/notifications' },
    { icon: <User size={20} />, label: t('dashboard.visitor.profile') || 'Profile', path: '/visitor-dashboard/profile' },
    { icon: <HelpCircle size={20} />, label: t('dashboard.visitor.help') || 'Help', path: '/visitor-dashboard/help' },
  ];

  return <DashboardLayout title="Visitor Dashboard" sidebarItems={sidebarItems} userRole="VISITOR" />;
}
