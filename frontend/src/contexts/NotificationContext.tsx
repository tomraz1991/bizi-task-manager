import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getNotifications, NotificationItem } from '../api';
import { format } from 'date-fns';

interface NotificationContextType {
  notifications: NotificationItem[];
  refreshNotifications: () => Promise<void>;
  requestPermission: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  const refreshNotifications = useCallback(async () => {
    try {
      const response = await getNotifications(7);
      setNotifications(response.data);
      
      // Show browser notifications for urgent items
      if ('Notification' in window && Notification.permission === 'granted') {
        const urgentNotifications = response.data.filter(n => n.priority === 'urgent');
        urgentNotifications.forEach(notif => {
          new Notification(notif.title, {
            body: notif.message,
            icon: '/vite.svg',
            tag: notif.id,
          });
        });
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  }, []);

  const requestPermission = useCallback(async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission();
    }
  }, []);

  useEffect(() => {
    requestPermission();
    refreshNotifications();
    
    // Refresh notifications every 5 minutes
    const interval = setInterval(refreshNotifications, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [refreshNotifications, requestPermission]);

  return (
    <NotificationContext.Provider value={{ notifications, refreshNotifications, requestPermission }}>
      {children}
    </NotificationContext.Provider>
  );
};
