/**
 * Video Player Screen
 * 
 * Plays video content using expo-video with native controls.
 * Shows yellow progress bar for previously watched portion.
 * Tracks watch position and resumes from last position.
 * 
 * IMPORTANT: This screen uses the backend's video proxy endpoint.
 * YouTube URLs are NEVER exposed to the client.
 */

import React, { useState, useEffect, useRef } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
    ActivityIndicator,
} from 'react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import { useEvent } from 'expo';
import ApiService from '../api/apiService';

/**
 * VideoPlayerScreen Component
 * 
 * @param {Object} props - Component props
 * @param {Object} props.route - Route params containing video object
 * @param {Object} props.navigation - Navigation object for screen events
 */
export default function VideoPlayerScreen({ route, navigation }) {
    const { video } = route.params;
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const [progress, setProgress] = useState(null);
    const [currentPosition, setCurrentPosition] = useState(0);
    const [videoDuration, setVideoDuration] = useState(0);

    // Refs for tracking
    const startTimeRef = useRef(Date.now());
    const hasTrackedRef = useRef(false);
    const lastSavedPositionRef = useRef(0);

    // Get proxied stream URL from backend
    const streamUrl = ApiService.getStreamUrl(video.id, video.playback_token);

    // Initialize video player with expo-video
    const player = useVideoPlayer(streamUrl, (player) => {
        player.loop = false;
    });

    // Listen for time updates
    const { isPlaying } = useEvent(player, 'playingChange', { isPlaying: player.playing });

    /**
     * Fetch user's previous watch progress
     */
    useEffect(() => {
        const loadProgress = async () => {
            try {
                const result = await ApiService.getProgress(video.id);
                if (result.progress) {
                    setProgress(result.progress);
                    // Seek to last position if previously watched
                    if (result.progress.last_position > 0) {
                        player.currentTime = result.progress.last_position;
                    }
                }
            } catch (err) {
                console.log('Failed to load progress:', err.message);
            } finally {
                setLoading(false);
                player.play();
            }
        };

        loadProgress();
    }, [video.id]);

    /**
     * Track current position periodically
     */
    useEffect(() => {
        const interval = setInterval(() => {
            if (player.currentTime !== undefined) {
                setCurrentPosition(player.currentTime);
            }
            if (player.duration !== undefined && player.duration > 0) {
                setVideoDuration(player.duration);
            }
        }, 1000);

        return () => clearInterval(interval);
    }, [player]);

    /**
     * Save watch progress when leaving screen
     */
    const saveProgress = async () => {
        if (hasTrackedRef.current) return;
        hasTrackedRef.current = true;

        const sessionDuration = Math.floor((Date.now() - startTimeRef.current) / 1000);
        const completed = videoDuration > 0 && currentPosition >= videoDuration * 0.9;

        try {
            console.log(`Saving progress: position ${Math.floor(currentPosition)}s / ${Math.floor(videoDuration)}s`);
            await ApiService.trackWatch(
                video.id,
                Math.floor(currentPosition),
                sessionDuration,
                Math.floor(videoDuration),
                completed
            );
            console.log('Progress saved!');
        } catch (err) {
            console.log('Failed to save progress:', err.message);
        }
    };

    // Save progress on screen unmount
    useEffect(() => {
        const unsubscribe = navigation.addListener('beforeRemove', () => {
            saveProgress();
        });

        return () => {
            unsubscribe();
            saveProgress();
        };
    }, [navigation, video.id, currentPosition, videoDuration]);

    /**
     * Calculate progress percentages
     */
    const previousWatchPercent = progress?.last_position && videoDuration > 0
        ? Math.min((progress.last_position / videoDuration) * 100, 100)
        : 0;

    const currentWatchPercent = videoDuration > 0
        ? Math.min((currentPosition / videoDuration) * 100, 100)
        : 0;

    // Error state
    if (error) {
        return (
            <View style={styles.centerContainer}>
                <Text style={styles.errorIcon}>⚠️</Text>
                <Text style={styles.errorText}>{error}</Text>
                <TouchableOpacity style={styles.retryButton} onPress={() => setError(null)}>
                    <Text style={styles.retryButtonText}>Try Again</Text>
                </TouchableOpacity>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            {/* Video Info Header */}
            <View style={styles.header}>
                <Text style={styles.title} numberOfLines={2}>{video.title}</Text>
                <Text style={styles.description} numberOfLines={2}>{video.description}</Text>
            </View>

            {/* Custom Progress Bar (Yellow = Previously Watched) */}
            <View style={styles.progressBarContainer}>
                {/* Background */}
                <View style={styles.progressBarBg} />

                {/* Yellow bar - Previously watched portion */}
                {previousWatchPercent > 0 && (
                    <View
                        style={[
                            styles.progressBarPrevious,
                            { width: `${previousWatchPercent}%` }
                        ]}
                    />
                )}

                {/* Purple bar - Current position */}
                <View
                    style={[
                        styles.progressBarCurrent,
                        { width: `${currentWatchPercent}%` }
                    ]}
                />

                {/* Position indicator */}
                {previousWatchPercent > 0 && currentWatchPercent < previousWatchPercent && (
                    <View style={[styles.resumeMarker, { left: `${previousWatchPercent}%` }]}>
                        <Text style={styles.resumeText}>▼</Text>
                    </View>
                )}
            </View>

            {/* Progress Info */}
            <View style={styles.progressInfo}>
                <Text style={styles.progressText}>
                    {formatTime(currentPosition)} / {formatTime(videoDuration)}
                </Text>
                {previousWatchPercent > 0 && (
                    <Text style={styles.previouslyWatched}>
                        🟡 Previously watched: {formatTime(progress?.last_position || 0)}
                    </Text>
                )}
            </View>

            {/* Video Player */}
            <View style={styles.playerContainer}>
                {loading && (
                    <View style={styles.loadingOverlay}>
                        <ActivityIndicator size="large" color="#6c63ff" />
                        <Text style={styles.loadingText}>Loading...</Text>
                    </View>
                )}
                <VideoView
                    player={player}
                    style={styles.video}
                    allowsPictureInPicture={true}
                    nativeControls={true}
                />
            </View>

            {/* Controls Info */}
            <View style={styles.controlsInfo}>
                <Text style={styles.controlsText}>🎬 Native Controls</Text>
            </View>
        </View>
    );
}

/**
 * Format seconds to mm:ss or hh:mm:ss
 */
function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    const s = Math.floor(seconds);
    const hours = Math.floor(s / 3600);
    const mins = Math.floor((s % 3600) / 60);
    const secs = s % 60;

    if (hours > 0) {
        return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
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
        padding: 16,
        paddingBottom: 8,
    },
    title: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#fff',
        marginBottom: 4,
    },
    description: {
        fontSize: 13,
        color: '#888',
    },
    // Progress Bar Styles
    progressBarContainer: {
        height: 8,
        backgroundColor: '#2d2d44',
        marginHorizontal: 16,
        borderRadius: 4,
        overflow: 'hidden',
        position: 'relative',
    },
    progressBarBg: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: '#2d2d44',
    },
    progressBarPrevious: {
        position: 'absolute',
        top: 0,
        left: 0,
        bottom: 0,
        backgroundColor: '#FFD700', // Yellow for previously watched
        opacity: 0.6,
    },
    progressBarCurrent: {
        position: 'absolute',
        top: 0,
        left: 0,
        bottom: 0,
        backgroundColor: '#6c63ff', // Purple for current
    },
    resumeMarker: {
        position: 'absolute',
        top: -12,
        marginLeft: -8,
    },
    resumeText: {
        color: '#FFD700',
        fontSize: 12,
    },
    progressInfo: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 16,
        paddingVertical: 8,
    },
    progressText: {
        fontSize: 12,
        color: '#888',
    },
    previouslyWatched: {
        fontSize: 11,
        color: '#FFD700',
    },
    playerContainer: {
        flex: 1,
        backgroundColor: '#000',
    },
    video: {
        flex: 1,
        width: '100%',
    },
    loadingOverlay: {
        ...StyleSheet.absoluteFillObject,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: 'rgba(0,0,0,0.8)',
        zIndex: 10,
    },
    loadingText: {
        color: '#888',
        marginTop: 8,
    },
    controlsInfo: {
        alignItems: 'center',
        padding: 12,
        backgroundColor: '#1a1a2e',
    },
    controlsText: {
        fontSize: 14,
        color: '#6c63ff',
        fontWeight: '600',
    },
    errorIcon: {
        fontSize: 48,
        marginBottom: 16,
    },
    errorText: {
        fontSize: 18,
        color: '#ff6b6b',
        textAlign: 'center',
        marginBottom: 16,
    },
    retryButton: {
        backgroundColor: '#6c63ff',
        paddingHorizontal: 24,
        paddingVertical: 12,
        borderRadius: 8,
    },
    retryButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
});
