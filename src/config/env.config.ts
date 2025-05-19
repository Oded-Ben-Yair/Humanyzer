// src/config/env.config.ts
import { z } from 'zod';

// Define schema for frontend environment variables
const envSchema = z.object({
  // API Configuration - for frontend to know where the backend is
  NEXT_PUBLIC_API_URL: z.string().url(),

  // Authentication - frontend might need to know expiry for UI reasons, but not the secret
  NEXT_PUBLIC_AUTH_EXPIRY_MINUTES: z.coerce.number().int().positive(), // Renamed for clarity

  // Feature Flags - safe to expose to frontend
  NEXT_PUBLIC_ENABLE_ANALYTICS: z.enum(['true', 'false']).transform(val => val === 'true').default('false'),
  NEXT_PUBLIC_ENABLE_NOTIFICATIONS: z.enum(['true', 'false']).transform(val => val === 'true').default('false'),
  NEXT_PUBLIC_ENABLE_ONBOARDING: z.enum(['true', 'false']).transform(val => val === 'true').default('false'),

  // Performance - safe to expose to frontend
  NEXT_PUBLIC_REDUCED_MOTION: z.enum(['true', 'false']).transform(val => val === 'true').default('false'),
  NEXT_PUBLIC_HIGH_CONTRAST: z.enum(['true', 'false']).transform(val => val === 'true').default('false'),

  // Logging - safe to expose to frontend
  NEXT_PUBLIC_LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),

  // NOTE: API_KEY and AUTH_SECRET have been removed.
  // If your frontend needs a *public* API key for a third-party service (like Google Maps),
  // you would add it here as NEXT_PUBLIC_THIRD_PARTY_API_KEY: z.string().min(10), for example.
  // AUTH_SECRET should never be exposed to the frontend.
});

// Function to validate environment variables
export function validateEnv() {
  try {
    const parsedEnv = envSchema.parse({
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      NEXT_PUBLIC_AUTH_EXPIRY_MINUTES: process.env.NEXT_PUBLIC_AUTH_EXPIRY_MINUTES,
      NEXT_PUBLIC_ENABLE_ANALYTICS: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS,
      NEXT_PUBLIC_ENABLE_NOTIFICATIONS: process.env.NEXT_PUBLIC_ENABLE_NOTIFICATIONS,
      NEXT_PUBLIC_ENABLE_ONBOARDING: process.env.NEXT_PUBLIC_ENABLE_ONBOARDING,
      NEXT_PUBLIC_REDUCED_MOTION: process.env.NEXT_PUBLIC_REDUCED_MOTION,
      NEXT_PUBLIC_HIGH_CONTRAST: process.env.NEXT_PUBLIC_HIGH_CONTRAST,
      NEXT_PUBLIC_LOG_LEVEL: process.env.NEXT_PUBLIC_LOG_LEVEL,
    });
    // console.log('Frontend environment variables loaded successfully:', parsedEnv); // Optional: for debugging
    return parsedEnv;
  } catch (error) {
    console.error('🔴 Invalid frontend environment variables. See Zod error details below:\n', error);
    throw new Error('Invalid environment configuration for frontend. Check terminal logs and .env file for required NEXT_PUBLIC_ variables.');
  }
}

// Export validated environment variables
export const env = validateEnv();

// Export a function to check if a feature is enabled
// (Updated to use the new NEXT_PUBLIC_ prefixed names from the 'env' object)
export function isFeatureEnabled(feature: 'analytics' | 'notifications' | 'onboarding'): boolean {
  switch (feature) {
    case 'analytics':
      return env.NEXT_PUBLIC_ENABLE_ANALYTICS;
    case 'notifications':
      return env.NEXT_PUBLIC_ENABLE_NOTIFICATIONS;
    case 'onboarding':
      return env.NEXT_PUBLIC_ENABLE_ONBOARDING;
    default:
      // It's good practice to handle the default case,
      // though TypeScript should prevent invalid 'feature' values here.
      // Making it exhaustive:
      const exhaustiveCheck: never = feature;
      return false;
  }
}
