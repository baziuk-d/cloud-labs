from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from src.api.routes import api_router
from src.services.emulator import emulator
from src.db.conn import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully")
    
    yield
    
    # Shutdown: Stop emulator and close database
    print("Shutting down...")
    await emulator.stop()
    await close_db()
    print("Shutdown complete")


app = FastAPI(title="Sensor Emulator", lifespan=lifespan)

# Include API routes
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Sensor Emulator API",
        "docs": "/docs",
        "status": "/api/emulator/status"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)