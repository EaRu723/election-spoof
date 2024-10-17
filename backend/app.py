import logging
import asyncio
import httpx
import json
import time
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

fetch_time = 0
spoof_time = 0

# Fetch headlines from external APIs
async def fetch_external_headlines():
    global fetch_time
    start_time = time.time()
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
            return headlines

        try:
            results = await asyncio.gather(*[fetch_source(source) for source in sources])
            all_headlines = [item for sublist in results for item in sublist]
            fetch_time = time.time() - start_time
            logger.info(f"Fetching headlines took {fetch_time:.2f} seconds")
            logger.info(f"Total headlines fetched: {len(all_headlines)}")
            return all_headlines
        except Exception as exc:
            logger.error(f"An error occurred while fetching headlines: {exc}")
            raise HTTPException(status_code=500, detail=str(exc))

        return all_headlines

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
    global spoof_time
    await websocket.accept()
    logger.info(f"WebSocket connection established at {datetime.now().isoformat()}")

    all_headlines = await fetch_external_headlines()

    # Separate Fox and CNN headlines
    fox_headlines = [h for h in all_headlines if h["source"].lower() == "fox"]
    cnn_headlines = [h for h in all_headlines if h["source"].lower() == "cnn"]

    spoof_start_time = time.time()

    # Alternate between Fox and CNN headlines
    for fox_headline, cnn_headline in zip(fox_headlines, cnn_headlines):
        for headline in (fox_headline, cnn_headline):
            try:
                spoofed_headline = generate_spoof(headline["headline"])
                logger.info(f"Spoofed headline for {headline['source']} index {headline['index']}: {spoofed_headline}")
                await websocket.send_json({
                    "index": headline["index"],
                    "source": headline["source"],
                    "spoofed_headline": spoofed_headline
                })
            except Exception as e:
                error_message = f"Failed to generate spoof: {str(e)}"
                logger.error(f"Error spoofing {headline['source']} headline {headline['index']}: {error_message}")
                await websocket.send_json({
                    "index": headline["index"],
                    "source": headline["source"],
                    "spoofed_headline": error_message
                })
            
            logger.info(f"Spoofed headline sent for {headline['source']} index {headline['index']}")

    # Handle any remaining headlines if the counts are uneven
    remaining_headlines = fox_headlines[len(cnn_headlines):] + cnn_headlines[len(fox_headlines):]
    for headline in remaining_headlines:
        try:
            spoofed_headline = generate_spoof(headline["headline"])
            logger.info(f"Spoofed headline for {headline['source']} index {headline['index']}: {spoofed_headline}")
            await websocket.send_json({
                "index": headline["index"],
                "source": headline["source"],
                "spoofed_headline": spoofed_headline
            })
        except Exception as e:
            error_message = f"Failed to generate spoof: {str(e)}"
            logger.error(f"Error spoofing {headline['source']} headline {headline['index']}: {error_message}")
            await websocket.send_json({
                "index": headline["index"],
                "source": headline["source"],
                "spoofed_headline": error_message
            })
        
        logger.info(f"Spoofed headline sent for {headline['source']} index {headline['index']}")

    spoof_time = time.time() - spoof_start_time
    logger.info(f"Spoof time: {spoof_time:.2f} seconds")

    await websocket.close()

# Add a new endpoint to retrieve the timing information
@app.get("/timing")
async def get_timing():
    return {"fetch_time": fetch_time, "spoof_time": spoof_time}
