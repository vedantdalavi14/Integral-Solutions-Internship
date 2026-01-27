from flask import Blueprint, request, jsonify, Response, stream_with_context
from app.models.video import Video
from app.utils.jwt_utils import (
    jwt_required,
    generate_playback_token,
    decode_playback_token,
)
import yt_dlp
import requests
import time

video_bp = Blueprint('video', __name__)

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


def extract_video_url(youtube_id):
    """
    Extract direct video URL using yt-dlp
    Returns a progressive MP4 URL for mobile streaming
    """
    # Check cache first
    cached = get_cached_url(youtube_id)
    if cached:
        print(f"✅ Using cached URL for {youtube_id}")
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
        print(f"🎬 Extracting video URL for {youtube_id}...")
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
                        print(f"✅ Found compatible format: {f.get('format_id')}")
                        break
            
            if video_url:
                print(f"✅ Extracted URL for {youtube_id}")
                cache_url(youtube_id, video_url)
                return video_url
            else:
                print(f"❌ No compatible format found for {youtube_id}")
    except Exception as e:
        print(f"❌ Error extracting video URL: {e}")
    
    return None


@video_bp.route('/dashboard', methods=['GET'])
@jwt_required
def get_dashboard():
    """
    Get dashboard with 2 active videos
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "videos": [
            {
                "id": "...",
                "title": "...",
                "description": "...",
                "thumbnail_url": "...",
                "playback_token": "..."  // Short-lived token for streaming
            }
        ]
    }
    
    IMPORTANT: youtube_id is NEVER exposed to the client
    """
    # Seed data if needed
    Video.seed_data()
    
    # Get 2 active videos
    videos = Video.find_active(limit=2)
    
    # Build response with playback tokens
    video_list = []
    for video in videos:
        playback_token = generate_playback_token(video._id, request.user_id)
        video_list.append(video.to_public_dict(playback_token=playback_token))
    
    return jsonify({
        'videos': video_list
    }), 200


@video_bp.route('/video/<video_id>/stream', methods=['GET'])
def get_stream(video_id):
    """
    Proxy video stream to the client
    
    This endpoint:
    1. Verifies the playback token
    2. Extracts direct video URL using yt-dlp
    3. Proxies the video bytes to the client
    
    The frontend uses expo-av Video component with native controls.
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
        return jsonify({'error': 'Invalid or expired playback token'}), 401
    
    # Verify video_id matches token
    if payload.get('video_id') != video_id:
        return jsonify({'error': 'Token does not match video'}), 403
    
    # Find video to get youtube_id
    video = Video.find_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    # Extract direct video URL using yt-dlp
    video_url = extract_video_url(video.youtube_id)
    
    if not video_url:
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
        print(f"❌ Streaming error: {e}")
        return jsonify({'error': 'Streaming failed'}), 500


@video_bp.route('/video/<video_id>/info', methods=['GET'])
@jwt_required
def get_video_info(video_id):
    """
    Get video information (for displaying before playing)
    
    Response includes a fresh playback token
    """
    video = Video.find_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    playback_token = generate_playback_token(video._id, request.user_id)
    
    return jsonify({
        'video': video.to_public_dict(playback_token=playback_token)
    }), 200
