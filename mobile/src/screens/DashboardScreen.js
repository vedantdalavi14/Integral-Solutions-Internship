/**
 * Dashboard Screen
 * 
 * Main screen showing featured videos.
 * Fetches videos from the backend API and displays them in a list.
 */

import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ActivityIndicator,
    FlatList,
    RefreshControl,
    TouchableOpacity,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import ApiService from '../api/apiService';
import VideoTile from '../components/VideoTile';

/**
 * DashboardScreen Component
 * 
 * @param {Object} props - Component props
 * @param {Object} props.navigation - React Navigation navigation object
 */
export default function DashboardScreen({ navigation }) {
    const { user } = useAuth();
    const [videos, setVideos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState(null);

    // Fetch videos on mount
    useEffect(() => {
        fetchVideos();
    }, []);

    /**
     * Fetch videos from the backend API
     */
    const fetchVideos = async () => {
        try {
            setError(null);
            const data = await ApiService.getDashboard();
            setVideos(data.videos);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    /**
     * Handle pull-to-refresh
     */
    const handleRefresh = () => {
        setRefreshing(true);
        fetchVideos();
    };

    /**
     * Navigate to video player
     * @param {Object} video - Video object with playback_token
     */
    const handleVideoPress = (video) => {
        navigation.navigate('VideoPlayer', { video });
    };

    // Loading state
    if (loading) {
        return (
            <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#6c63ff" />
            </View>
        );
    }

    // Error state
    if (error) {
        return (
            <View style={styles.centerContainer}>
                <Text style={styles.errorText}>⚠️ {error}</Text>
                <TouchableOpacity onPress={fetchVideos}>
                    <Text style={styles.retryText}>Tap to retry</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            {/* Header */}
            <View style={styles.header}>
                <Text style={styles.greeting}>Hello, {user?.name || 'User'}! 👋</Text>
                <Text style={styles.title}>Featured Videos</Text>
            </View>

            {/* Video List */}
            <FlatList
                data={videos}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => (
                    <VideoTile video={item} onPress={() => handleVideoPress(item)} />
                )}
                contentContainerStyle={styles.listContent}
                refreshControl={
                    <RefreshControl
                        refreshing={refreshing}
                        onRefresh={handleRefresh}
                        tintColor="#6c63ff"
                        colors={['#6c63ff']}
                    />
                }
                ListEmptyComponent={
                    <View style={styles.emptyContainer}>
                        <Text style={styles.emptyText}>No videos available</Text>
                    </View>
                }
            />
        </View>
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
    centerContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#0f0f1a',
    },
    header: {
        padding: 20,
        paddingTop: 8,
    },
    greeting: {
        fontSize: 16,
        color: '#888',
        marginBottom: 4,
    },
    title: {
        fontSize: 28,
        fontWeight: 'bold',
        color: '#fff',
    },
    listContent: {
        padding: 16,
        paddingTop: 0,
    },
    errorText: {
        fontSize: 18,
        color: '#ff6b6b',
        textAlign: 'center',
        marginBottom: 16,
    },
    retryText: {
        fontSize: 16,
        color: '#6c63ff',
        fontWeight: '600',
    },
    emptyContainer: {
        padding: 40,
        alignItems: 'center',
    },
    emptyText: {
        fontSize: 16,
        color: '#888',
    },
});
