import os
import tempfile
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

# GitHub પરથી cookies.txt વાંચો
COOKIE_FILE_PATH = 'cookies.txt'

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'error': 'URL is required. Use ?url=YOUR_VIDEO_LINK'}), 400
    
    # Check if cookie file exists
    if not os.path.exists(COOKIE_FILE_PATH):
        return jsonify({'error': 'cookies.txt file not found in repository'}), 500
    
    try:
        ydl_opts = {
            'format': 'best',
            'cookiefile': COOKIE_FILE_PATH,  # Direct file path
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_download_url = info.get('url')
            
            return jsonify({
                'success': True,
                'title': info.get('title'),
                'duration': info.get('duration'),
                'download_url': video_download_url
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return 'Unacademy Downloader Ready! Use /download?url=VIDEO_LINK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
