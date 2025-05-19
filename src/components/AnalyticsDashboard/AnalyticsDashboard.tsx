
import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';
import { useFeature } from '@/contexts/FeatureContext';
import { useNotification } from '@/contexts/NotificationContext';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

// Mock data for analytics
const mockUserData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    {
      label: 'Active Users',
      data: [1200, 1900, 3000, 5000, 4000, 6000],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.5)',
    },
  ],
};

const mockConversionData = {
  labels: ['Landing', 'Signup', 'Activation', 'Conversion'],
  datasets: [
    {
      label: 'Conversion Funnel',
      data: [1000, 700, 500, 300],
      backgroundColor: [
        'rgba(59, 130, 246, 0.6)',
        'rgba(16, 185, 129, 0.6)',
        'rgba(245, 158, 11, 0.6)',
        'rgba(239, 68, 68, 0.6)',
      ],
      borderColor: [
        'rgb(59, 130, 246)',
        'rgb(16, 185, 129)',
        'rgb(245, 158, 11)',
        'rgb(239, 68, 68)',
      ],
      borderWidth: 1,
    },
  ],
};

const mockDeviceData = {
  labels: ['Desktop', 'Mobile', 'Tablet'],
  datasets: [
    {
      label: 'Device Usage',
      data: [55, 35, 10],
      backgroundColor: [
        'rgba(59, 130, 246, 0.6)',
        'rgba(16, 185, 129, 0.6)',
        'rgba(245, 158, 11, 0.6)',
      ],
      borderColor: [
        'rgb(59, 130, 246)',
        'rgb(16, 185, 129)',
        'rgb(245, 158, 11)',
      ],
      borderWidth: 1,
    },
  ],
};

// Analytics Dashboard Component
export default function AnalyticsDashboard() {
  const [isLoading, setIsLoading] = useState(true);
  const { isEnabled } = useFeature();
  const { showNotification } = useNotification();
  
  // Check if analytics feature is enabled
  const analyticsEnabled = isEnabled('analytics');
  
  useEffect(() => {
    // Simulate data loading
    if (analyticsEnabled) {
      const timer = setTimeout(() => {
        setIsLoading(false);
        showNotification('success', 'Analytics data loaded successfully');
      }, 1000);
      
      return () => clearTimeout(timer);
    } else {
      showNotification('warning', 'Analytics feature is disabled');
    }
  }, [analyticsEnabled, showNotification]);
  
  // If analytics is disabled, show feature gate message
  if (!analyticsEnabled) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-gray-100 rounded-lg">
        <h2 className="text-2xl font-bold text-gray-700 mb-4">Analytics Dashboard</h2>
        <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 mb-4">
          <p className="font-bold">Feature Disabled</p>
          <p>Analytics features are currently disabled. Please enable them in your environment configuration.</p>
        </div>
        <button 
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          onClick={() => showNotification('info', 'Please contact your administrator to enable analytics')}
        >
          Request Access
        </button>
      </div>
    );
  }
  
  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  // Chart options
  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'User Growth',
      },
    },
  };
  
  const barOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Conversion Funnel',
      },
    },
  };
  
  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Device Distribution',
      },
    },
  };
  
  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Analytics Dashboard</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-blue-50 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-blue-700 mb-2">Total Users</h3>
          <p className="text-3xl font-bold">6,000</p>
          <p className="text-sm text-green-600">↑ 20% from last month</p>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-green-700 mb-2">Conversion Rate</h3>
          <p className="text-3xl font-bold">30%</p>
          <p className="text-sm text-green-600">↑ 5% from last month</p>
        </div>
        
        <div className="bg-amber-50 p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-amber-700 mb-2">Avg. Session</h3>
          <p className="text-3xl font-bold">4m 32s</p>
          <p className="text-sm text-red-600">↓ 10% from last month</p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-4 rounded-lg shadow">
          <Line options={lineOptions} data={mockUserData} />
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <Bar options={barOptions} data={mockConversionData} />
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <Pie options={pieOptions} data={mockDeviceData} />
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Top Referrers</h3>
          <ul className="space-y-2">
            <li className="flex justify-between items-center">
              <span>Google</span>
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">45%</span>
            </li>
            <li className="flex justify-between items-center">
              <span>Direct</span>
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">30%</span>
            </li>
            <li className="flex justify-between items-center">
              <span>Twitter</span>
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">15%</span>
            </li>
            <li className="flex justify-between items-center">
              <span>LinkedIn</span>
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">10%</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
