"""
Video Routes

Handles video dashboard, streaming, and playback token management.
Uses yt-dlp to extract video URLs and proxies streams to hide YouTube.
"""

from flask import Blueprint, request, jsonify, Response, stream_with_context
from app.models.video import Video
from app.models.watch_history import WatchHistory
from app.utils.jwt_utils import (
    jwt_required,
    generate_playback_token,
    decode_playback_token,
)
from app import get_logger
import yt_dlp
import requests
import time

video_bp = Blueprint('video', __name__)
logger = get_logger()

# =============================================================================
# URL CACHING
# =============================================================================

# Cache for extracted video URLs (expires after 5 minutes)
_url_cache = {}
CACHE_DURATION = 300  # 5 minutes


def get_cached_url(youtube_id):
    """Get cached video URL or None if expired/missing"""
    if youtube_id in _url_cache:
        url, timestamp = _url_cache[youtube_id]
        if time.time() - timestamp < CACHE_DURATION:
            return url
        del _url_cache[youtube_id]
    return None


def cache_url(youtube_id, url):
    """Cache the extracted URL"""
    _url_cache[youtube_id] = (url, time.time())


# =============================================================================
# VIDEO URL EXTRACTION
# =============================================================================

def extract_video_url(youtube_id):
    """
    Extract direct video URL using yt-dlp.
    Returns a progressive MP4 URL for mobile streaming.
    """
    # Check cache first
    cached = get_cached_url(youtube_id)
    if cached:
        logger.debug(f"Using cached URL for {youtube_id}")
        return cached
    
    youtube_url = f"https://www.youtube.com/watch?v={youtube_id}"
    
    # Request progressive MP4 formats that work on mobile
    # Avoid DASH/HLS which require special handling
    ydl_opts = {
        'format': 'best[ext=mp4][vcodec^=avc][protocol!=m3u8_native][protocol!=m3u8]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'socket_timeout': 30,
    }
    
    try:
        logger.info(f"Extracting video URL for {youtube_id}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video_url = info.get('url')
            
            if not video_url:
                # Try to get from formats - look for progressive MP4
                formats = info.get('formats', [])
                for f in reversed(formats):
                    if (f.get('ext') == 'mp4' and 
                        f.get('url') and 
                        f.get('vcodec', '').startswith('avc') and
                        'manifest' not in f.get('url', '').lower()):
                        video_url = f['url']
                        logger.debug(f"Found compatible format: {f.get('format_id')}")
                        break
            
            if video_url:
                logger.info(f"Extracted URL for {youtube_id}")
                cache_url(youtube_id, video_url)
                return video_url
            else:
                logger.error(f"No compatible format found for {youtube_id}")
    except Exception as e:
        logger.error(f"Error extracting video URL: {e}")
    
    return None


# =============================================================================
# ROUTES
# =============================================================================

@video_bp.route('/dashboard', methods=['GET'])
@jwt_required
def get_dashboard():
    """
    Get dashboard with active videos (paginated).
    
    Headers:
    Authorization: Bearer <access_token>
    
    Query Parameters:
    - page: Page number (default: 1)
    - limit: Items per page (default: 10, max: 50)
    
    Response:
    {
        "videos": [...],
        "pagination": {
            "page": 1,
            "limit": 10,
            "total": 25,
            "pages": 3,
            "has_more": true
        }
    }
    
    IMPORTANT: youtube_id is NEVER exposed to the client
    """
    # Seed data if needed
    Video.seed_data()
    
    # Get pagination params
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    # Validate params
    page = max(1, page)  # Minimum page is 1
    limit = min(max(1, limit), 50)  # Limit between 1 and 50
    
    # Get paginated videos
    videos, total = Video.find_active_paginated(page=page, limit=limit)
    
    # Calculate pagination metadata
    import math
    total_pages = math.ceil(total / limit) if total > 0 else 1
    
    logger.debug(f"Dashboard request from user {request.user_id}: page {page}, {len(videos)} videos")
    
    # Build response with playback tokens
    video_list = []
    for video in videos:
        playback_token = generate_playback_token(video._id, request.user_id)
        video_list.append(video.to_public_dict(playback_token=playback_token))
    
    return jsonify({
        'videos': video_list,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': total_pages,
            'has_more': page < total_pages
        }
    }), 200


@video_bp.route('/video/<video_id>/stream', methods=['GET'])
def get_stream(video_id):
    """
    Proxy video stream to the client.
    
    This endpoint:
    1. Verifies the playback token
    2. Extracts direct video URL using yt-dlp
    3. Proxies the video bytes to the client
    
    The frontend uses expo-video component with native controls.
    This proxy hides YouTube completely and bypasses IP restrictions.
    
    Query Parameters:
    - token: Playback token from dashboard response
    """
    playback_token = request.args.get('token')
    
    if not playback_token:
        return jsonify({'error': 'Playback token is required'}), 400
    
    # Decode and verify playback token
    payload = decode_playback_token(playback_token)
    if not payload:
        logger.warning(f"Invalid playback token for video {video_id}")
        return jsonify({'error': 'Invalid or expired playback token'}), 401
    
    # Verify video_id matches token
    if payload.get('video_id') != video_id:
        logger.warning(f"Token mismatch for video {video_id}")
        return jsonify({'error': 'Token does not match video'}), 403
    
    # Find video to get youtube_id
    video = Video.find_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    # Extract direct video URL using yt-dlp
    video_url = extract_video_url(video.youtube_id)
    
    if not video_url:
        logger.error(f"Failed to extract stream for video {video_id}")
        return jsonify({'error': 'Failed to extract video stream'}), 500
    
    # Handle Range requests for seeking
    range_header = request.headers.get('Range')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.youtube.com/',
    }
    
    if range_header:
        headers['Range'] = range_header
    
    try:
        # Stream the video through our server
        resp = requests.get(video_url, headers=headers, stream=True, timeout=30)
        
        # Build response headers
        response_headers = {
            'Content-Type': resp.headers.get('Content-Type', 'video/mp4'),
            'Accept-Ranges': 'bytes',
        }
        
        if 'Content-Length' in resp.headers:
            response_headers['Content-Length'] = resp.headers['Content-Length']
        if 'Content-Range' in resp.headers:
            response_headers['Content-Range'] = resp.headers['Content-Range']
        
        # Determine status code (206 for partial content, 200 for full)
        status_code = 206 if range_header and resp.status_code == 206 else 200
        
        def generate():
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            stream_with_context(generate()),
            status=status_code,
            headers=response_headers
        )
        
    except Exception as e:
        logger.error(f"Streaming error for video {video_id}: {e}")
        return jsonify({'error': 'Streaming failed'}), 500


@video_bp.route('/video/<video_id>/info', methods=['GET'])
@jwt_required
def get_video_info(video_id):
    """
    Get video information (for displaying before playing).
    Response includes a fresh playback token.
    """
    video = Video.find_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    playback_token = generate_playback_token(video._id, request.user_id)
    
    return jsonify({
        'video': video.to_public_dict(playback_token=playback_token)
    }), 200


@video_bp.route('/video/<video_id>/watch', methods=['POST'])
@jwt_required
def track_watch(video_id):
    """
    Track video watch progress.
    
    Request Body:
    {
        "duration": 120,      // Seconds watched
        "completed": false    // Whether video was completed
    }
    
    Response:
    {
        "message": "Watch tracked",
        "stats": {
            "view_count": 10,
            "total_watch_time": 3600,
            "completion_count": 5
        }
    }
    """
    # Verify video exists
    video = Video.find_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    data = request.get_json() or {}
    duration = data.get('duration', 0)
    completed = data.get('completed', False)
    
    # Update or create watch history
    WatchHistory.update_or_create(
        user_id=request.user_id,
        video_id=video_id,
        watch_duration=duration,
        completed=completed
    )
    
    logger.info(f"Watch tracked: user {request.user_id}, video {video_id}, duration {duration}s")
    
    # Return updated stats
    stats = WatchHistory.get_video_stats(video_id)
    
    return jsonify({
        'message': 'Watch tracked',
        'stats': stats
    }), 200


@video_bp.route('/video/<video_id>/stats', methods=['GET'])
@jwt_required
def get_video_stats(video_id):
    """
    Get watch statistics for a video.
    
    Response:
    {
        "stats": {
            "view_count": 10,
            "total_watch_time": 3600,
            "completion_count": 5
        }
    }
    """
    video = Video.find_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    stats = WatchHistory.get_video_stats(video_id)
    
    return jsonify({'stats': stats}), 200


@video_bp.route('/admin/reseed', methods=['POST'])
def reseed_videos():
    """
    Admin endpoint to force reseed the videos database.
    Clears existing videos and adds 10 sample videos.
    
    WARNING: This is for demo/testing only! Remove in production.
    """
    from app import get_db
    db = get_db()
    
    # Clear existing videos
    db.videos.delete_many({})
    logger.info("Cleared existing videos")
    
    # Force reseed
    Video.seed_data()
    
    # Get new count
    count = db.videos.count_documents({})
    logger.info(f"Reseeded {count} videos")
    
    return jsonify({
        'message': f'Database reseeded with {count} videos',
        'count': count
    }), 200

