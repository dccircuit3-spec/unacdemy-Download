import os
import tempfile
from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

COOKIES_CONTENT = os.environ.get('UNACADEMY_COOKIES', '')

@app.route('/download', methods=['GET', 'POST'])
def download():
    # GET માંથી url લો (?url=...)
    if request.method == 'GET':
        video_url = request.args.get('url')
    else:  # POST
        video_url = request.json.get('url') if request.is_json else None
    
    if not video_url:
        return jsonify({'error': 'URL is required. Use ?url=YOUR_VIDEO_LINK'}), 400
    
    if not COOKIES_CONTENT:
        return jsonify({'error': 'Cookies not configured. Add UNACADEMY_COOKIES variable in Railway.'}), 500
    
    # Temp cookie file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(COOKIES_CONTENT)
        cookie_file = f.name
    
    try:
        ydl_opts = {
            'format': 'best',
            'cookiefile': cookie_file,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            video_download_url = info.get('url')
            if not video_download_url and 'requested_formats' in info:
                video_download_url = info['requested_formats'][0]['url']
            
            return jsonify({
                'success': True,
                'title': info.get('title'),
                'duration': info.get('duration'),
                'download_url': video_download_url
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.unlink(cookie_file)

@app.route('/')
def home():
    return '''
    <h2>Unacademy Downloader</h2>
    <p><b>ઉપયોગ કરવાની રીત:</b></p>
    <code>GET /download?url=UNACADEMY_VIDEO_URL</code>
    <br><br>
    <b>ઉદાહરણ:</b>
    <br>
    <a href="/download?url=https://unacademy.com/course/.../lecture/...">/download?url=https://unacademy.com/course/.../lecture/...</a>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
