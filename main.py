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
        # The fix: Grab best video + best audio, or fallback to best single file
        'format': 'bv*+ba/b', 
        'cookiefile': cookie_path,
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
                # Only include formats that have a direct URL
                if f.get('url'):
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
                "formats": formats[:15] # Return more formats to be safe
            }
    except Exception as e:
        return {"error": f"YouTube Error: {str(e)}"}
