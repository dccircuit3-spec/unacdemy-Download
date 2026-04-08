import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import time

app = Flask(__name__)
CORS(app)

def extract_expiry_time(url):
    """YouTube URL માંથી expiry timestamp કાઢો"""
    import urllib.parse
    
    # expiry (exp) પેરામીટર શોધો
    match = re.search(r'expire=(\d+)', url)
    if match:
        expire_timestamp = int(match.group(1))
        return expire_timestamp
    return None

def format_expiry(expire_timestamp):
    """Timestamp ને રીડેબલ ફોર્મેટમાં બદલો"""
    if not expire_timestamp:
        return "Unknown"
    
    current_time = int(time.time())
    remaining = expire_timestamp - current_time
    
    if remaining <= 0:
        return "Expired"
    
    hours = remaining // 3600
    minutes = (remaining % 3600) // 60
    
    if hours > 0:
        return f"{hours} hour(s) {minutes} minute(s)"
    else:
        return f"{minutes} minute(s)"

def get_youtube_direct_link(youtube_url):
    """YouTube વીડિયોની Direct Download Link + Expiry Time મેળવો"""
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
            video_url = info.get('url')
            if not video_url and 'formats' in info:
                for f in info['formats']:
                    if f.get('ext') == 'mp4' and f.get('vcodec') != 'none':
                        video_url = f.get('url')
                        break
            
            if not video_url:
                return None, "No direct MP4 link found"
            
            # Expiry time extract કરો
            expire_timestamp = extract_expiry_time(video_url)
            
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'views': info.get('view_count', 0),
                'thumbnail': info.get('thumbnail', ''),
                'direct_link': video_url,
                'expiry_timestamp': expire_timestamp,
                'expiry_in': format_expiry(expire_timestamp),
                'current_time': int(time.time())
            }, None
            
    except Exception as e:
        return None, str(e)


@app.route('/yt', methods=['GET', 'POST'])
def youtube_direct():
    """YouTube Direct Link API - Expiry Time સાથે"""
    
    if request.method == 'GET':
        url = request.args.get('url')
    else:
        data = request.get_json()
        url = data.get('url') if data else None
    
    if not url:
        return jsonify({
            'success': False,
            'error': 'URL is required. Use ?url=YOUTUBE_LINK'
        }), 400
    
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return jsonify({
            'success': False,
            'error': 'This is not a YouTube URL.'
        }), 400
    
    video_info, error = get_youtube_direct_link(url)
    
    if error:
        return jsonify({
            'success': False,
            'error': error
        }), 500
    
    return jsonify({
        'success': True,
        'title': video_info['title'],
        'duration': f"{video_info['duration'] // 60}:{video_info['duration'] % 60:02d}",
        'uploader': video_info['uploader'],
        'views': video_info['views'],
        'thumbnail': video_info['thumbnail'],
        'direct_link': video_info['direct_link'],
        'expiry': {
            'timestamp': video_info['expiry_timestamp'],
            'human_readable': video_info['expiry_in'],
            'current_time': video_info['current_time']
        }
    })


@app.route('/', methods=['GET'])
def home():
    """API વપરાશની માહિતી"""
    return jsonify({
        'name': 'YouTube Direct Link Generator with Expiry',
        'version': '2.0.0',
        'endpoint': '/yt',
        'usage': {
            'method': 'GET or POST',
            'params': {'url': 'YouTube video URL'},
            'example': '/yt?url=https://youtu.be/dQw4w9WgXcQ'
        },
        'response': {
            'success': 'true/false',
            'title': 'Video title',
            'duration': 'Video duration',
            'uploader': 'Channel name',
            'views': 'View count',
            'thumbnail': 'Thumbnail URL',
            'direct_link': 'Direct MP4 download link',
            'expiry': {
                'timestamp': 'Unix timestamp when link expires',
                'human_readable': 'Remaining time (e.g., 5 hour(s) 30 minute(s))',
                'current_time': 'Current server time'
            }
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
