from typing import Annotated, List, Any, Optional, Dict, Hashable, Union
from pydantic import BaseModel, Field
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

from scrape import scrape_urls, find_target_urls


class ScraperSchema(BaseModel):
    urls: List[str] = Field(example=["https://google.com"])
    keywords: List[str] = Field(default=["esg", "investor"])


app = FastAPI()


@app.get("/")
def root():
    return {"Crawlee Scrape API": "Version 0.0"}


@app.post("/v0/scrape-urls/")
async def scrape_endpoint(
    items: ScraperSchema
):
    results = await scrape_urls(items.urls, items.keywords)
    return results


@app.post("/v0/find-embeded-urls/")
async def scrape_endpoint(
    items: ScraperSchema
):
    results = await find_target_urls(items.urls, items.keywords)
    return results
