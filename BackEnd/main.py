"""
main.py
--------
Application entrypoint. Run with:
    uvicorn main:app --reload --port 8000

Automatic docs (Swagger UI) available at: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from api.routes import router as predict_router

app = FastAPI(
    title="AI Montir - Predictive Maintenance API",
    description="Menggabungkan Predictive AI (deteksi kegagalan) dan Generative AI (instruksi perbaikan) untuk mesin conveyor & motor listrik pabrik.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "FrontEnd"

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.get("/")
def serve_index():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"status": "ok", "service": "AI Montir Backend", "docs": "/docs"}
