
import React, { createContext, useContext, ReactNode } from 'react';
import { isFeatureEnabled } from '@/config/env.config';

// Feature context interface
interface FeatureContextType {
  isEnabled: (feature: 'analytics' | 'notifications' | 'onboarding') => boolean;
}

// Create the feature context
const FeatureContext = createContext<FeatureContextType | undefined>(undefined);

// Feature provider component
export function FeatureProvider({ children }: { children: ReactNode }) {
  // Check if a feature is enabled
  const isEnabled = (feature: 'analytics' | 'notifications' | 'onboarding') => {
    return isFeatureEnabled(feature);
  };
  
  return (
    <FeatureContext.Provider value={{ isEnabled }}>
      {children}
    </FeatureContext.Provider>
  );
}

// Custom hook to use the feature context
export function useFeature() {
  const context = useContext(FeatureContext);
  if (context === undefined) {
    throw new Error('useFeature must be used within a FeatureProvider');
  }
  return context;
}
