/**
 * Dashboard Screen
 * 
 * Main screen showing featured videos with horizontal pagination.
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
    ScrollView,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import ApiService from '../api/apiService';
import VideoTile from '../components/VideoTile';

const ITEMS_PER_PAGE = 4; // Show 4 videos per page for visible pagination

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

    // Pagination state
    const [currentPage, setCurrentPage] = useState(1);
    const [pagination, setPagination] = useState(null);

    // Fetch videos on mount
    useEffect(() => {
        fetchVideos(1);
    }, []);

    /**
     * Fetch videos from the backend API
     * @param {number} page - Page number to fetch
     */
    const fetchVideos = async (page = 1) => {
        try {
            setError(null);
            setLoading(true);

            const data = await ApiService.getDashboard(page, ITEMS_PER_PAGE);
            setVideos(data.videos);
            setPagination(data.pagination);
            setCurrentPage(page);
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
        fetchVideos(currentPage);
    };

    /**
     * Navigate to a specific page
     */
    const goToPage = (page) => {
        if (page >= 1 && page <= (pagination?.pages || 1)) {
            fetchVideos(page);
        }
    };

    /**
     * Navigate to video player
     * @param {Object} video - Video object with playback_token
     */
    const handleVideoPress = (video) => {
        navigation.navigate('VideoPlayer', { video });
    };

    /**
     * Render horizontal pagination bar
     */
    const renderPagination = () => {
        if (!pagination || pagination.pages <= 1) return null;

        const pages = [];
        for (let i = 1; i <= pagination.pages; i++) {
            pages.push(i);
        }

        return (
            <View style={styles.paginationContainer}>
                <Text style={styles.paginationInfo}>
                    {pagination.total} videos
                </Text>

                <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    contentContainerStyle={styles.paginationScroll}
                >
                    {/* Previous Button */}
                    <TouchableOpacity
                        style={[
                            styles.pageButton,
                            styles.navButton,
                            currentPage === 1 && styles.pageButtonDisabled
                        ]}
                        onPress={() => goToPage(currentPage - 1)}
                        disabled={currentPage === 1}
                    >
                        <Text style={[
                            styles.pageButtonText,
                            currentPage === 1 && styles.pageButtonTextDisabled
                        ]}>←</Text>
                    </TouchableOpacity>

                    {/* Page Numbers */}
                    {pages.map(page => (
                        <TouchableOpacity
                            key={page}
                            style={[
                                styles.pageButton,
                                currentPage === page && styles.pageButtonActive
                            ]}
                            onPress={() => goToPage(page)}
                        >
                            <Text style={[
                                styles.pageButtonText,
                                currentPage === page && styles.pageButtonTextActive
                            ]}>
                                {page}
                            </Text>
                        </TouchableOpacity>
                    ))}

                    {/* Next Button */}
                    <TouchableOpacity
                        style={[
                            styles.pageButton,
                            styles.navButton,
                            currentPage === pagination.pages && styles.pageButtonDisabled
                        ]}
                        onPress={() => goToPage(currentPage + 1)}
                        disabled={currentPage === pagination.pages}
                    >
                        <Text style={[
                            styles.pageButtonText,
                            currentPage === pagination.pages && styles.pageButtonTextDisabled
                        ]}>→</Text>
                    </TouchableOpacity>
                </ScrollView>
            </View>
        );
    };

    // Loading state
    if (loading && videos.length === 0) {
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
                <TouchableOpacity onPress={() => fetchVideos(1)}>
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

            {/* Horizontal Pagination */}
            {renderPagination()}

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

            {/* Loading Overlay */}
            {loading && videos.length > 0 && (
                <View style={styles.loadingOverlay}>
                    <ActivityIndicator size="small" color="#6c63ff" />
                </View>
            )}
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
    // Pagination Styles
    paginationContainer: {
        paddingHorizontal: 16,
        paddingVertical: 12,
        borderBottomWidth: 1,
        borderBottomColor: '#1a1a2e',
    },
    paginationInfo: {
        fontSize: 12,
        color: '#666',
        marginBottom: 8,
        textAlign: 'center',
    },
    paginationScroll: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
    },
    pageButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: '#1a1a2e',
        justifyContent: 'center',
        alignItems: 'center',
        marginHorizontal: 4,
    },
    pageButtonActive: {
        backgroundColor: '#6c63ff',
    },
    pageButtonDisabled: {
        backgroundColor: '#0f0f1a',
        borderWidth: 1,
        borderColor: '#333',
    },
    navButton: {
        backgroundColor: '#2a2a3e',
    },
    pageButtonText: {
        fontSize: 16,
        fontWeight: '600',
        color: '#888',
    },
    pageButtonTextActive: {
        color: '#fff',
    },
    pageButtonTextDisabled: {
        color: '#444',
    },
    loadingOverlay: {
        position: 'absolute',
        top: 120,
        left: 0,
        right: 0,
        alignItems: 'center',
    },
});
