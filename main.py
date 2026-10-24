from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/extract")
async def extract(data: dict):
    url = data.get("url")
    if not url:
        return {"error": "No URL provided"}
    
    cookie_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        # 1. Force a specific, pre-merged format (18 = 360p MP4, 22 = 720p MP4)
        'format': '18/22/best', 
        # 2. Disable format checks to prevent the metadata error
        'check_formats': False, 
        'cookiefile': cookie_path,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web'],
                'skip': ['hls', 'dash'], # Skip streaming formats that require ffmpeg
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            formats = []
            # Loop through formats and safely extract URLs
            for f in info.get('formats', []):
                if f.get('url'):
                    formats.append({
                        "quality": f.get('format_note') or f.get('resolution') or f"Format {f.get('format_id')}",
                        "ext": f.get('ext', 'mp4'),
                        "filesize": f.get('filesize_string', ''),
                        "url": f.get('url')
                    })
            
            # If no formats found, try to get the direct URL from the root info
            if not formats and info.get('url'):
                 formats.append({
                        "quality": info.get('resolution') or 'HD',
                        "ext": info.get('ext', 'mp4'),
                        "filesize": info.get('filesize_string', ''),
                        "url": info.get('url')
                    })

            return {
                "title": info.get('title'),
                "author": info.get('uploader'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'),
                "formats": formats
            }
    except Exception as e:
        return {"error": f"yt-dlp Error: {str(e)}"}
