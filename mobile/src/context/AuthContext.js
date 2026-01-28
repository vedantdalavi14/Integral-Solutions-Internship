/**
 * Authentication Context
 * 
 * Provides global authentication state management using React Context.
 * Handles user authentication status, login, signup, and logout operations.
 * 
 * Usage:
 *   import { useAuth } from './context/AuthContext';
 *   const { user, isLoading, isAuthenticated, login, logout } = useAuth();
 */

import React, { createContext, useState, useEffect, useContext } from 'react';
import ApiService from '../api/apiService';

// =============================================================================
// CONTEXT CREATION
// =============================================================================

const AuthContext = createContext(null);

// =============================================================================
// AUTH PROVIDER COMPONENT
// =============================================================================

/**
 * AuthProvider Component
 * 
 * Wraps the app and provides authentication state to all children.
 * Automatically checks for existing authentication on mount.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // Check authentication status on app load
    useEffect(() => {
        checkAuthStatus();
    }, []);

    /**
     * Check if user is already authenticated (has valid token)
     * Also loads refresh token for automatic token refresh on expiry
     */
    const checkAuthStatus = async () => {
        try {
            const token = await ApiService.getToken();
            await ApiService.getRefreshToken(); // Load refresh token into memory

            if (token) {
                // Verify token by fetching profile
                // If token is expired, ApiService will auto-refresh
                const data = await ApiService.getProfile();
                setUser(data.user);
                setIsAuthenticated(true);
            }
        } catch (error) {
            console.log('Not authenticated:', error.message);
            await ApiService.removeTokens();
            setUser(null);
            setIsAuthenticated(false);
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Register a new user
     * @param {string} name - User's name
     * @param {string} email - User's email
     * @param {string} password - User's password
     */
    const signup = async (name, email, password) => {
        const data = await ApiService.signup(name, email, password);
        setUser(data.user);
        setIsAuthenticated(true);
        return data;
    };

    /**
     * Login an existing user
     * @param {string} email - User's email
     * @param {string} password - User's password
     */
    const login = async (email, password) => {
        const data = await ApiService.login(email, password);
        setUser(data.user);
        setIsAuthenticated(true);
        return data;
    };

    /**
     * Logout the current user
     */
    const logout = async () => {
        await ApiService.logout();
        setUser(null);
        setIsAuthenticated(false);
    };

    // Context value with all auth state and methods
    const contextValue = {
        user,
        isLoading: Boolean(isLoading),
        isAuthenticated: Boolean(isAuthenticated),
        signup,
        login,
        logout,
    };

    return (
        <AuthContext.Provider value={contextValue}>
            {children}
        </AuthContext.Provider>
    );
}

// =============================================================================
// CUSTOM HOOK
// =============================================================================

/**
 * useAuth Hook
 * 
 * Custom hook to access authentication context.
 * Must be used within an AuthProvider.
 * 
 * @returns {Object} Authentication state and methods
 *   - user: Current user object or null
 *   - isLoading: Whether auth status is being checked
 *   - isAuthenticated: Whether user is logged in
 *   - signup: Function to register new user
 *   - login: Function to login user
 *   - logout: Function to logout user
 */
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

export default AuthContext;
