from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

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
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
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
        return {"error": str(e)}
