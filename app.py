import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

def get_youtube_direct_link(youtube_url):
    """YouTube વીડિયોની Direct Download Link (MP4) મેળવો"""
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # ફક્ત MP4 ફોર્મેટ
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
            # Direct Video URL મેળવો
            video_url = info.get('url')
            
            # જો ના મળે તો બીજા ફોર્મેટમાં શોધો
            if not video_url and 'formats' in info:
                for f in info['formats']:
                    if f.get('ext') == 'mp4' and f.get('vcodec') != 'none':
                        video_url = f.get('url')
                        break
            
            if not video_url:
                return None, "No direct MP4 link found"
            
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'views': info.get('view_count', 0),
                'thumbnail': info.get('thumbnail', ''),
                'direct_link': video_url
            }, None
            
    except Exception as e:
        return None, str(e)


@app.route('/yt', methods=['GET', 'POST'])
def youtube_direct():
    """YouTube Direct Link API - GET અથવા POST બંને ચાલશે"""
    
    # URL મેળવો
    if request.method == 'GET':
        url = request.args.get('url')
    else:
        data = request.get_json()
        url = data.get('url') if data else None
    
    # URL ચેક
    if not url:
        return jsonify({
            'success': False,
            'error': 'URL is required. Use ?url=YOUTUBE_LINK or POST {"url": "YOUTUBE_LINK"}'
        }), 400
    
    # YouTube URL છે કે નહીં ચેક કરો
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return jsonify({
            'success': False,
            'error': 'This is not a YouTube URL. Please provide a valid YouTube link.'
        }), 400
    
    # Direct Link મેળવો
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
        'direct_link': video_info['direct_link']
    })


@app.route('/', methods=['GET'])
def home():
    """API વપરાશની માહિતી"""
    return jsonify({
        'name': 'YouTube Direct Link Generator',
        'version': '1.0.0',
        'endpoint': '/yt',
        'usage': {
            'method': 'GET or POST',
            'params': {'url': 'YouTube video URL'},
            'example_1': '/yt?url=https://youtu.be/dQw4w9WgXcQ',
            'example_2': '/yt?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        },
        'response': {
            'success': 'true/false',
            'title': 'Video title',
            'duration': 'Video duration',
            'uploader': 'Channel name',
            'views': 'View count',
            'thumbnail': 'Thumbnail URL',
            'direct_link': 'Direct MP4 download link'
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
