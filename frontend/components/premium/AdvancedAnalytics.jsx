/**
 * Advanced Analytics component for premium users.
 * 
 * This component is wrapped with a FeatureGate to ensure it's only
 * accessible to users with the appropriate subscription tier.
 */
import React, { useState, useEffect } from 'react';
import FeatureGate from '../common/FeatureGate';
import { getAuthToken } from '../../utils/auth';

const AdvancedAnalytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        
        const token = await getAuthToken();
        const response = await fetch('/api/premium-features/advanced-analytics', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setAnalyticsData(data.data);
          setError(null);
        } else {
          // Handle error responses
          if (response.status === 403) {
            setError('You need to upgrade your subscription to access advanced analytics.');
          } else {
            setError('Failed to load analytics data. Please try again later.');
          }
        }
      } catch (err) {
        setError('An error occurred while fetching analytics data.');
        console.error('Error fetching analytics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  // Render loading state
  if (loading) {
    return (
      <div className="analytics-loading">
        <div className="spinner"></div>
        <p>Loading advanced analytics...</p>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="analytics-error">
        <p>{error}</p>
      </div>
    );
  }

  // Render analytics data
  if (analyticsData) {
    return (
      <div className="advanced-analytics">
        <h2>Advanced Analytics</h2>
        
        <div className="analytics-insights">
          <h3>Performance Insights</h3>
          <div className="insights-grid">
            {analyticsData.insights.map((insight, index) => (
              <div key={index} className="insight-card">
                <h4>{insight.name}</h4>
                <div className="insight-score">
                  <div 
                    className="score-bar" 
                    style={{ width: `${insight.score}%`, backgroundColor: getScoreColor(insight.score) }}
                  ></div>
                  <span className="score-value">{insight.score}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="analytics-recommendations">
          <h3>Recommendations</h3>
          <ul>
            {analyticsData.recommendations.map((recommendation, index) => (
              <li key={index}>{recommendation}</li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  return null;
};

// Helper function to get color based on score
const getScoreColor = (score) => {
  if (score >= 90) return '#4CAF50'; // Green
  if (score >= 70) return '#2196F3'; // Blue
  if (score >= 50) return '#FF9800'; // Orange
  return '#F44336'; // Red
};

// Wrap the component with FeatureGate
const FeatureGatedAdvancedAnalytics = () => (
  <FeatureGate 
    flagKey="advanced_analytics"
    fallback={
      <div className="feature-upgrade-prompt">
        <h3>Advanced Analytics</h3>
        <p>Upgrade your subscription to access detailed analytics and insights.</p>
        <a href="/subscription" className="upgrade-button">View Plans</a>
      </div>
    }
  >
    <AdvancedAnalytics />
  </FeatureGate>
);

export default FeatureGatedAdvancedAnalytics;
