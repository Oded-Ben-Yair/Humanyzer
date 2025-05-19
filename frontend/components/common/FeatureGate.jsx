/**
 * FeatureGate component for conditional rendering based on feature flags.
 * 
 * This component checks if a feature flag is enabled for the current user
 * and renders its children only if the feature is enabled.
 */
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useAuth } from '../../hooks/useAuth';

// Cache for feature flag status to reduce API calls
const featureFlagCache = {};
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes in milliseconds

/**
 * FeatureGate component.
 * 
 * @param {Object} props - Component props
 * @param {string} props.flagKey - Feature flag key
 * @param {React.ReactNode} props.children - Children to render if feature is enabled
 * @param {React.ReactNode} props.fallback - Optional fallback to render if feature is disabled
 * @param {boolean} props.showLoading - Whether to show loading state
 * @returns {React.ReactNode} Rendered component
 */
const FeatureGate = ({ flagKey, children, fallback = null, showLoading = false }) => {
  const [isEnabled, setIsEnabled] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const { isAuthenticated, getToken } = useAuth();

  useEffect(() => {
    const checkFeatureFlag = async () => {
      // If not authenticated, feature is disabled
      if (!isAuthenticated) {
        setIsEnabled(false);
        setIsLoading(false);
        return;
      }

      try {
        // Check cache first
        const cacheKey = `feature_flag:${flagKey}`;
        const cachedValue = featureFlagCache[cacheKey];
        
        if (cachedValue && (Date.now() - cachedValue.timestamp) < CACHE_TTL) {
          setIsEnabled(cachedValue.enabled);
          setIsLoading(false);
          return;
        }

        // Fetch from API
        const token = await getToken();
        const response = await fetch(`/api/feature-flags/status/${flagKey}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setIsEnabled(data.enabled);
          
          // Update cache
          featureFlagCache[cacheKey] = {
            enabled: data.enabled,
            timestamp: Date.now()
          };
        } else {
          console.error(`Error checking feature flag ${flagKey}:`, await response.text());
          setIsEnabled(false);
        }
      } catch (error) {
        console.error(`Error checking feature flag ${flagKey}:`, error);
        setIsEnabled(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkFeatureFlag();
  }, [flagKey, isAuthenticated, getToken]);

  // Show loading state
  if (isLoading && showLoading) {
    return <div className="feature-gate-loading">Loading...</div>;
  }

  // Render children if feature is enabled
  if (isEnabled) {
    return children;
  }

  // Render fallback if feature is disabled
  return fallback;
};

FeatureGate.propTypes = {
  flagKey: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  fallback: PropTypes.node,
  showLoading: PropTypes.bool
};

export default FeatureGate;
