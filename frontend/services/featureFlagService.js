/**
 * Feature flag service for client-side feature flag checks.
 */
import { getAuthToken } from '../utils/auth';

// Cache for feature flag status to reduce API calls
const featureFlagCache = {};
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes in milliseconds

/**
 * Check if a feature flag is enabled.
 * 
 * @param {string} flagKey - Feature flag key
 * @returns {Promise<boolean>} Whether the feature is enabled
 */
export const isFeatureEnabled = async (flagKey) => {
  try {
    // Check cache first
    const cacheKey = `feature_flag:${flagKey}`;
    const cachedValue = featureFlagCache[cacheKey];
    
    if (cachedValue && (Date.now() - cachedValue.timestamp) < CACHE_TTL) {
      return cachedValue.enabled;
    }

    // Fetch from API
    const token = await getAuthToken();
    
    if (!token) {
      return false;
    }
    
    const response = await fetch(`/api/feature-flags/status/${flagKey}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      
      // Update cache
      featureFlagCache[cacheKey] = {
        enabled: data.enabled,
        timestamp: Date.now()
      };
      
      return data.enabled;
    }
    
    return false;
  } catch (error) {
    console.error(`Error checking feature flag ${flagKey}:`, error);
    return false;
  }
};

/**
 * Clear the feature flag cache.
 */
export const clearFeatureFlagCache = () => {
  Object.keys(featureFlagCache).forEach(key => {
    delete featureFlagCache[key];
  });
};

/**
 * Get all feature flags (admin only).
 * 
 * @returns {Promise<Array>} List of feature flags
 */
export const getAllFeatureFlags = async () => {
  try {
    const token = await getAuthToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch('/api/feature-flags', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      return data.flags;
    }
    
    throw new Error(`Error fetching feature flags: ${response.statusText}`);
  } catch (error) {
    console.error('Error fetching feature flags:', error);
    throw error;
  }
};

/**
 * Create a new feature flag (admin only).
 * 
 * @param {Object} flagData - Feature flag data
 * @returns {Promise<Object>} Created feature flag
 */
export const createFeatureFlag = async (flagData) => {
  try {
    const token = await getAuthToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch('/api/feature-flags', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(flagData)
    });

    if (response.ok) {
      const data = await response.json();
      
      // Clear cache
      clearFeatureFlagCache();
      
      return data;
    }
    
    throw new Error(`Error creating feature flag: ${response.statusText}`);
  } catch (error) {
    console.error('Error creating feature flag:', error);
    throw error;
  }
};

/**
 * Update a feature flag (admin only).
 * 
 * @param {string} flagKey - Feature flag key
 * @param {Object} flagData - Feature flag data to update
 * @returns {Promise<Object>} Updated feature flag
 */
export const updateFeatureFlag = async (flagKey, flagData) => {
  try {
    const token = await getAuthToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`/api/feature-flags/${flagKey}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(flagData)
    });

    if (response.ok) {
      const data = await response.json();
      
      // Clear cache
      clearFeatureFlagCache();
      
      return data;
    }
    
    throw new Error(`Error updating feature flag: ${response.statusText}`);
  } catch (error) {
    console.error(`Error updating feature flag ${flagKey}:`, error);
    throw error;
  }
};

/**
 * Delete a feature flag (admin only).
 * 
 * @param {string} flagKey - Feature flag key
 * @returns {Promise<boolean>} Whether the flag was deleted
 */
export const deleteFeatureFlag = async (flagKey) => {
  try {
    const token = await getAuthToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`/api/feature-flags/${flagKey}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      // Clear cache
      clearFeatureFlagCache();
      
      return true;
    }
    
    throw new Error(`Error deleting feature flag: ${response.statusText}`);
  } catch (error) {
    console.error(`Error deleting feature flag ${flagKey}:`, error);
    throw error;
  }
};

/**
 * Create a user-specific feature flag override (admin only).
 * 
 * @param {Object} overrideData - Feature override data
 * @returns {Promise<Object>} Created feature override
 */
export const createFeatureOverride = async (overrideData) => {
  try {
    const token = await getAuthToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch('/api/feature-flags/overrides', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(overrideData)
    });

    if (response.ok) {
      const data = await response.json();
      
      // Clear cache
      clearFeatureFlagCache();
      
      return data;
    }
    
    throw new Error(`Error creating feature override: ${response.statusText}`);
  } catch (error) {
    console.error('Error creating feature override:', error);
    throw error;
  }
};

/**
 * Delete a user-specific feature flag override (admin only).
 * 
 * @param {string} flagKey - Feature flag key
 * @param {string} userId - User ID
 * @returns {Promise<boolean>} Whether the override was deleted
 */
export const deleteFeatureOverride = async (flagKey, userId) => {
  try {
    const token = await getAuthToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`/api/feature-flags/overrides/${flagKey}/${userId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      // Clear cache
      clearFeatureFlagCache();
      
      return true;
    }
    
    throw new Error(`Error deleting feature override: ${response.statusText}`);
  } catch (error) {
    console.error(`Error deleting feature override for flag ${flagKey} and user ${userId}:`, error);
    throw error;
  }
};
