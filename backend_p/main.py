# backend_p/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Import our configuration
from .config import Config
# Import our API routes
from .api_routes import router

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/team", StaticFiles(directory="public/team"), name="team")
app.mount("/menu", StaticFiles(directory="public/menu"), name="menu")
app.mount("/events", StaticFiles(directory="public/events"), name="events")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(router)