/**
 * VideoTile Component
 * 
 * Displays a video thumbnail with title and description.
 * Used in the dashboard to show video cards.
 */

import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet } from 'react-native';

/**
 * VideoTile Component
 * 
 * @param {Object} props - Component props
 * @param {Object} props.video - Video object with title, description, thumbnail_url
 * @param {Function} props.onPress - Callback when tile is pressed
 */
export default function VideoTile({ video, onPress }) {
    return (
        <TouchableOpacity style={styles.videoTile} onPress={onPress} activeOpacity={0.8}>
            {/* Thumbnail with play button overlay */}
            <View style={styles.thumbnailContainer}>
                <Image
                    source={{ uri: video.thumbnail_url }}
                    style={styles.thumbnail}
                    resizeMode="cover"
                />
                <View style={styles.playButton}>
                    <Text style={styles.playIcon}>▶</Text>
                </View>
            </View>

            {/* Video info */}
            <View style={styles.videoContent}>
                <Text style={styles.videoTitle} numberOfLines={2}>
                    {video.title}
                </Text>
                <Text style={styles.videoDescription} numberOfLines={2}>
                    {video.description}
                </Text>
            </View>
        </TouchableOpacity>
    );
}

// =============================================================================
// STYLES
// =============================================================================

const styles = StyleSheet.create({
    videoTile: {
        backgroundColor: '#1a1a2e',
        borderRadius: 16,
        overflow: 'hidden',
        marginBottom: 16,
        borderWidth: 1,
        borderColor: '#2d2d44',
    },
    thumbnailContainer: {
        width: '100%',
        height: 180,
        position: 'relative',
    },
    thumbnail: {
        width: '100%',
        height: '100%',
    },
    playButton: {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: [{ translateX: -24 }, { translateY: -24 }],
        width: 48,
        height: 48,
        borderRadius: 24,
        backgroundColor: 'rgba(108, 99, 255, 0.9)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    playIcon: {
        color: '#fff',
        fontSize: 18,
        marginLeft: 4,
    },
    videoContent: {
        padding: 16,
    },
    videoTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#fff',
        marginBottom: 8,
    },
    videoDescription: {
        fontSize: 14,
        color: '#888',
        lineHeight: 20,
    },
});
