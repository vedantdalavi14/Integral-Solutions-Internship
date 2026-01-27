/**
 * App Navigator
 * 
 * Main navigation structure for the application.
 * Handles authentication flow and tab/stack navigation.
 * 
 * Navigation Structure:
 * - Auth Stack (unauthenticated): Login, Signup
 * - Main Stack (authenticated): 
 *   - Tab Navigator: Dashboard, Settings
 *   - VideoPlayer (modal)
 */

import React from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

// Screens
import LoginScreen from '../screens/LoginScreen';
import SignupScreen from '../screens/SignupScreen';
import DashboardScreen from '../screens/DashboardScreen';
import VideoPlayerScreen from '../screens/VideoPlayerScreen';
import SettingsScreen from '../screens/SettingsScreen';

// Context
import { useAuth } from '../context/AuthContext';

// =============================================================================
// NAVIGATION INSTANCES
// =============================================================================

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// =============================================================================
// TAB NAVIGATOR (authenticated users)
// =============================================================================

/**
 * Bottom tab navigator for main app screens
 */
function MainTabs() {
    return (
        <Tab.Navigator
            screenOptions={{
                tabBarStyle: {
                    backgroundColor: '#1a1a2e',
                    borderTopColor: '#2d2d44',
                    paddingBottom: 5,
                    paddingTop: 5,
                    height: 60,
                },
                tabBarActiveTintColor: '#6c63ff',
                tabBarInactiveTintColor: '#888',
                headerStyle: { backgroundColor: '#1a1a2e' },
                headerTintColor: '#fff',
            }}
        >
            <Tab.Screen
                name="Dashboard"
                component={DashboardScreen}
                options={{
                    title: 'Home',
                    tabBarIcon: ({ color }) => (
                        <Text style={{ color, fontSize: 20 }}>🏠</Text>
                    ),
                }}
            />
            <Tab.Screen
                name="Settings"
                component={SettingsScreen}
                options={{
                    tabBarIcon: ({ color }) => (
                        <Text style={{ color, fontSize: 20 }}>⚙️</Text>
                    ),
                }}
            />
        </Tab.Navigator>
    );
}

// =============================================================================
// AUTH STACK (unauthenticated users)
// =============================================================================

/**
 * Authentication flow for unauthenticated users
 */
function AuthStack() {
    return (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Signup" component={SignupScreen} />
        </Stack.Navigator>
    );
}

// =============================================================================
// MAIN STACK (authenticated users)
// =============================================================================

/**
 * Main app stack with tabs and video player
 */
function MainStack() {
    return (
        <Stack.Navigator
            screenOptions={{
                headerStyle: { backgroundColor: '#1a1a2e' },
                headerTintColor: '#fff',
            }}
        >
            <Stack.Screen
                name="Main"
                component={MainTabs}
                options={{ headerShown: false }}
            />
            <Stack.Screen
                name="VideoPlayer"
                component={VideoPlayerScreen}
                options={{ title: 'Now Playing' }}
            />
        </Stack.Navigator>
    );
}

// =============================================================================
// ROOT NAVIGATOR
// =============================================================================

/**
 * Root navigator that switches between auth and main stacks
 */
export default function AppNavigator() {
    const { isLoading, isAuthenticated } = useAuth();

    // Loading state while checking authentication
    if (isLoading === true) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#6c63ff" />
                <Text style={styles.loadingText}>Loading...</Text>
            </View>
        );
    }

    return (
        <NavigationContainer>
            {isAuthenticated === true ? <MainStack /> : <AuthStack />}
        </NavigationContainer>
    );
}

// =============================================================================
// STYLES
// =============================================================================

const styles = StyleSheet.create({
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#0f0f1a',
    },
    loadingText: {
        marginTop: 12,
        color: '#888',
        fontSize: 16,
    },
});
