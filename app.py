from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return jsonify({
            'title': info.get('title'),
            'url': info.get('url'),
        })

@app.route('/')
def home():
    return 'yt-dlp API is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
