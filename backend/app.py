from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from model import generate_spoof

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Be cautious with this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/spoof-headline")
async def spoof_headline(headline: str):
    spoofed_headline = generate_spoof(headline)
    return {"spoofed_headline": spoofed_headline}
