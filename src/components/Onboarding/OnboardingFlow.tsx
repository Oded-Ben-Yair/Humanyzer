
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import { useFeature } from '@/contexts/FeatureContext';
import { useNotification } from '@/contexts/NotificationContext';

// Onboarding steps
const steps = [
  {
    id: 'welcome',
    title: 'Welcome to Humanyzer',
    description: 'Discover how Humanyzer can help you analyze and understand human behavior patterns.',
    image: '/images/welcome.svg',
  },
  {
    id: 'features',
    title: 'Key Features',
    description: 'Explore our powerful analytics, real-time notifications, and customizable dashboards.',
    image: '/images/features.svg',
  },
  {
    id: 'dashboard',
    title: 'Your Dashboard',
    description: 'Get familiar with your personalized dashboard and how to navigate through different sections.',
    image: '/images/dashboard.svg',
  },
  {
    id: 'complete',
    title: 'You're All Set!',
    description: 'You're now ready to start using Humanyzer. Let's get started!',
    image: '/images/complete.svg',
  },
];

// Animation variants
const variants = {
  enter: (direction: number) => ({
    x: direction > 0 ? 1000 : -1000,
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
  },
  exit: (direction: number) => ({
    x: direction < 0 ? 1000 : -1000,
    opacity: 0,
  }),
};

// Onboarding Flow Component
export default function OnboardingFlow() {
  const [currentStep, setCurrentStep] = useState(0);
  const [direction, setDirection] = useState(0);
  const router = useRouter();
  const { isEnabled } = useFeature();
  const { showNotification } = useNotification();
  
  // Check if onboarding feature is enabled
  const onboardingEnabled = isEnabled('onboarding');
  
  // Check if user has completed onboarding
  useEffect(() => {
    const hasCompletedOnboarding = localStorage.getItem('onboarding_completed');
    
    if (hasCompletedOnboarding === 'true') {
      router.push('/dashboard');
    }
  }, [router]);
  
  // If onboarding is disabled, redirect to dashboard
  useEffect(() => {
    if (!onboardingEnabled) {
      showNotification('info', 'Onboarding is currently disabled');
      router.push('/dashboard');
    }
  }, [onboardingEnabled, router, showNotification]);
  
  // Handle next step
  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setDirection(1);
      setCurrentStep(currentStep + 1);
    } else {
      completeOnboarding();
    }
  };
  
  // Handle previous step
  const handlePrevious = () => {
    if (currentStep > 0) {
      setDirection(-1);
      setCurrentStep(currentStep - 1);
    }
  };
  
  // Handle skip onboarding
  const handleSkip = () => {
    completeOnboarding();
  };
  
  // Complete onboarding
  const completeOnboarding = () => {
    localStorage.setItem('onboarding_completed', 'true');
    showNotification('success', 'Onboarding completed successfully');
    router.push('/dashboard');
  };
  
  // If onboarding is disabled, show nothing (will redirect)
  if (!onboardingEnabled) {
    return null;
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-4xl bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="flex flex-col md:flex-row">
          {/* Progress indicator */}
          <div className="w-full md:w-1/3 bg-blue-600 p-8 text-white">
            <h2 className="text-2xl font-bold mb-6">Onboarding</h2>
            <div className="space-y-4">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center">
                  <div 
                    className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                      index <= currentStep ? 'bg-white text-blue-600' : 'bg-blue-500 text-white'
                    }`}
                  >
                    {index < currentStep ? (
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      index + 1
                    )}
                  </div>
                  <span className={index <= currentStep ? 'font-medium' : 'text-blue-200'}>
                    {step.title}
                  </span>
                </div>
              ))}
            </div>
            
            <button
              onClick={handleSkip}
              className="mt-8 text-sm text-blue-200 hover:text-white"
            >
              Skip onboarding
            </button>
          </div>
          
          {/* Content area */}
          <div className="w-full md:w-2/3 p-8">
            <AnimatePresence custom={direction} initial={false}>
              <motion.div
                key={currentStep}
                custom={direction}
                variants={variants}
                initial="enter"
                animate="center"
                exit="exit"
                transition={{
                  x: { type: 'spring', stiffness: 300, damping: 30 },
                  opacity: { duration: 0.2 },
                }}
                className="h-full"
              >
                <div className="flex flex-col items-center justify-center h-full">
                  <div className="w-64 h-64 mb-6 flex items-center justify-center">
                    {/* Placeholder for image */}
                    <div className="w-full h-full bg-gray-200 rounded-lg flex items-center justify-center">
                      <span className="text-gray-500">{steps[currentStep].image}</span>
                    </div>
                  </div>
                  
                  <h3 className="text-2xl font-bold text-gray-800 mb-4">
                    {steps[currentStep].title}
                  </h3>
                  
                  <p className="text-gray-600 text-center mb-8">
                    {steps[currentStep].description}
                  </p>
                  
                  <div className="flex space-x-4">
                    {currentStep > 0 && (
                      <button
                        onClick={handlePrevious}
                        className="px-6 py-2 border border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors mobile-optimized"
                      >
                        Previous
                      </button>
                    )}
                    
                    <button
                      onClick={handleNext}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mobile-optimized"
                    >
                      {currentStep < steps.length - 1 ? 'Next' : 'Get Started'}
                    </button>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
