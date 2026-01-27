/**
 * Video Player Screen
 * 
 * Plays video content using expo-video with native controls.
 * 
 * IMPORTANT: This screen uses the backend's video proxy endpoint.
 * YouTube URLs are NEVER exposed to the client - the backend extracts
 * direct video URLs using yt-dlp and proxies the stream.
 * 
 * Security Flow:
 * 1. Dashboard provides video with short-lived playback_token
 * 2. This screen requests stream from backend with token
 * 3. Backend validates token and proxies video bytes
 * 4. expo-video renders with native controls (no YouTube branding)
 */

import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    TouchableOpacity,
} from 'react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import ApiService from '../api/apiService';

/**
 * VideoPlayerScreen Component
 * 
 * @param {Object} props - Component props
 * @param {Object} props.route - Route params containing video object
 */
export default function VideoPlayerScreen({ route }) {
    const { video } = route.params;
    const [error, setError] = useState(null);

    // Get proxied stream URL from backend
    const streamUrl = ApiService.getStreamUrl(video.id, video.playback_token);

    // Initialize video player with expo-video
    const player = useVideoPlayer(streamUrl, (player) => {
        player.loop = false;
        player.play();
    });

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
                <Text style={styles.description} numberOfLines={3}>{video.description}</Text>
            </View>

            {/* Video Player - Native controls, no YouTube branding */}
            <View style={styles.playerContainer}>
                <VideoView
                    player={player}
                    style={styles.video}
                    allowsPictureInPicture={true}
                    nativeControls={true}
                />
            </View>

            {/* Controls Info */}
            <View style={styles.controlsInfo}>
                <Text style={styles.controlsText}>🎬 Native Controls Enabled</Text>
                <Text style={styles.controlsSubtext}>Play • Pause • Seek • Volume • Fullscreen</Text>
            </View>
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
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: '#2d2d44',
    },
    title: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#fff',
        marginBottom: 8,
    },
    description: {
        fontSize: 14,
        color: '#888',
        lineHeight: 20,
    },
    playerContainer: {
        flex: 1,
        backgroundColor: '#000',
    },
    video: {
        flex: 1,
        width: '100%',
    },
    controlsInfo: {
        alignItems: 'center',
        padding: 16,
        backgroundColor: '#1a1a2e',
        borderTopWidth: 1,
        borderTopColor: '#2d2d44',
    },
    controlsText: {
        fontSize: 16,
        color: '#6c63ff',
        fontWeight: '600',
        marginBottom: 4,
    },
    controlsSubtext: {
        fontSize: 12,
        color: '#888',
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
