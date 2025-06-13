"""Main module"""

import functools
import logging
import os
import re

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from qbittorrentapi import Client

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
SEARCH_URL = "https://thepiratebay.org/search.php?"
QBITTORRENT_API = f"http://127.0.0.1:{os.getenv('QBITTORRENT_WEBUI_PORT', 8080)}"
QBT_USERNAME = os.getenv("QBT_USERNAME")
QBT_PASSWORD = os.getenv("QBT_PASSWORD")
MAGNET_REGEX = re.compile(r"^magnet:\?xt=urn:btih:[0-9a-fA-F]{40}.*$")

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
            "category": int(item["category"]),
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
        results = search_tpb(query.strip().lower())
        return {"results": results}
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/download")
async def download(request: Request):
    """Download a torrent using qBittorrent."""
    TV_CATEGORIES = {205, 208, 212}  # TV shows
    MOVIE_CATEGORIES = {201, 202, 204, 207, 211, 501, 502, 505, 506, 507}  # Movies
    req = await request.json()
    logger.info(f"Download request: {req}")
    filename = req.get("filename")
    magnet_link = req.get("magnet_link")
    category = req.get("category")

    if not category or category not in (TV_CATEGORIES | MOVIE_CATEGORIES):
        raise HTTPException(status_code=400, detail="Invalid category specified.")

    if not filename or not magnet_link:
        print("Filename and magnet link are required.")
        raise HTTPException(status_code=400, detail="Filename and magnet link are required.")

    if not MAGNET_REGEX.match(magnet_link):
        raise HTTPException(status_code=400, detail="Invalid magnet link format.")

    if "/" in filename or "\\" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    target_directory = f"/mnt/movies"

    try:
        # Parse the target directory
        if category in TV_CATEGORIES:
            target_directory = parse_tv_show_filename(filename)

        # Connect to qBittorrent
        qb = Client(host=QBITTORRENT_API)
        qb.auth_log_in(QBT_USERNAME, QBT_PASSWORD)

        # Add torrent and set sequential download
        content_layout = "Subfolder" if category in MOVIE_CATEGORIES else "NoSubfolder"
        qb.torrents_add(
            urls=magnet_link,
            save_path=target_directory,
            is_sequential_download=True,
            content_layout=content_layout,
        )

        return {"message": "Download started successfully.", "directory": target_directory}
    except ValueError as ve:
        logger.error(f"ValueError: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Error: {str(ve)}") from ve
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
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
