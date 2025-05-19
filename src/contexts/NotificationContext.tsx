
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { toast, ToastContainer, ToastOptions } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Notification types
export type NotificationType = 'info' | 'success' | 'warning' | 'error';

// Notification interface
export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  title?: string;
  read: boolean;
  timestamp: Date;
}

// Notification context interface
interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  showNotification: (type: NotificationType, message: string, title?: string) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearNotifications: () => void;
}

// Create the notification context
const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// Toast configuration based on notification type
const toastConfig: Record<NotificationType, ToastOptions> = {
  info: {
    position: 'top-right',
    autoClose: 3000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  },
  success: {
    position: 'top-right',
    autoClose: 3000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  },
  warning: {
    position: 'top-right',
    autoClose: 5000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  },
  error: {
    position: 'top-right',
    autoClose: 5000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  },
};

// Notification provider component
export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  
  // Calculate unread count
  const unreadCount = notifications.filter(notification => !notification.read).length;
  
  // Load notifications from localStorage on mount
  useEffect(() => {
    const savedNotifications = localStorage.getItem('notifications');
    if (savedNotifications) {
      try {
        const parsedNotifications = JSON.parse(savedNotifications);
        // Convert string timestamps back to Date objects
        const formattedNotifications = parsedNotifications.map((notification: any) => ({
          ...notification,
          timestamp: new Date(notification.timestamp),
        }));
        setNotifications(formattedNotifications);
      } catch (error) {
        console.error('Failed to parse saved notifications:', error);
      }
    }
  }, []);
  
  // Save notifications to localStorage when they change
  useEffect(() => {
    localStorage.setItem('notifications', JSON.stringify(notifications));
  }, [notifications]);
  
  // Show a notification
  const showNotification = (type: NotificationType, message: string, title?: string) => {
    // Create a new notification
    const newNotification: Notification = {
      id: Date.now().toString(),
      type,
      message,
      title,
      read: false,
      timestamp: new Date(),
    };
    
    // Add to notifications list
    setNotifications(prev => [newNotification, ...prev]);
    
    // Show toast notification
    switch (type) {
      case 'info':
        toast.info(title ? `${title}: ${message}` : message, toastConfig.info);
        break;
      case 'success':
        toast.success(title ? `${title}: ${message}` : message, toastConfig.success);
        break;
      case 'warning':
        toast.warning(title ? `${title}: ${message}` : message, toastConfig.warning);
        break;
      case 'error':
        toast.error(title ? `${title}: ${message}` : message, toastConfig.error);
        break;
    }
  };
  
  // Mark a notification as read
  const markAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === id
          ? { ...notification, read: true }
          : notification
      )
    );
  };
  
  // Mark all notifications as read
  const markAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    );
  };
  
  // Clear all notifications
  const clearNotifications = () => {
    setNotifications([]);
  };
  
  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        showNotification,
        markAsRead,
        markAllAsRead,
        clearNotifications,
      }}
    >
      {children}
      <ToastContainer />
    </NotificationContext.Provider>
  );
}

// Custom hook to use the notification context
export function useNotification() {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
}
