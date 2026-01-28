/**
 * API Service
 * 
 * Centralized service for all backend API communication.
 * Handles JWT token storage, authentication, automatic token refresh, and API requests.
 * 
 * Architecture: React Native App → This Service → Flask Backend → MongoDB
 * 
 * Token Flow:
 * - Access Token: 15 minutes (stored in memory and SecureStore)
 * - Refresh Token: 7 days (stored in SecureStore)
 * - On 401 error: automatically attempts refresh before failing
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
const API_BASE_URL = 'http://192.168.1.7:5000';

// =============================================================================
// API SERVICE
// =============================================================================

const ApiService = {
    token: null,
    refreshToken: null,
    isRefreshing: false,

    // ---------------------------------------------------------------------------
    // Token Management
    // ---------------------------------------------------------------------------

    /**
     * Retrieve JWT access token from secure storage
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
     * Store JWT access token in secure storage
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
     * Get refresh token from secure storage
     * @returns {Promise<string|null>} The stored refresh token or null
     */
    async getRefreshToken() {
        try {
            const token = await SecureStore.getItemAsync('refresh_token');
            this.refreshToken = token;
            return token;
        } catch (error) {
            console.log('Error getting refresh token:', error);
            return null;
        }
    },

    /**
     * Store refresh token in secure storage
     * @param {string} token - The refresh token to store
     */
    async setRefreshToken(token) {
        try {
            await SecureStore.setItemAsync('refresh_token', token);
            this.refreshToken = token;
        } catch (error) {
            console.log('Error setting refresh token:', error);
        }
    },

    /**
     * Remove all tokens from secure storage (logout)
     */
    async removeTokens() {
        try {
            await SecureStore.deleteItemAsync('jwt_token');
            await SecureStore.deleteItemAsync('refresh_token');
            this.token = null;
            this.refreshToken = null;
        } catch (error) {
            console.log('Error removing tokens:', error);
        }
    },

    // Alias for backward compatibility
    async removeToken() {
        return this.removeTokens();
    },

    // ---------------------------------------------------------------------------
    // Token Refresh Logic
    // ---------------------------------------------------------------------------

    /**
     * Attempt to refresh the access token using the refresh token.
     * Implements token rotation for security.
     * 
     * @returns {Promise<boolean>} True if refresh succeeded, false otherwise
     */
    async refreshAccessToken() {
        if (this.isRefreshing) {
            // Wait for ongoing refresh
            await new Promise(resolve => setTimeout(resolve, 100));
            return !!this.token;
        }

        this.isRefreshing = true;

        try {
            const refreshToken = await this.getRefreshToken();
            if (!refreshToken) {
                console.log('No refresh token available');
                return false;
            }

            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (!response.ok) {
                console.log('Token refresh failed:', response.status);
                return false;
            }

            const data = await response.json();

            // Store new tokens (token rotation)
            if (data.access_token) {
                await this.setToken(data.access_token);
            }
            if (data.refresh_token) {
                await this.setRefreshToken(data.refresh_token);
            }

            console.log('Token refreshed successfully');
            return true;
        } catch (error) {
            console.log('Token refresh error:', error);
            return false;
        } finally {
            this.isRefreshing = false;
        }
    },

    // ---------------------------------------------------------------------------
    // HTTP Request Handler with Auto-Refresh
    // ---------------------------------------------------------------------------

    /**
     * Make an authenticated HTTP request to the backend.
     * Automatically attempts token refresh on 401 errors.
     * 
     * @param {string} endpoint - API endpoint (e.g., '/auth/login')
     * @param {Object} options - Fetch options (method, body, headers)
     * @param {boolean} isRetry - Internal flag to prevent infinite retry loops
     * @returns {Promise<Object>} Parsed JSON response
     * @throws {Error} If request fails after retry
     */
    async request(endpoint, options = {}, isRetry = false) {
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

        // Handle 401 Unauthorized - attempt token refresh
        if (response.status === 401 && !isRetry) {
            console.log('Received 401, attempting token refresh...');
            const refreshed = await this.refreshAccessToken();

            if (refreshed) {
                // Retry the original request with new token
                return this.request(endpoint, options, true);
            }

            // Refresh failed - clear tokens and throw error
            await this.removeTokens();
            throw new Error('Session expired. Please login again.');
        }

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
     * @returns {Promise<Object>} User data and tokens
     */
    async signup(name, email, password) {
        const data = await this.request('/auth/signup', {
            method: 'POST',
            body: JSON.stringify({ name, email, password }),
        });
        if (data.access_token) {
            await this.setToken(data.access_token);
        }
        if (data.refresh_token) {
            await this.setRefreshToken(data.refresh_token);
        }
        return data;
    },

    /**
     * Login an existing user
     * @param {string} email - User's email
     * @param {string} password - User's password
     * @returns {Promise<Object>} User data and tokens
     */
    async login(email, password) {
        const data = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
        if (data.access_token) {
            await this.setToken(data.access_token);
        }
        if (data.refresh_token) {
            await this.setRefreshToken(data.refresh_token);
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
        await this.removeTokens();
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
     * Get dashboard with featured videos (paginated)
     * @param {number} page - Page number (default: 1)
     * @param {number} limit - Items per page (default: 10)
     * @returns {Promise<Object>} Dashboard data with videos and pagination
     */
    async getDashboard(page = 1, limit = 10) {
        return this.request(`/dashboard?page=${page}&limit=${limit}`);
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

    /**
     * Track video watch progress
     * @param {string} videoId - Video ID
     * @param {number} duration - Seconds watched
     * @param {boolean} completed - Whether video was completed
     * @returns {Promise<Object>} Watch stats
     */
    async trackWatch(videoId, duration, completed = false) {
        return this.request(`/video/${videoId}/watch`, {
            method: 'POST',
            body: JSON.stringify({ duration, completed }),
        });
    },
};

export default ApiService;
