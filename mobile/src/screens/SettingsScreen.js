/**
 * Settings Screen
 * 
 * User profile and settings page.
 * Currently includes logout functionality.
 */

import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    Alert,
    ScrollView,
} from 'react-native';
import { useAuth } from '../context/AuthContext';

/**
 * SettingsScreen Component
 * 
 * Displays user profile and provides logout functionality.
 */
export default function SettingsScreen() {
    const { user, logout } = useAuth();
    const [loggingOut, setLoggingOut] = useState(false);

    /**
     * Handle logout with confirmation
     */
    const handleLogout = () => {
        Alert.alert(
            'Logout',
            'Are you sure you want to logout?',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Logout',
                    style: 'destructive',
                    onPress: async () => {
                        setLoggingOut(true);
                        await logout();
                    },
                },
            ]
        );
    };

    /**
     * Get user initials for avatar
     */
    const getInitials = () => {
        if (!user?.name) return '?';
        return user.name
            .split(' ')
            .map((n) => n[0])
            .join('')
            .toUpperCase()
            .slice(0, 2);
    };

    return (
        <ScrollView style={styles.container}>
            {/* Profile Section */}
            <View style={styles.profileSection}>
                <View style={styles.avatar}>
                    <Text style={styles.avatarText}>{getInitials()}</Text>
                </View>
                <Text style={styles.name}>{user?.name || 'User'}</Text>
                <Text style={styles.email}>{user?.email || ''}</Text>
            </View>

            {/* Actions Section */}
            <View style={styles.actionsSection}>
                <TouchableOpacity
                    style={styles.logoutButton}
                    onPress={handleLogout}
                    disabled={loggingOut}
                >
                    <Text style={styles.logoutText}>
                        {loggingOut ? 'Logging out...' : '🚪 Logout'}
                    </Text>
                </TouchableOpacity>
            </View>

            {/* App Info */}
            <View style={styles.infoSection}>
                <Text style={styles.infoText}>Video Streaming App</Text>
                <Text style={styles.infoSubtext}>Built with React Native + Flask</Text>
            </View>
        </ScrollView>
    );
}

// =============================================================================
// STYLES
// =============================================================================

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#0f0f1a',
    },
    profileSection: {
        alignItems: 'center',
        padding: 32,
        borderBottomWidth: 1,
        borderBottomColor: '#2d2d44',
    },
    avatar: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: '#6c63ff',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 16,
    },
    avatarText: {
        fontSize: 32,
        fontWeight: 'bold',
        color: '#fff',
    },
    name: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#fff',
        marginBottom: 4,
    },
    email: {
        fontSize: 16,
        color: '#888',
    },
    actionsSection: {
        padding: 24,
    },
    logoutButton: {
        backgroundColor: '#ff4757',
        borderRadius: 12,
        padding: 16,
        alignItems: 'center',
    },
    logoutText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    infoSection: {
        alignItems: 'center',
        padding: 24,
        marginTop: 'auto',
    },
    infoText: {
        fontSize: 14,
        color: '#666',
    },
    infoSubtext: {
        fontSize: 12,
        color: '#444',
        marginTop: 4,
    },
});
