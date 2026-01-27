/**
 * API Service
 * 
 * Centralized service for all backend API communication.
 * Handles JWT token storage, authentication, and API requests.
 * 
 * Architecture: React Native App → This Service → Flask Backend → MongoDB
 */

import * as SecureStore from 'expo-secure-store';

// =============================================================================
// CONFIGURATION
// =============================================================================

/**
 * Backend API URL
 * 
 * For Android Emulator: http://10.0.2.2:5000
 * For iOS Simulator: http://localhost:5000
 * For Physical Device: http://YOUR_IP:5000
 */
const API_BASE_URL = 'http://192.168.1.6:5000';

// =============================================================================
// API SERVICE
// =============================================================================

const ApiService = {
    token: null,

    // ---------------------------------------------------------------------------
    // Token Management
    // ---------------------------------------------------------------------------

    /**
     * Retrieve JWT token from secure storage
     * @returns {Promise<string|null>} The stored token or null
     */
    async getToken() {
        try {
            const token = await SecureStore.getItemAsync('jwt_token');
            this.token = token;
            return token;
        } catch (error) {
            console.log('Error getting token:', error);
            return null;
        }
    },

    /**
     * Store JWT token in secure storage
     * @param {string} token - The JWT token to store
     */
    async setToken(token) {
        try {
            await SecureStore.setItemAsync('jwt_token', token);
            this.token = token;
        } catch (error) {
            console.log('Error setting token:', error);
        }
    },

    /**
     * Remove JWT token from secure storage (logout)
     */
    async removeToken() {
        try {
            await SecureStore.deleteItemAsync('jwt_token');
            this.token = null;
        } catch (error) {
            console.log('Error removing token:', error);
        }
    },

    // ---------------------------------------------------------------------------
    // HTTP Request Handler
    // ---------------------------------------------------------------------------

    /**
     * Make an authenticated HTTP request to the backend
     * @param {string} endpoint - API endpoint (e.g., '/auth/login')
     * @param {Object} options - Fetch options (method, body, headers)
     * @returns {Promise<Object>} Parsed JSON response
     * @throws {Error} If request fails
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        // Add Authorization header if token exists
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        const response = await fetch(url, {
            ...options,
            headers,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    },

    // ---------------------------------------------------------------------------
    // Authentication Endpoints
    // ---------------------------------------------------------------------------

    /**
     * Register a new user
     * @param {string} name - User's name
     * @param {string} email - User's email
     * @param {string} password - User's password
     * @returns {Promise<Object>} User data and access token
     */
    async signup(name, email, password) {
        const data = await this.request('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ name, email, password }),
        });
        if (data.access_token) {
            await this.setToken(data.access_token);
        }
        return data;
    },

    /**
     * Login an existing user
     * @param {string} email - User's email
     * @param {string} password - User's password
     * @returns {Promise<Object>} User data and access token
     */
    async login(email, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        if (data.access_token) {
            await this.setToken(data.access_token);
        }
        return data;
    },

    /**
     * Logout the current user
     */
    async logout() {
        try {
            await this.request('/auth/logout', { method: 'POST' });
        } catch (error) {
            console.log('Logout error:', error);
        }
        await this.removeToken();
    },

    /**
     * Get current user's profile
     * @returns {Promise<Object>} User profile data
     */
    async getProfile() {
        return this.request('/auth/me');
    },

    // ---------------------------------------------------------------------------
    // Video Endpoints
    // ---------------------------------------------------------------------------

    /**
     * Get dashboard with featured videos
     * @returns {Promise<Object>} Dashboard data with videos array
     */
    async getDashboard() {
        return this.request('/dashboard');
    },

    /**
     * Get video stream URL for playback
     * Backend proxies the video stream - YouTube is completely hidden
     * 
     * @param {string} videoId - Database video ID
     * @param {string} playbackToken - Short-lived playback token
     * @returns {string} Stream URL for video player
     */
    getStreamUrl(videoId, playbackToken) {
        return `${API_BASE_URL}/video/${videoId}/stream?token=${playbackToken}`;
    },
};

export default ApiService;
