import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import admin, auth, cart, health, orders, products, users
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
def startup() -> None:
    os.makedirs(settings.uploads_dir, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    logger.info("Database ensured and application started.")

# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin.router)

# ✅ Correct static files setup (ONLY ONCE)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ✅ Serve homepage
@app.get("/")
def index():
    return FileResponse("app/static/index.html")