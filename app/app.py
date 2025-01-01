"""Main module"""

from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from qbittorrentapi import Client

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import os
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


# Selenium Setup
def setup_driver():
    """Set up Selenium WebDriver."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless if you don't need the GUI
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)


def search_tpb(query):
    """Search Pirate Bay for torrents using Selenium."""
    driver = setup_driver()
    try:
        driver.get(f"https://thepiratebay.org/search.php?q={query}&cat=0")  # Open Pirate Bay homepage

        # Locate the search box and enter the query
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Wait for the results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ol"))
        )

        # Extract results
        results = []
        rows = driver.find_elements(By.CSS_SELECTOR, "ol > li")
        for row in rows:
            try:
                category = row.find_element(By.CSS_SELECTOR, "a").text.strip()
                subcategory = row.find_elements(By.CSS_SELECTOR, "a")[1].text.strip()
                title = row.find_element(By.CSS_SELECTOR, ".item-title > a").text.strip()
                magnet = row.find_element(By.CSS_SELECTOR, "a[href^='magnet']").get_attribute("href")
                seeders = int(row.find_element(By.CSS_SELECTOR, ".item-seed").text.strip())
                leechers = int(row.find_element(By.CSS_SELECTOR, ".item-leech").text.strip())
                results.append({"category": category, "subcategory": subcategory, "title": title, "magnet": magnet, "seeders": seeders, "leechers": leechers})
            except Exception as e:
                print(f"Error parsing row: {e}")

        return sorted(results, key=lambda x: x["seeders"], reverse=True)
    finally:
        driver.quit()  # Close the browser


@app.get("/")
def index(request: Request, response_class=HTMLResponse):
    """Return index.html"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search")
def search(query: str = Query(..., description="Search query for torrents")):
    """Search The Pirate Bay for available torrents"""
    try:
        results = search_tpb(query)
        return {"results": results}
    except Exception as e:
        print(e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/download")
async def download(request: Request):
    """Download a torrent using qBittorrent."""
    req = await request.json()
    folder = f"/mnt/{req['category']}"

    try:
        # Connect to qBittorrent
        qb = Client(host=QBITTORRENT_API)
        qb.auth_log_in(QBT_USERNAME, QBT_PASSWORD)

        # Add torrent and set sequential download
        qb.torrents_add(
            urls=req['magnet_link'],
            save_path=folder,
            is_sequential_download=True
        )

        # Refresh Plex (if applicable, replace with your logic)
        # os.system("curl http://127.0.0.1:32400/library/sections/all/refresh")

        return {"message": "Download started successfully."}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") from e

