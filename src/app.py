from typing import Annotated, List, Any, Optional, Dict, Hashable, Union
from pathlib import Path
from fastapi import (
    Depends,
    FastAPI,
    File,
    UploadFile,
    HTTPException,
    BackgroundTasks,
    responses
)
import io
import time

from scrape import scrape_urls


app = FastAPI()


@app.get("/")
def root():
    return {"Crawlee Scrape API": "Version 0.0"}


@app.get("/v0/scrape-urls/")
async def scrape_endpoint(
    urls: List[str],
    keywords: List[str] = ["esg", "investor"]
):
    results = await scrape_urls(urls, keywords)
    return results
