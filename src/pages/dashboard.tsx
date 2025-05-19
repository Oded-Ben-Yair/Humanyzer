
import React from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';
import { useNotification } from '@/contexts/NotificationContext';
import AnalyticsDashboard from '@/components/AnalyticsDashboard';
import NotificationCenter from '@/components/Notification';
import FeatureGate from '@/components/FeatureGate';

export default function Dashboard() {
  const router = useRouter();
  const { user, logout, isLoading } = useAuth();
  const { showNotification } = useNotification();
  
  // Handle logout
  const handleLogout = async () => {
    try {
      await logout();
      showNotification('success', 'Logged out successfully');
      router.push('/login');
    } catch (error) {
      showNotification('error', 'Failed to logout');
      console.error('Logout error:', error);
    }
  };
  
  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  // If not authenticated, redirect to login
  if (!user) {
    router.push('/login');
    return null;
  }
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Humanyzer Dashboard</h1>
          
          <div className="flex items-center space-x-4">
            {/* Notification Center */}
            <FeatureGate feature="notifications">
              <NotificationCenter />
            </FeatureGate>
            
            {/* User Menu */}
            <div className="relative">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-700">{user.username}</span>
                <button
                  onClick={handleLogout}
                  className="px-3 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-md transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Welcome, {user.username}!</h2>
          <p className="text-gray-600">
            Here's an overview of your analytics and recent activities.
          </p>
        </div>
        
        {/* Analytics Dashboard */}
        <FeatureGate 
          feature="analytics"
          fallback={
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Analytics Dashboard</h3>
              <p className="text-gray-600 mb-4">
                Analytics features are currently disabled. Please enable them in your environment configuration.
              </p>
              <button 
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                onClick={() => showNotification('info', 'Please contact your administrator to enable analytics')}
              >
                Request Access
              </button>
            </div>
          }
        >
          <AnalyticsDashboard />
        </FeatureGate>
        
        {/* Risk Indicators Section */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Risk Assessment</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded-lg shadow-md">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-700">Security Risk</h4>
                <span className="risk-indicator risk-low px-2 py-1 text-xs font-bold rounded-full">Low</span>
              </div>
              <p className="text-sm text-gray-600">All security measures are up to date.</p>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-md">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-700">Compliance Risk</h4>
                <span className="risk-indicator risk-medium px-2 py-1 text-xs font-bold rounded-full">Medium</span>
              </div>
              <p className="text-sm text-gray-600">Some compliance documents need review.</p>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-md">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-700">Financial Risk</h4>
                <span className="risk-indicator risk-high px-2 py-1 text-xs font-bold rounded-full">High</span>
              </div>
              <p className="text-sm text-gray-600">Several invoices are overdue.</p>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow-md">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-700">Operational Risk</h4>
                <span className="risk-indicator risk-critical px-2 py-1 text-xs font-bold rounded-full">Critical</span>
              </div>
              <p className="text-sm text-gray-600">System maintenance required immediately.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
