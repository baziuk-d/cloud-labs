from fastapi import APIRouter
from src.api.emulator.views import router as emulator_router

api_router = APIRouter(prefix="/api")

# Include emulator routes
api_router.include_router(emulator_router)