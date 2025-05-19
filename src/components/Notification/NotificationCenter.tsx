
import React, { useState } from 'react';
import { useNotification, Notification } from '@/contexts/NotificationContext';
import { motion, AnimatePresence } from 'framer-motion';

// Format date for display
const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

// Get icon based on notification type
const getNotificationIcon = (type: Notification['type']) => {
  switch (type) {
    case 'info':
      return (
        <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
        </svg>
      );
    case 'success':
      return (
        <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      );
    case 'warning':
      return (
        <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      );
    case 'error':
      return (
        <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      );
    default:
      return null;
  }
};

// Get background color based on notification type
const getNotificationBgColor = (type: Notification['type'], read: boolean) => {
  const baseClass = read ? 'bg-opacity-50' : 'bg-opacity-80';
  
  switch (type) {
    case 'info':
      return `bg-blue-100 ${baseClass}`;
    case 'success':
      return `bg-green-100 ${baseClass}`;
    case 'warning':
      return `bg-yellow-100 ${baseClass}`;
    case 'error':
      return `bg-red-100 ${baseClass}`;
    default:
      return `bg-gray-100 ${baseClass}`;
  }
};

// Notification Item Component
const NotificationItem = ({ notification, onRead }: { notification: Notification; onRead: () => void }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
      className={`p-3 mb-2 rounded-lg shadow-sm ${getNotificationBgColor(notification.type, notification.read)} cursor-pointer`}
      onClick={onRead}
    >
      <div className="flex items-start">
        <div className="flex-shrink-0 mr-2">
          {getNotificationIcon(notification.type)}
        </div>
        <div className="flex-1">
          {notification.title && (
            <h4 className="text-sm font-semibold">{notification.title}</h4>
          )}
          <p className="text-sm">{notification.message}</p>
          <p className="text-xs text-gray-500 mt-1">{formatDate(notification.timestamp)}</p>
        </div>
        {!notification.read && (
          <div className="flex-shrink-0 ml-2">
            <span className="inline-block w-2 h-2 bg-blue-600 rounded-full"></span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

// Notification Center Component
export default function NotificationCenter() {
  const [isOpen, setIsOpen] = useState(false);
  const { notifications, unreadCount, markAsRead, markAllAsRead, clearNotifications } = useNotification();
  
  // Toggle notification panel
  const toggleNotifications = () => {
    setIsOpen(!isOpen);
  };
  
  // Handle marking a notification as read
  const handleMarkAsRead = (id: string) => {
    markAsRead(id);
  };
  
  return (
    <div className="relative">
      {/* Notification Bell Icon */}
      <button
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
        onClick={toggleNotifications}
        aria-label="Notifications"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        
        {/* Unread Badge */}
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-500 rounded-full">
            {unreadCount}
          </span>
        )}
      </button>
      
      {/* Notification Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg z-50 overflow-hidden"
          >
            <div className="p-3 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-semibold">Notifications</h3>
              <div className="flex space-x-2">
                <button
                  className="text-xs text-blue-600 hover:text-blue-800"
                  onClick={markAllAsRead}
                >
                  Mark all as read
                </button>
                <button
                  className="text-xs text-red-600 hover:text-red-800"
                  onClick={clearNotifications}
                >
                  Clear all
                </button>
              </div>
            </div>
            
            <div className="max-h-80 overflow-y-auto p-3">
              {notifications.length === 0 ? (
                <p className="text-center text-gray-500 py-4">No notifications</p>
              ) : (
                <AnimatePresence>
                  {notifications.map((notification) => (
                    <NotificationItem
                      key={notification.id}
                      notification={notification}
                      onRead={() => handleMarkAsRead(notification.id)}
                    />
                  ))}
                </AnimatePresence>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
