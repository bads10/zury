import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routers import dev, sellers, tryon

MEDIA_DIR = os.getenv("MEDIA_DIR", "/app/media")
os.makedirs(MEDIA_DIR, exist_ok=True)

app = FastAPI(title="Zury API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to specific origins in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/api/v1/media", StaticFiles(directory=MEDIA_DIR), name="media")

app.include_router(tryon.router)
app.include_router(sellers.router)
app.include_router(dev.router)


@app.get("/health")
def health():
    return {"status": "ok"}
