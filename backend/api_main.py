import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.game import router as game_router

load_dotenv()

app = FastAPI(
    title="Ink & Fate API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
