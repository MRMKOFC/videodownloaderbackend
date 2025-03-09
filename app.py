from flask import Flask, request, jsonify
import os
import yt_dlp
import instaloader
from facebook_scraper import get_posts  # For Facebook post details

app = Flask(__name__)

# Function to download YouTube videos
def download_youtube_video(url):
    try:
        ydl_opts = {
            'outtmpl': 'download/youtube/%(title)s.%(ext)s',
            'format': 'best',  # Best quality
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading YouTube video: {url}")
            ydl.download([url])
            print("Download complete!")
            return True
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")
        return False

# Function to download Instagram posts (video only)
def download_instagram_post(url):
    try:
        loader = instaloader.Instaloader(dirname_pattern="download/instagram")
        shortcode = url.split("/")[-2]  # Extract shortcode from URL
        post = instaloader.Post.from_shortcode(loader.context, shortcode)
        print(f"Downloading Instagram post: {post.url}")
        if post.is_video:
            loader.download_post(post, target=post.owner_username)
            print("Download complete!")
            return True
        else:
            print("This post does not contain a video.")
            return False
    except Exception as e:
        print(f"Error downloading Instagram post: {e}")
        return False

# Function to download Facebook videos
def download_facebook_video(url):
    try:
        ydl_opts = {
            'outtmpl': 'download/facebook/%(title)s.%(ext)s',
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading Facebook video: {url}")
            ydl.download([url])
            print("Download complete!")
            return True
    except Exception as e:
        print(f"Error downloading Facebook video: {e}")
        return False

# Function to scrape Facebook post details
def get_facebook_post_details(url):
    try:
        posts = list(get_posts(post_urls=[url], cookies="cookies.txt"))
        if posts:
            post = posts[0]
            return {
                "text": post.get('text', 'No text available'),
                "likes": post.get('likes', 0),
                "comments": post.get('comments', 0),
                "shares": post.get('shares', 0),
                "video_url": post.get('video', 'No video found'),
            }
        return {"error": "Could not fetch post details"}
    except Exception as e:
        return {"error": f"Facebook scraping failed: {e}"}

# Function to download Twitter (X) videos
def download_twitter_video(url):
    try:
        ydl_opts = {
            'outtmpl': 'download/twitter/%(title)s.%(ext)s',
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading Twitter video: {url}")
            ydl.download([url])
            print("Download complete!")
            return True
    except Exception as e:
        print(f"Error downloading Twitter video: {e}")
        return False

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    if "youtube.com" in url or "youtu.be" in url:
        success = download_youtube_video(url)
    elif "instagram.com" in url:
        success = download_instagram_post(url)
    elif "facebook.com" in url:
        success = download_facebook_video(url)
        post_details = get_facebook_post_details(url)
        return jsonify({"message": "Facebook video download started", "post_details": post_details}), 200
    elif "twitter.com" in url or "x.com" in url:
        success = download_twitter_video(url)
    else:
        return jsonify({"error": "Unsupported platform"}), 400

    if success:
        return jsonify({"message": "Download started"}), 200
    else:
        return jsonify({"error": "Download failed"}), 500

if __name__ == "__main__":
    # Create directories for downloads
    os.makedirs("download/youtube", exist_ok=True)
    os.makedirs("download/instagram", exist_ok=True)
    os.makedirs("download/facebook", exist_ok=True)
    os.makedirs("download/twitter", exist_ok=True)

    app.run(host="0.0.0.0", port=5000)