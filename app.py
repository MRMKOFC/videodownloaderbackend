from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import instaloader
import os
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Create a downloads folder if it doesn't exist
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Home Route
@app.route('/')
def home():
    return "Flask Server is Running!"

# YouTube Downloader
@app.route('/download/youtube', methods=['POST'])
def download_youtube():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    ydl_opts = {'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s'}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return jsonify({"title": info['title'], "file": f"{info['title']}.{info['ext']}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Instagram Downloader
@app.route('/download/instagram', methods=['POST'])
def download_instagram():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    L = instaloader.Instaloader(download_pictures=True, download_videos=True)
    try:
        post = instaloader.Post.from_shortcode(L.context, url.split("/")[-2])
        L.download_post(post, target=DOWNLOAD_FOLDER)
        return jsonify({"message": "Download successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Facebook Downloader (Using External API)
@app.route('/download/facebook', methods=['POST'])
def download_facebook():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    fb_api_url = f"https://fbdownloaderapi.com/api?url={url}"
    response = requests.get(fb_api_url)
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch video"}), 500

# Telegram & TeraBox (Workaround Needed)
@app.route('/download/telegram', methods=['POST'])
def download_telegram():
    return jsonify({"message": "Telegram downloading requires a bot implementation."})

@app.route('/download/terabox', methods=['POST'])
def download_terabox():
    return jsonify({"message": "TeraBox downloading requires API access."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
