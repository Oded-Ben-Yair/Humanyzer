/**
 * Feature Flag Manager component for admin interface.
 * 
 * This component allows administrators to manage feature flags,
 * including creating, updating, and deleting flags, as well as
 * managing user-specific overrides.
 */
import React, { useState, useEffect } from 'react';
import {
  getAllFeatureFlags,
  createFeatureFlag,
  updateFeatureFlag,
  deleteFeatureFlag,
  createFeatureOverride,
  deleteFeatureOverride
} from '../../services/featureFlagService';

const FeatureFlagManager = () => {
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFlag, setSelectedFlag] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isManagingOverrides, setIsManagingOverrides] = useState(false);
  
  // Form states
  const [formData, setFormData] = useState({
    key: '',
    name: '',
    description: '',
    enabled: true,
    min_subscription_tier: null,
    percentage_rollout: 100,
    start_date: '',
    end_date: '',
    metadata: {}
  });
  
  const [overrideData, setOverrideData] = useState({
    user_id: '',
    enabled: true
  });

  // Load feature flags
  useEffect(() => {
    const fetchFlags = async () => {
      try {
        setLoading(true);
        const data = await getAllFeatureFlags();
        setFlags(data);
        setError(null);
      } catch (err) {
        setError('Failed to load feature flags. Please try again.');
        console.error('Error loading feature flags:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchFlags();
  }, []);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      setFormData({ ...formData, [name]: checked });
    } else if (name === 'percentage_rollout') {
      setFormData({ ...formData, [name]: parseInt(value, 10) });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };
  
  // Handle override form input changes
  const handleOverrideInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      setOverrideData({ ...overrideData, [name]: checked });
    } else {
      setOverrideData({ ...overrideData, [name]: value });
    }
  };

  // Select a flag for editing
  const handleSelectFlag = (flag) => {
    setSelectedFlag(flag);
    setFormData({
      key: flag.key,
      name: flag.name,
      description: flag.description,
      enabled: flag.enabled,
      min_subscription_tier: flag.min_subscription_tier,
      percentage_rollout: flag.percentage_rollout,
      start_date: flag.start_date ? new Date(flag.start_date).toISOString().split('T')[0] : '',
      end_date: flag.end_date ? new Date(flag.end_date).toISOString().split('T')[0] : '',
      metadata: flag.metadata || {}
    });
    setIsEditing(true);
    setIsCreating(false);
    setIsManagingOverrides(false);
  };

  // Start creating a new flag
  const handleCreateNew = () => {
    setSelectedFlag(null);
    setFormData({
      key: '',
      name: '',
      description: '',
      enabled: true,
      min_subscription_tier: null,
      percentage_rollout: 100,
      start_date: '',
      end_date: '',
      metadata: {}
    });
    setIsCreating(true);
    setIsEditing(false);
    setIsManagingOverrides(false);
  };
  
  // Start managing overrides for a flag
  const handleManageOverrides = (flag) => {
    setSelectedFlag(flag);
    setOverrideData({
      user_id: '',
      enabled: true
    });
    setIsManagingOverrides(true);
    setIsEditing(false);
    setIsCreating(false);
  };

  // Submit form to create or update a flag
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      // Prepare data
      const data = {
        ...formData,
        start_date: formData.start_date ? new Date(formData.start_date).toISOString() : null,
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null
      };
      
      if (isCreating) {
        // Create new flag
        await createFeatureFlag(data);
      } else {
        // Update existing flag
        await updateFeatureFlag(selectedFlag.key, data);
      }
      
      // Refresh flags
      const updatedFlags = await getAllFeatureFlags();
      setFlags(updatedFlags);
      
      // Reset form
      setIsCreating(false);
      setIsEditing(false);
      setSelectedFlag(null);
      setError(null);
    } catch (err) {
      setError(`Failed to ${isCreating ? 'create' : 'update'} feature flag. Please try again.`);
      console.error(`Error ${isCreating ? 'creating' : 'updating'} feature flag:`, err);
    } finally {
      setLoading(false);
    }
  };
  
  // Submit override form
  const handleSubmitOverride = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      // Create override
      await createFeatureOverride({
        flag_key: selectedFlag.key,
        ...overrideData
      });
      
      // Reset form
      setOverrideData({
        user_id: '',
        enabled: true
      });
      
      setError(null);
    } catch (err) {
      setError('Failed to create feature override. Please try again.');
      console.error('Error creating feature override:', err);
    } finally {
      setLoading(false);
    }
  };

  // Delete a flag
  const handleDeleteFlag = async (flag) => {
    if (!window.confirm(`Are you sure you want to delete the feature flag "${flag.name}"?`)) {
      return;
    }
    
    try {
      setLoading(true);
      
      // Delete flag
      await deleteFeatureFlag(flag.key);
      
      // Refresh flags
      const updatedFlags = await getAllFeatureFlags();
      setFlags(updatedFlags);
      
      // Reset form if the deleted flag was selected
      if (selectedFlag && selectedFlag.key === flag.key) {
        setIsCreating(false);
        setIsEditing(false);
        setIsManagingOverrides(false);
        setSelectedFlag(null);
      }
      
      setError(null);
    } catch (err) {
      setError('Failed to delete feature flag. Please try again.');
      console.error('Error deleting feature flag:', err);
    } finally {
      setLoading(false);
    }
  };

  // Render loading state
  if (loading && !flags.length) {
    return <div className="loading">Loading feature flags...</div>;
  }

  return (
    <div className="feature-flag-manager">
      <h2>Feature Flag Management</h2>
      
      {error && <div className="error">{error}</div>}
      
      <div className="feature-flag-container">
        <div className="feature-flag-list">
          <h3>Feature Flags</h3>
          <button onClick={handleCreateNew} className="btn btn-primary">Create New Flag</button>
          
          {flags.length === 0 ? (
            <p>No feature flags found.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Key</th>
                  <th>Name</th>
                  <th>Status</th>
                  <th>Tier</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {flags.map(flag => (
                  <tr key={flag.key} className={selectedFlag && selectedFlag.key === flag.key ? 'selected' : ''}>
                    <td>{flag.key}</td>
                    <td>{flag.name}</td>
                    <td>
                      <span className={`status ${flag.enabled ? 'enabled' : 'disabled'}`}>
                        {flag.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </td>
                    <td>{flag.min_subscription_tier || 'All'}</td>
                    <td>
                      <button onClick={() => handleSelectFlag(flag)} className="btn btn-sm btn-info">Edit</button>
                      <button onClick={() => handleManageOverrides(flag)} className="btn btn-sm btn-secondary">Overrides</button>
                      <button onClick={() => handleDeleteFlag(flag)} className="btn btn-sm btn-danger">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        
        <div className="feature-flag-detail">
          {isCreating && (
            <div className="feature-flag-form">
              <h3>Create New Feature Flag</h3>
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="key">Key</label>
                  <input
                    type="text"
                    id="key"
                    name="key"
                    value={formData.key}
                    onChange={handleInputChange}
                    required
                    className="form-control"
                  />
                </div>
                
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
                  <label htmlFor="enabled">
                    <input
                      type="checkbox"
                      id="enabled"
                      name="enabled"
                      checked={formData.enabled}
                      onChange={handleInputChange}
                    />
                    Enabled
                  </label>
                </div>
                
                <div className="form-group">
                  <label htmlFor="min_subscription_tier">Minimum Subscription Tier</label>
                  <select
                    id="min_subscription_tier"
                    name="min_subscription_tier"
                    value={formData.min_subscription_tier || ''}
                    onChange={handleInputChange}
                    className="form-control"
                  >
                    <option value="">All Tiers</option>
                    <option value="basic">Basic</option>
                    <option value="pro">Pro</option>
                    <option value="enterprise">Enterprise</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label htmlFor="percentage_rollout">Percentage Rollout</label>
                  <input
                    type="number"
                    id="percentage_rollout"
                    name="percentage_rollout"
                    value={formData.percentage_rollout}
                    onChange={handleInputChange}
                    min="0"
                    max="100"
                    className="form-control"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="start_date">Start Date</label>
                  <input
                    type="date"
                    id="start_date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleInputChange}
                    className="form-control"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="end_date">End Date</label>
                  <input
                    type="date"
                    id="end_date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleInputChange}
                    className="form-control"
                  />
                </div>
                
                <div className="form-actions">
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Flag'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsCreating(false)}
                    className="btn btn-secondary"
                    disabled={loading}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
          
          {isEditing && selectedFlag && (
            <div className="feature-flag-form">
              <h3>Edit Feature Flag</h3>
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="key">Key</label>
                  <input
                    type="text"
                    id="key"
                    name="key"
                    value={formData.key}
                    disabled
                    className="form-control"
                  />
                </div>
                
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
                  <label htmlFor="enabled">
                    <input
                      type="checkbox"
                      id="enabled"
                      name="enabled"
                      checked={formData.enabled}
                      onChange={handleInputChange}
                    />
                    Enabled
                  </label>
                </div>
                
                <div className="form-group">
                  <label htmlFor="min_subscription_tier">Minimum Subscription Tier</label>
                  <select
                    id="min_subscription_tier"
                    name="min_subscription_tier"
                    value={formData.min_subscription_tier || ''}
                    onChange={handleInputChange}
                    className="form-control"
                  >
                    <option value="">All Tiers</option>
                    <option value="basic">Basic</option>
                    <option value="pro">Pro</option>
                    <option value="enterprise">Enterprise</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label htmlFor="percentage_rollout">Percentage Rollout</label>
                  <input
                    type="number"
                    id="percentage_rollout"
                    name="percentage_rollout"
                    value={formData.percentage_rollout}
                    onChange={handleInputChange}
                    min="0"
                    max="100"
                    className="form-control"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="start_date">Start Date</label>
                  <input
                    type="date"
                    id="start_date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleInputChange}
                    className="form-control"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="end_date">End Date</label>
                  <input
                    type="date"
                    id="end_date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleInputChange}
                    className="form-control"
                  />
                </div>
                
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
          
          {isManagingOverrides && selectedFlag && (
            <div className="feature-override-form">
              <h3>Manage Overrides for {selectedFlag.name}</h3>
              
              <form onSubmit={handleSubmitOverride}>
                <div className="form-group">
                  <label htmlFor="user_id">User ID</label>
                  <input
                    type="text"
                    id="user_id"
                    name="user_id"
                    value={overrideData.user_id}
                    onChange={handleOverrideInputChange}
                    required
                    className="form-control"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="override_enabled">
                    <input
                      type="checkbox"
                      id="override_enabled"
                      name="enabled"
                      checked={overrideData.enabled}
                      onChange={handleOverrideInputChange}
                    />
                    Enable Feature for User
                  </label>
                </div>
                
                <div className="form-actions">
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Override'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsManagingOverrides(false)}
                    className="btn btn-secondary"
                    disabled={loading}
                  >
                    Back to Flags
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FeatureFlagManager;
