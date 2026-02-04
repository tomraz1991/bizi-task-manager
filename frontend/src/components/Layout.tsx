import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useState, useRef, useEffect } from 'react';
import { Home, FileAudio, CheckSquare, Bell, Users, X } from 'lucide-react';
import { useNotifications } from '../contexts/NotificationContext';
import { formatDistanceToNow } from 'date-fns';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { notifications, requestPermission } = useNotifications();
  const [showNotifications, setShowNotifications] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const urgentCount = notifications.filter(n => n.priority === 'urgent').length;

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/episodes', label: 'Episodes', icon: FileAudio },
    { path: '/tasks', label: 'Tasks', icon: CheckSquare },
    { path: '/engineers', label: 'Engineers', icon: Users },
  ];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    };

    if (showNotifications) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showNotifications]);

  const handleNotificationClick = (notif: typeof notifications[0]) => {
    setShowNotifications(false);
    if (notif.episode_id) {
      navigate('/episodes');
    } else if (notif.task_id) {
      navigate('/tasks');
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'border-red-500 bg-gradient-to-r from-red-50 to-red-50/50';
      case 'high':
        return 'border-orange-500 bg-gradient-to-r from-orange-50 to-orange-50/50';
      case 'normal':
        return 'border-blue-500 bg-gradient-to-r from-blue-50 to-blue-50/50';
      default:
        return 'border-gray-500 bg-gradient-to-r from-gray-50 to-gray-50/50';
    }
  };

  return (
    <div className="min-h-screen">
      <nav className="glass-dark border-b border-gray-200/50 sticky top-0 z-40 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-400 bg-clip-text text-transparent">
                  Podcast Task Manager
                </h1>
              </div>
              <div className="hidden sm:ml-8 sm:flex sm:space-x-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                        isActive
                          ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/30'
                          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100/50'
                      }`}
                    >
                      <Icon className={`mr-2 h-4 w-4 ${isActive ? 'text-white' : ''}`} />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </div>
            <div className="flex items-center">
              <div className="relative" ref={dropdownRef}>
                <button
                  onClick={() => {
                    setShowNotifications(!showNotifications);
                    requestPermission();
                  }}
                  className="relative p-2.5 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100/50 transition-all duration-200"
                  title="Notifications"
                >
                  <Bell className="h-5 w-5" />
                  {urgentCount > 0 && (
                    <span className="absolute top-1 right-1 block h-2.5 w-2.5 rounded-full bg-red-500 ring-2 ring-white animate-pulse" />
                  )}
                </button>
                
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 glass-dark rounded-xl shadow-2xl border border-gray-200/50 z-50 max-h-96 overflow-y-auto animate-in fade-in slide-in-from-top-2 duration-200">
                    <div className="p-4 border-b border-gray-200/50 flex justify-between items-center bg-gradient-to-r from-primary-50 to-transparent">
                      <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
                      <button
                        onClick={() => setShowNotifications(false)}
                        className="text-gray-400 hover:text-gray-600 rounded-lg p-1 hover:bg-gray-100 transition-colors"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                    <div className="divide-y divide-gray-200/50">
                      {notifications.length === 0 ? (
                        <div className="p-8 text-center text-sm text-gray-500">
                          <Bell className="h-8 w-8 mx-auto mb-2 text-gray-300" />
                          No notifications
                        </div>
                      ) : (
                        notifications.map((notif) => (
                          <button
                            key={notif.id}
                            onClick={() => handleNotificationClick(notif)}
                            className={`w-full text-left p-4 hover:bg-gray-50/50 transition-all duration-200 border-l-4 ${getPriorityColor(notif.priority)} group`}
                          >
                            <p className="text-sm font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">{notif.title}</p>
                            <p className="text-sm text-gray-600 mt-1">{notif.message}</p>
                            <p className="text-xs text-gray-400 mt-2">
                              {formatDistanceToNow(new Date(notif.due_date), { addSuffix: true })}
                            </p>
                          </button>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
