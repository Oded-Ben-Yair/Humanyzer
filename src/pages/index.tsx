
import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';
import { useFeature } from '@/contexts/FeatureContext';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const { isEnabled } = useFeature();
  
  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        // Check if onboarding is enabled and not completed
        const onboardingEnabled = isEnabled('onboarding');
        const onboardingCompleted = localStorage.getItem('onboarding_completed') === 'true';
        
        if (onboardingEnabled && !onboardingCompleted) {
          router.push('/onboarding');
        } else {
          router.push('/dashboard');
        }
      } else {
        router.push('/login');
      }
    }
  }, [isAuthenticated, isLoading, router, isEnabled]);
  
  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  // This page will redirect, so we don't need to render anything
  return null;
}
