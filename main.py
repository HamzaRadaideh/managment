from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.schemas.database import init_db
from pathlib import Path

# API routers
from app.api.routers.auths_routers import router as auth_router
from app.api.routers.tasks_routers import router as tasks_router
from app.api.routers.notes_routers import router as notes_router
from app.api.routers.collections_routers import router as collections_router
from app.api.routers.tags_routers import router as tags_router
from app.api.routers.search_routers import router as search_router

# Web router
from app.web.web_routers import router as web_router

app = FastAPI(
    title="Task & Note Manager",
    description="A powerful app to manage tasks and notes with collections and tags.",
    version="1.0.0",
)

# CORS (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "app"
STATIC_DIR = APP_DIR / "static"
TEMPLATES_DIR = APP_DIR / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Create ONE templates env with an absolute path and share it
app.state.templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API routers with /api/v1 prefix
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(notes_router, prefix="/api/v1")
app.include_router(collections_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")

# Include web router (handles HTML pages)
app.include_router(web_router)

@app.on_event("startup")
async def on_startup():
    await init_db()

# API Health check
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)