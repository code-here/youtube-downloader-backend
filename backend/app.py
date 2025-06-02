from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/api/download', methods=['POST', 'OPTIONS'])
def download_video():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    data = request.get_json()
    url = data.get("url")
    quality = data.get("quality", "720")

    if not url:
        return {"error": "URL is required"}, 400

    video_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

    ydl_opts = {
        'format': f'bestvideo[height<={quality}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<={quality}]',
        'merge_output_format': 'mp4',
        'outtmpl': output_path,
        'quiet': True,
        'nooverwrites': True,
        'cachedir': False,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        def generate():
            with open(output_path, 'rb') as f:
                while chunk := f.read(8192):
                    yield chunk
            os.remove(output_path)

        return Response(generate(),
                        mimetype='video/mp4',
                        headers={
                            'Content-Disposition': f'attachment; filename="video_{quality}p.mp4"',
                            'Content-Type': 'application/octet-stream'
                        })

    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/api/info', methods=['POST', 'OPTIONS'])
def get_video_info():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()

    data = request.get_json()
    url = data.get("url")

    if not url:
        return {"error": "URL is required"}, 400

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail")
            }
    except Exception as e:
        return {"error": str(e)}, 500

def _build_cors_preflight_response():
    response = jsonify({'status': 'ok'})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

if __name__ == "__main__":
    app.run(port=5000, debug=True, threaded=True)
