
import { z } from 'zod';

// Define schema for environment variables with validation
const envSchema = z.object({
  // API Configuration
  API_URL: z.string().url(),
  API_KEY: z.string().min(10),

  // Authentication
  AUTH_SECRET: z.string().min(16),
  AUTH_EXPIRY: z.coerce.number().int().positive(),

  // Feature Flags
  ENABLE_ANALYTICS: z.enum(['true', 'false']).transform(val => val === 'true'),
  ENABLE_NOTIFICATIONS: z.enum(['true', 'false']).transform(val => val === 'true'),
  ENABLE_ONBOARDING: z.enum(['true', 'false']).transform(val => val === 'true'),

  // Performance
  REDUCED_MOTION: z.enum(['true', 'false']).transform(val => val === 'true'),
  HIGH_CONTRAST: z.enum(['true', 'false']).transform(val => val === 'true'),

  // Logging
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']),
});

// Function to validate environment variables
export function validateEnv() {
  try {
    return envSchema.parse({
      API_URL: process.env.API_URL,
      API_KEY: process.env.API_KEY,
      AUTH_SECRET: process.env.AUTH_SECRET,
      AUTH_EXPIRY: process.env.AUTH_EXPIRY,
      ENABLE_ANALYTICS: process.env.ENABLE_ANALYTICS,
      ENABLE_NOTIFICATIONS: process.env.ENABLE_NOTIFICATIONS,
      ENABLE_ONBOARDING: process.env.ENABLE_ONBOARDING,
      REDUCED_MOTION: process.env.REDUCED_MOTION,
      HIGH_CONTRAST: process.env.HIGH_CONTRAST,
      LOG_LEVEL: process.env.LOG_LEVEL,
    });
  } catch (error) {
    console.error('Invalid environment variables:', error);
    throw new Error('Invalid environment configuration');
  }
}

// Export validated environment variables
export const env = validateEnv();

// Export a function to check if a feature is enabled
export function isFeatureEnabled(feature: 'analytics' | 'notifications' | 'onboarding'): boolean {
  switch (feature) {
    case 'analytics':
      return env.ENABLE_ANALYTICS;
    case 'notifications':
      return env.ENABLE_NOTIFICATIONS;
    case 'onboarding':
      return env.ENABLE_ONBOARDING;
    default:
      return false;
  }
}
