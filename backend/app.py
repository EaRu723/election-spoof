from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model import generate_spoof
import asyncio
import httpx
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be cautious with this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/fetch-headlines")
async def fetch_headlines():
    print(f"fetch-headlines called at: {datetime.now().isoformat()}")
    async with httpx.AsyncClient(timeout=30.0) as client:  # Set a 30-second timeout
        fox_params = {
            "query": "give me every headline on this page",
            "url": "https://www.foxnews.com/politics",
        }
        cnn_params = {
            "query": "give me every headline on this page",
            "url": "https://www.cnn.com/election/2024",
        }

        try:
            fox_response, cnn_response = await asyncio.gather(
                client.get("https://lsd.so/knawledge", params=fox_params),
                client.get("https://lsd.so/knawledge", params=cnn_params)
            )
            print(f"External API requests completed at: {datetime.now().isoformat()}")
            fox_data = fox_response.json()
            cnn_data = cnn_response.json()

            fox_headlines = [{"headline": h["headline"], "source": "fox"} for h in fox_data.get("results", [])]
            cnn_headlines = [{"headline": h["headline"], "source": "cnn"} for h in cnn_data.get("results", [])]

            return {"fox_headlines": fox_headlines, "cnn_headlines": cnn_headlines}
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request to external API timed out")
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"HTTP error occurred: {exc}")
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {exc}")

@app.get("/spoof-headline")
async def spoof_headline(headline: str):
    print(f"spoof-headline called at: {datetime.now().isoformat()} for headline: {headline}")
    spoofed_headline = generate_spoof(headline)
    print(f"Generated spoofed headline at: {datetime.now().isoformat()}: {spoofed_headline}")
    return {"spoofed_headline": spoofed_headline}
