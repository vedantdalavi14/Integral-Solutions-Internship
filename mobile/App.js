/**
 * Video Streaming App - Main Entry Point
 * 
 * A React Native mobile application for video streaming.
 * 
 * Architecture:
 * - React Native (Expo) frontend
 * - Flask backend with MongoDB Atlas
 * - JWT authentication with secure token storage
 * - Video streaming with YouTube as hidden source (via yt-dlp)
 * 
 * Key Features:
 * - User authentication (signup/login)
 * - Video dashboard with featured content
 * - Native video player with no provider branding
 * - Secure playback tokens for video access
 * 
 * @author Your Name
 * @version 1.0.0
 */

import 'react-native-gesture-handler';
import React from 'react';
import { StatusBar } from 'expo-status-bar';

// Context Provider
import { AuthProvider } from './src/context/AuthContext';

// Navigation
import AppNavigator from './src/navigation/AppNavigator';

/**
 * App Component
 * 
 * Root component that sets up the AuthProvider and navigation.
 */
export default function App() {
  return (
    <AuthProvider>
      <StatusBar style="light" />
      <AppNavigator />
    </AuthProvider>
  );
}
