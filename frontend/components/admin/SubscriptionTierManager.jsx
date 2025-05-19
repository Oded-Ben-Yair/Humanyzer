/**
 * Subscription Tier Manager component for admin interface.
 * 
 * This component allows administrators to manage subscription tiers,
 * including viewing and editing tier features and assigning features to tiers.
 */
import React, { useState, useEffect } from 'react';
import { getAllFeatureFlags } from '../../services/featureFlagService';

// Mock API functions for subscription tier management
// In a real implementation, these would be actual API calls
const getSubscriptionTiers = async () => {
  // Fetch subscription tiers from API
  const response = await fetch('/api/payments/plans');
  if (!response.ok) {
    throw new Error('Failed to fetch subscription tiers');
  }
  const data = await response.json();
  return data.plans;
};

const updateSubscriptionTier = async (tierId, tierData) => {
  // Update subscription tier via API
  const response = await fetch(`/api/admin/subscription-tiers/${tierId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(tierData)
  });
  
  if (!response.ok) {
    throw new Error('Failed to update subscription tier');
  }
  
  return await response.json();
};

const SubscriptionTierManager = () => {
  const [tiers, setTiers] = useState([]);
  const [featureFlags, setFeatureFlags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTier, setSelectedTier] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price_amount: 0,
    features: {}
  });

  // Load subscription tiers and feature flags
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch tiers and feature flags in parallel
        const [tiersData, flagsData] = await Promise.all([
          getSubscriptionTiers(),
          getAllFeatureFlags()
        ]);
        
        setTiers(tiersData);
        setFeatureFlags(flagsData);
        setError(null);
      } catch (err) {
        setError('Failed to load data. Please try again.');
        console.error('Error loading data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      // For feature checkboxes
      if (name.startsWith('feature_')) {
        const featureKey = name.replace('feature_', '');
        setFormData({
          ...formData,
          features: {
            ...formData.features,
            [featureKey]: checked
          }
        });
      } else {
        setFormData({ ...formData, [name]: checked });
      }
    } else if (name === 'price_amount') {
      // Convert price to number
      setFormData({ ...formData, [name]: parseInt(value, 10) });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  // Select a tier for editing
  const handleSelectTier = (tier) => {
    setSelectedTier(tier);
    
    // Prepare form data
    const tierFeatures = {};
    featureFlags.forEach(flag => {
      // Check if this feature is available for this tier
      const minTier = flag.min_subscription_tier;
      const tierLevel = getTierLevel(tier.tier);
      const minTierLevel = minTier ? getTierLevel(minTier) : 0;
      
      tierFeatures[flag.key] = tierLevel >= minTierLevel;
    });
    
    setFormData({
      name: tier.name,
      description: tier.description,
      price_amount: tier.price_amount,
      features: tierFeatures
    });
    
    setIsEditing(true);
  };

  // Helper function to get tier level
  const getTierLevel = (tier) => {
    const levels = {
      'free': 0,
      'basic': 1,
      'pro': 2,
      'enterprise': 3
    };
    
    return levels[tier] || 0;
  };

  // Submit form to update a tier
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      // Prepare data for API
      const tierData = {
        ...formData,
        // Convert features to min_subscription_tier for each feature flag
        feature_assignments: Object.entries(formData.features).map(([key, enabled]) => ({
          feature_key: key,
          enabled,
          min_tier: enabled ? selectedTier.tier : null
        }))
      };
      
      // Update tier
      await updateSubscriptionTier(selectedTier.id, tierData);
      
      // Refresh tiers
      const updatedTiers = await getSubscriptionTiers();
      setTiers(updatedTiers);
      
      // Reset form
      setIsEditing(false);
      setSelectedTier(null);
      setError(null);
    } catch (err) {
      setError('Failed to update subscription tier. Please try again.');
      console.error('Error updating subscription tier:', err);
    } finally {
      setLoading(false);
    }
  };

  // Render loading state
  if (loading && !tiers.length) {
    return <div className="loading">Loading subscription tiers...</div>;
  }

  return (
    <div className="subscription-tier-manager">
      <h2>Subscription Tier Management</h2>
      
      {error && <div className="error">{error}</div>}
      
      <div className="subscription-tier-container">
        <div className="subscription-tier-list">
          <h3>Subscription Tiers</h3>
          
          {tiers.length === 0 ? (
            <p>No subscription tiers found.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Price</th>
                  <th>Description</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tiers.map(tier => (
                  <tr key={tier.id} className={selectedTier && selectedTier.id === tier.id ? 'selected' : ''}>
                    <td>{tier.name}</td>
                    <td>${(tier.price_amount / 100).toFixed(2)}/{tier.interval}</td>
                    <td>{tier.description}</td>
                    <td>
                      <button onClick={() => handleSelectTier(tier)} className="btn btn-sm btn-info">
                        Manage Features
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        
        {isEditing && selectedTier && (
          <div className="subscription-tier-detail">
            <h3>Manage Features for {selectedTier.name} Tier</h3>
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="name">Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="form-control"
                  disabled
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  className="form-control"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="price_amount">Price (in cents)</label>
                <input
                  type="number"
                  id="price_amount"
                  name="price_amount"
                  value={formData.price_amount}
                  onChange={handleInputChange}
                  min="0"
                  className="form-control"
                />
              </div>
              
              <h4>Available Features</h4>
              
              {featureFlags.length === 0 ? (
                <p>No feature flags found.</p>
              ) : (
                <div className="feature-list">
                  {featureFlags.map(flag => (
                    <div key={flag.key} className="feature-item">
                      <label htmlFor={`feature_${flag.key}`}>
                        <input
                          type="checkbox"
                          id={`feature_${flag.key}`}
                          name={`feature_${flag.key}`}
                          checked={formData.features[flag.key] || false}
                          onChange={handleInputChange}
                        />
                        {flag.name}
                      </label>
                      <p className="feature-description">{flag.description}</p>
                    </div>
                  ))}
                </div>
              )}
              
              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="btn btn-secondary"
                  disabled={loading}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubscriptionTierManager;
