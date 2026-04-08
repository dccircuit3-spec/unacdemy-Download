import os
import re
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # બધા domains માંથી access મળે

# Cookies ફાઈલનો પાથ (GitHub માં રાખેલી)
COOKIE_FILE_PATH = 'cookies.txt'

def get_video_info(video_url):
    """વીડિયોની માહિતી અને ડાઉનલોડ URL મેળવો"""
    
    # Cookies ફાઈલ ચેક કરો
    if not os.path.exists(COOKIE_FILE_PATH):
        return None, "cookies.txt file not found in repository"
    
    ydl_opts = {
        'format': 'best',  # શ્રેષ્ઠ ક્વોલિટી
        'cookiefile': COOKIE_FILE_PATH,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'extract_flat': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            if info is None:
                return None, "Video not found or access denied"
            
            # વીડિયો URL મેળવો
            video_download_url = info.get('url')
            if not video_download_url and 'requested_formats' in info:
                video_download_url = info['requested_formats'][0]['url']
            
            if not video_download_url:
                return None, "Could not extract video URL"
            
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'download_url': video_download_url
            }, None
            
    except Exception as e:
        return None, str(e)


@app.route('/download', methods=['GET', 'POST'])
def download():
    """મુખ્ય API એન્ડપોઈન્ટ - GET અને POST બંને સપોર્ટ કરે છે"""
    
    # URL મેળવો (GET અથવા POST માંથી)
    if request.method == 'GET':
        video_url = request.args.get('url')
    else:
        data = request.get_json()
        video_url = data.get('url') if data else None
    
    # URL ચેક કરો
    if not video_url:
        return jsonify({
            'success': False,
            'error': 'URL is required. Use ?url=VIDEO_LINK or POST {"url": "VIDEO_LINK"}'
        }), 400
    
    # /class/ લિંક હોય તો ગાઇડ કરો
    if '/class/' in video_url and 'live' not in video_url and 'classroom' not in video_url:
        return jsonify({
            'success': False,
            'error': 'This is a class page link, not a video link.\n\nHow to get video link:\n1. Open this class on Unacademy\n2. Click "Go to Classroom" or "Watch now"\n3. Copy the URL from browser address bar when video is playing\n4. Use that URL here'
        }), 400
    
    # વીડિયો માહિતી મેળવો
    video_info, error = get_video_info(video_url)
    
    if error:
        return jsonify({
            'success': False,
            'error': error
        }), 500
    
    return jsonify({
        'success': True,
        'title': video_info['title'],
        'duration': video_info['duration'],
        'uploader': video_info['uploader'],
        'download_url': video_info['download_url']
    })


@app.route('/', methods=['GET'])
def home():
    """હોમ પેજ - API વપરાશની માહિતી"""
    return jsonify({
        'name': 'Unacademy Video Downloader API',
        'version': '1.0.0',
        'endpoints': {
            '/download': {
                'method': 'GET or POST',
                'params': {
                    'url': 'Unacademy video URL (live session or classroom)'
                },
                'example': '/download?url=https://unacademy.com/livesession/...'
            },
            '/': {
                'method': 'GET',
                'description': 'This help page'
            }
        },
        'note': 'Do NOT use /class/ links. Play the video first, then copy the URL from browser.'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
