import logging
import asyncio
import httpx
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from model import generate_spoof

# Initialize FastAPI app and configure middleware
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fetch headlines from external APIs
async def fetch_external_headlines():
    async with httpx.AsyncClient(timeout=30.0) as client:
        sources = [
            {"name": "fox", "url": "https://www.foxnews.com/politics"},
            {"name": "cnn", "url": "https://www.cnn.com/election/2024"}
        ]
        
        async def fetch_source(source):
            logger.info(f"Fetching headlines from {source['name']} at {source['url']}")
            params = {"query": "give me every headline on this page", "url": source["url"]}
            response = await client.get("https://lsd.so/knawledge", params=params)
            data = response.json()
            headlines = [{"headline": h["headline"], "source": source["name"], "index": i, "spoofed": None} 
                         for i, h in enumerate(data.get("results", []))]
            logger.info(f"Fetched {len(headlines)} headlines from {source['name']}")
            logger.debug(f"Headlines from {source['name']}: {json.dumps(headlines, indent=2)}")
            return headlines

        try:
            results = await asyncio.gather(*[fetch_source(source) for source in sources])
            all_headlines = [item for sublist in results for item in sublist]
            logger.info(f"Total headlines fetched: {len(all_headlines)}")
            logger.debug(f"All headlines: {json.dumps(all_headlines, indent=2)}")
            return all_headlines
        except Exception as exc:
            logger.error(f"An error occurred while fetching headlines: {exc}")
            raise HTTPException(status_code=500, detail=str(exc))

# Home route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Fetch and return headlines from external sources
@app.get("/fetch-headlines")
async def fetch_headlines():
    logger.info(f"fetch-headlines called at: {datetime.now().isoformat()}")
    all_headlines = await fetch_external_headlines()
    return JSONResponse(content={"headlines": all_headlines})

# WebSocket for streaming spoofed headlines
@app.websocket("/ws/spoof-headlines")
async def websocket_spoof(websocket: WebSocket):
    await websocket.accept()
    logger.info(f"WebSocket connection established at {datetime.now().isoformat()}")

    all_headlines = await fetch_external_headlines()

    for headline in all_headlines:
        try:
            spoofed_headline = generate_spoof(headline["headline"])
            logger.info(f"Spoofed headline for index {headline['index']}: {spoofed_headline}")
            await websocket.send_json({
                "index": headline["index"],
                "source": headline["source"],
                "spoofed_headline": spoofed_headline
            })
        except Exception as e:
            error_message = f"Failed to generate spoof: {str(e)}"
            logger.error(f"Error spoofing headline {headline['index']}: {error_message}")
            await websocket.send_json({
                "index": headline["index"],
                "source": headline["source"],
                "spoofed_headline": error_message
            })
        
        logger.info(f"Spoofed headline sent for index {headline['index']}")

    await websocket.close()
