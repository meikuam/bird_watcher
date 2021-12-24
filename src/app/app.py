import os
import sys
sys.path.append('.')

import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, List
from fastapi import APIRouter, Request, Response, status

from src.app.video_router import video_router
from src.app.control_router import control_router


app = FastAPI()

app.include_router(video_router, prefix="/api/video", tags=["video"])
app.include_router(control_router, prefix="/api/control", tags=["control"])

templates = Jinja2Templates(directory="www/templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, log_level="info")
