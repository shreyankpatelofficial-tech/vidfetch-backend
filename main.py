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
    
    # This finds the cookies.txt file you uploaded to GitHub
    cookie_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[ext=mp4]/best',
        # Tell yt-dlp to use your cookies
        'cookiefile': cookie_path,
        # Force the web client now that we have cookies
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'mweb'],
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
            for f in info.get('formats', []):
                if f.get('url') and f.get('vcodec') != 'none':
                    formats.append({
                        "quality": f.get('format_note') or f.get('resolution') or 'unknown',
                        "ext": f.get('ext', 'mp4'),
                        "filesize": f.get('filesize_string', ''),
                        "url": f.get('url')
                    })
            
            return {
                "title": info.get('title'),
                "author": info.get('uploader'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'),
                "formats": formats[:10]
            }
    except Exception as e:
        return {"error": f"YouTube Error: {str(e)}"}
