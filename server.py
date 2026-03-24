from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the shared db instance
from core.database import db

# Import your new users router
from api.users import router as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to database...")
    await db.connect()
    yield
    print("Disconnecting from database...")
    await db.disconnect()

app = FastAPI(lifespan=lifespan)

# --- CORS Setup (CRITICAL FOR NEXT.JS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"], # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"], # Allows Authorization (JWT) headers
)

# --- Register Routers ---
app.include_router(users_router)

# --- Health Checks ---
@app.get("/")
@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "service": "Graphify Backend",
        "database": "connected" if db.is_connected() else "disconnected"
    }