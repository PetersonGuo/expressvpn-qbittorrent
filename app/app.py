"""Main module"""

from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from qbittorrentapi import Client

import os
import re
import functools
from dotenv import load_dotenv

load_dotenv()

# Configuration
SEARCH_URL = "https://thepiratebay.org/search.php?"
QBITTORRENT_API = "http://127.0.0.1:8080"
QBT_USERNAME = os.getenv("QBT_USERNAME")
QBT_PASSWORD = os.getenv("QBT_PASSWORD")

templates = Jinja2Templates(directory="templates")

# FastAPI App
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to your frontend domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@functools.lru_cache(maxsize=128)
def search_tpb(query: str):
    resp = requests.get(f"https://apibay.org/q.php?q={query}", timeout=10)
    resp.raise_for_status()
    data = resp.json()  # a list of dicts
    results = []
    for item in data:
        results.append({
            "category": item["category"],
            "title":    item["name"],
            "magnet":   f"magnet:?xt=urn:btih:{item['info_hash']}",
            "seeders":  int(item["seeders"]),
            "leechers": int(item["leechers"]),
        })
    return sorted(results, key=lambda x: x["seeders"], reverse=True)


@app.get("/")
def index(request: Request, response_class=HTMLResponse):
    """Return index.html"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search")
def search(query: str = Query(..., description="Search query for torrents")):
    """Search The Pirate Bay for available torrents"""
    try:
        results = search_tpb(query.lower())
        return {"results": results}
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/download")
async def download(request: Request):
    """Download a torrent using qBittorrent."""
    req = await request.json()
    target_directory = f"/mnt/{req['category']}"
    filename = req.get("filename")
    magnet_link = req.get("magnet_link")

    if not filename or not magnet_link:
        print("Filename and magnet link are required.")
        raise HTTPException(status_code=400, detail="Filename and magnet link are required.")

    # CATEGORY_MAP = {
    #     0:   'All',
    #     100: 'Audio', 101: 'Music', 102: 'Audio books', 103: 'Sound clips', 104: 'FLAC', 199: 'Audio Other',
    #     200: 'Video', 201: 'Movies', 202: 'Movies DVDR', 203: 'Music videos', 204: 'Movie clips',
    #     205: 'TV shows', 206: 'Video Handheld', 207: 'HD – Movies', 208: 'HD – TV shows', 209: '3D', 299: 'Video Other',
    #     300: 'Applications', 301: 'App Windows', 302: 'App Mac', 303: 'App UNIX', 304: 'App Handheld',
    #     305: 'App iOS', 306: 'App Android', 399: 'App Other OS',
    #     400: 'Games', 401: 'Game PC', 402: 'Game Mac', 403: 'Game PSx', 404: 'Game XBOX360', 405: 'Game Wii',
    #     406: 'Game Handheld', 407: 'Game iOS', 408: 'Game Android', 499: 'Game Other',
    #     500: 'Porn', 501: 'Porn Movies', 502: 'Porn Movies DVDR', 503: 'Porn Pictures', 504: 'Porn Games',
    #     505: 'Porn HD – Movies', 506: 'Porn Movie clips', 599: 'Porn Other',
    #     600: 'Other', 601: 'E-books', 602: 'Comics', 603: 'Pictures', 604: 'Covers', 605: 'Physibles', 699: 'Other Other'
    # }

    try:
        # Parse the target directory
        if req['category'] in {205, 208}:
            target_directory = parse_tv_show_filename(filename)

            # Ensure the directory exists
            os.makedirs(target_directory, exist_ok=True)

        # Connect to qBittorrent
        qb = Client(host=QBITTORRENT_API)
        qb.auth_log_in(QBT_USERNAME, QBT_PASSWORD)

        # Add torrent and set sequential download
        qb.torrents_add(
            urls=magnet_link,
            save_path=target_directory,
            is_sequential_download=True,
            root_folder=(req['category'] != "tv")
        )

        return {"message": "Download started successfully.", "directory": target_directory}
    except ValueError as ve:
        print(ve)
        raise HTTPException(status_code=400, detail=f"Error: {str(ve)}") from ve
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e
    

def parse_tv_show_filename(filename: str) -> str:
    """
    Parse the filename to extract the show name and season,
    and construct the target directory path in the Plex format.
    Handles cases where entire seasons are downloaded as a package.
    """

    # Match "Show Name Sxx" format or generic "Show Name"
    pattern = r"^(.*?)(?:[.\s]*(?:Season\s|[Ss])(\d{1,2}))"
    match = re.match(pattern, filename)
    if not match:
        return f"/mnt/tv/{filename}"

    show_name = match.group(1).strip()
    season_number = int(match.group(2))

    # Base directory: Show Name/Season XX
    target_directory = os.path.join(
        "/mnt/tv",
        show_name,
        f"Season {season_number:02d}"
    )

    return target_directory
