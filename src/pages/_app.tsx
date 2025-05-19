
import React from 'react';
import type { AppProps } from 'next/app';
import { AuthProvider } from '@/contexts/AuthContext';
import { NotificationProvider } from '@/contexts/NotificationContext';
import { FeatureProvider } from '@/contexts/FeatureContext';
import '@/styles/globals.css';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <FeatureProvider>
        <NotificationProvider>
          <Component {...pageProps} />
        </NotificationProvider>
      </FeatureProvider>
    </AuthProvider>
  );
}
