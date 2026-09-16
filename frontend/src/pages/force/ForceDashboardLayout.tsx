import { LayoutDashboard, ListTodo, ShieldAlert, Bell, History, FileBarChart, User, Settings } from 'lucide-react';
import DashboardLayout, { type SidebarItem } from '../../layouts/DashboardLayout';
import { useTranslation } from 'react-i18next';

export default function ForceDashboardLayout() {
  const { t } = useTranslation();
  
  const sidebarItems: SidebarItem[] = [
    { icon: <LayoutDashboard size={20} />, label: t('dashboard.force.home') || 'Dashboard', path: '/force-dashboard' },
    { icon: <ListTodo size={20} />, label: t('dashboard.force.queue') || 'Verification Queue', path: '/force-dashboard/queue' },
    { icon: <ShieldAlert size={20} />, label: t('dashboard.force.alerts') || 'Alerts', path: '/force-dashboard/alerts' },
    { icon: <Bell size={20} />, label: t('dashboard.force.notifications') || 'Notifications', path: '/force-dashboard/notifications' },
    { icon: <History size={20} />, label: t('dashboard.force.history') || 'Verification History', path: '/force-dashboard/history' },
    { icon: <FileBarChart size={20} />, label: t('dashboard.force.reports') || 'Reports', path: '/force-dashboard/reports' },
    { icon: <User size={20} />, label: t('dashboard.force.profile') || 'Profile', path: '/force-dashboard/profile' },
    { icon: <Settings size={20} />, label: t('dashboard.force.settings') || 'Settings', path: '/force-dashboard/settings' },
  ];

  return <DashboardLayout title="Force Operations" sidebarItems={sidebarItems} userRole="FORCE" />;
}
